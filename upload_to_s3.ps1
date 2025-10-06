# Script para subir datos de ejemplo a S3
# Ejecuta este script desde PowerShell en Windows

$BUCKET = "mvanalitica"
$REGION = "us-east-1"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Subiendo datos de ejemplo a S3" -ForegroundColor Cyan
Write-Host "  Bucket: $BUCKET" -ForegroundColor Cyan
Write-Host "  Region: $REGION" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que AWS CLI esté instalado
try {
    aws --version | Out-Null
} catch {
    Write-Host "❌ ERROR: AWS CLI no está instalado" -ForegroundColor Red
    Write-Host "   Instala desde: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Verificar que el bucket existe
Write-Host "🔍 Verificando bucket S3..." -ForegroundColor Yellow
$bucketExists = aws s3 ls "s3://$BUCKET" --region $REGION 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ El bucket s3://$BUCKET no existe o no tienes permisos" -ForegroundColor Red
    Write-Host "   Creando bucket..." -ForegroundColor Yellow
    aws s3 mb "s3://$BUCKET" --region $REGION
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Bucket creado exitosamente" -ForegroundColor Green
    } else {
        Write-Host "❌ Error al crear el bucket" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Bucket verificado" -ForegroundColor Green
}

Write-Host ""

# Subir cada archivo CSV
$files = @(
    @{file="scraped_acount.csv"; path="scraped_acount/"},
    @{file="admin_profiles.csv"; path="admin_profiles/"},
    @{file="quest_and_answer.csv"; path="quest_and_answer/"},
    @{file="admin_tiktok_metrics.csv"; path="admin_tiktok_metrics/"}
)

foreach ($item in $files) {
    $file = $item.file
    $s3path = $item.path
    
    if (Test-Path "sample_data\$file") {
        Write-Host "📤 Subiendo $file..." -ForegroundColor Yellow
        aws s3 cp "sample_data\$file" "s3://$BUCKET/$s3path" --region $REGION
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $file subido exitosamente" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Error al subir $file" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️  Archivo $file no encontrado" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ✅ Proceso completado" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Ve a AWS Athena Console: https://console.aws.amazon.com/athena/" -ForegroundColor White
Write-Host "2. Ejecuta el script: create_athena_tables.sql" -ForegroundColor White
Write-Host "3. Verifica las tablas: SHOW TABLES IN scrapetok;" -ForegroundColor White
Write-Host "4. Prueba tu API: curl http://localhost:8006/users/most_scraped?limit=5" -ForegroundColor White
Write-Host ""
