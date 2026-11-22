"""
Diagnostic Assessment Service for Prerequisite-Based Learning (Feature 2)
Generates targeted diagnostic questions for concepts and their prerequisites to test student understanding.
"""

from typing import List, Dict, Any, Optional
from ..graph.graph_service import get_graph_service
from ...models.schemas import AssessmentQuestion, AssessmentQuizResponse, QuizOption

ASSESSMENT_BANK = {
    "Limits": [
        {
            "id": 101,
            "concept": "Limits",
            "question": "What is the value of the limit \\lim_{x \\to 0} \\frac{\\sin(x)}{x}?",
            "latex_formula": "\\lim_{x \\to 0} \\frac{\\sin(x)}{x}",
            "options": [
                {"id": "A", "text": "0"},
                {"id": "B", "text": "1"},
                {"id": "C", "text": "Undefined"},
                {"id": "D", "text": "\\infty"}
            ],
            "correct_option": "B",
            "explanation": "By L'Hopital's Rule or geometric proof, the fundamental trigonometric limit as x approaches 0 is 1."
        },
        {
            "id": 102,
            "concept": "Limits",
            "question": "Evaluate \\lim_{x \\to 2} \\frac{x^2 - 4}{x - 2}.",
            "latex_formula": "\\lim_{x \\to 2} \\frac{x^2 - 4}{x - 2}",
            "options": [
                {"id": "A", "text": "2"},
                {"id": "B", "text": "4"},
                {"id": "C", "text": "0"},
                {"id": "D", "text": "Does not exist"}
            ],
            "correct_option": "B",
            "explanation": "Factoring the numerator: (x-2)(x+2)/(x-2) = x+2. As x -> 2, the limit is 2 + 2 = 4."
        }
    ],
    "Functions": [
        {
            "id": 201,
            "concept": "Functions",
            "question": "Which of the following defines a function f: X -> Y?",
            "latex_formula": "f: X \\to Y",
            "options": [
                {"id": "A", "text": "Every input x in X is assigned to exactly one output y in Y"},
                {"id": "B", "text": "An input x can map to multiple outputs y"},
                {"id": "C", "text": "Outputs must always be distinct from inputs"},
                {"id": "D", "text": "The domain must equal the codomain"}
            ],
            "correct_option": "A",
            "explanation": "By definition, a function associates each element of a domain with uniquely one element in the codomain."
        }
    ],
    "Continuity": [
        {
            "id": 301,
            "concept": "Continuity",
            "question": "A function f(x) is continuous at x = a if and only if:",
            "latex_formula": "\\lim_{x \\to a} f(x) = f(a)",
            "options": [
                {"id": "A", "text": "f(a) is defined and \\lim_{x \\to a} f(x) = f(a)"},
                {"id": "B", "text": "f'(a) exists"},
                {"id": "C", "text": "f(x) is positive everywhere"},
                {"id": "D", "text": "f(x) has no horizontal asymptotes"}
            ],
            "correct_option": "A",
            "explanation": "Continuity requires that the two-sided limit exists, the function value exists, and they are equal."
        }
    ],
    "Differentiation": [
        {
            "id": 401,
            "concept": "Differentiation",
            "question": "What is the derivative of f(x) = x^3 - 4x with respect to x?",
            "latex_formula": "\\frac{d}{dx}[x^3 - 4x]",
            "options": [
                {"id": "A", "text": "3x^2 - 4"},
                {"id": "B", "text": "x^2 - 4"},
                {"id": "C", "text": "3x^2 - 4x"},
                {"id": "D", "text": "6x"}
            ],
            "correct_option": "A",
            "explanation": "Applying the Power Rule: d/dx(x^3) = 3x^2 and d/dx(-4x) = -4."
        },
        {
            "id": 402,
            "concept": "Differentiation",
            "question": "According to the Product Rule, what is \\frac{d}{dx}[u \\cdot v]?",
            "latex_formula": "\\frac{d}{dx}[u \\cdot v]",
            "options": [
                {"id": "A", "text": "u'v'"},
                {"id": "B", "text": "u'v + uv'"},
                {"id": "C", "text": "u' + v'"},
                {"id": "D", "text": "u v' - v u'"}
            ],
            "correct_option": "B",
            "explanation": "The derivative of a product is the derivative of the first times the second, plus the first times derivative of the second."
        }
    ],
    "Linear Equations": [
        {
            "id": 501,
            "concept": "Linear Equations",
            "question": "Solve for x: 3x - 9 = 0",
            "latex_formula": "3x - 9 = 0",
            "options": [
                {"id": "A", "text": "x = 3"},
                {"id": "B", "text": "x = -3"},
                {"id": "C", "text": "x = 9"},
                {"id": "D", "text": "x = 0"}
            ],
            "correct_option": "A",
            "explanation": "Adding 9 to both sides gives 3x = 9, dividing by 3 yields x = 3."
        }
    ],
    "Quadratic Equations": [
        {
            "id": 601,
            "concept": "Quadratic Equations",
            "question": "What are the solutions to x^2 - 5x + 6 = 0?",
            "latex_formula": "x^2 - 5x + 6 = 0",
            "options": [
                {"id": "A", "text": "x = 2 and x = 3"},
                {"id": "B", "text": "x = -2 and x = -3"},
                {"id": "C", "text": "x = 1 and x = 6"},
                {"id": "D", "text": "x = -1 and x = -6"}
            ],
            "correct_option": "A",
            "explanation": "Factoring: (x - 2)(x - 3) = 0 gives roots x = 2, 3."
        }
    ],
    "Sample Space and Events": [
        {
            "id": 701,
            "concept": "Sample Space and Events",
            "question": "What is the sample space S when rolling a standard fair six-sided die?",
            "latex_formula": "S = \\{1, 2, 3, 4, 5, 6\\}",
            "options": [
                {"id": "A", "text": "{1, 2, 3, 4, 5, 6}"},
                {"id": "B", "text": "{0, 1, 2, 3, 4, 5}"},
                {"id": "C", "text": "{2, 4, 6}"},
                {"id": "D", "text": "[1, 6] continuous"}
            ],
            "correct_option": "A",
            "explanation": "The set of all possible discrete outcomes when rolling a six-sided die is {1, 2, 3, 4, 5, 6}."
        }
    ]
}

def get_assessment_for_concept(concept_name: str) -> AssessmentQuizResponse:
    """
    Constructs a diagnostic quiz tailored to a target concept and its prerequisites.
    For example, if the student asks for Integration, it returns questions testing
    Limits, Functions, and Differentiation!
    """
    graph_service = get_graph_service()
    prereq_info = graph_service.get_prerequisites_chain(concept_name)
    prereqs = prereq_info["direct_prerequisites"]

    # Gather questions from target concept + prerequisites
    selected_questions: List[AssessmentQuestion] = []
    concepts_to_query = list(prereqs) + [concept_name]

    for c in concepts_to_query:
        # Check assessment bank
        for bank_key, q_list in ASSESSMENT_BANK.items():
            if bank_key.lower() == c.lower() or bank_key.lower() in c.lower() or c.lower() in bank_key.lower():
                for q in q_list:
                    selected_questions.append(
                        AssessmentQuestion(
                            id=q["id"],
                            concept=q["concept"],
                            question=q["question"],
                            latex_formula=q.get("latex_formula"),
                            options=[QuizOption(**opt) for opt in q["options"]],
                            explanation=q["explanation"]
                        )
                    )

    # If no specific questions found, provide standard foundational diagnostic questions
    if not selected_questions:
        for bank_key in ["Differentiation", "Limits", "Linear Equations"]:
            for q in ASSESSMENT_BANK[bank_key]:
                selected_questions.append(
                    AssessmentQuestion(
                        id=q["id"],
                        concept=q["concept"],
                        question=q["question"],
                        latex_formula=q.get("latex_formula"),
                        options=[QuizOption(**opt) for opt in q["options"]],
                        explanation=q["explanation"]
                    )
                )

    return AssessmentQuizResponse(
        target_concept=concept_name,
        prerequisite_concepts=prereqs,
        questions=selected_questions[:5]  # Keep quiz focused to 3-5 questions
    )

def evaluate_assessment(target_concept: str, answers: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Score submitted student answers and identify weak prerequisite topics.
    """
    total = len(answers)
    if total == 0:
        return {
            "score_percentage": 0.0,
            "total_questions": 0,
            "correct_count": 0,
            "passed": False,
            "weak_prerequisites": [],
            "recommended_topics": [target_concept],
            "detailed_feedback": []
        }

    correct_count = 0
    weak_prereqs = set()
    feedback = []

    # Map question id to correct option & explanation
    q_map = {}
    for c_list in ASSESSMENT_BANK.values():
        for q in c_list:
            q_map[q["id"]] = q

    for ans in answers:
        qid = ans.get("question_id")
        selected = ans.get("selected_option", "").strip().upper()
        q_info = q_map.get(qid)

        if q_info:
            is_correct = (selected == q_info["correct_option"])
            if is_correct:
                correct_count += 1
            else:
                weak_prereqs.add(q_info["concept"])

            feedback.append({
                "question_id": qid,
                "concept": q_info["concept"],
                "question": q_info["question"],
                "user_selected": selected,
                "correct_option": q_info["correct_option"],
                "is_correct": is_correct,
                "explanation": q_info["explanation"]
            })

    score_pct = round((correct_count / total) * 100.0, 1)
    passed = (score_pct >= 70.0)

    # Recommendations
    recommended = list(weak_prereqs)
    if not passed:
        recommended.append(target_concept)

    return {
        "score_percentage": score_pct,
        "total_questions": total,
        "correct_count": correct_count,
        "passed": passed,
        "weak_prerequisites": list(weak_prereqs),
        "recommended_topics": recommended,
        "detailed_feedback": feedback
    }
