"""
SymPy Mathematical Engine for MathGPT
Provides tools for symbolic math: solving, calculus, matrices, stats.
"""

import sympy as sp
from sympy import (
    symbols, solve, diff, integrate, Matrix,
    latex, simplify, expand, factor, Symbol,
    oo, pi, E, sqrt, Rational, sympify,
    laplace_transform, inverse_laplace_transform,
    fourier_transform, dsolve, Function, Eq
)


def safe_sympify(expr_str: str):
    """Safely parse a mathematical expression string."""
    try:
        # Allow common math symbols
        local_dict = {
            "x": symbols("x"), "y": symbols("y"), "z": symbols("z"),
            "t": symbols("t"), "n": symbols("n"), "k": symbols("k"),
            "pi": pi, "E": E, "oo": oo, "sqrt": sqrt,
            "Rational": Rational,
        }
        return sympify(expr_str, locals=local_dict)
    except Exception as e:
        raise ValueError(f"Could not parse expression '{expr_str}': {e}")


def solve_equation(equation_str: str, variable: str = "x") -> dict:
    """
    Solve an equation or expression for a variable.
    Example: solve_equation("x**2 - 4", "x") → [2, -2]
    """
    try:
        var = symbols(variable)
        expr = safe_sympify(equation_str)
        solutions = solve(expr, var)
        return {
            "success": True,
            "variable": variable,
            "equation": equation_str,
            "solutions": [str(s) for s in solutions],
            "solutions_latex": [latex(s) for s in solutions],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def differentiate(expr_str: str, variable: str = "x", order: int = 1) -> dict:
    """
    Compute the derivative of an expression.
    Example: differentiate("x**3 + 2*x", "x") → 3*x**2 + 2
    """
    try:
        var = symbols(variable)
        expr = safe_sympify(expr_str)
        result = diff(expr, var, order)
        simplified = simplify(result)
        return {
            "success": True,
            "expression": expr_str,
            "variable": variable,
            "order": order,
            "derivative": str(simplified),
            "derivative_latex": latex(simplified),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def integrate_expression(expr_str: str, variable: str = "x",
                          lower: str = None, upper: str = None) -> dict:
    """
    Compute definite or indefinite integral.
    Example: integrate_expression("x**2", "x", "0", "1") → 1/3
    """
    try:
        var = symbols(variable)
        expr = safe_sympify(expr_str)

        if lower is not None and upper is not None:
            lo = safe_sympify(lower)
            hi = safe_sympify(upper)
            result = integrate(expr, (var, lo, hi))
            integral_type = "definite"
        else:
            result = integrate(expr, var)
            integral_type = "indefinite"

        simplified = simplify(result)
        return {
            "success": True,
            "expression": expr_str,
            "variable": variable,
            "type": integral_type,
            "result": str(simplified),
            "result_latex": latex(simplified),
            "bounds": f"[{lower}, {upper}]" if lower else None,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def matrix_operations(matrix_data: list[list], operation: str = "determinant") -> dict:
    """
    Perform matrix operations.
    Operations: determinant, inverse, eigenvalues, eigenvectors, rref
    """
    try:
        mat = Matrix(matrix_data)
        result = {}

        if operation == "determinant":
            det = mat.det()
            result = {"determinant": str(det), "determinant_latex": latex(det)}
        elif operation == "inverse":
            if mat.det() == 0:
                return {"success": False, "error": "Matrix is singular (determinant = 0)"}
            inv = mat.inv()
            result = {"inverse": str(inv), "inverse_latex": latex(inv)}
        elif operation == "eigenvalues":
            evals = mat.eigenvals()
            result = {"eigenvalues": {str(k): v for k, v in evals.items()}}
        elif operation == "eigenvectors":
            evecs = mat.eigenvects()
            result = {"eigenvectors": str(evecs)}
        elif operation == "rref":
            rref, pivots = mat.rref()
            result = {"rref": str(rref), "rref_latex": latex(rref), "pivots": list(pivots)}
        elif operation == "transpose":
            result = {"transpose": str(mat.T), "transpose_latex": latex(mat.T)}
        elif operation == "rank":
            result = {"rank": mat.rank()}
        else:
            return {"success": False, "error": f"Unknown operation: {operation}"}

        return {"success": True, "operation": operation, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def solve_ode(equation_str: str, function_name: str = "y", variable: str = "x") -> dict:
    """
    Solve an Ordinary Differential Equation.
    Example: equation_str = "y(x).diff(x) - y(x)" → y = C1*e^x
    """
    try:
        var = symbols(variable)
        func = Function(function_name)
        # Parse the ODE
        ode = safe_sympify(equation_str.replace(
            f"{function_name}({variable})", f"func({variable})")
        )
        eq = Eq(ode, 0)
        solution = dsolve(eq, func(var))
        return {
            "success": True,
            "ode": equation_str,
            "solution": str(solution),
            "solution_latex": latex(solution),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def compute_laplace(expr_str: str, variable: str = "t", transform_var: str = "s") -> dict:
    """Compute Laplace Transform of an expression."""
    try:
        t = symbols(variable, positive=True)
        s = symbols(transform_var)
        expr = safe_sympify(expr_str)
        result, _, _ = laplace_transform(expr, t, s)
        simplified = simplify(result)
        return {
            "success": True,
            "expression": expr_str,
            "laplace_transform": str(simplified),
            "laplace_transform_latex": latex(simplified),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def simplify_expression(expr_str: str) -> dict:
    """Simplify a mathematical expression."""
    try:
        expr = safe_sympify(expr_str)
        result = simplify(expr)
        return {
            "success": True,
            "original": expr_str,
            "simplified": str(result),
            "simplified_latex": latex(result),
            "expanded": str(expand(result)),
            "factored": str(factor(result)),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Tool registry for the LangChain agent
MATH_TOOLS = {
    "solve": solve_equation,
    "differentiate": differentiate,
    "integrate": integrate_expression,
    "matrix": matrix_operations,
    "ode": solve_ode,
    "laplace": compute_laplace,
    "simplify": simplify_expression,
}


def dispatch_math_tool(tool_name: str, **kwargs) -> dict:
    """Dispatch a math computation by tool name."""
    if tool_name not in MATH_TOOLS:
        return {"success": False, "error": f"Unknown math tool: {tool_name}. Available: {list(MATH_TOOLS.keys())}"}
    return MATH_TOOLS[tool_name](**kwargs)


async def process_sympy_blocks(code: str) -> str:
    """
    Safely execute a SymPy block and return its LaTeX representation.
    Supports single expressions or multi-line assignments.
    """
    import sympy as sp
    # Create a safe execution environment with sympy imported and variables
    local_dict = {
        "x": sp.Symbol("x"), "y": sp.Symbol("y"), "z": sp.Symbol("z"),
        "t": sp.Symbol("t"), "n": sp.Symbol("n"), "k": sp.Symbol("k"),
        "sympy": sp, "sp": sp,
    }
    # Add all sympy functions and symbols to the environment
    for attr in dir(sp):
        if not attr.startswith("_"):
            local_dict[attr] = getattr(sp, attr)
            
    # Try to evaluate as a single expression first
    try:
        expr = sp.sympify(code, locals=local_dict)
        return sp.latex(expr)
    except Exception:
        # If it fails, it might be a multiline block or statement. Exec it.
        try:
            # We want to capture the last statement's value or the 'result' variable
            # Split the code into lines
            lines = [line for line in code.strip().split("\n") if line.strip()]
            if not lines:
                return "\\text{Empty}"
            
            # If the last line is an expression, we can assign it to a special variable
            last_line = lines[-1].strip()
            # If it's not an assignment, try to capture it
            if "=" not in last_line and "import" not in last_line and "print" not in last_line:
                lines[-1] = f"_res_val = {last_line}"
            
            exec_code = "\n".join(lines)
            exec_globals = {}
            exec_locals = local_dict
            exec(exec_code, exec_globals, exec_locals)
            
            if "_res_val" in exec_locals:
                return sp.latex(exec_locals["_res_val"])
            elif "result" in exec_locals:
                return sp.latex(exec_locals["result"])
            else:
                # Return the last variable in the local dict that isn't built-in or sympy
                custom_vars = {k: v for k, v in exec_locals.items() if k not in local_dict and not k.startswith("_")}
                if custom_vars:
                    # Return the value of the last modified custom variable
                    last_var = list(custom_vars.keys())[-1]
                    return sp.latex(custom_vars[last_var])
                return "\\text{Executed successfully}"
        except Exception as e:
            return f"\\text{{Error evaluating SymPy: {str(e)}}}"
