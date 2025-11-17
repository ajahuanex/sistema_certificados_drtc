# Pruebas Locales Automatizadas
# PowerShell Script

$ErrorActionPreference = "Continue"
$SERVER_URL = "http://localhost:7070"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧪 PRUEBAS LOCALES AUTOMATIZADAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testResults = @()

# Función para registrar resultados
function Add-TestResult {
    param($Name, $Status, $Message)
    $script:testResults += [PSCustomObject]@{
        Test = $Name
        Status = $Status
        Message = $Message
    }
}

# ============================================
# 1. Verificar servidor
# ============================================
Write-Host "[1/10] Verificando servidor..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$SERVER_URL/admin/" -Method Head -TimeoutSec 5 -UseBasicParsing
    Write-Host "[OK] Servidor respondiendo (Status: $($response.StatusCode))" -ForegroundColor Green
    Add-TestResult "Servidor" "OK" "Respondiendo correctamente"
} catch {
    Write-Host "[ERROR] Servidor no responde" -ForegroundColor Red
    Write-Host "Inicia el servidor con: python manage.py runserver 7070" -ForegroundColor Yellow
    Add-TestResult "Servidor" "ERROR" "No responde"
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}
Write-Host ""

# ============================================
# 2. Verificar archivos estáticos
# ============================================
Write-Host "[2/10] Verificando archivos estáticos..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$SERVER_URL/static/admin/css/base.css" -Method Head -TimeoutSec 5 -UseBasicParsing
    Write-Host "[OK] Archivos estáticos accesibles" -ForegroundColor Green
    Add-TestResult "Archivos Estáticos" "OK" "Accesibles"
} catch {
    Write-Host "[WARN] Archivos estáticos no accesibles" -ForegroundColor Yellow
    Add-TestResult "Archivos Estáticos" "WARN" "No accesibles"
}
Write-Host ""

# ============================================
# 3. Verificar base de datos
# ============================================
Write-Host "[3/10] Verificando base de datos..." -ForegroundColor Yellow
$dbCheck = python manage.py check --database default 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Base de datos OK" -ForegroundColor Green
    Add-TestResult "Base de Datos" "OK" "Funcionando"
} else {
    Write-Host "[ERROR] Problemas con la base de datos" -ForegroundColor Red
    Add-TestResult "Base de Datos" "ERROR" "Problemas detectados"
}
Write-Host ""

# ============================================
# 4. Verificar migraciones
# ============================================
Write-Host "[4/10] Verificando migraciones..." -ForegroundColor Yellow
$migrations = python manage.py showmigrations --plan | Select-String "\[ \]"
if ($migrations) {
    Write-Host "[WARN] Hay migraciones pendientes" -ForegroundColor Yellow
    Write-Host "Ejecuta: python manage.py migrate" -ForegroundColor Yellow
    Add-TestResult "Migraciones" "WARN" "Pendientes"
} else {
    Write-Host "[OK] Todas las migraciones aplicadas" -ForegroundColor Green
    Add-TestResult "Migraciones" "OK" "Aplicadas"
}
Write-Host ""

# ============================================
# 5. Verificar superusuario
# ============================================
Write-Host "[5/10] Verificando superusuario..." -ForegroundColor Yellow
$superuserCheck = python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0 if User.objects.filter(is_superuser=True).exists() else 1)"
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Superusuario existe" -ForegroundColor Green
    Add-TestResult "Superusuario" "OK" "Existe"
} else {
    Write-Host "[WARN] No hay superusuario" -ForegroundColor Yellow
    Write-Host "Ejecuta: python manage.py create_superuser_if_not_exists" -ForegroundColor Yellow
    Add-TestResult "Superusuario" "WARN" "No existe"
}
Write-Host ""

# ============================================
# 6. Contar registros
# ============================================
Write-Host "[6/10] Contando registros..." -ForegroundColor Yellow
$counts = python manage.py shell -c "from certificates.models import Event, Participant, Certificate; print(f'{Event.objects.count()}|{Participant.objects.count()}|{Certificate.objects.count()}')"
$countsArray = $counts -split '\|'
Write-Host "  - Eventos: $($countsArray[0])" -ForegroundColor Cyan
Write-Host "  - Participantes: $($countsArray[1])" -ForegroundColor Cyan
Write-Host "  - Certificados: $($countsArray[2])" -ForegroundColor Cyan
Add-TestResult "Registros" "OK" "Eventos: $($countsArray[0]), Participantes: $($countsArray[1]), Certificados: $($countsArray[2])"
Write-Host ""

# ============================================
# 7. Verificar configuración
# ============================================
Write-Host "[7/10] Verificando configuración..." -ForegroundColor Yellow
$configCheck = python manage.py check 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Configuración correcta" -ForegroundColor Green
    Add-TestResult "Configuración" "OK" "Correcta"
} else {
    Write-Host "[ERROR] Problemas de configuración" -ForegroundColor Red
    Write-Host $configCheck
    Add-TestResult "Configuración" "ERROR" "Problemas detectados"
}
Write-Host ""

# ============================================
# 8. Verificar templates
# ============================================
Write-Host "[8/10] Verificando templates..." -ForegroundColor Yellow
$templatesOK = $true
if (Test-Path "templates\admin\dashboard.html") {
    Write-Host "[OK] Template dashboard existe" -ForegroundColor Green
} else {
    Write-Host "[WARN] Template dashboard no encontrado" -ForegroundColor Yellow
    $templatesOK = $false
}
if (Test-Path "templates\certificates\query.html") {
    Write-Host "[OK] Template query existe" -ForegroundColor Green
} else {
    Write-Host "[WARN] Template query no encontrado" -ForegroundColor Yellow
    $templatesOK = $false
}
Add-TestResult "Templates" $(if ($templatesOK) {"OK"} else {"WARN"}) "Verificados"
Write-Host ""

# ============================================
# 9. Verificar directorio media
# ============================================
Write-Host "[9/10] Verificando directorio media..." -ForegroundColor Yellow
if (Test-Path "media") {
    Write-Host "[OK] Directorio media existe" -ForegroundColor Green
    $certCount = (Get-ChildItem "media\certificates" -ErrorAction SilentlyContinue | Measure-Object).Count
    if ($certCount -gt 0) {
        Write-Host "[OK] Hay $certCount certificados generados" -ForegroundColor Green
    } else {
        Write-Host "[INFO] No hay certificados generados aún" -ForegroundColor Cyan
    }
    Add-TestResult "Directorio Media" "OK" "Existe con $certCount certificados"
} else {
    Write-Host "[WARN] Directorio media no existe" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "media\certificates" -Force | Out-Null
    Write-Host "[OK] Directorios creados" -ForegroundColor Green
    Add-TestResult "Directorio Media" "WARN" "Creado"
}
Write-Host ""

# ============================================
# 10. Probar endpoints principales
# ============================================
Write-Host "[10/10] Probando endpoints principales..." -ForegroundColor Yellow
$endpoints = @(
    @{Name="Admin"; URL="$SERVER_URL/admin/"},
    @{Name="Dashboard"; URL="$SERVER_URL/admin/dashboard/"},
    @{Name="Consulta"; URL="$SERVER_URL/consulta/"}
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $endpoint.URL -Method Head -TimeoutSec 5 -UseBasicParsing
        Write-Host "[OK] $($endpoint.Name): $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] $($endpoint.Name): No accesible" -ForegroundColor Yellow
    }
}
Write-Host ""

# ============================================
# RESUMEN
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ RESUMEN DE PRUEBAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$okCount = ($testResults | Where-Object {$_.Status -eq "OK"}).Count
$warnCount = ($testResults | Where-Object {$_.Status -eq "WARN"}).Count
$errorCount = ($testResults | Where-Object {$_.Status -eq "ERROR"}).Count

Write-Host "Total de pruebas: $($testResults.Count)" -ForegroundColor Cyan
Write-Host "  ✅ OK: $okCount" -ForegroundColor Green
Write-Host "  ⚠️  WARN: $warnCount" -ForegroundColor Yellow
Write-Host "  ❌ ERROR: $errorCount" -ForegroundColor Red
Write-Host ""

# Mostrar tabla de resultados
$testResults | Format-Table -AutoSize

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📋 URLs PARA PRUEBAS MANUALES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Admin:      $SERVER_URL/admin/" -ForegroundColor White
Write-Host "   Usuario:    admin" -ForegroundColor Gray
Write-Host "   Contraseña: admin123" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Dashboard:  $SERVER_URL/admin/dashboard/" -ForegroundColor White
Write-Host ""
Write-Host "3. Consulta:   $SERVER_URL/consulta/" -ForegroundColor White
Write-Host "   DNI prueba: 99238323" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Verificar:  $SERVER_URL/verificar/9f446c3e-6acc-4ba9-a49d-8a998a331f89/" -ForegroundColor White
Write-Host ""

# ============================================
# Preguntar si abrir navegador
# ============================================
$openBrowser = Read-Host "¿Abrir navegador para pruebas manuales? (S/N)"
if ($openBrowser -eq "S" -or $openBrowser -eq "s") {
    Write-Host ""
    Write-Host "Abriendo navegador..." -ForegroundColor Yellow
    Start-Process "$SERVER_URL/admin/"
    Start-Sleep -Seconds 2
    Start-Process "$SERVER_URL/admin/dashboard/"
    Start-Sleep -Seconds 2
    Start-Process "$SERVER_URL/consulta/"
    Write-Host "[OK] Navegador abierto con las URLs principales" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📋 SIGUIENTE PASO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Revisa la guía completa en: GUIA_PRUEBAS_LOCALES.md" -ForegroundColor White
Write-Host ""
Write-Host "Para pruebas de producción local con Docker:" -ForegroundColor White
Write-Host "  test-produccion-local.bat" -ForegroundColor Cyan
Write-Host ""
Read-Host "Presiona Enter para salir"
