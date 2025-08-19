from flask import Flask, request, jsonify, render_template
import json
import traceback
from metodos.interpolacion import *
from metodos.integracion import *
from metodos.derivacion import *

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# ============= API INTERPOLACIÓN =============
@app.route("/api/interpolate", methods=["POST"])
def api_interpolate():
    try:
        data = request.get_json(force=True)
        method = str(data.get("method", "")).lower()
        x = data.get("x", [])
        y = data.get("y", [])
        xq = data.get("xq", [])

        if method not in {"linear", "newton", "lagrange", "spline"}:
            return jsonify(error="Método inválido. Usa 'linear', 'newton', 'lagrange' o 'spline'."), 400
        
        if not isinstance(x, list) or not isinstance(y, list) or not isinstance(xq, list):
            return jsonify(error="x, y, xq deben ser listas."), 400

        try:
            x = [float(val) for val in x]
            y = [float(val) for val in y]
            xq = [float(val) for val in xq]
        except (ValueError, TypeError):
            return jsonify(error="Todos los valores deben ser números."), 400

        if method == "linear":
            result = linear_interpolate(x, y, xq)
            explanation = get_linear_explanation(x, y, xq)
        elif method == "newton":
            x_nodes, coef = newton_divided_diffs(x, y)
            result = eval_newton_poly(x_nodes, coef, xq)
            explanation = get_newton_explanation(x_nodes, y, coef)
        elif method == "lagrange":
            result = lagrange_interpolate(x, y, xq)
            explanation = get_lagrange_explanation(x, y)
        elif method == "spline":
            result = cubic_spline_interpolate(x, y, xq)
            explanation = get_spline_explanation(x, y)

        return jsonify({
            "success": True,
            "method": method,
            "input": {"x": x, "y": y, "xq": xq},
            "result": result,
            "explanation": explanation,
            "points_count": len(x)
        })

    except Exception as e:
        return jsonify({
            "error": f"Error en interpolación: {str(e)}",
            "traceback": traceback.format_exc() if app.debug else None
        }), 500


# ============= API INTEGRACIÓN =============
@app.route("/api/integrate", methods=["POST"])
def api_integrate():
    try:
        data = request.get_json(force=True)
        method = str(data.get("method", "")).lower()
        func_str = data.get("function", "")
        a = float(data.get("a", 0))
        b = float(data.get("b", 1))
        n = int(data.get("n", 10))

        if method not in {"trapecio", "simpson13", "simpson38", "gauss"}:
            return jsonify(error="Método inválido para integración."), 400

        if method == "trapecio":
            result, steps = trapecio_compuesto(func_str, a, b, n)
            explanation = get_trapecio_explanation(func_str, a, b, n)
        elif method == "simpson13":
            result, steps = simpson_13_compuesto(func_str, a, b, n)
            explanation = get_simpson13_explanation(func_str, a, b, n)
        elif method == "simpson38":
            result, steps = simpson_38_compuesto(func_str, a, b, n)
            explanation = get_simpson38_explanation(func_str, a, b, n)
        elif method == "gauss":
            result, steps = gauss_legendre(func_str, a, b, n)
            explanation = get_gauss_explanation(func_str, a, b, n)

        return jsonify({
            "success": True,
            "method": method,
            "input": {"function": func_str, "a": a, "b": b, "n": n},
            "result": result,
            "steps": steps,
            "explanation": explanation
        })

    except Exception as e:
        return jsonify({
            "error": f"Error en integración: {str(e)}",
            "traceback": traceback.format_exc() if app.debug else None
        }), 500


# ============= API DERIVACIÓN =============
@app.route("/api/derive", methods=["POST"])
def api_derive():
    try:
        data = request.get_json(force=True)
        method = str(data.get("method", "")).lower()
        func_str = data.get("function", "")
        x = float(data.get("x", 0))
        h = float(data.get("h", 0.001))
        order = int(data.get("order", 1))

        if method not in {"adelante", "atras", "centrada"}:
            return jsonify(error="Método inválido para derivación."), 400

        if method == "adelante":
            result, formula = diff_adelante(func_str, x, h, order)
            explanation = get_adelante_explanation(func_str, x, h, order)
        elif method == "atras":
            result, formula = diff_atras(func_str, x, h, order)
            explanation = get_atras_explanation(func_str, x, h, order)
        elif method == "centrada":
            result, formula = diff_centrada(func_str, x, h, order)
            explanation = get_centrada_explanation(func_str, x, h, order)

        return jsonify({
            "success": True,
            "method": method,
            "input": {"function": func_str, "x": x, "h": h, "order": order},
            "result": result,
            "formula": formula,
            "explanation": explanation
        })

    except Exception as e:
        return jsonify({
            "error": f"Error en derivación: {str(e)}",
            "traceback": traceback.format_exc() if app.debug else None
        }), 500


# ============= API UTILIDADES =============
@app.route("/api/validate", methods=["POST"])
def api_validate():
    try:
        data = request.get_json(force=True)
        return jsonify({"valid": True, "message": "Datos válidos"})
    except Exception as e:
        return jsonify({"valid": False, "message": str(e)})


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="Endpoint no encontrado"), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(error="Error interno del servidor"), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
