def python_type_to_html_input_type(val: str):
    if val in ("int", "float"):
        return "number"

    return "text"
