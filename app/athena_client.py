import boto3
import time
import os
from dotenv import load_dotenv

# 📦 Cargar variables del archivo .env
load_dotenv()

DATABASE = os.getenv('DATABASE', 'scrapetok_db')
OUTPUT_BUCKET = os.getenv('OUTPUT_BUCKET', 's3://default-bucket/athena-results/')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')  # Para credenciales temporales

# Validaciones mínimas
if not DATABASE or not OUTPUT_BUCKET:
    print("⚠️  WARNING: Variables DATABASE u OUTPUT_BUCKET no configuradas. Usando valores por defecto.")
    print(f"   DATABASE={DATABASE}")
    print(f"   OUTPUT_BUCKET={OUTPUT_BUCKET}")

# Crear cliente de Athena
try:
    # Si hay credenciales en las variables de entorno, usarlas directamente
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        print("🔑 Usando credenciales de AWS desde variables de entorno")
        session_kwargs = {
            'aws_access_key_id': AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
            'region_name': AWS_DEFAULT_REGION
        }
        # Agregar session token si existe (credenciales temporales)
        if AWS_SESSION_TOKEN:
            session_kwargs['aws_session_token'] = AWS_SESSION_TOKEN
            print("🔐 Usando credenciales temporales (con session token)")
        
        session = boto3.Session(**session_kwargs)
        athena_client = session.client('athena')
        print(f"✅ Cliente de Athena inicializado correctamente en región: {AWS_DEFAULT_REGION}")
    else:
        # Intentar usar el perfil default de AWS CLI
        print("🔑 Intentando usar perfil 'default' de AWS CLI")
        session = boto3.Session(profile_name='default')
        athena_client = session.client('athena')
        print("✅ Cliente de Athena inicializado correctamente usando perfil 'default'")
except Exception as e:
    print(f"⚠️  WARNING: No se pudo inicializar el cliente de Athena: {e}")
    print("   La API funcionará pero las consultas a Athena fallarán.")
    athena_client = None


def run_athena_query(query: str):
    """
    Ejecuta una consulta en AWS Athena y retorna los resultados.
    
    Args:
        query: String con la consulta SQL a ejecutar
        
    Returns:
        Lista de diccionarios con los resultados
        
    Raises:
        Exception: Si no hay cliente de Athena o la consulta falla
    """
    if athena_client is None:
        raise Exception("Cliente de Athena no inicializado. Verifica la configuración de AWS.")
    
    # Ejecutar la consulta
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': DATABASE},
        ResultConfiguration={'OutputLocation': OUTPUT_BUCKET}
    )

    query_execution_id = response['QueryExecutionId']

    # Esperar a que termine
    while True:
        status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        state = status['QueryExecution']['Status']['State']

        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(1)

    if state != 'SUCCEEDED':
        reason = status['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
        raise Exception(f'Query failed: {state} - {reason}')

    # Obtener resultados
    results = athena_client.get_query_results(QueryExecutionId=query_execution_id)

    # Transformar a JSON legible
    rows = results['ResultSet']['Rows']
    headers = [col['VarCharValue'] for col in rows[0]['Data']]  # Primera fila = headers
    data = []

    for row in rows[1:]:
        data.append({headers[i]: col.get('VarCharValue', None) for i, col in enumerate(row['Data'])})

    return data