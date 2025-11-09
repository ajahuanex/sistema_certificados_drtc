#!/bin/bash

# 🧪 Script de Prueba del Sistema de Rollback
# Sistema de Certificados DRTC

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "🧪 Prueba del Sistema de Rollback"
echo "   DRTC Certificados"
echo "==========================================${NC}"
echo ""

# Configuración
COMPOSE_FILE="docker-compose.prod.yml"
TEST_BACKUP_DIR="test_backups"
TEST_LOG_DIR="test_logs"

# Función de utilidad
print_test() {
    echo -e "${BLUE}🧪 TEST: $1${NC}"
}

print_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
}

print_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  INFO: $1${NC}"
}

# Limpiar entorno de prueba
cleanup() {
    echo ""
    print_info "Limpiando entorno de prueba..."
    rm -rf "$TEST_BACKUP_DIR" "$TEST_LOG_DIR" 2>/dev/null || true
}

# Test 1: Verificar que los scripts existen
test_scripts_exist() {
    print_test "Verificando que los scripts existen"
    
    local all_exist=true
    
    if [ -f "update-production.sh" ]; then
        print_pass "update-production.sh existe"
    else
        print_fail "update-production.sh no existe"
        all_exist=false
    fi
    
    if [ -f "update-production.bat" ]; then
        print_pass "update-production.bat existe"
    else
        print_fail "update-production.bat no existe"
        all_exist=false
    fi
    
    if [ -f "rollback.sh" ]; then
        print_pass "rollback.sh existe"
    else
        print_fail "rollback.sh no existe"
        all_exist=false
    fi
    
    if [ -f "rollback.bat" ]; then
        print_pass "rollback.bat existe"
    else
        print_fail "rollback.bat no existe"
        all_exist=false
    fi
    
    if [ "$all_exist" = true ]; then
        return 0
    else
        return 1
    fi
}

# Test 2: Verificar que los scripts son ejecutables
test_scripts_executable() {
    print_test "Verificando que los scripts son ejecutables"
    
    if [ -x "update-production.sh" ]; then
        print_pass "update-production.sh es ejecutable"
    else
        print_info "Haciendo update-production.sh ejecutable"
        chmod +x update-production.sh
    fi
    
    if [ -x "rollback.sh" ]; then
        print_pass "rollback.sh es ejecutable"
    else
        print_info "Haciendo rollback.sh ejecutable"
        chmod +x rollback.sh
    fi
}

# Test 3: Verificar funciones en update-production.sh
test_update_script_functions() {
    print_test "Verificando funciones en update-production.sh"
    
    local functions=(
        "create_backup"
        "restore_backup"
        "check_health"
        "check_application_integrity"
        "perform_rollback"
        "send_notification"
    )
    
    local all_found=true
    
    for func in "${functions[@]}"; do
        if grep -q "^$func()" update-production.sh || grep -q "^# $func" update-production.sh; then
            print_pass "Función '$func' encontrada"
        else
            print_fail "Función '$func' no encontrada"
            all_found=false
        fi
    done
    
    if [ "$all_found" = true ]; then
        return 0
    else
        return 1
    fi
}

# Test 4: Verificar funciones en rollback.sh
test_rollback_script_functions() {
    print_test "Verificando funciones en rollback.sh"
    
    local functions=(
        "list_commits"
        "list_backups"
        "rollback_to_commit"
        "restore_database"
        "check_system_status"
        "full_rollback"
        "quick_rollback"
    )
    
    local all_found=true
    
    for func in "${functions[@]}"; do
        if grep -q "^$func()" rollback.sh || grep -q "^# $func" rollback.sh; then
            print_pass "Función '$func' encontrada"
        else
            print_fail "Función '$func' no encontrada"
            all_found=false
        fi
    done
    
    if [ "$all_found" = true ]; then
        return 0
    else
        return 1
    fi
}

# Test 5: Verificar variables de configuración
test_configuration_variables() {
    print_test "Verificando variables de configuración"
    
    local variables=(
        "ROLLBACK_ENABLED"
        "AUTO_ROLLBACK"
        "HEALTH_CHECK_RETRIES"
        "HEALTH_CHECK_DELAY"
        "BACKUP_DIR"
        "LOG_FILE"
    )
    
    local all_found=true
    
    for var in "${variables[@]}"; do
        if grep -q "$var=" update-production.sh; then
            print_pass "Variable '$var' encontrada"
        else
            print_fail "Variable '$var' no encontrada"
            all_found=false
        fi
    done
    
    if [ "$all_found" = true ]; then
        return 0
    else
        return 1
    fi
}

# Test 6: Verificar documentación
test_documentation() {
    print_test "Verificando documentación"
    
    local all_exist=true
    
    if [ -f "docs/ROLLBACK_SYSTEM.md" ]; then
        print_pass "docs/ROLLBACK_SYSTEM.md existe"
    else
        print_fail "docs/ROLLBACK_SYSTEM.md no existe"
        all_exist=false
    fi
    
    if [ -f "TASK_9_ROLLBACK_SUMMARY.md" ]; then
        print_pass "TASK_9_ROLLBACK_SUMMARY.md existe"
    else
        print_fail "TASK_9_ROLLBACK_SUMMARY.md no existe"
        all_exist=false
    fi
    
    if [ -f "ROLLBACK_QUICK_REFERENCE.md" ]; then
        print_pass "ROLLBACK_QUICK_REFERENCE.md existe"
    else
        print_fail "ROLLBACK_QUICK_REFERENCE.md no existe"
        all_exist=false
    fi
    
    if [ "$all_exist" = true ]; then
        return 0
    else
        return 1
    fi
}

# Test 7: Verificar estructura de directorios
test_directory_structure() {
    print_test "Verificando estructura de directorios"
    
    if [ -d "backups" ]; then
        print_pass "Directorio 'backups' existe"
    else
        print_info "Creando directorio 'backups'"
        mkdir -p backups
    fi
    
    if [ -d "logs" ]; then
        print_pass "Directorio 'logs' existe"
    else
        print_info "Creando directorio 'logs'"
        mkdir -p logs
    fi
}

# Test 8: Verificar sintaxis de scripts
test_script_syntax() {
    print_test "Verificando sintaxis de scripts bash"
    
    if bash -n update-production.sh 2>/dev/null; then
        print_pass "update-production.sh: sintaxis correcta"
    else
        print_fail "update-production.sh: error de sintaxis"
        return 1
    fi
    
    if bash -n rollback.sh 2>/dev/null; then
        print_pass "rollback.sh: sintaxis correcta"
    else
        print_fail "rollback.sh: error de sintaxis"
        return 1
    fi
}

# Test 9: Verificar manejo de errores
test_error_handling() {
    print_test "Verificando manejo de errores"
    
    if grep -q "set -e" update-production.sh; then
        print_pass "update-production.sh usa 'set -e'"
    else
        print_fail "update-production.sh no usa 'set -e'"
    fi
    
    if grep -q "trap" update-production.sh; then
        print_pass "update-production.sh tiene trap para señales"
    else
        print_info "update-production.sh no tiene trap (opcional)"
    fi
}

# Test 10: Verificar integración con Docker Compose
test_docker_compose_integration() {
    print_test "Verificando integración con Docker Compose"
    
    if grep -q "docker-compose.*exec.*db.*pg_dump" update-production.sh; then
        print_pass "Comando de backup de PostgreSQL encontrado"
    else
        print_fail "Comando de backup de PostgreSQL no encontrado"
        return 1
    fi
    
    if grep -q "docker-compose.*exec.*db.*psql" update-production.sh || \
       grep -q "docker-compose.*exec.*db.*psql" rollback.sh; then
        print_pass "Comando de restauración de PostgreSQL encontrado"
    else
        print_fail "Comando de restauración de PostgreSQL no encontrado"
        return 1
    fi
}

# Ejecutar todos los tests
run_all_tests() {
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    echo ""
    echo "Ejecutando tests..."
    echo ""
    
    # Test 1
    total_tests=$((total_tests + 1))
    if test_scripts_exist; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Test 2
    total_tests=$((total_tests + 1))
    if test_scripts_executable; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Test 3
    total_tests=$((total_tests + 1))
    if test_update_script_functions; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Test 4
    total_tests=$((total_tests + 1))
    if test_rollback_script_functions; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Test 5
    total_tests=$((total_tests + 1))
    if test_configuration_variables; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Test 6
    total_tests=$((total_tests + 1))
    if test_documentation; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Test 7
    total_tests=$((total_tests + 1))
    if test_directory_structure; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Test 8
    total_tests=$((total_tests + 1))
    if test_script_syntax; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Test 9
    total_tests=$((total_tests + 1))
    if test_error_handling; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Test 10
    total_tests=$((total_tests + 1))
    if test_docker_compose_integration; then
        passed_tests=$((passed_tests + 1))
    else
        failed_tests=$((failed_tests + 1))
    fi
    echo ""
    
    # Resumen
    echo "=========================================="
    echo "RESUMEN DE TESTS"
    echo "=========================================="
    echo "Total de tests: $total_tests"
    echo -e "${GREEN}Tests pasados: $passed_tests${NC}"
    if [ $failed_tests -gt 0 ]; then
        echo -e "${RED}Tests fallidos: $failed_tests${NC}"
    else
        echo -e "${GREEN}Tests fallidos: $failed_tests${NC}"
    fi
    echo "=========================================="
    
    if [ $failed_tests -eq 0 ]; then
        echo -e "${GREEN}✅ TODOS LOS TESTS PASARON${NC}"
        return 0
    else
        echo -e "${RED}❌ ALGUNOS TESTS FALLARON${NC}"
        return 1
    fi
}

# Función principal
main() {
    run_all_tests
    local result=$?
    
    cleanup
    
    exit $result
}

# Ejecutar
main
