"""
Servicio para procesamiento de archivos PDF.

Este servicio maneja:
- Importación masiva de PDFs
- Extracción de nombres de participantes
- Inserción de códigos QR en PDFs
- Validación de calidad de PDFs
- Creación de archivos ZIP para exportación
"""
import os
import re
import zipfile
from io import BytesIO
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from django.db import transaction

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image

from certificates.models import Certificate, Participant, Event, QRProcessingConfig
from certificates.services.qr_service import QRCodeService


class PDFProcessingService:
    """Servicio para procesamiento de archivos PDF"""
    
    def __init__(self):
        self.qr_service = QRCodeService()
    
    # ============================================================================
    # IMPORTACIÓN DE PDFs
    # ============================================================================
    
    def import_pdf_batch(
        self,
        pdf_files: List[UploadedFile],
        event: Event,
        auto_extract_names: bool = True
    ) -> Dict:
        """
        Importa un lote de archivos PDF.
        
        Args:
            pdf_files: Lista de archivos PDF subidos
            event: Evento al que pertenecen los certificados
            auto_extract_names: Si debe extraer nombres automáticamente
            
        Returns:
            Dict con resultados de importación:
            {
                'success': [list of certificates],
                'errors': [list of error messages],
                'warnings': [list of warnings],
                'total': int,
                'success_count': int,
                'error_count': int
            }
        """
        results = {
            'success': [],
            'errors': [],
            'warnings': [],
            'total': len(pdf_files),
            'success_count': 0,
            'error_count': 0
        }
        
        config = QRProcessingConfig.get_active_config()
        
        for pdf_file in pdf_files:
            try:
                # Validar PDF
                if not self._validate_pdf_file(pdf_file, config):
                    results['errors'].append(
                        f"PDF inválido o demasiado grande: {pdf_file.name}"
                    )
                    results['error_count'] += 1
                    continue
                
                # Extraer nombre del participante
                if auto_extract_names:
                    participant_name = self.extract_participant_name(pdf_file)
                    if not participant_name:
                        results['warnings'].append(
                            f"No se pudo extraer nombre de: {pdf_file.name}"
                        )
                        participant_name = pdf_file.name.replace('.pdf', '')
                else:
                    participant_name = pdf_file.name.replace('.pdf', '')
                
                # Buscar o crear participante
                participant = self._find_or_create_participant(
                    participant_name,
                    event
                )
                
                # Crear certificado
                certificate = self._create_certificate_from_pdf(
                    pdf_file,
                    participant,
                    config
                )
                
                results['success'].append(certificate)
                results['success_count'] += 1
                
            except Exception as e:
                results['errors'].append(
                    f"Error procesando {pdf_file.name}: {str(e)}"
                )
                results['error_count'] += 1
        
        return results
    
    def extract_participant_name(self, pdf_file: UploadedFile) -> Optional[str]:
        """
        Extrae el nombre del participante del PDF.
        Intenta múltiples métodos: nombre de archivo, contenido PDF, etc.
        
        Args:
            pdf_file: Archivo PDF
            
        Returns:
            Nombre del participante o None si no se puede extraer
        """
        # Método 1: Extraer del nombre del archivo
        filename = pdf_file.name
        # Remover extensión y caracteres especiales
        name_from_file = re.sub(r'[_-]', ' ', filename.replace('.pdf', ''))
        name_from_file = re.sub(r'\s+', ' ', name_from_file).strip()
        
        # Si el nombre del archivo parece válido (tiene al menos 2 palabras)
        if len(name_from_file.split()) >= 2:
            return name_from_file.upper()
        
        # Método 2: Intentar extraer del contenido del PDF
        try:
            pdf_file.seek(0)
            reader = PdfReader(pdf_file)
            
            # Buscar en la primera página
            if len(reader.pages) > 0:
                text = reader.pages[0].extract_text()
                
                # Buscar patrones comunes de nombres
                # Ejemplo: "Certificado de: JUAN PEREZ"
                patterns = [
                    r'(?:Certificado\s+(?:de|para|a):?\s+)([A-ZÁÉÍÓÚÑ\s]+)',
                    r'(?:Otorgado\s+a:?\s+)([A-ZÁÉÍÓÚÑ\s]+)',
                    r'(?:Participante:?\s+)([A-ZÁÉÍÓÚÑ\s]+)',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        name = match.group(1).strip()
                        if len(name.split()) >= 2:
                            return name.upper()
            
            pdf_file.seek(0)
        except Exception:
            pass
        
        # Si no se pudo extraer, retornar el nombre del archivo limpio
        return name_from_file.upper() if name_from_file else None
    
    # ============================================================================
    # INSERCIÓN DE QR EN PDFs
    # ============================================================================
    
    def insert_qr_into_pdf(
        self,
        pdf_path: str,
        qr_image_path: str,
        x: int,
        y: int,
        size: int
    ) -> bytes:
        """
        Inserta un código QR en un PDF existente.
        
        Args:
            pdf_path: Ruta del PDF original
            qr_image_path: Ruta de la imagen QR
            x: Posición X del QR
            y: Posición Y del QR
            size: Tamaño del QR
            
        Returns:
            Bytes del nuevo PDF con QR insertado
        """
        # Leer el PDF original
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Crear un PDF temporal con el QR
        qr_pdf_buffer = BytesIO()
        qr_canvas = canvas.Canvas(qr_pdf_buffer, pagesize=letter)
        
        # Dibujar el QR en la posición especificada
        qr_canvas.drawImage(
            qr_image_path,
            x, y,
            width=size,
            height=size,
            preserveAspectRatio=True
        )
        qr_canvas.save()
        
        # Leer el PDF del QR
        qr_pdf_buffer.seek(0)
        qr_reader = PdfReader(qr_pdf_buffer)
        qr_page = qr_reader.pages[0]
        
        # Superponer el QR en cada página del PDF original
        for page in reader.pages:
            page.merge_page(qr_page)
            writer.add_page(page)
        
        # Escribir el resultado
        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        return output_buffer.getvalue()
    
    def process_qr_for_certificate(
        self,
        certificate: Certificate,
        config: Optional[QRProcessingConfig] = None
    ) -> Dict:
        """
        Procesa el QR para un certificado específico.
        
        Args:
            certificate: Certificado a procesar
            config: Configuración de QR (opcional, usa la activa por defecto)
            
        Returns:
            Dict con resultado del procesamiento
        """
        if not config:
            config = QRProcessingConfig.get_active_config()
        
        result = {
            'success': False,
            'error': None,
            'certificate': certificate
        }
        
        try:
            # Verificar que el certificado pueda procesarse
            if not certificate.can_process_qr():
                result['error'] = "El certificado no está en estado válido para procesar QR"
                return result
            
            # Generar URL de preview
            preview_url = config.get_qr_preview_url(certificate.uuid)
            
            # Generar código QR
            qr_buffer = self.qr_service.generate_qr(
                preview_url,
                error_correction=config.qr_error_correction,
                box_size=config.qr_box_size,
                border=config.qr_border
            )
            
            # Guardar imagen QR
            qr_filename = f"qr_{certificate.uuid}.png"
            certificate.qr_image.save(
                qr_filename,
                ContentFile(qr_buffer.getvalue())
            )
            
            # Validar QR si está habilitado
            if config.enable_qr_validation:
                if not self._validate_qr_readability(certificate.qr_image.path):
                    result['error'] = "El QR generado no es legible"
                    return result
            
            # Insertar QR en el PDF
            pdf_with_qr = self.insert_qr_into_pdf(
                certificate.original_pdf.path,
                certificate.qr_image.path,
                config.default_qr_x,
                config.default_qr_y,
                config.default_qr_size
            )
            
            # Guardar PDF con QR
            qr_pdf_filename = f"cert_qr_{certificate.uuid}.pdf"
            certificate.qr_pdf.save(
                qr_pdf_filename,
                ContentFile(pdf_with_qr)
            )
            
            # Actualizar estado
            certificate.processing_status = 'QR_INSERTED'
            certificate.processed_at = timezone.now()
            certificate.qr_position_x = config.default_qr_x
            certificate.qr_position_y = config.default_qr_y
            certificate.qr_size = config.default_qr_size
            certificate.save()
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            certificate.mark_processing_error(str(e))
        
        return result
    
    # ============================================================================
    # EXPORTACIÓN
    # ============================================================================
    
    def create_export_zip(
        self,
        certificates: List[Certificate],
        include_metadata: bool = True
    ) -> Tuple[bytes, str]:
        """
        Crea un archivo ZIP con certificados para exportar.
        
        Args:
            certificates: Lista de certificados a exportar
            include_metadata: Si debe incluir archivo CSV con metadatos
            
        Returns:
            Tuple de (bytes del ZIP, nombre del archivo)
        """
        zip_buffer = BytesIO()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"certificados_export_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Agregar PDFs
            for cert in certificates:
                if cert.qr_pdf:
                    # Nombre del archivo incluye UUID para facilitar reimportación
                    pdf_filename = f"{cert.uuid}_{cert.participant.dni}.pdf"
                    
                    cert.qr_pdf.seek(0)
                    zip_file.writestr(pdf_filename, cert.qr_pdf.read())
                    
                    # Actualizar estado
                    cert.processing_status = 'EXPORTED_FOR_SIGNING'
                    cert.exported_at = timezone.now()
                    cert.save()
            
            # Agregar archivo de metadatos CSV
            if include_metadata:
                csv_content = self._generate_metadata_csv(certificates)
                zip_file.writestr('metadata.csv', csv_content)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue(), zip_filename
    
    # ============================================================================
    # IMPORTACIÓN DE CERTIFICADOS FINALES
    # ============================================================================
    
    def import_final_certificates(
        self,
        pdf_files: List[UploadedFile]
    ) -> Dict:
        """
        Importa certificados firmados finales.
        
        Args:
            pdf_files: Lista de archivos PDF firmados
            
        Returns:
            Dict con resultados de importación
        """
        results = {
            'success': [],
            'errors': [],
            'total': len(pdf_files),
            'success_count': 0,
            'error_count': 0
        }
        
        for pdf_file in pdf_files:
            try:
                # Extraer UUID del nombre del archivo
                uuid_str = self._extract_uuid_from_filename(pdf_file.name)
                
                if not uuid_str:
                    results['errors'].append(
                        f"No se pudo extraer UUID de: {pdf_file.name}"
                    )
                    results['error_count'] += 1
                    continue
                
                # Buscar certificado
                try:
                    certificate = Certificate.objects.get(uuid=uuid_str)
                except Certificate.DoesNotExist:
                    results['errors'].append(
                        f"Certificado no encontrado para UUID: {uuid_str}"
                    )
                    results['error_count'] += 1
                    continue
                
                # Verificar que pueda importarse
                if not certificate.can_import_final():
                    results['errors'].append(
                        f"Certificado {uuid_str} no está en estado válido para importar"
                    )
                    results['error_count'] += 1
                    continue
                
                # Guardar PDF final
                final_pdf_filename = f"cert_final_{certificate.uuid}.pdf"
                certificate.final_pdf.save(
                    final_pdf_filename,
                    pdf_file
                )
                
                # Actualizar estado
                certificate.processing_status = 'SIGNED_FINAL'
                certificate.final_imported_at = timezone.now()
                certificate.is_signed = True
                certificate.signed_at = timezone.now()
                certificate.save()
                
                results['success'].append(certificate)
                results['success_count'] += 1
                
            except Exception as e:
                results['errors'].append(
                    f"Error procesando {pdf_file.name}: {str(e)}"
                )
                results['error_count'] += 1
        
        return results
    
    # ============================================================================
    # VALIDACIÓN
    # ============================================================================
    
    def validate_pdf_quality(self, pdf_path: str) -> bool:
        """
        Valida que el PDF no esté corrupto.
        
        Args:
            pdf_path: Ruta del PDF a validar
            
        Returns:
            True si el PDF es válido, False en caso contrario
        """
        try:
            reader = PdfReader(pdf_path)
            # Intentar leer todas las páginas
            for page in reader.pages:
                _ = page.extract_text()
            return True
        except Exception:
            return False
    
    # ============================================================================
    # MÉTODOS PRIVADOS
    # ============================================================================
    
    def _validate_pdf_file(
        self,
        pdf_file: UploadedFile,
        config: QRProcessingConfig
    ) -> bool:
        """Valida un archivo PDF"""
        # Validar tamaño
        if not config.validate_pdf_size(pdf_file.size):
            return False
        
        # Validar que sea un PDF válido
        try:
            pdf_file.seek(0)
            reader = PdfReader(pdf_file)
            if len(reader.pages) == 0:
                return False
            pdf_file.seek(0)
            return True
        except Exception:
            return False
    
    def _find_or_create_participant(
        self,
        participant_name: str,
        event: Event
    ) -> Participant:
        """Busca o crea un participante"""
        # Intentar buscar por nombre
        participant = Participant.objects.filter(
            full_name__iexact=participant_name,
            event=event
        ).first()
        
        if not participant:
            # Crear nuevo participante con DNI temporal
            dni_temp = f"TEMP{timezone.now().timestamp()}"[:8]
            participant = Participant.objects.create(
                dni=dni_temp,
                full_name=participant_name,
                event=event,
                attendee_type='ASISTENTE'
            )
        
        return participant
    
    def _create_certificate_from_pdf(
        self,
        pdf_file: UploadedFile,
        participant: Participant,
        config: QRProcessingConfig
    ) -> Certificate:
        """Crea un certificado desde un PDF"""
        # Verificar si ya existe certificado para este participante
        certificate, created = Certificate.objects.get_or_create(
            participant=participant,
            defaults={
                'processing_status': 'IMPORTED',
                'qr_position_x': config.default_qr_x,
                'qr_position_y': config.default_qr_y,
                'qr_size': config.default_qr_size,
            }
        )
        
        # Guardar PDF original
        original_pdf_filename = f"cert_original_{certificate.uuid}.pdf"
        certificate.original_pdf.save(
            original_pdf_filename,
            pdf_file
        )
        
        return certificate
    
    def _validate_qr_readability(self, qr_image_path: str) -> bool:
        """Valida que el QR sea legible"""
        try:
            # Abrir imagen y verificar que sea válida
            img = Image.open(qr_image_path)
            img.verify()
            return True
        except Exception:
            return False
    
    def _generate_metadata_csv(self, certificates: List[Certificate]) -> str:
        """Genera un CSV con metadatos de certificados"""
        lines = ['UUID,DNI,Nombre,Evento,Fecha_Exportacion']
        
        for cert in certificates:
            lines.append(
                f"{cert.uuid},"
                f"{cert.participant.dni},"
                f"{cert.participant.full_name},"
                f"{cert.participant.event.name},"
                f"{cert.exported_at.strftime('%Y-%m-%d %H:%M:%S') if cert.exported_at else ''}"
            )
        
        return '\n'.join(lines)
    
    def _extract_uuid_from_filename(self, filename: str) -> Optional[str]:
        """Extrae el UUID del nombre del archivo"""
        # Buscar patrón UUID en el nombre del archivo
        uuid_pattern = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
        match = re.search(uuid_pattern, filename, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        return None
