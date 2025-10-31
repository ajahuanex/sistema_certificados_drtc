# Makefile para Sistema de Certificados DRTC Puno

.PHONY: help build up down restart logs shell migrate collectstatic backup clean

help: ## Mostrar esta ayuda
	@echo "Sistema de Certificados DRTC Puno - Comandos Docker"
	@echo "===================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construir imágenes Docker
	docker-compose build

up: ## Levantar servicios
	docker-compose up -d
	@echo "✅ Servicios levantados"
	@echo "🌐 Accede en: http://localhost"

down: ## Detener y eliminar contenedores
	docker-compose down

restart: ## Reiniciar servicios
	docker-compose restart

logs: ## Ver logs de todos los servicios
	docker-compose logs -f

logs-web: ## Ver logs solo de Django
	docker-compose logs -f web

logs-db: ## Ver logs solo de PostgreSQL
	docker-compose logs -f db

logs-nginx: ## Ver logs solo de Nginx
	docker-compose logs -f nginx

shell: ## Acceder al shell del contenedor web
	docker-compose exec web bash

shell-db: ## Acceder a PostgreSQL
	docker-compose exec db psql -U certificados_user -d certificados_db

django-shell: ## Acceder al shell de Django
	docker-compose exec web python manage.py shell

migrate: ## Ejecutar migraciones
	docker-compose exec web python manage.py migrate

makemigrations: ## Crear migraciones
	docker-compose exec web python manage.py makemigrations

collectstatic: ## Recolectar archivos estáticos
	docker-compose exec web python manage.py collectstatic --noinput

createsuperuser: ## Crear superusuario
	docker-compose exec web python manage.py createsuperuser

load-template: ## Cargar plantilla por defecto
	docker-compose exec web python manage.py load_default_template

load-qr-config: ## Cargar configuración de QR
	docker-compose exec web python manage.py load_qr_config

backup-db: ## Backup de base de datos
	@mkdir -p backups
	docker-compose exec db pg_dump -U certificados_user certificados_db > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup creado en backups/"

restore-db: ## Restaurar base de datos (usar: make restore-db FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then echo "❌ Especifica el archivo: make restore-db FILE=backup.sql"; exit 1; fi
	docker-compose exec -T db psql -U certificados_user certificados_db < $(FILE)
	@echo "✅ Base de datos restaurada"

ps: ## Ver estado de contenedores
	docker-compose ps

stats: ## Ver uso de recursos
	docker stats

clean: ## Limpiar contenedores, volúmenes e imágenes
	docker-compose down -v
	docker system prune -f
	@echo "✅ Limpieza completada"

clean-all: ## Limpiar TODO (incluyendo imágenes)
	docker-compose down -v --rmi all
	docker system prune -af
	@echo "✅ Limpieza completa"

update: ## Actualizar aplicación
	@echo "🔄 Actualizando aplicación..."
	git pull origin main
	docker-compose build
	docker-compose up -d
	docker-compose exec web python manage.py migrate
	docker-compose exec web python manage.py collectstatic --noinput
	@echo "✅ Actualización completada"

test: ## Ejecutar tests
	docker-compose exec web python manage.py test

check: ## Verificar configuración de Django
	docker-compose exec web python manage.py check

quick-start: ## Inicio rápido (construir y levantar)
	@chmod +x quick-start.sh
	@./quick-start.sh

.DEFAULT_GOAL := help
