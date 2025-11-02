"""Servicio para generar certificados en PDF"""
from django.template import Template, Context
from django.core.files.base import ContentFile
from certificates.services.qr_service import QRCodeService
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import logging

logger = logging.getLogger("certificates")


class CertificateGeneratorService:
    """Genera certificados en PDF con código QR"""

    def __init__(self, qr_service=None):
        """
        Inicializa el servicio

        Args:
            qr_service: Instancia de QRCodeService (opcional, se crea si no se provee)
        """
        self.qr_service = qr_service or QRCodeService()

    def _render_template(self, template_html: str, context_data: dict) -> str:
        """
        Renderiza una plantilla HTML con datos del participante

        Args:
            template_html: HTML de la plantilla
            context_data: Diccionario con datos para la plantilla

        Returns:
            HTML renderizado como string
        """
        template = Template(template_html)
        context = Context(context_data)
        rendered_html = template.render(context)

        logger.debug(f"Plantilla renderizada para {context_data.get('full_name', 'N/A')}")

        return rendered_html

    def _get_template(self, participant):
        """
        Obtiene la plantilla a usar para un participante

        Args:
            participant: Instancia de Participant

        Returns:
            Instancia de CertificateTemplate
        """
        from certificates.models import CertificateTemplate

        # Intentar usar la plantilla del evento
        if participant.event.template:
            return participant.event.template

        # Si no hay plantilla en el evento, usar la plantilla por defecto
        default_template = CertificateTemplate.objects.filter(is_default=True).first()

        if not default_template:
            raise ValueError("No hay plantilla por defecto configurada")

        return default_template

    def _create_pdf(
        self, context_data: dict, template_obj, qr_buffer: BytesIO = None
    ) -> bytes:
        """
        Crea un PDF usando la plantilla visual o fallback al método simple

        Args:
            context_data: Datos del participante
            template_obj: Objeto CertificateTemplate
            qr_buffer: Buffer con imagen QR (opcional)

        Returns:
            Bytes del PDF generado
        """
        # Verificar si la plantilla tiene elementos visuales
        if hasattr(template_obj, 'elements') and template_obj.elements.exists():
            # Usar el nuevo sistema de renderizado visual
            return self._create_visual_pdf(context_data, template_obj, qr_buffer)
        else:
            # Usar el método simple original para compatibilidad
            return self._create_simple_pdf(context_data, template_obj, qr_buffer)

    def _create_visual_pdf(
        self, context_data: dict, template_obj, qr_buffer: BytesIO = None
    ) -> bytes:
        """
        Crea un PDF usando el sistema de plantillas visuales

        Args:
            context_data: Datos del participante
            template_obj: Objeto CertificateTemplate
            qr_buffer: Buffer con imagen QR (opcional)

        Returns:
            Bytes del PDF generado
        """
        try:
            from certificates.services.template_renderer import TemplateRenderingService
        except ImportError:
            logger.warning("WeasyPrint not available, falling back to simple PDF generation")
            return self._create_simple_pdf(context_data, template_obj, qr_buffer)
        
        # Mapear datos del contexto al formato esperado por el renderer
        participant_data = {
            'participant_name': context_data.get('full_name', ''),
            'participant_dni': context_data.get('dni', ''),
            'event_name': context_data.get('event_name', ''),
            'event_date': context_data.get('event_date', ''),
            'attendee_type': context_data.get('attendee_type', ''),
            'certificate_uuid': context_data.get('certificate_uuid', ''),
            'verification_url': context_data.get('verification_url', ''),
        }
        
        try:
            # Usar el servicio de renderizado visual
            renderer = TemplateRenderingService()
            pdf_bytes = renderer.render_template_to_pdf(template_obj.id, participant_data)
            
            logger.info(f"PDF visual generado: {len(pdf_bytes)} bytes")
            return pdf_bytes
        except ImportError:
            logger.warning("WeasyPrint dependencies not available, falling back to simple PDF")
            return self._create_simple_pdf(context_data, template_obj, qr_buffer)

    def _create_simple_pdf(
        self, context_data: dict, template_obj, qr_buffer: BytesIO = None
    ) -> bytes:
        """
        Crea un PDF simple con los datos del certificado (método original)

        Args:
            context_data: Datos del participante
            template_obj: Objeto CertificateTemplate
            qr_buffer: Buffer con imagen QR (opcional)

        Returns:
            Bytes del PDF generado
        """
        pdf_buffer = BytesIO()

        # Crear PDF en orientación horizontal (landscape)
        page_width, page_height = landscape(A4)
        c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))

        # Título
        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(page_width / 2, page_height - 100, "CERTIFICADO")

        # Subtítulo
        c.setFont("Helvetica", 16)
        c.drawCentredString(
            page_width / 2, page_height - 140, "Se otorga el presente certificado a:"
        )

        # Nombre del participante
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(
            page_width / 2, page_height - 200, context_data.get("full_name", "")
        )

        # DNI
        c.setFont("Helvetica", 14)
        c.drawCentredString(
            page_width / 2,
            page_height - 240,
            f"DNI: {context_data.get('dni', '')}",
        )

        # Texto del evento
        c.setFont("Helvetica", 14)
        c.drawCentredString(
            page_width / 2, page_height - 280, "Por su participación como"
        )

        # Tipo de asistente
        c.setFont("Helvetica-Bold", 16)
        attendee_type_display = {
            "ASISTENTE": "Asistente",
            "PONENTE": "Ponente",
            "ORGANIZADOR": "Organizador",
        }.get(context_data.get("attendee_type", ""), "Asistente")

        c.drawCentredString(page_width / 2, page_height - 310, attendee_type_display)

        # Nombre del evento
        c.setFont("Helvetica", 14)
        c.drawCentredString(page_width / 2, page_height - 340, "en el evento:")

        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(
            page_width / 2, page_height - 370, context_data.get("event_name", "")
        )

        # Fecha del evento
        c.setFont("Helvetica", 12)
        c.drawCentredString(
            page_width / 2,
            page_height - 400,
            f"Realizado el {context_data.get('event_date', '')}",
        )

        # Código QR (si existe)
        if qr_buffer:
            qr_buffer.seek(0)
            qr_image = ImageReader(qr_buffer)
            qr_size = 100
            c.drawImage(
                qr_image,
                page_width - qr_size - 50,
                50,
                width=qr_size,
                height=qr_size,
            )

            # Texto debajo del QR
            c.setFont("Helvetica", 8)
            c.drawCentredString(
                page_width - qr_size / 2 - 50, 35, "Escanea para verificar"
            )

        # Pie de página
        c.setFont("Helvetica", 10)
        c.drawCentredString(
            page_width / 2, 50, "Dirección Regional de Trabajo y Promoción del Empleo"
        )
        c.drawCentredString(page_width / 2, 35, "Puno - Perú")

        c.showPage()
        c.save()

        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.read()

        logger.info(f"PDF simple generado: {len(pdf_bytes)} bytes")

        return pdf_bytes

    def generate_certificate(self, participant, user=None):
        """
        Genera un certificado completo para un participante

        Args:
            participant: Instancia de Participant
            user: Usuario que genera el certificado (opcional)

        Returns:
            Instancia de Certificate creada
        """
        from certificates.models import Certificate, AuditLog
        import uuid as uuid_lib

        # Verificar si ya existe un certificado para este participante
        existing_cert = Certificate.objects.filter(participant=participant).first()
        if existing_cert:
            logger.warning(
                f"Ya existe certificado para {participant.full_name} ({participant.dni})"
            )
            return existing_cert

        # Generar UUID para el certificado
        cert_uuid = uuid_lib.uuid4()

        # Generar código QR
        qr_buffer = self.qr_service.generate_qr(str(cert_uuid))

        # Obtener plantilla
        template_obj = self._get_template(participant)

        # Preparar datos del contexto
        context_data = {
            "full_name": participant.full_name,
            "dni": participant.dni,
            "event_name": participant.event.name,
            "event_date": participant.event.event_date.strftime("%d/%m/%Y"),
            "attendee_type": participant.attendee_type,
            "certificate_uuid": str(cert_uuid),
            "verification_url": self.qr_service.get_verification_url(str(cert_uuid)),
        }

        # Generar PDF
        pdf_bytes = self._create_pdf(context_data, template_obj, qr_buffer)

        # Crear instancia de Certificate
        certificate = Certificate(
            uuid=cert_uuid,
            participant=participant,
            verification_url=self.qr_service.get_verification_url(str(cert_uuid)),
        )

        # Guardar archivos
        pdf_filename = f"certificado_{participant.dni}_{cert_uuid}.pdf"
        certificate.pdf_file.save(pdf_filename, ContentFile(pdf_bytes), save=False)

        qr_buffer.seek(0)
        qr_filename = f"qr_{cert_uuid}.png"
        certificate.qr_code.save(qr_filename, ContentFile(qr_buffer.read()), save=False)

        certificate.save()

        # Registrar en auditoría
        AuditLog.objects.create(
            action_type="GENERATE",
            user=user,
            description=f"Certificado generado para {participant.full_name} ({participant.dni})",
            metadata={
                "certificate_uuid": str(cert_uuid),
                "participant_dni": participant.dni,
                "event_name": participant.event.name,
            },
        )

        logger.info(
            f"Certificado generado: {cert_uuid} para {participant.full_name}"
        )

        return certificate

    def generate_bulk_certificates(self, event, user=None):
        """
        Genera certificados para todos los participantes de un evento

        Args:
            event: Instancia de Event
            user: Usuario que genera los certificados (opcional)

        Returns:
            Diccionario con resultados: {
                'success_count': int,
                'error_count': int,
                'certificates': list,
                'errors': list
            }
        """
        participants = event.participants.all()

        if not participants.exists():
            logger.warning(f"No hay participantes en el evento {event.name}")
            return {
                "success_count": 0,
                "error_count": 0,
                "certificates": [],
                "errors": ["No hay participantes en este evento"],
            }

        success_count = 0
        error_count = 0
        certificates = []
        errors = []

        for participant in participants:
            try:
                certificate = self.generate_certificate(participant, user=user)
                certificates.append(certificate)
                success_count += 1
            except Exception as e:
                error_count += 1
                error_msg = f"Error al generar certificado para {participant.full_name} ({participant.dni}): {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        logger.info(
            f"Generación masiva completada para evento {event.name}: {success_count} éxitos, {error_count} errores"
        )

        return {
            "success_count": success_count,
            "error_count": error_count,
            "certificates": certificates,
            "errors": errors,
        }
