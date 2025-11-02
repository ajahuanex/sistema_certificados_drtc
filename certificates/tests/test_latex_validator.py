"""
Tests para el validador de LaTeX.
"""
from django.test import TestCase
from certificates.services.latex_validator import LaTeXValidator, validate_latex_quick, sanitize_latex


class LaTeXValidatorTests(TestCase):
    """Tests para la clase LaTeXValidator"""
    
    def setUp(self):
        self.validator = LaTeXValidator()
    
    def test_valid_inline_math(self):
        """Verifica validación de matemáticas inline válidas"""
        latex_code = "$E = mc^2$"
        result = self.validator.validate_latex(latex_code)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(result['sanitized_code'], latex_code)
    
    def test_valid_display_math(self):
        """Verifica validación de matemáticas display válidas"""
        latex_code = "$$\\int_0^1 x^2 dx = \\frac{1}{3}$$"
        result = self.validator.validate_latex(latex_code)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_valid_fraction(self):
        """Verifica validación de fracciones"""
        latex_code = "$\\frac{a}{b} + \\frac{c}{d}$"
        result = self.validator.validate_latex(latex_code)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_valid_matrix(self):
        """Verifica validación de matrices"""
        latex_code = """$$\\begin{pmatrix}
        a & b \\\\
        c & d
        \\end{pmatrix}$$"""
        result = self.validator.validate_latex(latex_code)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_empty_code(self):
        """Verifica que código vacío sea inválido"""
        result = self.validator.validate_latex("")
        
        self.assertFalse(result['is_valid'])
        self.assertIn('no puede estar vacío', result['errors'][0])
    
    def test_forbidden_commands(self):
        """Verifica que comandos prohibidos sean rechazados"""
        forbidden_codes = [
            "\\input{malicious.tex}",
            "\\write18{rm -rf /}",
            "\\def\\hack{dangerous}",
            "\\catcode`\\@=11",
            "\\immediate\\write18{echo hack}"
        ]
        
        for code in forbidden_codes:
            result = self.validator.validate_latex(code)
            self.assertFalse(result['is_valid'], f"Código prohibido no detectado: {code}")
            self.assertGreater(len(result['errors']), 0)
    
    def test_unbalanced_delimiters(self):
        """Verifica detección de delimitadores desbalanceados"""
        unbalanced_codes = [
            "$E = mc^2",  # Falta $
            "$$E = mc^2$",  # Desbalanceado
            "$E = mc^2$$$",  # Extra $
            "\\(E = mc^2",  # Falta \\)
        ]
        
        for code in unbalanced_codes:
            result = self.validator.validate_latex(code)
            self.assertFalse(result['is_valid'], f"Delimitadores desbalanceados no detectados: {code}")
    
    def test_unbalanced_braces(self):
        """Verifica detección de llaves desbalanceadas"""
        unbalanced_codes = [
            "\\frac{a{b}",  # Falta }
            "\\frac{a}b}",  # Extra }
            "\\sqrt{x + y",  # Falta }
        ]
        
        for code in unbalanced_codes:
            result = self.validator.validate_latex(code)
            self.assertFalse(result['is_valid'], f"Llaves desbalanceadas no detectadas: {code}")
    
    def test_unbalanced_environments(self):
        """Verifica detección de entornos desbalanceados"""
        unbalanced_codes = [
            "\\begin{matrix} a & b \\\\ c & d",  # Falta \\end{matrix}
            "\\begin{pmatrix} a \\\\ b \\end{matrix}",  # Entorno incorrecto
            "a \\\\ b \\end{pmatrix}",  # Falta \\begin{pmatrix}
        ]
        
        for code in unbalanced_codes:
            result = self.validator.validate_latex(code)
            self.assertFalse(result['is_valid'], f"Entornos desbalanceados no detectados: {code}")
    
    def test_unknown_commands_warning(self):
        """Verifica que comandos desconocidos generen advertencias"""
        latex_code = "$\\unknowncommand{x} + \\anotherbadcmd$"
        result = self.validator.validate_latex(latex_code)
        
        # Debe ser válido pero con advertencias
        self.assertTrue(result['is_valid'])
        self.assertGreater(len(result['warnings']), 0)
        self.assertTrue(any('desconocido' in warning for warning in result['warnings']))
    
    def test_sanitization(self):
        """Verifica sanitización de código"""
        dirty_code = """
        % Este es un comentario
        $E = mc^2$   % Otro comentario
        
        \\input{hack}  % Comando prohibido
        """
        
        result = self.validator.validate_latex(dirty_code)
        sanitized = result['sanitized_code']
        
        # No debe contener comentarios ni comandos prohibidos
        self.assertNotIn('%', sanitized)
        self.assertNotIn('\\input', sanitized)
        self.assertIn('$E = mc^2$', sanitized)
    
    def test_extract_math_content(self):
        """Verifica extracción de contenido matemático"""
        latex_code = "Texto normal $E = mc^2$ más texto $$\\int_0^1 x dx$$ final"
        math_blocks = self.validator.extract_math_content(latex_code)
        
        self.assertEqual(len(math_blocks), 2)
        
        # Primer bloque (inline)
        self.assertEqual(math_blocks[0]['type'], 'inline')
        self.assertEqual(math_blocks[0]['content'], 'E = mc^2')
        
        # Segundo bloque (display)
        self.assertEqual(math_blocks[1]['type'], 'display')
        self.assertEqual(math_blocks[1]['content'], '\\int_0^1 x dx')
    
    def test_extract_math_environments(self):
        """Verifica extracción de entornos matemáticos"""
        latex_code = """
        \\begin{equation}
        E = mc^2
        \\end{equation}
        
        \\begin{align}
        a &= b \\\\
        c &= d
        \\end{align}
        """
        
        math_blocks = self.validator.extract_math_content(latex_code)
        
        self.assertEqual(len(math_blocks), 2)
        self.assertEqual(math_blocks[0]['environment'], 'equation')
        self.assertEqual(math_blocks[1]['environment'], 'align')
    
    def test_suggest_corrections(self):
        """Verifica sugerencias de corrección"""
        # Código con errores comunes
        latex_code = "alpha + beta >= gamma"
        suggestions = self.validator.suggest_corrections(latex_code)
        
        self.assertGreater(len(suggestions), 0)
        
        # Debe sugerir usar símbolos LaTeX
        suggestion_texts = [s['message'] for s in suggestions]
        self.assertTrue(any('alpha' in text for text in suggestion_texts))
        self.assertTrue(any('>=' in text for text in suggestion_texts))
    
    def test_complex_valid_formula(self):
        """Verifica fórmula compleja válida"""
        latex_code = """$$
        \\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}
        $$"""
        
        result = self.validator.validate_latex(latex_code)
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_greek_letters(self):
        """Verifica letras griegas"""
        latex_code = "$\\alpha + \\beta = \\gamma \\cdot \\delta$"
        result = self.validator.validate_latex(latex_code)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_mathematical_operators(self):
        """Verifica operadores matemáticos"""
        latex_code = "$\\sin(x) + \\cos(y) = \\log(z) \\cdot \\exp(w)$"
        result = self.validator.validate_latex(latex_code)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)


class LaTeXUtilityFunctionsTests(TestCase):
    """Tests para funciones de utilidad"""
    
    def test_validate_latex_quick_valid(self):
        """Verifica validación rápida con código válido"""
        self.assertTrue(validate_latex_quick("$E = mc^2$"))
    
    def test_validate_latex_quick_invalid(self):
        """Verifica validación rápida con código inválido"""
        self.assertFalse(validate_latex_quick("\\input{hack}"))
    
    def test_sanitize_latex_function(self):
        """Verifica función de sanitización"""
        dirty_code = "% Comentario\n$E = mc^2$ \\input{hack}"
        clean_code = sanitize_latex(dirty_code)
        
        self.assertNotIn('%', clean_code)
        self.assertNotIn('\\input', clean_code)
        self.assertIn('$E = mc^2$', clean_code)


class LaTeXSecurityTests(TestCase):
    """Tests específicos de seguridad"""
    
    def setUp(self):
        self.validator = LaTeXValidator()
    
    def test_file_inclusion_blocked(self):
        """Verifica que inclusión de archivos esté bloqueada"""
        malicious_codes = [
            "\\input{/etc/passwd}",
            "\\include{../../../etc/shadow}",
            "\\InputIfFileExists{config.txt}{}{}",
        ]
        
        for code in malicious_codes:
            result = self.validator.validate_latex(code)
            self.assertFalse(result['is_valid'])
    
    def test_command_execution_blocked(self):
        """Verifica que ejecución de comandos esté bloqueada"""
        malicious_codes = [
            "\\immediate\\write18{rm -rf /}",
            "\\write18{cat /etc/passwd}",
            "\\special{sh:rm important.txt}",
        ]
        
        for code in malicious_codes:
            result = self.validator.validate_latex(code)
            self.assertFalse(result['is_valid'])
    
    def test_catcode_manipulation_blocked(self):
        """Verifica que manipulación de catcodes esté bloqueada"""
        malicious_codes = [
            "\\catcode`\\@=11",
            "\\catcode`\\!=0",
            "\\def\\malicious{hack}",
        ]
        
        for code in malicious_codes:
            result = self.validator.validate_latex(code)
            self.assertFalse(result['is_valid'])
    
    def test_safe_math_commands_allowed(self):
        """Verifica que comandos matemáticos seguros estén permitidos"""
        safe_codes = [
            "$\\frac{1}{2}$",
            "$\\sqrt{x}$",
            "$\\sum_{i=1}^n i$",
            "$\\int_0^1 f(x) dx$",
            "$\\alpha + \\beta$",
            "$\\sin(x) + \\cos(y)$",
        ]
        
        for code in safe_codes:
            result = self.validator.validate_latex(code)
            self.assertTrue(result['is_valid'], f"Código seguro rechazado: {code}")


class LaTeXComplexFormulasTests(TestCase):
    """Tests con fórmulas complejas reales"""
    
    def setUp(self):
        self.validator = LaTeXValidator()
    
    def test_quadratic_formula(self):
        """Verifica fórmula cuadrática"""
        latex_code = "$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$"
        result = self.validator.validate_latex(latex_code)
        self.assertTrue(result['is_valid'])
    
    def test_euler_identity(self):
        """Verifica identidad de Euler"""
        latex_code = "$e^{i\\pi} + 1 = 0$"
        result = self.validator.validate_latex(latex_code)
        self.assertTrue(result['is_valid'])
    
    def test_integral_formula(self):
        """Verifica fórmula integral compleja"""
        latex_code = "$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$"
        result = self.validator.validate_latex(latex_code)
        self.assertTrue(result['is_valid'])
    
    def test_matrix_determinant(self):
        """Verifica determinante de matriz"""
        latex_code = """$$
        \\det\\begin{pmatrix}
        a & b \\\\
        c & d
        \\end{pmatrix} = ad - bc
        $$"""
        result = self.validator.validate_latex(latex_code)
        self.assertTrue(result['is_valid'])
    
    def test_summation_formula(self):
        """Verifica fórmula de sumatoria"""
        latex_code = "$$\\sum_{k=1}^{n} k = \\frac{n(n+1)}{2}$$"
        result = self.validator.validate_latex(latex_code)
        self.assertTrue(result['is_valid'])
    
    def test_limit_formula(self):
        """Verifica fórmula de límite"""
        latex_code = "$$\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1$$"
        result = self.validator.validate_latex(latex_code)
        self.assertTrue(result['is_valid'])