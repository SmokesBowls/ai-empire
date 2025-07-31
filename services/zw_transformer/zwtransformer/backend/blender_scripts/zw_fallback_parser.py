# zw_fallback_parser.py

def parse_zw_to_dict(zw_string):
    """Simple fallback parser for ZW (YAML-ish) syntax."""
    import ast

    result = {}
    stack = [result]
    indent_levels = [0]

    for line in zw_string.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())
        while indent < indent_levels[-1]:
            stack.pop()
            indent_levels.pop()

        if ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()

            if not value:
                new_dict = {}
                stack[-1][key] = new_dict
                stack.append(new_dict)
                indent_levels.append(indent)
            else:
                try:
                    parsed_value = ast.literal_eval(value)
                except:
                    parsed_value = value.strip('"').strip("'")
                stack[-1][key] = parsed_value

    return result

