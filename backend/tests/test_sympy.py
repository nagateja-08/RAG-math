import pytest
from backend.app.services.math_engine.sympy_service import verify_expression, auto_extract_and_verify

def test_differentiate_verification():
    res = verify_expression("x**3 + 2*x", operation="differentiate", variable="x", target_equals="3*x**2 + 2")
    assert res["success"] is True
    assert res["verified"] is True
    assert res["is_equal"] is True

def test_integrate_verification():
    res = verify_expression("3*x**2", operation="integrate", variable="x", target_equals="x**3")
    assert res["success"] is True
    assert res["verified"] is True
    assert res["is_equal"] is True

def test_solve_equation():
    res = verify_expression("x**2 - 5*x + 6 = 0", operation="solve", variable="x")
    assert res["success"] is True
    assert "2" in res["symbolic_result"]
    assert "3" in res["symbolic_result"]

def test_limit_verification():
    res = verify_expression("sin(x)/x", operation="limit", variable="x", limit_point="0")
    assert res["success"] is True
    assert res["symbolic_result"] == "1"

def test_equality_check_identity():
    res = verify_expression("sin(x)**2 + cos(x)**2", operation="equality_check", target_equals="1")
    assert res["success"] is True
    assert res["verified"] is True
    assert res["is_equal"] is True

def test_auto_extract_and_verify():
    text = "Find the derivative of x^2 + 4x with respect to x"
    res = auto_extract_and_verify(text)
    assert res is not None
    assert res["operation"] == "differentiate"
    assert "2*x + 4" in res["symbolic_result"]
