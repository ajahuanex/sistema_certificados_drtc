"""
Vistas para el editor de plantillas visual.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.contrib import messages
from django.urls import reverse

from ..models import CertificateTemplate


@method_decorator(staff_member_required, name='dispatch')
class TemplateEditorView(View):
    """Vista principal del editor de plantillas visual"""
    
    def get(self, request, template_id):
        """Muestra el editor para una plantilla específica"""
        template = get_object_or_404(CertificateTemplate, id=template_id)
        
        context = {
            'template': template,
            'title': f'Editor de Plantillas - {template.name}',
            'opts': CertificateTemplate._meta,
            'has_change_permission': True,
            'original': template,
        }
        
        return render(request, 'admin/certificates/template_editor.html', context)


@method_decorator(staff_member_required, name='dispatch')
class TemplateEditorCreateView(View):
    """Vista para crear nueva plantilla en el editor visual"""
    
    def get(self, request):
        """Muestra el editor para crear nueva plantilla"""
        from certificates.utils.canvas_sizes import CanvasSizes
        
        context = {
            'template': None,
            'title': 'Editor de Plantillas - Nueva Plantilla',
            'opts': CertificateTemplate._meta,
            'has_add_permission': True,
            'canvas_presets': CanvasSizes.get_all_sizes(),
            'default_size': CanvasSizes.get_default_size(),
        }
        
        return render(request, 'admin/certificates/template_editor.html', context)
    
    def post(self, request):
        """Crea una nueva plantilla básica y redirige al editor"""
        name = request.POST.get('name', 'Nueva Plantilla')
        
        # Crear plantilla básica
        template = CertificateTemplate.objects.create(
            name=name,
            html_template='<!-- Plantilla creada con editor visual -->',
            css_styles='/* Estilos generados por editor visual */',
            canvas_width=842,
            canvas_height=595,
            editor_version='1.0',
            last_edited_by=request.user
        )
        
        messages.success(request, f'Plantilla "{name}" creada exitosamente.')
        
        return redirect('certificates:template_editor', template_id=template.id)