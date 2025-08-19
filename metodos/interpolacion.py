import numpy as np
from typing import List, Tuple, Dict, Any

def _validate_input(x: List[float], y: List[float]) -> None:
    """Validación robusta de entrada para todos los métodos"""
    if not x or not y:
        raise ValueError("Las listas x e y no pueden estar vacías")
    
    if len(x) != len(y):
        raise ValueError(f"x y y deben tener la misma longitud. x: {len(x)}, y: {len(y)}")
    
    if len(x) < 2:
        raise ValueError("Se requieren al menos 2 puntos para interpolación")
    
    if len(set(x)) != len(x):
        raise ValueError("Los valores de x deben ser únicos (no duplicados)")
    
    # Verificar que sean números válidos
    for i, val in enumerate(x):
        if not isinstance(val, (int, float)) or np.isnan(val) or np.isinf(val):
            raise ValueError(f"x[{i}] = {val} no es un número válido")
    
    for i, val in enumerate(y):
        if not isinstance(val, (int, float)) or np.isnan(val) or np.isinf(val):
            raise ValueError(f"y[{i}] = {val} no es un número válido")

def _sort_points(x: List[float], y: List[float]) -> Tuple[List[float], List[float]]:
    """Ordena los puntos por x creciente"""
    paired = list(zip(x, y))
    paired.sort(key=lambda point: point[0])
    return [p[0] for p in paired], [p[1] for p in paired]

# ============= INTERPOLACIÓN LINEAL =============
def linear_interpolate(x: List[float], y: List[float], xq: List[float]) -> List[float]:
    """Interpolación lineal por tramos robusta"""
    _validate_input(x, y)
    x_sorted, y_sorted = _sort_points(x, y)
    
    if not xq:
        raise ValueError("xq no puede estar vacío")
    
    result = []
    for xi in xq:
        if xi < x_sorted[0] or xi > x_sorted[-1]:
            # Extrapolación lineal usando los extremos
            if xi < x_sorted[0]:
                # Extrapolación usando los dos primeros puntos
                slope = (y_sorted[1] - y_sorted[0]) / (x_sorted[1] - x_sorted[0])
                yi = y_sorted[0] + slope * (xi - x_sorted[0])
            else:
                # Extrapolación usando los dos últimos puntos
                slope = (y_sorted[-1] - y_sorted[-2]) / (x_sorted[-1] - x_sorted[-2])
                yi = y_sorted[-1] + slope * (xi - x_sorted[-1])
        else:
            # Interpolación
            for i in range(len(x_sorted) - 1):
                if x_sorted[i] <= xi <= x_sorted[i + 1]:
                    t = (xi - x_sorted[i]) / (x_sorted[i + 1] - x_sorted[i])
                    yi = (1 - t) * y_sorted[i] + t * y_sorted[i + 1]
                    break
        
        result.append(yi)
    
    return result

# ============= POLINOMIO DE NEWTON =============
def newton_divided_diffs(x: List[float], y: List[float]) -> Tuple[List[float], List[float]]:
    """Calcula diferencias divididas para el polinomio de Newton"""
    _validate_input(x, y)
    x_sorted, y_sorted = _sort_points(x, y)
    
    n = len(x_sorted)
    # Tabla de diferencias divididas
    F = [[0.0 for _ in range(n)] for _ in range(n)]
    
    # Primera columna: valores de y
    for i in range(n):
        F[i][0] = y_sorted[i]
    
    # Calcular diferencias divididas
    for j in range(1, n):
        for i in range(n - j):
            denominator = x_sorted[i + j] - x_sorted[i]
            if abs(denominator) < 1e-15:
                raise ValueError(f"División por cero en diferencias divididas: x[{i+j}] ≈ x[{i}]")
            F[i][j] = (F[i + 1][j - 1] - F[i][j - 1]) / denominator
    
    # Coeficientes del polinomio (primera fila de la tabla)
    coefficients = [F[0][j] for j in range(n)]
    
    return x_sorted, coefficients

def eval_newton_poly(x_nodes: List[float], coefficients: List[float], xq: List[float]) -> List[float]:
    """Evalúa el polinomio de Newton en los puntos xq"""
    if len(x_nodes) != len(coefficients):
        raise ValueError("x_nodes y coefficients deben tener la misma longitud")
    
    result = []
    n = len(coefficients)
    
    for xi in xq:
        # Esquema de Horner modificado para Newton
        value = coefficients[n - 1]
        for i in range(n - 2, -1, -1):
            value = value * (xi - x_nodes[i]) + coefficients[i]
        result.append(value)
    
    return result

# ============= INTERPOLACIÓN DE LAGRANGE =============
def lagrange_interpolate(x: List[float], y: List[float], xq: List[float]) -> List[float]:
    """Interpolación usando polinomios de Lagrange"""
    _validate_input(x, y)
    
    result = []
    n = len(x)
    
    for xi in xq:
        total = 0.0
        
        for i in range(n):
            # Calcular Li(xi)
            li = 1.0
            for j in range(n):
                if i != j:
                    denominator = x[i] - x[j]
                    if abs(denominator) < 1e-15:
                        raise ValueError(f"División por cero en Lagrange: x[{i}] ≈ x[{j}]")
                    li *= (xi - x[j]) / denominator
            
            total += y[i] * li
        
        result.append(total)
    
    return result

# ============= SPLINES CÚBICOS =============
def cubic_spline_interpolate(x: List[float], y: List[float], xq: List[float]) -> List[float]:
    """Interpolación con splines cúbicos naturales"""
    _validate_input(x, y)
    x_sorted, y_sorted = _sort_points(x, y)
    
    n = len(x_sorted)
    
    if n < 3:
        # Para menos de 3 puntos, usar interpolación lineal
        return linear_interpolate(x_sorted, y_sorted, xq)
    
    # Calcular espaciamientos
    h = [x_sorted[i + 1] - x_sorted[i] for i in range(n - 1)]
    
    # Sistema tridiagonal para encontrar segundas derivadas
    A = np.zeros((n - 2, n - 2))
    b = np.zeros(n - 2)
    
    for i in range(n - 2):
        if i > 0:
            A[i, i - 1] = h[i]
        A[i, i] = 2 * (h[i] + h[i + 1])
        if i < n - 3:
            A[i, i + 1] = h[i + 1]
        
        b[i] = 6 * ((y_sorted[i + 2] - y_sorted[i + 1]) / h[i + 1] - 
                   (y_sorted[i + 1] - y_sorted[i]) / h[i])
    
    # Resolver sistema (splines naturales: S''(x0) = S''(xn) = 0)
    if n > 2:
        second_derivs_inner = np.linalg.solve(A, b)
        second_derivs = np.zeros(n)
        second_derivs[1:-1] = second_derivs_inner
    else:
        second_derivs = np.zeros(n)
    
    # Evaluar splines
    result = []
    for xi in xq:
        # Encontrar intervalo
        if xi <= x_sorted[0]:
            # Extrapolación lineal
            slope = (y_sorted[1] - y_sorted[0]) / h[0]
            yi = y_sorted[0] + slope * (xi - x_sorted[0])
        elif xi >= x_sorted[-1]:
            # Extrapolación lineal
            slope = (y_sorted[-1] - y_sorted[-2]) / h[-1]
            yi = y_sorted[-1] + slope * (xi - x_sorted[-1])
        else:
            # Interpolación con spline
            for i in range(n - 1):
                if x_sorted[i] <= xi <= x_sorted[i + 1]:
                    dx = xi - x_sorted[i]
                    
                    yi = (y_sorted[i] + 
                          dx * ((y_sorted[i + 1] - y_sorted[i]) / h[i] - 
                               h[i] * (2 * second_derivs[i] + second_derivs[i + 1]) / 6) +
                          dx**2 * second_derivs[i] / 2 +
                          dx**3 * (second_derivs[i + 1] - second_derivs[i]) / (6 * h[i]))
                    break
        
        result.append(yi)
    
    return result

# ============= FUNCIONES DE EXPLICACIÓN =============
def get_linear_explanation(x: List[float], y: List[float], xq: List[float]) -> Dict[str, Any]:
    return {
        "method": "Interpolación Lineal por Tramos",
        "description": "Conecta puntos consecutivos con líneas rectas",
        "formula": "y = y₁ + (y₂-y₁)/(x₂-x₁) * (x-x₁)",
        "pros": ["Simple y rápida", "Siempre estable", "Fácil de implementar"],
        "cons": ["No suave en los nodos", "Precisión limitada"],
        "complexity": "O(log n) por evaluación"
    }

def get_newton_explanation(x: List[float], y: List[float], coefficients: List[float]) -> Dict[str, Any]:
    return {
        "method": "Polinomio de Newton con Diferencias Divididas",
        "description": "Construye un polinomio único que pasa por todos los puntos",
        "formula": "P(x) = f[x₀] + f[x₀,x₁](x-x₀) + f[x₀,x₁,x₂](x-x₀)(x-x₁) + ...",
        "coefficients": coefficients[:5],  # Mostrar solo los primeros 5
        "pros": ["Polinomio único", "Fácil agregar puntos", "Numéricamente estable"],
        "cons": ["Oscilación de Runge con muchos puntos", "Grado alto"],
        "degree": len(coefficients) - 1
    }

def get_lagrange_explanation(x: List[float], y: List[float]) -> Dict[str, Any]:
    return {
        "method": "Interpolación de Lagrange",
        "description": "Suma ponderada de polinomios de Lagrange",
        "formula": "P(x) = Σ yᵢ * Lᵢ(x), donde Lᵢ(x) = Π(x-xⱼ)/(xᵢ-xⱼ) para j≠i",
        "pros": ["Conceptualmente simple", "Fácil de programar"],
        "cons": ["Computacionalmente costoso", "Numéricamente inestable"],
        "complexity": "O(n²) por evaluación"
    }

def get_spline_explanation(x: List[float], y: List[float]) -> Dict[str, Any]:
    return {
        "method": "Splines Cúbicos Naturales",
        "description": "Polinomios cúbicos por tramos con continuidad C²",
        "formula": "Sᵢ(x) = aᵢ + bᵢ(x-xᵢ) + cᵢ(x-xᵢ)² + dᵢ(x-xᵢ)³",
        "pros": ["Suave (C²)", "No oscila", "Interpolación óptima"],
        "cons": ["Más complejo", "Requiere resolver sistema"],
        "properties": ["Continuidad", "Primera derivada continua", "Segunda derivada continua"]
    }