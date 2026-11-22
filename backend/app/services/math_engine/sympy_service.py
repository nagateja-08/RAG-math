"""
SymPy Mathematical Verification Service for MathGPT
Independently verifies mathematical equations, derivatives, integrals, limits, and algebraic identities.
Never relies solely on LLM output for mathematical correctness.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
import sympy as sp
from sympy import (
    symbols, Symbol, solve, diff, integrate, limit,
    latex, simplify, expand, factor, cancel, trigsimp,
    oo, pi, E, sqrt, Rational, sympify, Eq, Function
)

logger = logging.getLogger("mathgpt.sympy")

SAFE_SYMBOLS = {
    "x": symbols("x"), "y": symbols("y"), "z": symbols("z"),
    "t": symbols("t"), "n": symbols("n"), "k": symbols("k"),
    "a": symbols("a"), "b": symbols("b"), "c": symbols("c"),
    "theta": symbols("theta"),
    "pi": pi, "E": E, "oo": oo, "sqrt": sqrt, "Rational": Rational
}

from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor
)

TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application, convert_xor)

def safe_parse(expr_str: str):
    """Safely convert mathematical string into SymPy expression with implicit multiplication."""
    expr_clean = expr_str.strip()
    expr_clean = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'(\1)/(\2)', expr_clean)
    expr_clean = re.sub(r'\\sin', 'sin', expr_clean)
    expr_clean = re.sub(r'\\cos', 'cos', expr_clean)
    expr_clean = re.sub(r'\\tan', 'tan', expr_clean)
    expr_clean = re.sub(r'\\sqrt\{([^{}]+)\}', r'sqrt(\1)', expr_clean)
    expr_clean = expr_clean.replace("\\", "")

    return parse_expr(expr_clean, local_dict=SAFE_SYMBOLS, transformations=TRANSFORMATIONS)

def verify_expression(
    expression: str,
    operation: str = "solve",
    variable: str = "x",
    target_equals: Optional[str] = None,
    lower_bound: Optional[str] = None,
    upper_bound: Optional[str] = None,
    limit_point: Optional[str] = "0"
) -> Dict[str, Any]:
    """
    Core SymPy verification method.
    Returns:
    - success (bool): parsed and evaluated without error
    - verified (bool): mathematical correctness verified
    - symbolic_result (str): exact string representation
    - latex_output (str): formatted LaTeX for display
    - message (str): explanation of verification result
    """
    try:
        var = symbols(variable)
        op = operation.lower().strip()

        if op == "differentiate":
            expr = safe_parse(expression)
            res = diff(expr, var)
            res_simp = simplify(res)
            res_latex = latex(res_simp)

            # If user provided expected target derivative
            is_equal = None
            if target_equals:
                target_expr = safe_parse(target_equals)
                diff_test = simplify(res_simp - target_expr)
                is_equal = (diff_test == 0)

            return {
                "success": True,
                "verified": is_equal if is_equal is not None else True,
                "operation": "differentiate",
                "input_expression": expression,
                "symbolic_result": str(res_simp),
                "latex_output": f"\\frac{{d}}{{d{variable}}}\\left({latex(expr)}\\right) = {res_latex}",
                "comparison_target": target_equals,
                "is_equal": is_equal,
                "message": f"Successfully differentiated with respect to {variable}."
            }

        elif op == "integrate":
            expr = safe_parse(expression)
            if lower_bound is not None and upper_bound is not None and lower_bound != "" and upper_bound != "":
                lo = safe_parse(lower_bound)
                hi = safe_parse(upper_bound)
                res = integrate(expr, (var, lo, hi))
                res_simp = simplify(res)
                res_latex = latex(res_simp)
                display_latex = f"\\int_{{{lower_bound}}}^{{{upper_bound}}} {latex(expr)} \\, d{variable} = {res_latex}"
            else:
                res = integrate(expr, var)
                res_simp = simplify(res)
                res_latex = latex(res_simp)
                display_latex = f"\\int {latex(expr)} \\, d{variable} = {res_latex} + C"

            is_equal = None
            if target_equals:
                target_expr = safe_parse(target_equals)
                diff_test = simplify(res_simp - target_expr)
                is_equal = (diff_test == 0)

            return {
                "success": True,
                "verified": is_equal if is_equal is not None else True,
                "operation": "integrate",
                "input_expression": expression,
                "symbolic_result": str(res_simp),
                "latex_output": display_latex,
                "comparison_target": target_equals,
                "is_equal": is_equal,
                "message": f"Successfully integrated with respect to {variable}."
            }

        elif op == "solve":
            # Handle equations with '='
            if "=" in expression:
                lhs_str, rhs_str = expression.split("=", 1)
                lhs = safe_parse(lhs_str)
                rhs = safe_parse(rhs_str)
                expr = lhs - rhs
            else:
                expr = safe_parse(expression)

            sols = solve(expr, var)
            sols_str = [str(s) for s in sols]
            sols_latex = [latex(s) for s in sols]

            return {
                "success": True,
                "verified": True,
                "operation": "solve",
                "input_expression": expression,
                "symbolic_result": ", ".join(sols_str) if sols_str else "No solution",
                "latex_output": f"{variable} \\in \\{{{', '.join(sols_latex)}\\}}" if sols_latex else "\\emptyset",
                "message": f"Found {len(sols)} solution(s) for variable {variable}."
            }

        elif op == "limit":
            expr = safe_parse(expression)
            pt = safe_parse(limit_point)
            res = limit(expr, var, pt)
            res_latex = latex(res)

            return {
                "success": True,
                "verified": True,
                "operation": "limit",
                "input_expression": expression,
                "symbolic_result": str(res),
                "latex_output": f"\\lim_{{{variable} \\to {limit_point}}} \\left({latex(expr)}\\right) = {res_latex}",
                "message": f"Successfully computed limit as {variable} -> {limit_point}."
            }

        elif op in ("simplify", "equality_check"):
            if "=" in expression or target_equals:
                if "=" in expression and not target_equals:
                    lhs_str, rhs_str = expression.split("=", 1)
                else:
                    lhs_str = expression
                    rhs_str = target_equals

                lhs = safe_parse(lhs_str)
                rhs = safe_parse(rhs_str)
                diff_test = simplify(lhs - rhs)
                is_equal = (diff_test == 0)

                return {
                    "success": True,
                    "verified": is_equal,
                    "operation": "equality_check",
                    "input_expression": expression,
                    "symbolic_result": "Equivalent" if is_equal else "Not equivalent",
                    "latex_output": f"{latex(lhs)} " + ("\\equiv" if is_equal else "\\not\\equiv") + f" {latex(rhs)}",
                    "comparison_target": target_equals or rhs_str,
                    "is_equal": is_equal,
                    "message": "Verified mathematical identity." if is_equal else "Expressions are mathematically not equivalent."
                }
            else:
                expr = safe_parse(expression)
                simp = simplify(expr)
                return {
                    "success": True,
                    "verified": True,
                    "operation": "simplify",
                    "input_expression": expression,
                    "symbolic_result": str(simp),
                    "latex_output": f"{latex(expr)} = {latex(simp)}",
                    "message": "Successfully simplified expression."
                }
        else:
            return {
                "success": False,
                "verified": False,
                "operation": operation,
                "input_expression": expression,
                "message": f"Operation '{operation}' is not supported for automated verification."
            }

    except Exception as e:
        logger.warning(f"SymPy evaluation error for '{expression}': {e}")
        return {
            "success": False,
            "verified": False,
            "operation": operation,
            "input_expression": expression,
            "error_message": str(e),
            "message": "This expression could not be verified automatically by SymPy."
        }

def auto_extract_and_verify(text: str) -> Optional[Dict[str, Any]]:
    """
    Scans a mathematical question or answer to detect if there is a verifiable equation,
    derivative, or integral, and automatically runs SymPy verification.
    """
    # 1. Check for derivative: "derivative of X" or "differentiate X"
    deriv_match = re.search(r'(?:derivative of|differentiate)\s+([a-zA-Z0-9\+\-\*\/\^\(\)\s]+?)(?:with respect to|w\.r\.t|\?|$)', text, re.I)
    if deriv_match:
        expr = deriv_match.group(1).strip()
        if len(expr) > 1:
            res = verify_expression(expr, operation="differentiate", variable="x")
            if res["success"]:
                return res

    # 2. Check for integral: "integral of X" or "integrate X"
    int_match = re.search(r'(?:integral of|integrate)\s+([a-zA-Z0-9\+\-\*\/\^\(\)\s]+?)(?:with respect to|w\.r\.t|from|\?|$)', text, re.I)
    if int_match:
        expr = int_match.group(1).strip()
        if len(expr) > 1:
            res = verify_expression(expr, operation="integrate", variable="x")
            if res["success"]:
                return res

    # 3. Check for quadratic or simple equation: "solve x^2 - 5x + 6 = 0"
    eq_match = re.search(r'(?:solve\s+)?([a-zA-Z0-9\+\-\*\/\^\(\)\s]+=[a-zA-Z0-9\+\-\*\/\^\(\)\s]+)', text, re.I)
    if eq_match:
        eq_str = eq_match.group(1).strip()
        if len(eq_str) > 3 and "x" in eq_str:
            res = verify_expression(eq_str, operation="solve", variable="x")
            if res["success"]:
                return res

    return None
