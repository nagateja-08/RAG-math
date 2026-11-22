"""
Comprehensive Seed Data for Mathematical Knowledge Graph
Covers 5 core subjects:
1. Calculus
2. Algebra
3. Trigonometry
4. Probability
5. Statistics

Node Types:
- Concept
- Formula
- Theorem
- Topic
- Subtopic
- Example

Relationship Types:
- PREREQUISITE_OF
- RELATED_TO
- PART_OF
- USES_FORMULA
- PROVES
- EXPLAINS
"""

SEED_NODES = [
    # ---------------- CALCULUS: Topics & Subtopics ----------------
    {"id": "topic_calculus", "name": "Calculus", "type": "Topic", "subject": "Calculus", "description": "The mathematical study of continuous change."},
    {"id": "sub_diff_calc", "name": "Differential Calculus", "type": "Subtopic", "subject": "Calculus", "description": "Study of rates of change and slopes of curves."},
    {"id": "sub_int_calc", "name": "Integral Calculus", "type": "Subtopic", "subject": "Calculus", "description": "Study of accumulation of quantities and areas under curves."},

    # CALCULUS: Concepts
    {"id": "concept_functions", "name": "Functions", "type": "Concept", "subject": "Calculus", "difficulty": "Beginner", "description": "A relation between a set of inputs and allowable outputs with the property that each input is related to exactly one output."},
    {"id": "concept_limits", "name": "Limits", "type": "Concept", "subject": "Calculus", "difficulty": "Beginner", "description": "The value that a function approaches as the input approaches some specific value."},
    {"id": "concept_continuity", "name": "Continuity", "type": "Concept", "subject": "Calculus", "difficulty": "Intermediate", "description": "A function where small changes in the input result in small changes in the output without jumps or gaps."},
    {"id": "concept_differentiation", "name": "Differentiation", "type": "Concept", "subject": "Calculus", "difficulty": "Intermediate", "description": "The process of finding the instantaneous rate of change (derivative) of a function."},
    {"id": "concept_derivative_rules", "name": "Derivative Rules", "type": "Concept", "subject": "Calculus", "difficulty": "Intermediate", "description": "Systematic rules for differentiating functions including Power, Product, Quotient, and Chain rules."},
    {"id": "concept_integration", "name": "Integration", "type": "Concept", "subject": "Calculus", "difficulty": "Advanced", "description": "The process of calculating integrals, representing total accumulation, area under curves, or the reverse of differentiation."},
    {"id": "concept_integration_by_parts", "name": "Integration by Parts", "type": "Concept", "subject": "Calculus", "difficulty": "Advanced", "description": "A technique for integrating the product of two functions."},
    {"id": "concept_differential_equations", "name": "Differential Equations", "type": "Concept", "subject": "Calculus", "difficulty": "Advanced", "description": "Equations involving an unknown function and one or more of its derivatives."},
    {"id": "concept_taylor_series", "name": "Taylor Series", "type": "Concept", "subject": "Calculus", "difficulty": "Advanced", "description": "Representation of a function as an infinite sum of terms calculated from its derivatives at a single point."},

    # CALCULUS: Formulas
    {"id": "form_power_rule", "name": "Power Rule for Derivatives", "type": "Formula", "subject": "Calculus", "latex": "\\frac{d}{dx}[x^n] = n x^{n-1}", "description": "Derivative of a power function."},
    {"id": "form_product_rule", "name": "Product Rule", "type": "Formula", "subject": "Calculus", "latex": "\\frac{d}{dx}[u \\cdot v] = u'v + uv'", "description": "Derivative of the product of two differentiable functions."},
    {"id": "form_chain_rule", "name": "Chain Rule", "type": "Formula", "subject": "Calculus", "latex": "\\frac{d}{dx}[f(g(x))] = f'(g(x)) \\cdot g'(x)", "description": "Derivative of a composite function."},
    {"id": "form_integral_power", "name": "Power Rule for Integration", "type": "Formula", "subject": "Calculus", "latex": "\\int x^n dx = \\frac{x^{n+1}}{n+1} + C, \\quad (n \\neq -1)", "description": "Indefinite integral of a monomial."},
    {"id": "form_int_by_parts", "name": "Integration by Parts Formula", "type": "Formula", "subject": "Calculus", "latex": "\\int u \\, dv = uv - \\int v \\, du", "description": "Integration formula derived from the product rule."},

    # CALCULUS: Theorems
    {"id": "thm_ftc", "name": "Fundamental Theorem of Calculus", "type": "Theorem", "subject": "Calculus", "description": "Connects differentiation and integration: if f is continuous on [a, b] and F is an antiderivative, then \\int_a^b f(x)dx = F(b) - F(a)."},
    {"id": "thm_mvt", "name": "Mean Value Theorem", "type": "Theorem", "subject": "Calculus", "description": "If a function is continuous on [a, b] and differentiable on (a, b), there exists c in (a, b) where f'(c) = (f(b)-f(a))/(b-a)."},
    {"id": "thm_lhopital", "name": "L'Hopital's Rule", "type": "Theorem", "subject": "Calculus", "description": "Used to evaluate limits of indeterminate forms 0/0 or \\infty/\\infty using derivatives of numerator and denominator."},

    # ---------------- ALGEBRA: Topics & Concepts ----------------
    {"id": "topic_algebra", "name": "Algebra", "type": "Topic", "subject": "Algebra", "description": "The study of mathematical symbols and the rules for manipulating these symbols."},
    {"id": "concept_linear_equations", "name": "Linear Equations", "type": "Concept", "subject": "Algebra", "difficulty": "Beginner", "description": "An algebraic equation in which each term is either a constant or the product of a constant and a single variable."},
    {"id": "concept_quadratic_equations", "name": "Quadratic Equations", "type": "Concept", "subject": "Algebra", "difficulty": "Intermediate", "description": "A second-order polynomial equation of the form ax^2 + bx + c = 0."},
    {"id": "concept_polynomials", "name": "Polynomials", "type": "Concept", "subject": "Algebra", "difficulty": "Intermediate", "description": "Mathematical expressions involving a sum of powers in one or more variables multiplied by coefficients."},
    {"id": "concept_matrices", "name": "Matrices", "type": "Concept", "subject": "Algebra", "difficulty": "Intermediate", "description": "Rectangular arrays of numbers or expressions arranged in rows and columns."},
    {"id": "concept_determinants", "name": "Determinants", "type": "Concept", "subject": "Algebra", "difficulty": "Advanced", "description": "A scalar attribute of a square matrix that characterizes the invertibility and scaling factor of the linear transformation."},
    {"id": "concept_eigenvalues", "name": "Eigenvalues and Eigenvectors", "type": "Concept", "subject": "Algebra", "difficulty": "Advanced", "description": "Scalars and non-zero vectors that satisfy Av = \\lambda v for a square matrix A."},

    # ALGEBRA: Formulas & Theorems
    {"id": "form_quadratic_formula", "name": "Quadratic Formula", "type": "Formula", "subject": "Algebra", "latex": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}", "description": "Closed-form solution for quadratic equations ax^2 + bx + c = 0."},
    {"id": "form_determinant_2x2", "name": "2x2 Matrix Determinant", "type": "Formula", "subject": "Algebra", "latex": "\\det \\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix} = ad - bc", "description": "Formula for the determinant of a 2x2 matrix."},
    {"id": "thm_fundamental_algebra", "name": "Fundamental Theorem of Algebra", "type": "Theorem", "subject": "Algebra", "description": "Every non-zero single-variable polynomial with complex coefficients has at least one complex root."},

    # ---------------- TRIGONOMETRY ----------------
    {"id": "topic_trigonometry", "name": "Trigonometry", "type": "Topic", "subject": "Trigonometry", "description": "Branch of mathematics that studies relationships between side lengths and angles of triangles."},
    {"id": "concept_unit_circle", "name": "Unit Circle", "type": "Concept", "subject": "Trigonometry", "difficulty": "Beginner", "description": "A circle of unit radius centered at the origin used to define trigonometric functions for all real angles."},
    {"id": "concept_trig_functions", "name": "Trigonometric Functions", "type": "Concept", "subject": "Trigonometry", "difficulty": "Intermediate", "description": "Real functions (sine, cosine, tangent) which relate an angle of a right-angled triangle to ratios of two side lengths."},
    {"id": "concept_trig_identities", "name": "Trigonometric Identities", "type": "Concept", "subject": "Trigonometry", "difficulty": "Intermediate", "description": "Equalities that involve trigonometric functions and are true for every value of the occurring variables."},
    {"id": "concept_inverse_trig", "name": "Inverse Trigonometric Functions", "type": "Concept", "subject": "Trigonometry", "difficulty": "Advanced", "description": "The inverse functions of the trigonometric functions (arcsin, arccos, arctan)."},

    # TRIGONOMETRY: Formulas
    {"id": "form_pythagorean_identity", "name": "Pythagorean Trigonometric Identity", "type": "Formula", "subject": "Trigonometry", "latex": "\\sin^2(\\theta) + \\cos^2(\\theta) = 1", "description": "Fundamental trigonometric identity relating sine and cosine."},
    {"id": "form_double_angle_sine", "name": "Double Angle Sine Formula", "type": "Formula", "subject": "Trigonometry", "latex": "\\sin(2\\theta) = 2\\sin(\\theta)\\cos(\\theta)", "description": "Expresses sine of double angle in terms of single angle."},
    {"id": "form_law_of_cosines", "name": "Law of Cosines", "type": "Formula", "subject": "Trigonometry", "latex": "c^2 = a^2 + b^2 - 2ab\\cos(C)", "description": "Relates the lengths of the sides of a triangle to the cosine of one of its angles."},

    # ---------------- PROBABILITY ----------------
    {"id": "topic_probability", "name": "Probability", "type": "Topic", "subject": "Probability", "description": "Branch of mathematics concerning numerical descriptions of how likely an event is to occur."},
    {"id": "concept_sample_space", "name": "Sample Space and Events", "type": "Concept", "subject": "Probability", "difficulty": "Beginner", "description": "The set of all possible outcomes of a random experiment and its subsets."},
    {"id": "concept_conditional_probability", "name": "Conditional Probability", "type": "Concept", "subject": "Probability", "difficulty": "Intermediate", "description": "The measure of the probability of an event given that another event has occurred."},
    {"id": "concept_random_variables", "name": "Random Variables", "type": "Concept", "subject": "Probability", "difficulty": "Intermediate", "description": "Variables whose values depend on outcomes of a random phenomenon."},
    {"id": "concept_probability_distributions", "name": "Probability Distributions", "type": "Concept", "subject": "Probability", "difficulty": "Intermediate", "description": "Mathematical functions that provide the probabilities of occurrence of different possible outcomes in an experiment."},
    {"id": "concept_expected_value", "name": "Expected Value", "type": "Concept", "subject": "Probability", "difficulty": "Intermediate", "description": "A generalization of the weighted average; the theoretical mean of a random variable."},

    # PROBABILITY: Formulas & Theorems
    {"id": "form_conditional_prob", "name": "Conditional Probability Formula", "type": "Formula", "subject": "Probability", "latex": "P(A|B) = \\frac{P(A \\cap B)}{P(B)}", "description": "Definition of conditional probability when P(B) > 0."},
    {"id": "thm_bayes", "name": "Bayes' Theorem", "type": "Theorem", "subject": "Probability", "description": "Mathematical formula used for calculating conditional probabilities: P(A|B) = [P(B|A)P(A)] / P(B)."},
    {"id": "form_bayes_formula", "name": "Bayes' Formula", "type": "Formula", "subject": "Probability", "latex": "P(A|B) = \\frac{P(B|A)P(A)}{P(B)}", "description": "Mathematical formulation of Bayes Theorem."},

    # ---------------- STATISTICS ----------------
    {"id": "topic_statistics", "name": "Statistics", "type": "Topic", "subject": "Statistics", "description": "The discipline concerning the collection, organization, analysis, interpretation, and presentation of data."},
    {"id": "concept_mean_median_mode", "name": "Measures of Central Tendency", "type": "Concept", "subject": "Statistics", "difficulty": "Beginner", "description": "Summary measures that attempt to describe a whole set of data with a single value that represents the middle of its distribution."},
    {"id": "concept_variance_std", "name": "Variance and Standard Deviation", "type": "Concept", "subject": "Statistics", "difficulty": "Intermediate", "description": "Measures of the amount of variation or dispersion of a set of values from its mean."},
    {"id": "concept_z_score", "name": "Z-Score and Normal Distribution", "type": "Concept", "subject": "Statistics", "difficulty": "Intermediate", "description": "The number of standard deviations a data point lies above or below the mean in a normal distribution."},
    {"id": "concept_hypothesis_testing", "name": "Hypothesis Testing", "type": "Concept", "subject": "Statistics", "difficulty": "Advanced", "description": "An act in statistics whereby an analyst tests an assumption regarding a population parameter."},
    {"id": "concept_linear_regression", "name": "Linear Regression", "type": "Concept", "subject": "Statistics", "difficulty": "Advanced", "description": "A linear approach to modeling the relationship between a dependent scalar response and one or more explanatory variables."},

    # STATISTICS: Formulas & Theorems
    {"id": "form_sample_mean", "name": "Sample Mean Formula", "type": "Formula", "subject": "Statistics", "latex": "\\bar{x} = \\frac{1}{n}\\sum_{i=1}^{n} x_i", "description": "Arithmetic average of sample observations."},
    {"id": "form_std_dev", "name": "Standard Deviation Formula", "type": "Formula", "subject": "Statistics", "latex": "\\sigma = \\sqrt{\\frac{1}{N}\\sum_{i=1}^{N}(x_i - \\mu)^2}", "description": "Square root of the population variance."},
    {"id": "thm_clt", "name": "Central Limit Theorem", "type": "Theorem", "subject": "Statistics", "description": "States that the distribution of sample means approximates a normal distribution as sample size becomes large, regardless of population distribution shape."},

    # ---------------- EXAMPLES ----------------
    {"id": "example_integration_parts", "name": "Integration by Parts Example", "type": "Example", "subject": "Calculus", "description": "Evaluate \\int x e^x dx by choosing u = x and dv = e^x dx."},
    {"id": "example_derivative_chain", "name": "Chain Rule Example", "type": "Example", "subject": "Calculus", "description": "Find the derivative of f(x) = sin(x^2). Solution: 2x cos(x^2)."},
    {"id": "example_quadratic_solve", "name": "Quadratic Equation Example", "type": "Example", "subject": "Algebra", "description": "Solve x^2 - 5x + 6 = 0 using factoring or the quadratic formula. Roots: x = 2, 3."},
    {"id": "example_bayes_calc", "name": "Bayes Theorem Medical Test Example", "type": "Example", "subject": "Probability", "description": "Calculating posterior probability of disease given a positive test result."}
]

SEED_RELATIONSHIPS = [
    # Topic -> Subtopic & Concepts PART_OF
    {"source": "sub_diff_calc", "target": "topic_calculus", "type": "PART_OF"},
    {"source": "sub_int_calc", "target": "topic_calculus", "type": "PART_OF"},
    {"source": "concept_functions", "target": "sub_diff_calc", "type": "PART_OF"},
    {"source": "concept_limits", "target": "sub_diff_calc", "type": "PART_OF"},
    {"source": "concept_continuity", "target": "sub_diff_calc", "type": "PART_OF"},
    {"source": "concept_differentiation", "target": "sub_diff_calc", "type": "PART_OF"},
    {"source": "concept_integration", "target": "sub_int_calc", "type": "PART_OF"},
    {"source": "concept_linear_equations", "target": "topic_algebra", "type": "PART_OF"},
    {"source": "concept_quadratic_equations", "target": "topic_algebra", "type": "PART_OF"},
    {"source": "concept_matrices", "target": "topic_algebra", "type": "PART_OF"},
    {"source": "concept_trig_functions", "target": "topic_trigonometry", "type": "PART_OF"},
    {"source": "concept_conditional_probability", "target": "topic_probability", "type": "PART_OF"},
    {"source": "concept_hypothesis_testing", "target": "topic_statistics", "type": "PART_OF"},

    # PREREQUISITE_OF Relationships (Critical for Feature 2: Prerequisite-Based Learning)
    # Functions -> Limits -> Continuity -> Differentiation -> Integration
    {"source": "concept_functions", "target": "concept_limits", "type": "PREREQUISITE_OF"},
    {"source": "concept_limits", "target": "concept_continuity", "type": "PREREQUISITE_OF"},
    {"source": "concept_continuity", "target": "concept_differentiation", "type": "PREREQUISITE_OF"},
    {"source": "concept_functions", "target": "concept_differentiation", "type": "PREREQUISITE_OF"},
    {"source": "concept_differentiation", "target": "concept_derivative_rules", "type": "PREREQUISITE_OF"},
    {"source": "concept_differentiation", "target": "concept_integration", "type": "PREREQUISITE_OF"},
    {"source": "concept_limits", "target": "concept_integration", "type": "PREREQUISITE_OF"},
    {"source": "concept_integration", "target": "concept_integration_by_parts", "type": "PREREQUISITE_OF"},
    {"source": "concept_derivative_rules", "target": "concept_integration_by_parts", "type": "PREREQUISITE_OF"},
    {"source": "concept_differentiation", "target": "concept_differential_equations", "type": "PREREQUISITE_OF"},
    {"source": "concept_integration", "target": "concept_differential_equations", "type": "PREREQUISITE_OF"},
    {"source": "concept_differentiation", "target": "concept_taylor_series", "type": "PREREQUISITE_OF"},

    # Algebra Prerequisites
    {"source": "concept_linear_equations", "target": "concept_quadratic_equations", "type": "PREREQUISITE_OF"},
    {"source": "concept_polynomials", "target": "concept_quadratic_equations", "type": "PREREQUISITE_OF"},
    {"source": "concept_matrices", "target": "concept_determinants", "type": "PREREQUISITE_OF"},
    {"source": "concept_determinants", "target": "concept_eigenvalues", "type": "PREREQUISITE_OF"},
    {"source": "concept_quadratic_equations", "target": "concept_polynomials", "type": "RELATED_TO"},

    # Trigonometry Prerequisites
    {"source": "concept_unit_circle", "target": "concept_trig_functions", "type": "PREREQUISITE_OF"},
    {"source": "concept_trig_functions", "target": "concept_trig_identities", "type": "PREREQUISITE_OF"},
    {"source": "concept_trig_functions", "target": "concept_inverse_trig", "type": "PREREQUISITE_OF"},
    {"source": "concept_trig_functions", "target": "concept_differentiation", "type": "RELATED_TO"},

    # Probability Prerequisites
    {"source": "concept_sample_space", "target": "concept_conditional_probability", "type": "PREREQUISITE_OF"},
    {"source": "concept_conditional_probability", "target": "thm_bayes", "type": "PREREQUISITE_OF"},
    {"source": "concept_sample_space", "target": "concept_random_variables", "type": "PREREQUISITE_OF"},
    {"source": "concept_random_variables", "target": "concept_probability_distributions", "type": "PREREQUISITE_OF"},
    {"source": "concept_probability_distributions", "target": "concept_expected_value", "type": "PREREQUISITE_OF"},

    # Statistics Prerequisites
    {"source": "concept_mean_median_mode", "target": "concept_variance_std", "type": "PREREQUISITE_OF"},
    {"source": "concept_variance_std", "target": "concept_z_score", "type": "PREREQUISITE_OF"},
    {"source": "concept_probability_distributions", "target": "concept_hypothesis_testing", "type": "PREREQUISITE_OF"},
    {"source": "concept_z_score", "target": "concept_hypothesis_testing", "type": "PREREQUISITE_OF"},
    {"source": "concept_variance_std", "target": "concept_linear_regression", "type": "PREREQUISITE_OF"},

    # Cross-Discipline Relationships
    {"source": "concept_integration", "target": "concept_probability_distributions", "type": "PREREQUISITE_OF"},
    {"source": "concept_expected_value", "target": "concept_variance_std", "type": "RELATED_TO"},
    {"source": "concept_matrices", "target": "concept_linear_regression", "type": "RELATED_TO"},

    # USES_FORMULA Relationships
    {"source": "concept_differentiation", "target": "form_power_rule", "type": "USES_FORMULA"},
    {"source": "concept_derivative_rules", "target": "form_product_rule", "type": "USES_FORMULA"},
    {"source": "concept_derivative_rules", "target": "form_chain_rule", "type": "USES_FORMULA"},
    {"source": "concept_integration", "target": "form_integral_power", "type": "USES_FORMULA"},
    {"source": "concept_integration_by_parts", "target": "form_int_by_parts", "type": "USES_FORMULA"},
    {"source": "concept_quadratic_equations", "target": "form_quadratic_formula", "type": "USES_FORMULA"},
    {"source": "concept_determinants", "target": "form_determinant_2x2", "type": "USES_FORMULA"},
    {"source": "concept_trig_identities", "target": "form_pythagorean_identity", "type": "USES_FORMULA"},
    {"source": "concept_trig_identities", "target": "form_double_angle_sine", "type": "USES_FORMULA"},
    {"source": "concept_trig_functions", "target": "form_law_of_cosines", "type": "USES_FORMULA"},
    {"source": "concept_conditional_probability", "target": "form_conditional_prob", "type": "USES_FORMULA"},
    {"source": "thm_bayes", "target": "form_bayes_formula", "type": "USES_FORMULA"},
    {"source": "concept_mean_median_mode", "target": "form_sample_mean", "type": "USES_FORMULA"},
    {"source": "concept_variance_std", "target": "form_std_dev", "type": "USES_FORMULA"},

    # PROVES and EXPLAINS Relationships
    {"source": "thm_ftc", "target": "concept_integration", "type": "EXPLAINS"},
    {"source": "thm_ftc", "target": "concept_differentiation", "type": "PROVES"},
    {"source": "thm_mvt", "target": "concept_differentiation", "type": "EXPLAINS"},
    {"source": "thm_lhopital", "target": "concept_limits", "type": "EXPLAINS"},
    {"source": "thm_fundamental_algebra", "target": "concept_polynomials", "type": "EXPLAINS"},
    {"source": "thm_clt", "target": "concept_probability_distributions", "type": "PROVES"},

    # Examples EXPLAINS
    {"source": "example_integration_parts", "target": "concept_integration_by_parts", "type": "EXPLAINS"},
    {"source": "example_derivative_chain", "target": "concept_derivative_rules", "type": "EXPLAINS"},
    {"source": "example_quadratic_solve", "target": "concept_quadratic_equations", "type": "EXPLAINS"},
    {"source": "example_bayes_calc", "target": "thm_bayes", "type": "EXPLAINS"}
]
