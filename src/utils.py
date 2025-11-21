from typing import Any
from src.logging_config import get_logger

logger = get_logger()


def table_logger(obj: Any, table_header: str = None, extra_space: bool = False) -> None:
    max_widths = {}

    if extra_space:
        logger.info("")

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
            logger.info("|" + "-" * total_width + "|")
            logger.info(
                "|"+str(table_header[:total_width]).center(total_width)+"|"
            )            

        logger.info(
            "|-" + "-+-".join("-" * (max_widths[key] + 2) for key in header) + "-|"
        )

        logger.info(
            "| "
            + " | ".join(
                str(key[: max_widths[key] + 2]).center(max_widths[key] + 2)
                for key in header
            )
            + " |"
        )

        logger.info(
            "|-" + "-+-".join("-" * (max_widths[key] + 2) for key in header) + "-|"
        )

        for row in obj:
            logger.info(
                "| "
                + " | ".join(
                    str(row[key]).center(max_widths[key] + 2) for key in header
                )
                + " |"
            )

        logger.info(
            "|-" + "-+-".join("-" * (max_widths[key] + 2) for key in header) + "-|"
        )

    


def extract_nested_json(text: str):
    """
    Extracts a single, complete, and correctly nested JSON object from a string.

    Args:
        text: The input string containing text and a JSON object.

    Returns:
        The extracted JSON string, or None if no valid starting brace is found.
    """
    brace_count = 0
    start_index = -1

    # 1. Find the starting point (first '{')
    for i, char in enumerate(text):
        if char == '{':
            start_index = i
            break

    if start_index == -1:
        return None  # No starting brace found

    # 2. Iterate from the starting point, counting braces
    for i in range(start_index, len(text)):
        char = text[i]

        if char == '{':
            # Increase count for an opening brace
            brace_count += 1
        elif char == '}':
            # Decrease count for a closing brace
            brace_count -= 1

            # 3. Stop when the count returns to zero (balanced)
            if brace_count == 0:
                # Return the substring from the start index up to and including the current index
                json_string = text[start_index : i + 1]

                # 4. Return the result nested in the requested format
                return json_string
    # If the loop finishes without the brace_count reaching zero (unbalanced JSON)
    return None