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


def table_logger(
    obj: Any,
    table_header: str = None,
    extra_space: bool = False,
    max_column_width: int = 80,
    ellipsis: bool = False,
) -> None:
    """
    Log/display a table of dictionaries or dict using ASCII box drawing.
    If max_column_width is set, any cell value longer than this will be 
    split into multiple lines for that cell.
    """
    max_widths = {}

    result = ""

    if extra_space:
        result += "\n"

    if isinstance(obj, dict):
        obj = [obj]

    if isinstance(obj, list) and obj:
        get_first_item = obj[0]
        header = list(get_first_item.keys())

        # Prepare max widths for each column (before applying max_column_width)
        for key in header:
            max_widths[key] = max(len(str(get_first_item[key])), max_widths.get(key, 0))

        for row in obj:
            for key in header:
                value_str = str(row[key])
                # For multiline, consider longest split part
                if max_column_width is not None:
                    split_lines = [
                        value_str[i : i + max_column_width]
                        for i in range(0, len(value_str), max_column_width)
                    ]
                    max_line_len = max((len(line) for line in split_lines), default=0)
                    cell_width = max_line_len
                else:
                    cell_width = len(value_str)
                max_widths[key] = max(cell_width, max_widths.get(key, 0), len(str(key)))

        # apply max_column_width restriction to width, but never less than header length
        if max_column_width is not None:
            for key in header:
                max_widths[key] = max(min(max_widths[key], max_column_width), len(str(key)))

        total_width = sum(max_widths.values()) + 5 * len(header) - 1

        if table_header:
            result += "|" + "-" * total_width + "|\n"
            result += "|" + str(table_header[:total_width]).center(total_width) + "|\n"

        result += "|-" + "-+-".join("-" * (max_widths[key] + 2) for key in header) + "-|\n"

        # Render the header
        result += (
            "| "
            + " | ".join(
                str(key[: max_widths[key]]).center(max_widths[key] + 2)
                for key in header
            )
            + " |\n"
        )

        result += "|-" + "-+-".join("-" * (max_widths[key] + 2) for key in header) + "-|\n"

        # Render the table body with multiline cells
        for row in obj:
            # For each key, split contents if needed
            cell_lines = []
            max_lines = 1
            for key in header:
                value = str(row[key])
                # if ellipsis is true then replace \n with ...
                if ellipsis and "\n" in value:
                    value = value.replace("\n", " ")
                if ellipsis and len(value) > max_column_width:
                    value = value[:max_column_width-3] + "..."
                if max_column_width is not None and len(value) > max_column_width:
                    lines = [
                        value[i : i + max_column_width]
                        for i in range(0, len(value), max_column_width)
                    ]
                else:
                    lines = [value]
                cell_lines.append(lines)
                if len(lines) > max_lines:
                    max_lines = len(lines)
            # For each line in row (for multiline cells)
            for line_no in range(max_lines):
                row_str = "| "
                for col, lines in enumerate(cell_lines):
                    cell = lines[line_no] if line_no < len(lines) else ""
                    pad_width = max_widths[header[col]] + 2
                    row_str += cell.center(pad_width)
                    if col != len(cell_lines) - 1:
                        row_str += " | "
                    else:
                        row_str += " |\n"
                result += row_str
        result += "|-" + "-+-".join("-" * (max_widths[key] + 2) for key in header) + "-|\n"

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