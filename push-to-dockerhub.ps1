# Script para subir Microservicio 6 a Docker Hub
# PowerShell Script

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Subir Microservicio 6 a Docker Hub" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Solicitar usuario de Docker Hub
$dockerUsername = Read-Host "Ingresa tu usuario de Docker Hub"

if ([string]::IsNullOrWhiteSpace($dockerUsername)) {
    Write-Host "Error: Debes ingresar un usuario de Docker Hub" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Paso 1: Iniciando sesión en Docker Hub..." -ForegroundColor Yellow
docker login

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: No se pudo iniciar sesión en Docker Hub" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Paso 2: Etiquetando la imagen..." -ForegroundColor Yellow
$imageName = "microservicio6"
$tag = "latest"
$dockerHubImage = "$dockerUsername/$imageName`:$tag"

docker tag $imageName`:$tag $dockerHubImage

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: No se pudo etiquetar la imagen" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Imagen etiquetada como: $dockerHubImage" -ForegroundColor Green

Write-Host ""
Write-Host "Paso 3: Subiendo la imagen a Docker Hub..." -ForegroundColor Yellow
docker push $dockerHubImage

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: No se pudo subir la imagen" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  ✓ Imagen subida exitosamente!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "Tu imagen está disponible en:" -ForegroundColor Cyan
Write-Host "  docker pull $dockerHubImage" -ForegroundColor White
Write-Host ""
Write-Host "También puedes etiquetarla con una versión específica:" -ForegroundColor Yellow
Write-Host "  docker tag $imageName`:latest $dockerUsername/$imageName`:v1.0.0" -ForegroundColor White
Write-Host "  docker push $dockerUsername/$imageName`:v1.0.0" -ForegroundColor White
Write-Host ""
