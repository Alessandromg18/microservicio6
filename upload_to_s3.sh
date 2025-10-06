#!/bin/bash
# Script para subir datos de ejemplo a S3
# Ejecuta este script desde Bash/Linux/Mac

BUCKET="mvanalitica"
REGION="us-east-1"

echo "================================================"
echo "  Subiendo datos de ejemplo a S3"
echo "  Bucket: $BUCKET"
echo "  Region: $REGION"
echo "================================================"
echo ""

# Verificar que AWS CLI esté instalado
if ! command -v aws &> /dev/null; then
    echo "❌ ERROR: AWS CLI no está instalado"
    echo "   Instala desde: https://aws.amazon.com/cli/"
    exit 1
fi

# Verificar que el bucket existe
echo "🔍 Verificando bucket S3..."
if ! aws s3 ls "s3://$BUCKET" --region $REGION &> /dev/null; then
    echo "❌ El bucket s3://$BUCKET no existe o no tienes permisos"
    echo "   Creando bucket..."
    aws s3 mb "s3://$BUCKET" --region $REGION
    if [ $? -eq 0 ]; then
        echo "✅ Bucket creado exitosamente"
    else
        echo "❌ Error al crear el bucket"
        exit 1
    fi
else
    echo "✅ Bucket verificado"
fi

echo ""

# Subir cada archivo CSV
declare -a files=(
    "scraped_acount.csv:scraped_acount/"
    "admin_profiles.csv:admin_profiles/"
    "quest_and_answer.csv:quest_and_answer/"
    "admin_tiktok_metrics.csv:admin_tiktok_metrics/"
)

for item in "${files[@]}"; do
    IFS=':' read -r file s3path <<< "$item"
    
    if [ -f "sample_data/$file" ]; then
        echo "📤 Subiendo $file..."
        aws s3 cp "sample_data/$file" "s3://$BUCKET/$s3path" --region $REGION
        
        if [ $? -eq 0 ]; then
            echo "   ✅ $file subido exitosamente"
        else
            echo "   ❌ Error al subir $file"
        fi
    else
        echo "   ⚠️  Archivo $file no encontrado"
    fi
done

echo ""
echo "================================================"
echo "  ✅ Proceso completado"
echo "================================================"
echo ""
echo "Próximos pasos:"
echo "1. Ve a AWS Athena Console: https://console.aws.amazon.com/athena/"
echo "2. Ejecuta el script: create_athena_tables.sql"
echo "3. Verifica las tablas: SHOW TABLES IN scrapetok;"
echo "4. Prueba tu API: curl http://localhost:8006/users/most_scraped?limit=5"
echo ""
