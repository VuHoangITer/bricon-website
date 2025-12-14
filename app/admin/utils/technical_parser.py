# File: app/admin/utils/technical_parser.py
"""
Helper đơn giản để parse text ↔ JSON cho technical_info
"""


def parse_technical_info(raw_text):
    """
    Parse text → JSON

    Input:
        Thành phần: Xi măng | Cát
        Độ bám dính: ≥ 1.0 MPa

    Output:
        {
            "Thành phần": ["Xi măng", "Cát"],
            "Độ bám dính": "≥ 1.0 MPa"
        }
    """
    if not raw_text or not raw_text.strip():
        return None

    result = {}

    for line in raw_text.split('\n'):
        line = line.strip()

        # Skip empty lines và comments
        if not line or line.startswith('#'):
            continue

        # Parse key: value
        if ':' not in line:
            continue

        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()

        if not key or not value:
            continue

        # Detect list (dấu |)
        if '|' in value:
            value_list = [v.strip() for v in value.split('|') if v.strip()]
            result[key] = value_list
        else:
            result[key] = value

    return result if result else None


def technical_info_to_text(technical_info):
    """
    Convert JSON → text

    Input:
        {
            "Thành phần": ["Xi măng", "Cát"],
            "Độ bám dính": "≥ 1.0 MPa"
        }

    Output:
        Thành phần: Xi măng | Cát
        Độ bám dính: ≥ 1.0 MPa
    """
    if not technical_info:
        return ''

    lines = []

    for key, value in technical_info.items():
        if isinstance(value, list):
            lines.append(f"{key}: {' | '.join(value)}")
        else:
            lines.append(f"{key}: {value}")

    return '\n'.join(lines)


def validate_technical_info(raw_text):
    """
    Validate format

    Returns: (bool, str)
    """
    if not raw_text or not raw_text.strip():
        return True, "OK"

    lines = [l.strip() for l in raw_text.split('\n')
             if l.strip() and not l.strip().startswith('#')]

    invalid_lines = []
    for line in lines:
        if ':' not in line:
            invalid_lines.append(line)

    if invalid_lines:
        return False, f"Các dòng sau thiếu dấu ':':\n" + '\n'.join(invalid_lines[:3])

    return True, "OK"