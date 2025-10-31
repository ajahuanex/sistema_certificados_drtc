# Implementation Plan

- [x] 1. Crear servicio de estadísticas del dashboard



  - Implementar `DashboardStatsService` en `certificates/services/dashboard_stats.py`
  - Incluir métodos para calcular estadísticas de certificados, consultas y plantillas
  - Implementar sistema de caché con TTL de 5 minutos
  - Agregar queries optimizadas con agregaciones de Django ORM


  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 7.1, 7.2, 7.3_

- [ ] 2. Crear vista del dashboard
  - Implementar `dashboard_view` en `certificates/views/dashboard_views.py`
  - Agregar decorador `@staff_member_required` para seguridad


  - Integrar con `DashboardStatsService`
  - Manejar errores y casos edge
  - _Requirements: 1.1, 1.2, 1.3_



- [ ] 3. Configurar URLs del dashboard
  - Agregar ruta `/admin/dashboard/` en `certificates/urls.py`
  - Asegurar que la ruta esté protegida y accesible desde el admin
  - _Requirements: 1.1_



- [ ] 4. Crear template HTML del dashboard
  - Crear `templates/admin/dashboard.html` extendiendo `admin/base_site.html`
  - Implementar estructura con header, stats cards, gráficos y acciones rápidas
  - Agregar sección de certificados recientes
  - Incluir indicador de última actualización



  - _Requirements: 1.1, 1.2, 5.1, 5.2, 5.3, 6.1, 6.2, 6.3_

- [ ] 5. Crear estilos CSS del dashboard
  - Crear `static/admin/css/dashboard.css`
  - Implementar diseño de cards con hover effects


  - Crear grid responsive para stats y gráficos
  - Definir color scheme consistente con el admin
  - Agregar media queries para mobile
  - _Requirements: 5.1, 5.2, 5.3, 5.4_



- [ ] 6. Implementar gráficos con Chart.js
  - Crear `static/admin/js/dashboard.js`
  - Implementar gráfico de barras para certificados por mes
  - Implementar gráfico de líneas para consultas por día
  - Configurar opciones de Chart.js (responsive, tooltips, etc.)
  - Pasar datos desde el template al JavaScript de forma segura


  - _Requirements: 2.4, 3.3, 5.4_

- [ ] 7. Integrar dashboard en el admin index
  - Modificar `templates/admin/index.html` para agregar enlace al dashboard
  - Crear card destacada con botón de acceso al dashboard
  - Usar context processor para pasar URL del dashboard



  - _Requirements: 1.1, 6.1, 6.2_

- [ ] 8. Crear tests unitarios del servicio
  - Crear `certificates/tests/test_dashboard_stats.py`
  - Escribir tests para `_calculate_certificate_stats()`
  - Escribir tests para `_calculate_query_stats()`
  - Escribir tests para `_calculate_template_stats()`
  - Escribir tests para funcionalidad de caché
  - Escribir tests para manejo de base de datos vacía
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 7.1, 7.2, 7.3_



- [ ] 9. Crear tests de integración de la vista
  - Agregar tests en `certificates/tests/test_dashboard_views.py`
  - Verificar que requiere autenticación staff
  - Verificar que muestra estadísticas correctamente


  - Verificar manejo de errores
  - Verificar que el template se renderiza correctamente
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 10. Optimizar queries con índices de base de datos
  - Crear migración para agregar índices en `Certificate.generated_at`
  - Verificar índices existentes en `AuditLog.timestamp` y `AuditLog.action_type`
  - Documentar índices en comentarios del modelo
  - _Requirements: 7.1, 7.2_

- [ ] 11. Agregar documentación del dashboard
  - Crear `docs/DASHBOARD.md` con guía de uso
  - Documentar métricas disponibles y su significado
  - Incluir screenshots del dashboard
  - Documentar configuración de caché
  - _Requirements: 1.1, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_

- [ ] 12. Agregar botón de actualización manual
  - Implementar endpoint para limpiar caché del dashboard
  - Agregar botón "Actualizar" en el template
  - Mostrar mensaje de confirmación después de actualizar
  - _Requirements: 7.3_
