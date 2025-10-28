"""Servicio para firma digital de certificados"""
import requests
import time
from django.conf import settings
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger("certificates.signature")


class DigitalSignatureService:
    """Servicio para firmar certificados digitalmente usando servicio externo"""

    MAX_RETRIES = 3
    RETRY_DELAY = 2  # segundos

    def __init__(self):
        """Inicializa el servicio con configuración desde settings"""
        self.signature_service_url = getattr(
            settings, "SIGNATURE_SERVICE_URL", "http://localhost:8080/api/sign"
        )
        self.signature_api_key = getattr(settings, "SIGNATURE_API_KEY", "")
        self.timeout = 30  # segundos

    def _send_to_signature_service(self, pdf_file) -> bytes:
        """
        Envía un PDF al servicio de firma digital

        Args:
            pdf_file: Archivo PDF a firmar

        Returns:
            Bytes del PDF firmado

        Raises:
            requests.exceptions.RequestException: Si hay error en la comunicación
        """
        # Preparar headers con autenticación
        headers = {"Authorization": f"Bearer {self.signature_api_key}"}

        # Leer el archivo PDF
        pdf_file.seek(0)
        pdf_content = pdf_file.read()

        # Preparar el archivo para envío
        files = {"file": ("certificate.pdf", pdf_content, "application/pdf")}

        logger.debug(f"Enviando PDF al servicio de firma: {self.signature_service_url}")

        # Enviar petición POST
        response = requests.post(
            self.signature_service_url,
            files=files,
            headers=headers,
            timeout=self.timeout,
        )

        # Verificar respuesta
        response.raise_for_status()

        # Retornar PDF firmado
        signed_pdf = response.content

        logger.info(f"PDF firmado recibido: {len(signed_pdf)} bytes")

        return signed_pdf

    def sign_certificate(self, certificate):
        """
        Firma un certificado digitalmente con lógica de reintentos

        Args:
            certificate: Instancia de Certificate

        Returns:
            Certificate actualizado con PDF firmado

        Raises:
            Exception: Si falla después de todos los reintentos
        """
        # Validar que el certificado no esté ya firmado
        if certificate.is_signed:
            logger.warning(
                f"Certificado {certificate.uuid} ya está firmado, omitiendo"
            )
            return certificate

        last_error = None

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.info(
                    f"Intento {attempt}/{self.MAX_RETRIES} de firmar certificado {certificate.uuid}"
                )

                # Enviar al servicio de firma
                signed_pdf_bytes = self._send_to_signature_service(
                    certificate.pdf_file
                )

                # Actualizar certificado con PDF firmado
                self._update_certificate_status(certificate, signed_pdf_bytes)

                logger.info(f"Certificado {certificate.uuid} firmado exitosamente")

                return certificate

            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
            ) as e:
                last_error = e
                logger.warning(
                    f"Intento {attempt} falló para certificado {certificate.uuid}: {str(e)}"
                )

                # Si no es el último intento, esperar antes de reintentar
                if attempt < self.MAX_RETRIES:
                    logger.debug(f"Esperando {self.RETRY_DELAY} segundos antes de reintentar")
                    time.sleep(self.RETRY_DELAY)

        # Si llegamos aquí, todos los intentos fallaron
        error_msg = f"Falló la firma del certificado {certificate.uuid} después de {self.MAX_RETRIES} intentos: {str(last_error)}"
        logger.error(error_msg)
        raise Exception(error_msg)

    def _update_certificate_status(self, certificate, signed_pdf_bytes: bytes):
        """
        Actualiza el estado del certificado después de firmarlo

        Args:
            certificate: Instancia de Certificate
            signed_pdf_bytes: Bytes del PDF firmado
        """
        from django.utils import timezone
        from certificates.models import AuditLog

        # Reemplazar PDF con versión firmada
        pdf_filename = f"certificado_firmado_{certificate.participant.dni}_{certificate.uuid}.pdf"
        certificate.pdf_file.save(pdf_filename, ContentFile(signed_pdf_bytes), save=False)

        # Actualizar estado
        certificate.is_signed = True
        certificate.signed_at = timezone.now()
        certificate.save()

        # Registrar en auditoría
        AuditLog.objects.create(
            action_type="SIGN",
            description=f"Certificado firmado digitalmente para {certificate.participant.full_name} ({certificate.participant.dni})",
            metadata={
                "certificate_uuid": str(certificate.uuid),
                "participant_dni": certificate.participant.dni,
                "event_name": certificate.participant.event.name,
            },
        )

        logger.info(f"Estado del certificado {certificate.uuid} actualizado: firmado=True")

    def sign_bulk_certificates(self, certificates, user=None):
        """
        Firma múltiples certificados

        Args:
            certificates: QuerySet o lista de Certificate
            user: Usuario que realiza la firma (opcional)

        Returns:
            Diccionario con resultados: {
                'success_count': int,
                'error_count': int,
                'errors': list
            }
        """
        success_count = 0
        error_count = 0
        errors = []

        # Filtrar solo certificados no firmados
        unsigned_certs = [cert for cert in certificates if not cert.is_signed]

        if not unsigned_certs:
            logger.info("No hay certificados sin firmar")
            return {
                "success_count": 0,
                "error_count": 0,
                "errors": ["No hay certificados sin firmar"],
            }

        logger.info(f"Iniciando firma masiva de {len(unsigned_certs)} certificados")

        for certificate in unsigned_certs:
            try:
                self.sign_certificate(certificate)
                success_count += 1
            except Exception as e:
                error_count += 1
                error_msg = f"Error al firmar certificado {certificate.uuid}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        logger.info(
            f"Firma masiva completada: {success_count} éxitos, {error_count} errores"
        )

        return {
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
        }
