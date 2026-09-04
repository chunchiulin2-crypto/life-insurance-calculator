"""Validation helpers for actuarial input ranges."""


def validate_issue_age(age, max_age):
    """Validate that issue age is within the selected table range."""
    if age < 0:
        raise ValueError("Issue age must be non-negative.")
    if age >= max_age:
        raise ValueError(f"Issue age {age} must be below limit age {max_age}.")
    return True


def validate_term(age, term, max_age):
    """Validate a fixed coverage or payment term against the table range."""
    validate_issue_age(age, max_age)
    if term <= 0:
        raise ValueError("Term must be positive.")
    if age + term > max_age:
        raise ValueError(f"Age + term = {age + term} exceeds limit age {max_age}.")
    return True


def validate_deferment(age, defer, max_age):
    """Validate a deferment period against the table range."""
    validate_issue_age(age, max_age)
    if defer < 0:
        raise ValueError("Deferment must be non-negative.")
    if age + defer >= max_age:
        raise ValueError(f"Age + deferment = {age + defer} must be below limit age {max_age}.")
    return True


def validate_coverage_window(age, defer, coverage, max_age):
    """Validate deferred coverage from issue age through deferment plus coverage."""
    validate_deferment(age, defer, max_age)
    if coverage <= 0:
        raise ValueError("Coverage period must be positive.")
    if age + defer + coverage > max_age:
        raise ValueError(
            f"Age + deferment + coverage = {age + defer + coverage} exceeds limit age {max_age}."
        )
    return True
