import numpy as np
import sympy as sp
from typing import List, Tuple, Dict, Any, Callable

def _parse_function(func_str: str) -> Callable[[float], float]:
    """Convierte string de función a función evaluable de forma segura"""
    if not func_str or not func_str.strip():
        raise ValueError("La función no puede estar vacía")
    
    # Limpiar y preparar la función
    func_str = func_str.strip().replace('^', '**')
    
    # Símbolos permitidos y funciones seguras
    allowed_names = {
        'x': None,
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'exp': np.exp, 'log': np.log, 'ln': np.log,
        'sqrt': np.sqrt, 'abs': np.abs,
        'pi': np.pi, 'e': np.e,
        'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
        'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
        'pow': pow, 'log10': np.log10
    }
    
    try:
        # Usar sympy para parsing seguro
        x = sp.Symbol('x')
        expr = sp.sympify(func_str, locals={'x': x})
        
        # Convertir a función numérica
        func = sp.lambdify(x, expr, 'numpy')
        
        # Probar que funcione
        test_val = func(1.0)
        if not isinstance(test_val, (int, float, np.number)) or np.isnan(test_val):
            if not np.isinf(test_val):  # Infinito puede ser válido en algunos casos
                raise ValueError("La función no devuelve valores numéricos válidos")
        
        return func
    
    except Exception as e:
        raise ValueError(f"Error al parsear la función '{func_str}': {str(e)}")

def _validate_integration_params(a: float, b: float, n: int) -> None:
    """Valida parámetros de integración"""
    if not isinstance(a, (int, float)) or np.isnan(a) or np.isinf(a):
        raise ValueError(f"Límite inferior 'a' no válido: {a}")
    
    if not isinstance(b, (int, float)) or np.isnan(b) or np.isinf(b):
        raise ValueError(f"Límite superior 'b' no válido: {b}")
    
    if a >= b:
        raise ValueError(f"El límite inferior debe ser menor al superior: {a} >= {b}")
    
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"Número de subdivisiones debe ser entero positivo: {n}")
    
    if n > 10000:
        raise ValueError(f"Número de subdivisiones demasiado grande: {n} > 10000")

# ============= REGLA DEL TRAPECIO =============
def trapecio_simple(func: Callable, a: float, b: float) -> float:
    """Regla del trapecio simple"""
    return (b - a) * (func(a) + func(b)) / 2

def trapecio_compuesto(func_str: str, a: float, b: float, n: int) -> Tuple[float, List[Dict]]:
    """Regla del trapecio compuesta con pasos detallados"""
    _validate_integration_params(a, b, n)
    func = _parse_function(func_str)
    
    h = (b - a) / n
    steps = []
    
    # Evaluar en los extremos
    fa = func(a)
    fb = func(b)
    
    steps.append({
        "step": 1,
        "description": f"h = (b-a)/n = ({b}-{a})/{n} = {h}",
        "x": a,
        "fx": fa
    })
    
    # Evaluar en puntos intermedios
    sum_intermediate = 0
    for i in range(1, n):
        xi = a + i * h
        fxi = func(xi)
        sum_intermediate += fxi
        
        if i <= 5:  # Mostrar solo los primeros 5 pasos
            steps.append({
                "step": i + 1,
                "description": f"x_{i} = {xi:.6f}",
                "x": xi,
                "fx": fxi
            })
    
    steps.append({
        "step": "final",
        "description": f"x_n = {b}",
        "x": b,
        "fx": fb
    })
    
    # Aplicar fórmula del trapecio compuesto
    result = h * (fa + 2 * sum_intermediate + fb) / 2
    
    steps.append({
        "step": "result",
        "description": f"Integral ≈ h/2 * [f(a) + 2*Σf(xi) + f(b)]",
        "formula": f"{h}/2 * [{fa:.6f} + 2*{sum_intermediate:.6f} + {fb:.6f}]",
        "result": result
    })
    
    return result, steps

# ============= REGLA DE SIMPSON 1/3 =============
def simpson_13_simple(func: Callable, a: float, b: float) -> float:
    """Regla de Simpson 1/3 simple"""
    c = (a + b) / 2
    return (b - a) * (func(a) + 4 * func(c) + func(b)) / 6

def simpson_13_compuesto(func_str: str, a: float, b: float, n: int) -> Tuple[float, List[Dict]]:
    """Regla de Simpson 1/3 compuesta"""
    _validate_integration_params(a, b, n)
    
    # n debe ser par para Simpson
    if n % 2 != 0:
        n += 1
    
    func = _parse_function(func_str)
    h = (b - a) / n
    steps = []
    
    # Evaluar función en todos los puntos
    x_vals = [a + i * h for i in range(n + 1)]
    f_vals = [func(x) for x in x_vals]
    
    steps.append({
        "step": 1,
        "description": f"h = (b-a)/n = ({b}-{a})/{n} = {h}",
        "n_adjusted": n
    })
    
    # Suma de términos
    sum_odd = sum(f_vals[i] for i in range(1, n, 2))
    sum_even = sum(f_vals[i] for i in range(2, n, 2))
    
    result = h * (f_vals[0] + 4 * sum_odd + 2 * sum_even + f_vals[n]) / 3
    
    steps.append({
        "step": "calculation",
        "f_a": f_vals[0],
        "f_b": f_vals[n],
        "sum_odd": sum_odd,
        "sum_even": sum_even,
        "result": result
    })
    
    return result, steps

# ============= REGLA DE SIMPSON 3/8 =============
def simpson_38_compuesto(func_str: str, a: float, b: float, n: int) -> Tuple[float, List[Dict]]:
    """Regla de Simpson 3/8 compuesta"""
    _validate_integration_params(a, b, n)
    
    # n debe ser múltiplo de 3 para Simpson 3/8
    if n % 3 != 0:
        n = ((n // 3) + 1) * 3
    
    func = _parse_function(func_str)
    h = (b - a) / n
    steps = []
    
    steps.append({
        "step": 1,
        "description": f"h = (b-a)/n = ({b}-{a})/{n} = {h}",
        "n_adjusted": n
    })
    
    # Evaluar función
    total = func(a) + func(b)
    
    for i in range(1, n):
        xi = a + i * h
        fxi = func(xi)
        if i % 3 == 0:
            total += 2 * fxi
        else:
            total += 3 * fxi
    
    result = 3 * h * total / 8
    
    steps.append({
        "step": "result",
        "description": "Aplicando fórmula de Simpson 3/8",
        "result": result
    })
    
    return result, steps

# ============= CUADRATURA DE GAUSS-LEGENDRE =============
def gauss_legendre(func_str: str, a: float, b: float, n: int) -> Tuple[float, List[Dict]]:
    """Cuadratura de Gauss-Legendre"""
    _validate_integration_params(a, b, n)
    
    if n > 10:
        n = 10  # Limitar para estabilidad
    
    func = _parse_function(func_str)
    steps = []
    
    # Nodos y pesos de Gauss-Legendre (precomputados para n común)
    gauss_data = {
        1: (np.array([0.0]), np.array([2.0])),
        2: (np.array([-0.5773502692, 0.5773502692]), 
            np.array([1.0, 1.0])),
        3: (np.array([-0.7745966692, 0.0, 0.7745966692]),
            np.array([0.5555555556, 0.8888888889, 0.5555555556])),
        4: (np.array([-0.8611363116, -0.3399810436, 0.3399810436, 0.8611363116]),
            np.array([0.3478548451, 0.6521451549, 0.6521451549, 0.3478548451])),
        5: (np.array([-0.9061798459, -0.5384693101, 0.0, 0.5384693101, 0.9061798459]),
            np.array([0.2369268851, 0.4786286705, 0.5688888889, 0.4786286705, 0.2369268851]))
    }
    
    if n not in gauss_data:
        # Para n > 5, usar numpy
        nodes, weights = np.polynomial.legendre.leggauss(n)
    else:
        nodes, weights = gauss_data[n]
    
    # Transformar del intervalo [-1,1] a [a,b]
    transformed_nodes = (b - a) / 2 * nodes + (a + b) / 2
    
    steps.append({
        "step": "nodes",
        "description": f"Nodos de Gauss-Legendre para n={n}",
        "nodes": transformed_nodes.tolist(),
        "weights": weights.tolist()
    })
    
    # Evaluar integral
    integral_sum = 0
    for i in range(n):
        xi = transformed_nodes[i]
        fxi = func(xi)
        contribution = weights[i] * fxi
        integral_sum += contribution
        
        if i < 5:  # Mostrar primeros 5
            steps.append({
                "step": f"eval_{i+1}",
                "x": xi,
                "fx": fxi,
                "weight": weights[i],
                "contribution": contribution
            })
    
    result = (b - a) / 2 * integral_sum
    
    steps.append({
        "step": "result",
        "description": "Integral = (b-a)/2 * Σ(wi * f(xi))",
        "result": result
    })
    
    return result, steps

# ============= FUNCIONES DE EXPLICACIÓN =============
def get_trapecio_explanation(func_str: str, a: float, b: float, n: int) -> Dict[str, Any]:
    return {
        "method": "Regla del Trapecio Compuesta",
        "description": "Aproxima el área bajo la curva usando trapecios",
        "formula": "∫f(x)dx ≈ h/2 * [f(x₀) + 2Σf(xᵢ) + f(xₙ)]",
        "error": f"Error = O(h²) = O({((b-a)/n)**2:.2e})",
        "pros": ["Simple", "Estable", "Converge para funciones continuas"],
        "cons": ["Precisión limitada", "Requiere muchos puntos para alta precisión"],
        "accuracy": "Segundo orden"
    }

def get_simpson13_explanation(func_str: str, a: float, b: float, n: int) -> Dict[str, Any]:
    return {
        "method": "Regla de Simpson 1/3 Compuesta",
        "description": "Aproxima usando parábolas (polinomios de grado 2)",
        "formula": "∫f(x)dx ≈ h/3 * [f(x₀) + 4Σf(x₂ᵢ₊₁) + 2Σf(x₂ᵢ) + f(xₙ)]",
        "error": f"Error = O(h⁴) = O({((b-a)/n)**4:.2e})",
        "pros": ["Mayor precisión que trapecio", "Exacta para polinomios de grado ≤ 3"],
        "cons": ["Requiere número par de intervalos"],
        "accuracy": "Cuarto orden"
    }

def get_simpson38_explanation(func_str: str, a: float, b: float, n: int) -> Dict[str, Any]:
    return {
        "method": "Regla de Simpson 3/8 Compuesta",
        "description": "Usa polinomios de grado 3 con 4 puntos",
        "formula": "∫f(x)dx ≈ 3h/8 * [f(x₀) + 3f(x₁) + 3f(x₂) + f(x₃)]",
        "error": f"Error = O(h⁴) = O({((b-a)/n)**4:.2e})",
        "pros": ["Alta precisión", "Útil cuando n no es par"],
        "cons": ["Requiere múltiplos de 3 intervalos"],
        "accuracy": "Cuarto orden"
    }

def get_gauss_explanation(func_str: str, a: float, b: float, n: int) -> Dict[str, Any]:
    return {
        "method": "Cuadratura de Gauss-Legendre",
        "description": "Usa puntos y pesos óptimos para máxima precisión",
        "formula": "∫f(x)dx ≈ (b-a)/2 * Σwᵢf(xᵢ)",
        "error": f"Error = O(h^{2*n}) para polinomios",
        "pros": ["Máxima precisión", "Pocos puntos necesarios", "Exacta para polinomios de grado ≤ 2n-1"],
        "cons": ["Puntos no equiespaciados", "Más compleja"],
        "accuracy": f"Orden {2*n}"
    }