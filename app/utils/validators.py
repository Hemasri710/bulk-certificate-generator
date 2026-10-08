import re
from typing import List, Tuple
from email_validator import validate_email, EmailNotValidError


def sanitize_filename(name: str) -> str:
    """Sanitizes strings to create safe filesystem names without path traversal or invalid characters.
    """
    # Replace non-alphanumeric characters (except dashes and underscores) with underscores
    sanitized = re.sub(r"[^\w\s-]", "", name).strip().lower()
    sanitized = re.sub(r"[-\s]+", "_", sanitized)
    return sanitized or "recipient"


def validate_email_address(email: str) -> str:
    """Validates an email address and returns normalized form.

    Raises ValueError if invalid.
    """
    try:
        valid = validate_email(email, check_deliverability=False)
        return valid.normalized
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email address '{email}': {str(e)}")
