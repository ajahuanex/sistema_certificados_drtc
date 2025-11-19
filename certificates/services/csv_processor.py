"""Servicio para procesar archivos CSV de participantes"""
import csv
from typing import Dict, List, Tuple
from datetime import datetime
import re
import logging

logger = logging.getLogger('certificates')


class CSVProcessorService:
    """Procesa archivos CSV y crea participantes"""
    
    REQUIRED_COLUMNS = [
        'DNI',
        'Nombres y Apellidos',
        'Fecha del Evento',
        'Tipo de Asistente',
        'Nombre del Evento'
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.rows_data = []
    
    def validate_file(self, file) -> Tuple[bool, List[str], List[Dict]]:
        """
        Valida un archivo CSV antes de importarlo
        
        Args:
            file: Archivo CSV a validar
            
        Returns:
            Tuple con (es_válido, lista_de_errores, lista_de_filas_validadas)
        """
        errors = []
        warnings = []
        validated_rows = []
        
        try:
            # Leer el archivo CSV
            file.seek(0)
            content = file.read().decode('utf-8-sig')  # utf-8-sig para manejar BOM
            lines = content.splitlines()
            
            if not lines:
                errors.append("El archivo está vacío")
                return (False, errors, [])
            
            # Parsear CSV
            csv_reader = csv.DictReader(lines)
            headers = csv_reader.fieldnames
            
            # Verificar columnas requeridas
            missing_columns = []
            for required_col in self.REQUIRED_COLUMNS:
                if required_col not in headers:
                    missing_columns.append(required_col)
            
            if missing_columns:
                errors.append(f"Columnas faltantes: {', '.join(missing_columns)}")
                return (False, errors, [])
            
            # Validar cada fila
            for row_idx, row in enumerate(csv_reader, start=2):
                row_result = self._validate_row(row, row_idx)
                
                if row_result['valid']:
                    validated_rows.append(row_result)
                else:
                    errors.extend(row_result['errors'])
                
                if row_result.get('warnings'):
                    warnings.extend(row_result['warnings'])
            
            # Si no hay filas válidas
            if not validated_rows and not errors:
                errors.append("No se encontraron filas válidas en el archivo")
            
            return (len(errors) == 0, errors + warnings, validated_rows)
            
        except Exception as e:
            errors.append(f"Error al leer el archivo: {str(e)}")
            return (False, errors, [])
    
    def _validate_row(self, row: Dict, row_idx: int) -> Dict:
        """
        Valida una fila del CSV
        
        Returns:
            Dict con información de validación
        """
        result = {
            'row_number': row_idx,
            'valid': True,
            'errors': [],
            'warnings': [],
            'data': {}
        }
        
        # Verificar si la fila está vacía
        if all(not str(v).strip() for v in row.values()):
            result['valid'] = False
            return result
        
        # Validar y normalizar DNI
        dni_raw = str(row.get('DNI', '')).strip()
        dni_clean = ''.join(filter(str.isdigit, dni_raw))
        
        if not dni_clean:
            result['errors'].append(f"Fila {row_idx}: DNI '{dni_raw}' debe contener dígitos numéricos")
            result['valid'] = False
        elif len(dni_clean) > 8:
            result['errors'].append(f"Fila {row_idx}: DNI '{dni_raw}' no puede tener más de 8 dígitos")
            result['valid'] = False
        else:
            # Normalizar con ceros a la izquierda
            dni_normalized = dni_clean.zfill(8)
            result['data']['dni'] = dni_normalized
            
            # Advertir si se agregaron ceros
            if dni_normalized != dni_raw:
                result['warnings'].append(
                    f"Fila {row_idx}: DNI '{dni_raw}' se normalizará a '{dni_normalized}'"
                )
        
        # Validar nombre
        full_name = str(row.get('Nombres y Apellidos', '')).strip()
        if not full_name:
            result['errors'].append(f"Fila {row_idx}: 'Nombres y Apellidos' no puede estar vacío")
            result['valid'] = False
        else:
            result['data']['full_name'] = full_name
        
        # Validar tipo de asistente
        attendee_type = str(row.get('Tipo de Asistente', '')).strip().upper()
        valid_types = ['ASISTENTE', 'PONENTE', 'ORGANIZADOR']
        if attendee_type not in valid_types:
            result['errors'].append(
                f"Fila {row_idx}: Tipo de Asistente '{attendee_type}' no es válido. "
                f"Debe ser: {', '.join(valid_types)}"
            )
            result['valid'] = False
        else:
            result['data']['attendee_type'] = attendee_type
        
        # Validar fecha
        fecha_raw = row.get('Fecha del Evento', '')
        try:
            fecha = self._parse_date(fecha_raw)
            result['data']['event_date'] = fecha
        except ValueError as e:
            result['errors'].append(f"Fila {row_idx}: {str(e)}")
            result['valid'] = False
        
        # Validar nombre del evento
        event_name = str(row.get('Nombre del Evento', '')).strip()
        if not event_name:
            result['errors'].append(f"Fila {row_idx}: 'Nombre del Evento' no puede estar vacío")
            result['valid'] = False
        else:
            result['data']['event_name'] = event_name
        
        return result
    
    def _parse_date(self, date_value):
        """Parsea una fecha desde el CSV"""
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, str):
            date_value = date_value.strip()
            # Intentar varios formatos
            formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y', '%Y/%m/%d']
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
            
            raise ValueError(f"Formato de fecha inválido: '{date_value}'. Use DD/MM/YYYY")
        
        raise ValueError(f"Fecha del Evento debe ser una fecha válida, recibido: {type(date_value)}")
    
    def process_csv(self, file, user=None) -> Dict:
        """
        Procesa un archivo CSV completo y crea participantes
        
        Args:
            file: Archivo CSV a procesar
            user: Usuario que realiza la importación (opcional)
            
        Returns:
            Diccionario con resultados
        """
        from certificates.models import Event, Participant, AuditLog
        
        # Validar archivo primero
        is_valid, messages, validated_rows = self.validate_file(file)
        
        if not is_valid:
            logger.error(f"Archivo CSV inválido: {messages}")
            return {
                'success_count': 0,
                'error_count': 1,
                'errors': messages
            }
        
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            # Procesar cada fila validada
            for row_result in validated_rows:
                if not row_result['valid']:
                    continue
                
                try:
                    data = row_result['data']
                    
                    # Crear o obtener el evento
                    event, created = Event.objects.get_or_create(
                        name=data['event_name'],
                        event_date=data['event_date'],
                        defaults={'description': ''}
                    )
                    
                    if created:
                        logger.info(f"Evento creado: {event.name} - {event.event_date}")
                    
                    # Crear o actualizar el participante
                    participant, created = Participant.objects.update_or_create(
                        dni=data['dni'],
                        event=event,
                        defaults={
                            'full_name': data['full_name'],
                            'attendee_type': data['attendee_type']
                        }
                    )
                    
                    if created:
                        logger.info(f"Participante creado: {participant.full_name} ({participant.dni})")
                    else:
                        logger.info(f"Participante actualizado: {participant.full_name} ({participant.dni})")
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"Fila {row_result['row_number']}: Error al procesar - {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Registrar en auditoría
            AuditLog.objects.create(
                action_type='IMPORT',
                user=user,
                description=f"Importación de CSV: {success_count} éxitos, {error_count} errores",
                metadata={
                    'success_count': success_count,
                    'error_count': error_count,
                    'total_rows': success_count + error_count,
                    'file_type': 'CSV'
                }
            )
            
            logger.info(f"Importación CSV completada: {success_count} éxitos, {error_count} errores")
            
        except Exception as e:
            error_msg = f"Error al procesar archivo: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            error_count += 1
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }
