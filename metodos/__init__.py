# metodos/__init__.py
"""
Módulo de Métodos Numéricos
============================

Este módulo implementa métodos numéricos robustos para:
- Interpolación (lineal, Newton, Lagrange, splines)
- Integración numérica (trapecio, Simpson, Gauss-Legendre)
- Derivación numérica (diferencias finitas)

Todos los métodos incluyen:
- Validación exhaustiva de entrada
- Manejo robusto de errores
- Explicaciones matemáticas detalladas
- Análisis de precisión y error
"""

# Importar métodos de interpolación
from .interpolacion import (
    linear_interpolate,
    newton_divided_diffs,
    eval_newton_poly,
    lagrange_interpolate,
    cubic_spline_interpolate,
    get_linear_explanation,
    get_newton_explanation,
    get_lagrange_explanation,
    get_spline_explanation
)

# Importar métodos de integración
from .integracion import (
    trapecio_compuesto,
    simpson_13_compuesto,
    simpson_38_compuesto,
    gauss_legendre,
    get_trapecio_explanation,
    get_simpson13_explanation,
    get_simpson38_explanation,
    get_gauss_explanation
)

# Importar métodos de derivación
from .derivacion import (
    diff_adelante,
    diff_atras,
    diff_centrada,
    compare_methods,
    estimate_error,
    get_adelante_explanation,
    get_atras_explanation,
    get_centrada_explanation
)

# Definir qué se exporta cuando se hace "from metodos import *"
__all__ = [
    # Interpolación
    'linear_interpolate',
    'newton_divided_diffs', 
    'eval_newton_poly',
    'lagrange_interpolate',
    'cubic_spline_interpolate',
    'get_linear_explanation',
    'get_newton_explanation',
    'get_lagrange_explanation',
    'get_spline_explanation',
    
    # Integración
    'trapecio_compuesto',
    'simpson_13_compuesto',
    'simpson_38_compuesto',
    'gauss_legendre',
    'get_trapecio_explanation',
    'get_simpson13_explanation',
    'get_simpson38_explanation',
    'get_gauss_explanation',
    
    # Derivación
    'diff_adelante',
    'diff_atras',
    'diff_centrada',
    'compare_methods',
    'estimate_error',
    'get_adelante_explanation',
    'get_atras_explanation',
    'get_centrada_explanation'
]

# Información del módulo
__version__ = "1.0.0"
__author__ = "Equipo Métodos Numéricos"
__description__ = "Herramientas robustas para métodos numéricos"