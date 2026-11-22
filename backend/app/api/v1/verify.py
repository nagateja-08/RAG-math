from fastapi import APIRouter, HTTPException
from ...models.schemas import VerifyRequest, VerifyResponse
from ...services.math_engine.sympy_service import verify_expression

router = APIRouter()

@router.post("/verify", response_model=VerifyResponse)
def verify_math_expression(request: VerifyRequest):
    """
    Independently verify supported mathematical expressions, equations,
    derivatives, integrals, limits, and equivalences using SymPy (Feature 4).
    """
    if not request.expression or not request.expression.strip():
        raise HTTPException(status_code=400, detail="Mathematical expression cannot be empty.")

    res = verify_expression(
        expression=request.expression,
        operation=request.operation,
        variable=request.variable or "x",
        target_equals=request.target_equals,
        lower_bound=request.lower_bound,
        upper_bound=request.upper_bound,
        limit_point=request.limit_point or "0"
    )

    return VerifyResponse(
        success=res["success"],
        verified=res.get("verified", False),
        operation=res["operation"],
        input_expression=res["input_expression"],
        symbolic_result=res.get("symbolic_result"),
        latex_output=res.get("latex_output"),
        comparison_target=res.get("comparison_target"),
        is_equal=res.get("is_equal"),
        message=res["message"]
    )
