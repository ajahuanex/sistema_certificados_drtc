"""Vistas de administración para certificados"""
from django.views.generic import FormView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy
from certificates.forms import ExcelImportForm
from certificates.services.excel_processor import ExcelProcessorService


@method_decorator(staff_member_required, name="dispatch")
class ExcelImportView(FormView):
    """Vista para importar participantes desde Excel"""

    template_name = "admin/certificates/excel_import.html"
    form_class = ExcelImportForm
    success_url = reverse_lazy("certificates:import_excel")

    def form_valid(self, form):
        """Procesa el archivo Excel cuando el formulario es válido"""
        excel_file = form.cleaned_data["excel_file"]

        # Procesar archivo con el servicio
        service = ExcelProcessorService()
        result = service.process_excel(excel_file, user=self.request.user)

        # Mostrar mensajes según el resultado
        if result["success_count"] > 0:
            messages.success(
                self.request,
                f"✓ Importación exitosa: {result['success_count']} participantes procesados.",
            )

        if result["error_count"] > 0:
            messages.warning(
                self.request,
                f"⚠ Se encontraron {result['error_count']} errores durante la importación.",
            )

            # Mostrar los primeros 5 errores
            for error in result["errors"][:5]:
                messages.error(self.request, error)

            if len(result["errors"]) > 5:
                messages.info(
                    self.request,
                    f"... y {len(result['errors']) - 5} errores más.",
                )

        # Guardar resultado en la sesión para mostrarlo en el template
        self.request.session["import_result"] = result

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Agrega datos adicionales al contexto"""
        context = super().get_context_data(**kwargs)

        # Recuperar resultado de importación si existe
        import_result = self.request.session.pop("import_result", None)
        if import_result:
            context["import_result"] = import_result

        context["title"] = "Importar Participantes desde Excel"

        return context



@method_decorator(staff_member_required, name="dispatch")
class ExternalCertificateImportView(FormView):
    """Vista para importar certificados externos desde Excel"""

    template_name = "admin/certificates/external_import.html"
    form_class = ExcelImportForm  # Reutilizamos el mismo formulario
    success_url = reverse_lazy("certificates:import_external")

    def get_context_data(self, **kwargs):
        """Agrega contexto adicional al template"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Importar Certificados Externos'
        return context

    def form_valid(self, form):
        """Procesa el archivo Excel cuando el formulario es válido"""
        excel_file = form.cleaned_data["excel_file"]

        # Procesar archivo con el servicio de importación externa
        from certificates.services.external_certificate_importer import ExternalCertificateImporter
        
        service = ExternalCertificateImporter()
        result = service.import_from_file(excel_file.temporary_file_path())

        # Mostrar mensajes según el resultado
        if result.get('success', False):
            if result["success_count"] > 0:
                messages.success(
                    self.request,
                    f"✓ {result['success_count']} certificados externos importados exitosamente.",
                )
            
            if result["updated_count"] > 0:
                messages.info(
                    self.request,
                    f"ℹ {result['updated_count']} certificados existentes actualizados.",
                )

            if result["error_count"] > 0:
                messages.warning(
                    self.request,
                    f"⚠ Se encontraron {result['error_count']} errores durante la importación.",
                )

                # Mostrar los primeros 5 errores
                for error in result["errors"][:5]:
                    messages.error(self.request, error)

                if len(result["errors"]) > 5:
                    messages.info(
                        self.request,
                        f"... y {len(result['errors']) - 5} errores más.",
                    )
        else:
            messages.error(
                self.request,
                f"✗ Error en la importación: {result.get('error', 'Error desconocido')}"
            )

        # Guardar resultado en la sesión para mostrarlo en el template
        self.request.session["import_result"] = result

        # Registrar en auditoría
        from certificates.models import AuditLog
        AuditLog.objects.create(
            action_type="IMPORT",
            user=self.request.user,
            description=f"Importación de certificados externos: {result['success_count']} éxitos, {result['error_count']} errores",
            metadata=result,
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )

        return super().form_valid(form)
