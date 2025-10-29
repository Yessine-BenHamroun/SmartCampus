"""
Code validation utilities for assignments
Uses Python's ast module for syntax checking without external APIs
"""
import ast
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr


def validate_python_syntax(code):
    """
    Validate Python code syntax and return errors if any
    
    Args:
        code (str): Python code to validate
        
    Returns:
        dict: Contains validation results with errors and line numbers
    """
    result = {
        'valid': True,
        'errors': [],
        'line_numbers': [],
        'warnings': []
    }
    
    if not code or not code.strip():
        result['valid'] = False
        result['errors'].append('Code cannot be empty')
        return result
    
    try:
        # Try to parse the code using AST
        ast.parse(code)
    except SyntaxError as e:
        result['valid'] = False
        error_msg = f"Line {e.lineno}: {e.msg}"
        if e.text:
            error_msg += f" - '{e.text.strip()}'"
        result['errors'].append(error_msg)
        result['line_numbers'].append(e.lineno)
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Parsing error: {str(e)}")
    
    return result


def get_syntax_highlighted_code(code, language='python'):
    """
    Get syntax highlighted HTML for code
    
    Args:
        code (str): Code to highlight
        language (str): Programming language
        
    Returns:
        str: HTML with syntax highlighting
    """
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import HtmlFormatter
        
        lexer = get_lexer_by_name(language, stripall=True)
        formatter = HtmlFormatter(
            linenos=True,
            cssclass='source',
            style='monokai',
            linenostart=1
        )
        
        result = highlight(code, lexer, formatter)
        css = formatter.get_style_defs('.source')
        
        return {
            'html': result,
            'css': css
        }
    except ImportError:
        # Fallback if Pygments is not installed
        lines = code.split('\n')
        html = '<pre class="source">'
        for i, line in enumerate(lines, 1):
            html += f'<span class="line-number">{i}</span> {line}\n'
        html += '</pre>'
        return {
            'html': html,
            'css': ''
        }


def check_code_quality(code):
    """
    Basic code quality checks
    
    Args:
        code (str): Python code to check
        
    Returns:
        dict: Quality metrics and suggestions
    """
    result = {
        'line_count': 0,
        'has_comments': False,
        'has_docstrings': False,
        'suggestions': []
    }
    
    if not code:
        return result
    
    lines = code.split('\n')
    result['line_count'] = len([l for l in lines if l.strip()])
    
    # Check for comments
    result['has_comments'] = any('#' in line for line in lines)
    
    # Check for docstrings
    result['has_docstrings'] = '"""' in code or "'''" in code
    
    # Suggestions
    if not result['has_comments'] and result['line_count'] > 10:
        result['suggestions'].append('Consider adding comments to explain complex logic')
    
    if not result['has_docstrings'] and 'def ' in code:
        result['suggestions'].append('Consider adding docstrings to your functions')
    
    # Check for common issues
    if 'print(' in code:
        result['suggestions'].append('Code contains print statements - consider using logging')
    
    return result


def safe_execute_code(code, test_input=None, timeout=5):
    """
    Safely execute Python code with timeout and capture output
    WARNING: This should be used with caution and proper sandboxing
    
    Args:
        code (str): Python code to execute
        test_input (str): Input to provide to the code
        timeout (int): Maximum execution time in seconds
        
    Returns:
        dict: Execution results
    """
    result = {
        'success': False,
        'output': '',
        'errors': '',
        'execution_time': 0
    }
    
    # First validate syntax
    validation = validate_python_syntax(code)
    if not validation['valid']:
        result['errors'] = '\n'.join(validation['errors'])
        return result
    
    # Capture stdout and stderr
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    try:
        import time
        start_time = time.time()
        
        # Create a restricted namespace
        namespace = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'bool': bool,
                'abs': abs,
                'max': max,
                'min': min,
                'sum': sum,
                'sorted': sorted,
                'enumerate': enumerate,
                'zip': zip,
            }
        }
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, namespace)
        
        result['success'] = True
        result['output'] = stdout_capture.getvalue()
        result['execution_time'] = time.time() - start_time
        
    except Exception as e:
        result['errors'] = str(e)
        result['output'] = stdout_capture.getvalue()
        
    if stderr_capture.getvalue():
        result['errors'] += '\n' + stderr_capture.getvalue()
    
    return result
