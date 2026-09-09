
def normalize_course_code(code: str) -> str:
    """API course codes look like 'I&CSCI31' with no spaces. User input might
    come in as 'I&C SCI 31' or lowercase, so we normalize both sides the same way."""
    return code.upper().replace(" ", "")