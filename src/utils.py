from typing import Any
from src.logging_config import get_logger
import json
logger = get_logger()


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def table_logger(obj: Any, table_header: str = None, extra_space: bool = False) -> None:
    max_widths = {}

    result = ""

    if extra_space:
        result += "\n"

    if isinstance(obj, dict):
        obj = [obj]

    if isinstance(obj, list):
        get_first_item = obj[0]

        header = list(get_first_item.keys())

        for key in header:
            max_widths[key] = max(len(str(get_first_item[key])), max_widths.get(key, 0))

        for row in obj:
            for key in header:
                max_widths[key] = max(len(str(row[key])), max_widths.get(key, 0))


        total_width = sum(max_widths.values()) + 5 * len(header) -1

        if table_header:
            result += "|" + "-" * total_width + "|\n"
            result += "|"+str(table_header[:total_width]).center(total_width)+"|\n"
                        

        result += "|-" + "-+-".join("-" * (max_widths[key] + 2) for key in header) + "-|\n"
        

        result += "| " + " | ".join(
                str(key[: max_widths[key] + 2]).center(max_widths[key] + 2)
                for key in header
            ) + " |\n"
    

        result +=  "|-" + "-+-".join("-" * (max_widths[key] + 2) for key in header) + "-|\n"
    

        for row in obj:
            result += "| "  + " | ".join(
                    str(row[key]).center(max_widths[key] + 2) for key in header
                ) + " |\n"

        result +=  "|-" + "-+-".join("-" * (max_widths[key] + 2) for key in header) + "-|\n"

        return result
        

    


def extract_nested_json(text: str, convert_to_json: bool = False):
    """
    Extracts a single, complete, and correctly nested JSON object or array from a string.

    Args:
        text: The input string containing text and a JSON object or array.
        convert_to_json: If True, the extracted JSON string will be converted to a JSON object.
    Returns:
        The extracted JSON string, or None if no valid start is found.
    """
    brace_count = 0
    bracket_count = 0
    start_index = -1
    is_object = False
    is_array = False

    # Find the first non-whitespace occurrence of '{' or '['
    for i, char in enumerate(text):
        if char == '{':
            start_index = i
            is_object = True
            brace_count = 1
            break
        elif char == '[':
            start_index = i
            is_array = True
            bracket_count = 1
            break

    if start_index == -1:
        return None  # No starting brace/bracket found

    if is_object:
        # Iterate from the starting '{'
        for i in range(start_index + 1, len(text)):
            ch = text[i]
            if ch == '{':
                brace_count += 1
            elif ch == '}':
                brace_count -= 1
                if brace_count == 0:
                    if convert_to_json:
                        return json.loads(text[start_index : i + 1])
                    else:
                        return text[start_index : i + 1]
        # If loop finishes without brace_count reaching zero (unbalanced JSON object)
        return None
    elif is_array:
        # Iterate from the starting '['
        for i in range(start_index + 1, len(text)):
            ch = text[i]
            if ch == '[':
                bracket_count += 1
            elif ch == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    if convert_to_json:
                        return json.loads(text[start_index : i + 1])
                    else:
                        return text[start_index : i + 1]
        # If loop finishes without bracket_count reaching zero (unbalanced JSON array)
        return None

    return None  # fallback, should not reach here