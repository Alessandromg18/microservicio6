import boto3
import time
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from app.athena_client import run_athena_query
from app.models import EchoRequest

# 📦 Cargar variables del archivo .env
load_dotenv()

DATABASE = os.getenv('DATABASE')
OUTPUT_BUCKET = os.getenv('OUTPUT_BUCKET')

# Validaciones mínimas
if not DATABASE or not OUTPUT_BUCKET:
    raise Exception("Faltan variables DATABASE u OUTPUT_BUCKET en el .env")

# Crear cliente de Athena con el perfil default (sin forzar región)
session = boto3.Session(profile_name='default')
athena_client = session.client('athena')


def run_athena_query(query: str):
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