import numpy as np
import sympy as sp
from typing import List, Tuple, Dict, Any, Callable

def _parse_function(func_str: str) -> Callable[[float], float]:
    """Convierte string de función a función evaluable de forma segura"""
    if not func_str or not func_str.strip():
        raise ValueError("La función no puede estar vacía")
    
    func_str = func_str.strip().replace('^', '**')
    
    try:
        x = sp.Symbol('x')
        expr = sp.sympify(func_str, locals={'x': x})
        func = sp.lambdify(x, expr, 'numpy')
        
        # Probar que funcione
        test_val = func(1.0)
        if not isinstance(test_val, (int, float, np.number)) or np.isnan(test_val):
            if not np.isinf(test_val):  # Infinito puede ser válido en algunos casos
                raise ValueError("La función no devuelve valores numéricos válidos")
        
        return func
    
    except Exception as e:
        raise ValueError(f"Error al parsear la función '{func_str}': {str(e)}")

def _validate_derivative_params(x: float, h: float, order: int) -> None:
    """Valida parámetros de derivación"""
    if not isinstance(x, (int, float)) or np.isnan(x) or np.isinf(x):
        raise ValueError(f"Punto de evaluación 'x' no válido: {x}")
    
    if not isinstance(h, (int, float)) or h <= 0 or np.isnan(h) or np.isinf(h):
        raise ValueError(f"Paso 'h' debe ser positivo: {h}")
    
    if h > 1.0:
        raise ValueError(f"Paso 'h' demasiado grande, puede causar errores: {h}")
    
    if h < 1e-12:
        raise ValueError(f"Paso 'h' demasiado pequeño, puede causar errores numéricos: {h}")
    
    if not isinstance(order, int) or order < 1 or order > 4:
        raise ValueError(f"Orden de derivada debe ser 1, 2, 3 o 4: {order}")

# ============= DIFERENCIAS HACIA ADELANTE =============
def diff_adelante(func_str: str, x: float, h: float, order: int = 1) -> Tuple[float, str]:
    """Diferencias finitas hacia adelante"""
    _validate_derivative_params(x, h, order)
    func = _parse_function(func_str)
    
    try:
        if order == 1:
            # f'(x) ≈ [f(x+h) - f(x)] / h
            fx = func(x)
            fx_h = func(x + h)
            derivative = (fx_h - fx) / h
            formula = "f'(x) ≈ [f(x+h) - f(x)] / h"
            
        elif order == 2:
            # f''(x) ≈ [f(x+2h) - 2f(x+h) + f(x)] / h²
            fx = func(x)
            fx_h = func(x + h)
            fx_2h = func(x + 2*h)
            derivative = (fx_2h - 2*fx_h + fx) / (h**2)
            formula = "f''(x) ≈ [f(x+2h) - 2f(x+h) + f(x)] / h²"
            
        elif order == 3:
            # f'''(x) ≈ [f(x+3h) - 3f(x+2h) + 3f(x+h) - f(x)] / h³
            fx = func(x)
            fx_h = func(x + h)
            fx_2h = func(x + 2*h)
            fx_3h = func(x + 3*h)
            derivative = (fx_3h - 3*fx_2h + 3*fx_h - fx) / (h**3)
            formula = "f'''(x) ≈ [f(x+3h) - 3f(x+2h) + 3f(x+h) - f(x)] / h³"
            
        elif order == 4:
            # f⁽⁴⁾(x) ≈ [f(x+4h) - 4f(x+3h) + 6f(x+2h) - 4f(x+h) + f(x)] / h⁴
            fx = func(x)
            fx_h = func(x + h)
            fx_2h = func(x + 2*h)
            fx_3h = func(x + 3*h)
            fx_4h = func(x + 4*h)
            derivative = (fx_4h - 4*fx_3h + 6*fx_2h - 4*fx_h + fx) / (h**4)
            formula = "f⁽⁴⁾(x) ≈ [f(x+4h) - 4f(x+3h) + 6f(x+2h) - 4f(x+h) + f(x)] / h⁴"
            
        # Verificar que el resultado sea válido
        if np.isnan(derivative) or np.isinf(derivative):
            raise ValueError(f"El cálculo resultó en {derivative}. Intenta con un h diferente.")
            
        return float(derivative), formula
        
    except Exception as e:
        raise ValueError(f"Error al calcular derivada hacia adelante: {str(e)}")

# ============= DIFERENCIAS HACIA ATRÁS =============
def diff_atras(func_str: str, x: float, h: float, order: int = 1) -> Tuple[float, str]:
    """Diferencias finitas hacia atrás"""
    _validate_derivative_params(x, h, order)
    func = _parse_function(func_str)
    
    try:
        if order == 1:
            # f'(x) ≈ [f(x) - f(x-h)] / h
            fx = func(x)
            fx_h = func(x - h)
            derivative = (fx - fx_h) / h
            formula = "f'(x) ≈ [f(x) - f(x-h)] / h"
            
        elif order == 2:
            # f''(x) ≈ [f(x) - 2f(x-h) + f(x-2h)] / h²
            fx = func(x)
            fx_h = func(x - h)
            fx_2h = func(x - 2*h)
            derivative = (fx - 2*fx_h + fx_2h) / (h**2)
            formula = "f''(x) ≈ [f(x) - 2f(x-h) + f(x-2h)] / h²"
            
        elif order == 3:
            # f'''(x) ≈ [f(x) - 3f(x-h) + 3f(x-2h) - f(x-3h)] / h³
            fx = func(x)
            fx_h = func(x - h)
            fx_2h = func(x - 2*h)
            fx_3h = func(x - 3*h)
            derivative = (fx - 3*fx_h + 3*fx_2h - fx_3h) / (h**3)
            formula = "f'''(x) ≈ [f(x) - 3f(x-h) + 3f(x-2h) - f(x-3h)] / h³"
            
        elif order == 4:
            # f⁽⁴⁾(x) ≈ [f(x) - 4f(x-h) + 6f(x-2h) - 4f(x-3h) + f(x-4h)] / h⁴
            fx = func(x)
            fx_h = func(x - h)
            fx_2h = func(x - 2*h)
            fx_3h = func(x - 3*h)
            fx_4h = func(x - 4*h)
            derivative = (fx - 4*fx_h + 6*fx_2h - 4*fx_3h + fx_4h) / (h**4)
            formula = "f⁽⁴⁾(x) ≈ [f(x) - 4f(x-h) + 6f(x-2h) - 4f(x-3h) + f(x-4h)] / h⁴"
            
        # Verificar que el resultado sea válido
        if np.isnan(derivative) or np.isinf(derivative):
            raise ValueError(f"El cálculo resultó en {derivative}. Intenta con un h diferente.")
            
        return float(derivative), formula
        
    except Exception as e:
        raise ValueError(f"Error al calcular derivada hacia atrás: {str(e)}")

# ============= DIFERENCIAS CENTRADAS =============
def diff_centrada(func_str: str, x: float, h: float, order: int = 1) -> Tuple[float, str]:
    """Diferencias finitas centradas (mayor precisión)"""
    _validate_derivative_params(x, h, order)
    func = _parse_function(func_str)
    
    try:
        if order == 1:
            # f'(x) ≈ [f(x+h) - f(x-h)] / (2h)
            fx_pos = func(x + h)
            fx_neg = func(x - h)
            derivative = (fx_pos - fx_neg) / (2*h)
            formula = "f'(x) ≈ [f(x+h) - f(x-h)] / (2h)"
            
        elif order == 2:
            # f''(x) ≈ [f(x+h) - 2f(x) + f(x-h)] / h²
            fx = func(x)
            fx_pos = func(x + h)
            fx_neg = func(x - h)
            derivative = (fx_pos - 2*fx + fx_neg) / (h**2)
            formula = "f''(x) ≈ [f(x+h) - 2f(x) + f(x-h)] / h²"
            
        elif order == 3:
            # f'''(x) ≈ [f(x+2h) - 2f(x+h) + 2f(x-h) - f(x-2h)] / (2h³)
            fx_2pos = func(x + 2*h)
            fx_pos = func(x + h)
            fx_neg = func(x - h)
            fx_2neg = func(x - 2*h)
            derivative = (fx_2pos - 2*fx_pos + 2*fx_neg - fx_2neg) / (2*h**3)
            formula = "f'''(x) ≈ [f(x+2h) - 2f(x+h) + 2f(x-h) - f(x-2h)] / (2h³)"
            
        elif order == 4:
            # f⁽⁴⁾(x) ≈ [f(x+2h) - 4f(x+h) + 6f(x) - 4f(x-h) + f(x-2h)] / h⁴
            fx = func(x)
            fx_pos = func(x + h)
            fx_neg = func(x - h)
            fx_2pos = func(x + 2*h)
            fx_2neg = func(x - 2*h)
            derivative = (fx_2pos - 4*fx_pos + 6*fx - 4*fx_neg + fx_2neg) / (h**4)
            formula = "f⁽⁴⁾(x) ≈ [f(x+2h) - 4f(x+h) + 6f(x) - 4f(x-h) + f(x-2h)] / h⁴"
            
        # Verificar que el resultado sea válido
        if np.isnan(derivative) or np.isinf(derivative):
            raise ValueError(f"El cálculo resultó en {derivative}. Intenta con un h diferente.")
            
        return float(derivative), formula
        
    except Exception as e:
        raise ValueError(f"Error al calcular derivada centrada: {str(e)}")

# ============= ANÁLISIS DE ERROR =============
def estimate_error(func_str: str, x: float, h: float, method: str, order: int = 1) -> Dict[str, Any]:
    """Estima el error de truncamiento de los métodos de derivación"""
    
    error_formulas = {
        "adelante": {
            1: f"Error ≈ O(h) = O({h:.2e})",
            2: f"Error ≈ O(h) = O({h:.2e})",
            3: f"Error ≈ O(h) = O({h:.2e})",
            4: f"Error ≈ O(h) = O({h:.2e})"
        },
        "atras": {
            1: f"Error ≈ O(h) = O({h:.2e})",
            2: f"Error ≈ O(h) = O({h:.2e})",
            3: f"Error ≈ O(h) = O({h:.2e})",
            4: f"Error ≈ O(h) = O({h:.2e})"
        },
        "centrada": {
            1: f"Error ≈ O(h²) = O({h**2:.2e})",
            2: f"Error ≈ O(h²) = O({h**2:.2e})",
            3: f"Error ≈ O(h²) = O({h**2:.2e})",
            4: f"Error ≈ O(h²) = O({h**2:.2e})"
        }
    }
    
    return {
        "method": method,
        "order": order,
        "error_formula": error_formulas.get(method, {}).get(order, "Error no disponible"),
        "truncation_order": 2 if method == "centrada" else 1,
        "recommendation": "Usar diferencias centradas para mayor precisión" if method != "centrada" else "Método óptimo seleccionado"
    }

# ============= COMPARACIÓN DE MÉTODOS =============
def compare_methods(func_str: str, x: float, h: float, order: int = 1) -> Dict[str, Any]:
    """Compara los tres métodos de diferenciación"""
    
    try:
        deriv_adelante, _ = diff_adelante(func_str, x, h, order)
        deriv_atras, _ = diff_atras(func_str, x, h, order)
        deriv_centrada, _ = diff_centrada(func_str, x, h, order)
        
        # Calcular derivada exacta si es posible
        exact_deriv = None
        try:
            x_sym = sp.Symbol('x')
            expr = sp.sympify(func_str.replace('^', '**'))
            exact_expr = sp.diff(expr, x_sym, order)
            exact_func = sp.lambdify(x_sym, exact_expr, 'numpy')
            exact_deriv = float(exact_func(x))
        except:
            pass
        
        result = {
            "adelante": deriv_adelante,
            "atras": deriv_atras,
            "centrada": deriv_centrada,
            "exact": exact_deriv
        }
        
        if exact_deriv is not None:
            result["errors"] = {
                "adelante": abs(deriv_adelante - exact_deriv),
                "atras": abs(deriv_atras - exact_deriv),
                "centrada": abs(deriv_centrada - exact_deriv)
            }
            
            # Determinar el mejor método
            errors = result["errors"]
            best_method = min(errors.keys(), key=lambda k: errors[k])
            result["best_method"] = best_method
        
        return result
        
    except Exception as e:
        raise ValueError(f"Error en comparación de métodos: {str(e)}")

# ============= FUNCIONES DE EXPLICACIÓN =============
def get_adelante_explanation(func_str: str, x: float, h: float, order: int) -> Dict[str, Any]:
    return {
        "method": "Diferencias Finitas Hacia Adelante",
        "description": f"Aproxima la derivada de orden {order} usando puntos hacia adelante",
        "accuracy": "Primer orden O(h)",
        "pros": ["Simple de implementar", "Útil en extremo izquierdo del dominio"],
        "cons": ["Menor precisión", "Requiere puntos hacia adelante"],
        "use_case": "Cuando solo se tienen puntos hacia la derecha",
        "complexity": "O(1) por evaluación"
    }

def get_atras_explanation(func_str: str, x: float, h: float, order: int) -> Dict[str, Any]:
    return {
        "method": "Diferencias Finitas Hacia Atrás",
        "description": f"Aproxima la derivada de orden {order} usando puntos hacia atrás",
        "accuracy": "Primer orden O(h)",
        "pros": ["Simple de implementar", "Útil en extremo derecho del dominio"],
        "cons": ["Menor precisión", "Requiere puntos hacia atrás"],
        "use_case": "Cuando solo se tienen puntos hacia la izquierda",
        "complexity": "O(1) por evaluación"
    }

def get_centrada_explanation(func_str: str, x: float, h: float, order: int) -> Dict[str, Any]:
    return {
        "method": "Diferencias Finitas Centradas",
        "description": f"Aproxima la derivada de orden {order} usando puntos simétricos",
        "accuracy": "Segundo orden O(h²) - Mayor precisión",
        "pros": ["Mayor precisión", "Simétrica", "Menor error de truncamiento"],
        "cons": ["Requiere puntos en ambos lados"],
        "use_case": "Método preferido cuando es posible usarlo",
        "complexity": "O(1) por evaluación",
        "recommendation": "Método recomendado para máxima precisión"
    }