"""
Servicio para validación y procesamiento de código LaTeX.
"""
import re
from typing import Dict, List, Tuple, Optional


class LaTeXValidator:
    """Validador de sintaxis LaTeX para el editor de plantillas"""
    
    # Comandos LaTeX peligrosos que deben ser bloqueados por seguridad
    FORBIDDEN_COMMANDS = [
        r'\\input',
        r'\\include',
        r'\\write',
        r'\\immediate',
        r'\\openout',
        r'\\openin',
        r'\\read',
        r'\\catcode',
        r'\\def',
        r'\\gdef',
        r'\\edef',
        r'\\xdef',
        r'\\let',
        r'\\futurelet',
        r'\\expandafter',
        r'\\noexpand',
        r'\\csname',
        r'\\endcsname',
        r'\\string',
        r'\\meaning',
        r'\\jobname',
        r'\\special',
        r'\\message',
        r'\\errmessage',
        r'\\show',
        r'\\showthe',
        r'\\tracingall',
        r'\\end\{document\}',
        r'\\documentclass',
        r'\\usepackage',
    ]
    
    # Comandos LaTeX permitidos para matemáticas
    ALLOWED_MATH_COMMANDS = [
        # Operadores básicos
        r'\\frac', r'\\sqrt', r'\\sum', r'\\int', r'\\prod', r'\\lim',
        r'\\sin', r'\\cos', r'\\tan', r'\\log', r'\\ln', r'\\exp',
        r'\\alpha', r'\\beta', r'\\gamma', r'\\delta', r'\\epsilon',
        r'\\theta', r'\\lambda', r'\\mu', r'\\pi', r'\\sigma', r'\\phi',
        r'\\omega', r'\\Gamma', r'\\Delta', r'\\Theta', r'\\Lambda',
        r'\\Pi', r'\\Sigma', r'\\Phi', r'\\Omega',
        
        # Símbolos matemáticos
        r'\\infty', r'\\partial', r'\\nabla', r'\\pm', r'\\mp',
        r'\\times', r'\\div', r'\\cdot', r'\\bullet', r'\\circ',
        r'\\leq', r'\\geq', r'\\neq', r'\\approx', r'\\equiv',
        r'\\subset', r'\\supset', r'\\subseteq', r'\\supseteq',
        r'\\in', r'\\notin', r'\\cup', r'\\cap', r'\\emptyset',
        
        # Estructuras
        r'\\left', r'\\right', r'\\big', r'\\Big', r'\\bigg', r'\\Bigg',
        r'\\overline', r'\\underline', r'\\hat', r'\\tilde', r'\\vec',
        r'\\dot', r'\\ddot', r'\\bar', r'\\acute', r'\\grave',
        
        # Matrices y arrays
        r'\\begin\{matrix\}', r'\\end\{matrix\}',
        r'\\begin\{pmatrix\}', r'\\end\{pmatrix\}',
        r'\\begin\{bmatrix\}', r'\\end\{bmatrix\}',
        r'\\begin\{vmatrix\}', r'\\end\{vmatrix\}',
        r'\\begin\{array\}', r'\\end\{array\}',
        
        # Espaciado
        r'\\quad', r'\\qquad', r'\\,', r'\\:', r'\\;', r'\\!',
        
        # Texto en matemáticas
        r'\\text', r'\\mathrm', r'\\mathbf', r'\\mathit', r'\\mathcal',
        r'\\mathbb', r'\\mathfrak', r'\\mathsf', r'\\mathtt',
    ]
    
    def __init__(self):
        self.forbidden_pattern = '|'.join(self.FORBIDDEN_COMMANDS)
        self.allowed_pattern = '|'.join(self.ALLOWED_MATH_COMMANDS)
    
    def validate_latex(self, latex_code: str) -> Dict[str, any]:
        """
        Valida código LaTeX y retorna resultado de validación.
        
        Args:
            latex_code: Código LaTeX a validar
            
        Returns:
            Dict con resultado de validación:
            {
                'is_valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'sanitized_code': str
            }
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'sanitized_code': latex_code.strip()
        }
        
        if not latex_code.strip():
            result['errors'].append('El código LaTeX no puede estar vacío')
            result['is_valid'] = False
            return result
        
        # Verificar comandos prohibidos
        security_check = self._check_security(latex_code)
        if not security_check['is_safe']:
            result['errors'].extend(security_check['violations'])
            result['is_valid'] = False
            return result
        
        # Verificar sintaxis básica
        syntax_check = self._check_syntax(latex_code)
        if not syntax_check['is_valid']:
            result['errors'].extend(syntax_check['errors'])
            result['is_valid'] = False
        
        result['warnings'].extend(syntax_check.get('warnings', []))
        
        # Sanitizar código
        result['sanitized_code'] = self._sanitize_code(latex_code)
        
        return result
    
    def _check_security(self, latex_code: str) -> Dict[str, any]:
        """Verifica que no haya comandos peligrosos"""
        violations = []
        
        # Buscar comandos prohibidos
        for forbidden_cmd in self.FORBIDDEN_COMMANDS:
            if re.search(forbidden_cmd, latex_code, re.IGNORECASE):
                command_name = forbidden_cmd.replace('\\\\', '\\').replace('\\{', '{').replace('\\}', '}')
                violations.append(f'Comando prohibido por seguridad: {command_name}')
        
        # Verificar intentos de escape
        if '\\catcode' in latex_code or '\\def' in latex_code:
            violations.append('Definiciones de comandos no permitidas')
        
        # Verificar archivos externos
        if re.search(r'\\(input|include|InputIfFileExists)', latex_code, re.IGNORECASE):
            violations.append('Inclusión de archivos externos no permitida')
        
        return {
            'is_safe': len(violations) == 0,
            'violations': violations
        }
    
    def _check_syntax(self, latex_code: str) -> Dict[str, any]:
        """Verifica sintaxis básica de LaTeX"""
        errors = []
        warnings = []
        
        # Verificar delimitadores matemáticos balanceados
        math_delimiters = [
            ('$', '$'),
            ('$$', '$$'),
            ('\\(', '\\)'),
            ('\\[', '\\]')
        ]
        
        for open_delim, close_delim in math_delimiters:
            open_count = latex_code.count(open_delim)
            close_count = latex_code.count(close_delim)
            
            if open_count != close_count:
                errors.append(f'Delimitadores matemáticos desbalanceados: {open_delim}...{close_delim}')
        
        # Verificar llaves balanceadas
        brace_balance = self._check_brace_balance(latex_code)
        if not brace_balance['balanced']:
            errors.append('Llaves desbalanceadas en el código LaTeX')
        
        # Verificar entornos (begin/end)
        env_check = self._check_environments(latex_code)
        if not env_check['valid']:
            errors.extend(env_check['errors'])
        
        # Verificar comandos válidos
        unknown_commands = self._find_unknown_commands(latex_code)
        if unknown_commands:
            warnings.extend([f'Comando desconocido: {cmd}' for cmd in unknown_commands])
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _check_brace_balance(self, latex_code: str) -> Dict[str, any]:
        """Verifica que las llaves estén balanceadas"""
        stack = []
        position = 0
        
        for char in latex_code:
            if char == '{':
                stack.append(position)
            elif char == '}':
                if not stack:
                    return {
                        'balanced': False,
                        'error_position': position,
                        'error': 'Llave de cierre sin apertura correspondiente'
                    }
                stack.pop()
            position += 1
        
        if stack:
            return {
                'balanced': False,
                'error_position': stack[-1],
                'error': 'Llave de apertura sin cierre correspondiente'
            }
        
        return {'balanced': True}
    
    def _check_environments(self, latex_code: str) -> Dict[str, any]:
        """Verifica que los entornos begin/end estén balanceados"""
        begin_pattern = r'\\begin\{([^}]+)\}'
        end_pattern = r'\\end\{([^}]+)\}'
        
        begins = re.findall(begin_pattern, latex_code)
        ends = re.findall(end_pattern, latex_code)
        
        errors = []
        
        # Verificar que cada begin tenga su end correspondiente
        begin_stack = begins.copy()
        for env in ends:
            if env in begin_stack:
                begin_stack.remove(env)
            else:
                errors.append(f'\\end{{{env}}} sin \\begin{{{env}}} correspondiente')
        
        # Verificar begins sin end
        for env in begin_stack:
            errors.append(f'\\begin{{{env}}} sin \\end{{{env}}} correspondiente')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _find_unknown_commands(self, latex_code: str) -> List[str]:
        """Encuentra comandos LaTeX que no están en la lista de permitidos"""
        # Extraer todos los comandos LaTeX
        command_pattern = r'\\([a-zA-Z]+)'
        commands = re.findall(command_pattern, latex_code)
        
        unknown_commands = []
        
        for cmd in set(commands):  # Usar set para evitar duplicados
            full_cmd = f'\\{cmd}'
            
            # Verificar si el comando está en la lista de permitidos
            is_allowed = any(
                re.search(allowed_cmd.replace('\\\\', '\\'), full_cmd)
                for allowed_cmd in self.ALLOWED_MATH_COMMANDS
            )
            
            if not is_allowed:
                unknown_commands.append(full_cmd)
        
        return unknown_commands
    
    def _sanitize_code(self, latex_code: str) -> str:
        """Sanitiza el código LaTeX removiendo elementos peligrosos"""
        sanitized = latex_code.strip()
        
        # Remover comentarios LaTeX
        sanitized = re.sub(r'%.*$', '', sanitized, flags=re.MULTILINE)
        
        # Remover espacios extra
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remover comandos prohibidos (por si acaso)
        for forbidden_cmd in self.FORBIDDEN_COMMANDS:
            sanitized = re.sub(forbidden_cmd, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def extract_math_content(self, latex_code: str) -> List[Dict[str, str]]:
        """
        Extrae contenido matemático del código LaTeX.
        
        Returns:
            Lista de diccionarios con:
            {
                'type': 'inline' | 'display',
                'content': str,
                'start': int,
                'end': int
            }
        """
        math_blocks = []
        
        # Buscar matemáticas display ($$...$$)
        display_pattern = r'\$\$(.*?)\$\$'
        for match in re.finditer(display_pattern, latex_code, re.DOTALL):
            math_blocks.append({
                'type': 'display',
                'content': match.group(1).strip(),
                'start': match.start(),
                'end': match.end()
            })
        
        # Buscar matemáticas inline ($...$) que no sean parte de display
        inline_pattern = r'(?<!\$)\$([^$]+?)\$(?!\$)'
        for match in re.finditer(inline_pattern, latex_code):
            # Verificar que no esté dentro de un bloque display
            is_inside_display = any(
                block['start'] <= match.start() <= block['end']
                for block in math_blocks
                if block['type'] == 'display'
            )
            
            if not is_inside_display:
                math_blocks.append({
                    'type': 'inline',
                    'content': match.group(1).strip(),
                    'start': match.start(),
                    'end': match.end()
                })
        
        # Buscar entornos matemáticos
        env_pattern = r'\\begin\{(equation|align|gather|multline|split)\}(.*?)\\end\{\1\}'
        for match in re.finditer(env_pattern, latex_code, re.DOTALL):
            math_blocks.append({
                'type': 'display',
                'content': match.group(2).strip(),
                'start': match.start(),
                'end': match.end(),
                'environment': match.group(1)
            })
        
        # Ordenar por posición
        math_blocks.sort(key=lambda x: x['start'])
        
        return math_blocks
    
    def suggest_corrections(self, latex_code: str) -> List[Dict[str, str]]:
        """
        Sugiere correcciones para errores comunes en LaTeX.
        
        Returns:
            Lista de sugerencias con:
            {
                'type': 'error' | 'warning' | 'suggestion',
                'message': str,
                'suggestion': str (opcional)
            }
        """
        suggestions = []
        
        # Sugerir delimitadores matemáticos
        if not re.search(r'[\$\\]', latex_code):
            suggestions.append({
                'type': 'suggestion',
                'message': 'Considera usar delimitadores matemáticos',
                'suggestion': 'Usa $ para matemáticas inline o $$ para display'
            })
        
        # Detectar fracciones mal formadas
        if 'frac' in latex_code and not re.search(r'\\frac\{[^}]*\}\{[^}]*\}', latex_code):
            suggestions.append({
                'type': 'warning',
                'message': 'Fracción posiblemente mal formada',
                'suggestion': 'Usa \\frac{numerador}{denominador}'
            })
        
        # Detectar raíces mal formadas
        if 'sqrt' in latex_code and not re.search(r'\\sqrt(\[[^\]]*\])?\{[^}]*\}', latex_code):
            suggestions.append({
                'type': 'warning',
                'message': 'Raíz posiblemente mal formada',
                'suggestion': 'Usa \\sqrt{expresión} o \\sqrt[n]{expresión}'
            })
        
        # Sugerir uso de comandos matemáticos
        common_replacements = {
            'infinity': '\\infty',
            'alpha': '\\alpha',
            'beta': '\\beta',
            'gamma': '\\gamma',
            'delta': '\\delta',
            'pi': '\\pi',
            'theta': '\\theta',
            'lambda': '\\lambda',
            'sigma': '\\sigma',
            'omega': '\\omega',
            '<=': '\\leq',
            '>=': '\\geq',
            '!=': '\\neq',
            '+-': '\\pm',
            '*': '\\cdot',
        }
        
        for text, latex_cmd in common_replacements.items():
            if text in latex_code.lower():
                suggestions.append({
                    'type': 'suggestion',
                    'message': f'Considera reemplazar "{text}" con "{latex_cmd}"',
                    'suggestion': latex_cmd
                })
        
        return suggestions


# Función de utilidad para validación rápida
def validate_latex_quick(latex_code: str) -> bool:
    """
    Validación rápida de LaTeX para uso en formularios.
    
    Args:
        latex_code: Código LaTeX a validar
        
    Returns:
        True si el código es válido, False en caso contrario
    """
    validator = LaTeXValidator()
    result = validator.validate_latex(latex_code)
    return result['is_valid']


# Función para sanitizar LaTeX
def sanitize_latex(latex_code: str) -> str:
    """
    Sanitiza código LaTeX removiendo elementos peligrosos.
    
    Args:
        latex_code: Código LaTeX a sanitizar
        
    Returns:
        Código LaTeX sanitizado
    """
    validator = LaTeXValidator()
    result = validator.validate_latex(latex_code)
    return result['sanitized_code']