"""Servicio para generar códigos QR de verificación"""
import qrcode
from io import BytesIO
from django.conf import settings
import logging

logger = logging.getLogger("certificates")


class QRCodeService:
    """Genera códigos QR para verificación de certificados"""

    def __init__(self):
        self.qr_size = 300  # Tamaño del QR en píxeles
        self.box_size = 10
        self.border = 4

    def get_verification_url(self, certificate_uuid: str) -> str:
        """
        Genera la URL de verificación para un certificado

        Args:
            certificate_uuid: UUID del certificado

        Returns:
            URL completa de verificación
        """
        base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
        return f"{base_url}/verificar/{certificate_uuid}/"

    def generate_qr(self, certificate_uuid: str) -> BytesIO:
        """
        Genera una imagen QR para un certificado

        Args:
            certificate_uuid: UUID del certificado

        Returns:
            BytesIO con la imagen PNG del código QR
        """
        # Obtener URL de verificación
        verification_url = self.get_verification_url(certificate_uuid)

        # Crear código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=self.box_size,
            border=self.border,
        )

        qr.add_data(verification_url)
        qr.make(fit=True)

        # Generar imagen
        img = qr.make_image(fill_color="black", back_color="white")

        # Redimensionar a tamaño específico
        img = img.resize((self.qr_size, self.qr_size))

        # Guardar en BytesIO
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        logger.info(f"Código QR generado para certificado {certificate_uuid}")

        return buffer
