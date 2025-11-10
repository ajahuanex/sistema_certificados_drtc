#!/usr/bin/env python
"""
Script de verificación para tests de integración Docker
Verifica que todos los componentes necesarios están presentes
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Verifica que un archivo existe"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} NO ENCONTRADO: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Verifica que un directorio existe"""
    if Path(dirpath).exists() and Path(dirpath).is_dir():
        print(f"✓ {description}: {dirpath}")
        return True
    else:
        print(f"✗ {description} NO ENCONTRADO: {dirpath}")
        return False

def main():
    print("=" * 60)
    print("Verificación de Tests de Integración Docker")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # Verificar archivos de test
    print("📋 Archivos de Test:")
    all_ok &= check_file_exists(
        "certificates/tests/test_docker_integration.py",
        "Tests de integración Docker"
    )
    print()
    
    # Verificar configuración Docker
    print("🐳 Configuración Docker:")
    all_ok &= check_file_exists(
        "docker-compose.test.yml",
        "Docker Compose para tests"
    )
    all_ok &= check_file_exists(
        "Dockerfile",
        "Dockerfile"
    )
    print()
    
    # Verificar scripts de ejecución
    print("🚀 Scripts de Ejecución:")
    all_ok &= check_file_exists(
        "test-docker-integration.sh",
        "Script para Linux/Mac"
    )
    all_ok &= check_file_exists(
        "test-docker-integration.bat",
        "Script para Windows"
    )
    print()
    
    # Verificar documentación
    print("📚 Documentación:")
    all_ok &= check_file_exists(
        "docs/DOCKER_INTEGRATION_TESTS.md",
        "Documentación completa"
    )
    all_ok &= check_file_exists(
        "DOCKER_TESTS_QUICK_REFERENCE.md",
        "Referencia rápida"
    )
    print()
    
    # Verificar CI/CD
    print("⚙️ CI/CD:")
    all_ok &= check_file_exists(
        ".github/workflows/docker-tests.yml",
        "GitHub Actions workflow"
    )
    print()
    
    # Verificar directorios necesarios
    print("📁 Directorios:")
    all_ok &= check_directory_exists(
        "certificates/tests",
        "Directorio de tests"
    )
    all_ok &= check_directory_exists(
        ".github/workflows",
        "Directorio de workflows"
    )
    print()
    
    # Contar tests en el archivo
    print("🔍 Análisis de Tests:")
    test_file = Path("certificates/tests/test_docker_integration.py")
    if test_file.exists():
        content = test_file.read_text(encoding='utf-8')
        test_count = content.count("def test_")
        class_count = content.count("class Docker")
        print(f"✓ Clases de test encontradas: {class_count}")
        print(f"✓ Métodos de test encontrados: {test_count}")
        
        # Verificar clases específicas
        expected_classes = [
            "DockerDatabaseConnectionTest",
            "DockerRedisConnectionTest",
            "DockerServiceCommunicationTest",
            "DockerDataPersistenceTest",
            "DockerEnvironmentConfigTest",
            "DockerHealthCheckTest",
            "DockerPerformanceTest"
        ]
        
        print("\n📊 Clases de Test:")
        for class_name in expected_classes:
            if class_name in content:
                print(f"  ✓ {class_name}")
            else:
                print(f"  ✗ {class_name} NO ENCONTRADA")
                all_ok = False
    print()
    
    # Verificar docker-compose.test.yml
    print("🔧 Configuración de Servicios:")
    compose_file = Path("docker-compose.test.yml")
    if compose_file.exists():
        content = compose_file.read_text(encoding='utf-8')
        services = ["test-db", "test-redis", "test-web"]
        for service in services:
            if service in content:
                print(f"  ✓ Servicio '{service}' configurado")
            else:
                print(f"  ✗ Servicio '{service}' NO ENCONTRADO")
                all_ok = False
        
        # Verificar health checks
        if "healthcheck:" in content:
            print(f"  ✓ Health checks configurados")
        else:
            print(f"  ✗ Health checks NO configurados")
            all_ok = False
    print()
    
    # Resumen final
    print("=" * 60)
    if all_ok:
        print("✅ VERIFICACIÓN EXITOSA")
        print()
        print("Todos los componentes necesarios están presentes.")
        print("Los tests de integración Docker están listos para ejecutarse.")
        print()
        print("Para ejecutar los tests:")
        print("  Linux/Mac: ./test-docker-integration.sh")
        print("  Windows:   test-docker-integration.bat")
        print()
        return 0
    else:
        print("❌ VERIFICACIÓN FALLIDA")
        print()
        print("Algunos componentes están faltando.")
        print("Revisa los mensajes arriba para más detalles.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
