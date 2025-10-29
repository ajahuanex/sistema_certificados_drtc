"""Servicio para importar certificados externos desde Excel"""
import openpyxl
from datetime import datetime
from django.db import transaction
from certificates.models import Event, Participant, Certificate
from certificates.services.qr_service import QRCodeService
import logging

logger = logging.getLogger("certificates")


class ExternalCertificateImporter:
    """Importa certificados externos desde un archivo Excel"""
    
    REQUIRED_COLUMNS = [
        'DNI',
        'Nombres y Apellidos',
        'Fecha del Evento',
        'Tipo de Asistente',
        'Nombre del Evento',
        'URL del Certificado',  # Nueva columna
    ]
    
    OPTIONAL_COLUMNS = [
        'Sistema Externo',  # Opcional: nombre del sistema origen
    ]
    
    def __init__(self):
        self.qr_service = QRCodeService()
        self.errors = []
        self.success_count = 0
        self.updated_count = 0
    
    def import_from_file(self, file_path):
        """
        Importa certificados externos desde un archivo Excel
        
        Args:
            file_path: Ruta al archivo Excel
            
        Returns:
            dict con resultados de la importación
        """
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            sheet = workbook.active
            
            # Validar columnas
            if not self._validate_columns(sheet):
                return {
                    'success': False,
                    'error': 'El archivo no tiene las columnas requeridas',
                    'required_columns': self.REQUIRED_COLUMNS,
                    'success_count': 0,
                    'updated_count': 0,
                    'error_count': 0,
                    'errors': []
                }
            
            # Procesar filas
            self._process_rows(sheet)
            
            return {
                'success': True,
                'success_count': self.success_count,
                'updated_count': self.updated_count,
                'error_count': len(self.errors),
                'errors': self.errors
            }
            
        except Exception as e:
            logger.error(f"Error al importar certificados externos: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'success_count': 0,
                'updated_count': 0,
                'error_count': 0,
                'errors': []
            }
    
    def _validate_columns(self, sheet):
        """Valida que el Excel tenga las columnas requeridas"""
        header_row = [cell.value for cell in sheet[1]]
        
        for required_col in self.REQUIRED_COLUMNS:
            if required_col not in header_row:
                logger.error(f"Columna requerida no encontrada: {required_col}")
                return False
        
        return True
    
    def _process_rows(self, sheet):
        """Procesa todas las filas del Excel"""
        header_row = [cell.value for cell in sheet[1]]
        
        # Mapear índices de columnas
        col_indices = {col: header_row.index(col) for col in self.REQUIRED_COLUMNS}
        
        # Agregar columnas opcionales si existen
        for optional_col in self.OPTIONAL_COLUMNS:
            if optional_col in header_row:
                col_indices[optional_col] = header_row.index(optional_col)
        
        # Procesar cada fila (empezando desde la fila 2)
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                self._process_row(row, col_indices, row_num)
            except Exception as e:
                error_msg = f"Fila {row_num}: {str(e)}"
                self.errors.append(error_msg)
                logger.error(error_msg)
    
    @transaction.atomic
    def _process_row(self, row, col_indices, row_num):
        """Procesa una fila individual del Excel"""
        # Extraer datos
        dni = str(row[col_indices['DNI']]).strip()
        full_name = str(row[col_indices['Nombres y Apellidos']]).strip()
        event_date_value = row[col_indices['Fecha del Evento']]
        attendee_type = str(row[col_indices['Tipo de Asistente']]).strip().upper()
        event_name = str(row[col_indices['Nombre del Evento']]).strip()
        certificate_url = str(row[col_indices['URL del Certificado']]).strip()
        
        # Sistema externo (opcional)
        external_system = ''
        if 'Sistema Externo' in col_indices:
            external_system = str(row[col_indices['Sistema Externo']] or '').strip()
        
        # Validar datos
        self._validate_row_data(dni, full_name, event_date_value, attendee_type, 
                               event_name, certificate_url, row_num)
        
        # Parsear fecha
        event_date = self._parse_date(event_date_value, row_num)
        
        # Obtener o crear evento
        event, _ = Event.objects.get_or_create(
            name=event_name,
            event_date=event_date,
            defaults={'description': f'Evento importado desde sistema externo'}
        )
        
        # Obtener o crear participante
        participant, _ = Participant.objects.get_or_create(
            dni=dni,
            event=event,
            defaults={
                'full_name': full_name,
                'attendee_type': attendee_type
            }
        )
        
        # Si el participante ya existía, actualizar datos
        if participant.full_name != full_name or participant.attendee_type != attendee_type:
            participant.full_name = full_name
            participant.attendee_type = attendee_type
            participant.save()
        
        # Verificar si ya existe un certificado
        certificate_exists = hasattr(participant, 'certificate')
        
        if certificate_exists:
            # Actualizar certificado existente
            certificate = participant.certificate
            certificate.is_external = True
            certificate.external_url = certificate_url
            certificate.external_system = external_system or 'Sistema Externo'
            
            # Regenerar QR code con la URL externa
            qr_buffer = self.qr_service.generate_qr_code(certificate_url)
            qr_filename = f"qr_{certificate.uuid}.png"
            certificate.qr_code.save(qr_filename, qr_buffer, save=False)
            
            certificate.save()
            self.updated_count += 1
            logger.info(f"Certificado externo actualizado para {full_name} ({dni})")
        else:
            # Crear nuevo certificado externo
            certificate = Certificate.objects.create(
                participant=participant,
                is_external=True,
                external_url=certificate_url,
                external_system=external_system or 'Sistema Externo',
                verification_url=certificate_url,  # Usar la URL externa como verificación
                is_signed=False  # Los certificados externos no están firmados por nuestro sistema
            )
            
            # Generar QR code con la URL externa
            qr_buffer = self.qr_service.generate_qr_code(certificate_url)
            qr_filename = f"qr_{certificate.uuid}.png"
            certificate.qr_code.save(qr_filename, qr_buffer, save=True)
            
            self.success_count += 1
            logger.info(f"Certificado externo creado para {full_name} ({dni})")
    
    def _validate_row_data(self, dni, full_name, event_date, attendee_type, 
                          event_name, certificate_url, row_num):
        """Valida los datos de una fila"""
        errors = []
        
        # Validar DNI
        if not dni or len(dni) != 8 or not dni.isdigit():
            errors.append(f"DNI inválido: {dni}")
        
        # Validar nombre
        if not full_name:
            errors.append("Nombres y Apellidos no puede estar vacío")
        
        # Validar tipo de asistente
        valid_types = ['ASISTENTE', 'PONENTE', 'ORGANIZADOR']
        if attendee_type not in valid_types:
            errors.append(f"Tipo de Asistente inválido: {attendee_type}. Debe ser uno de: {', '.join(valid_types)}")
        
        # Validar nombre del evento
        if not event_name:
            errors.append("Nombre del Evento no puede estar vacío")
        
        # Validar URL del certificado
        if not certificate_url:
            errors.append("URL del Certificado no puede estar vacía")
        elif not certificate_url.startswith(('http://', 'https://')):
            errors.append(f"URL del Certificado inválida: {certificate_url}")
        
        if errors:
            raise ValueError(f"Fila {row_num}: " + "; ".join(errors))
    
    def _parse_date(self, date_value, row_num):
        """Parsea una fecha desde el Excel"""
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, str):
            # Intentar varios formatos
            formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y']
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
            
            raise ValueError(f"Fila {row_num}: Formato de fecha inválido: {date_value}")
        
        raise ValueError(f"Fila {row_num}: Fecha del Evento debe ser una fecha válida")
