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
