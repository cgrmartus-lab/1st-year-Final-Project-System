import csv
import io
from typing import Union

REQUIRED_COLUMNS = {"prodCode", "prodName", "category", "price", "stock"}


def parse_csv(source: Union[str, bytes]) -> tuple:
    """
    Parse a CSV file from a file path (str) or raw bytes.
    Returns (rows, errors).
    """
    errors = []
    file_handle = None

    try:
        if isinstance(source, bytes):
            text = source.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text))
        else:
            file_handle = open(source, newline="", encoding="utf-8-sig")
            reader = csv.DictReader(file_handle)

        reader.fieldnames = [h.strip() for h in (reader.fieldnames or [])]
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            errors.append(
                f"CSV missing required columns: {', '.join(sorted(missing))}"
            )
            return [], errors

        rows = []
        for i, row in enumerate(reader, start=2):
            cleaned = {k.strip(): v.strip() for k, v in row.items()}
            row_errors = []
            try:
                v = float(cleaned.get("price", ""))
                if v < 0:
                    row_errors.append("price must be >= 0")
            except (ValueError, TypeError):
                row_errors.append("price must be numeric")
            try:
                v = int(cleaned.get("stock", ""))
                if v < 0:
                    row_errors.append("stock must be >= 0")
            except (ValueError, TypeError):
                row_errors.append("stock must be a whole number")
            if not cleaned.get("prodCode", "").strip():
                row_errors.append("prodCode is required")
            if not cleaned.get("prodName", "").strip():
                row_errors.append("prodName is required")

            if row_errors:
                errors.append(f"Row {i}: " + "; ".join(row_errors))
            else:
                rows.append(cleaned)

        return rows, errors

    except FileNotFoundError:
        return [], [f"File not found: {source}"]
    except Exception as e:
        return [], [f"File read error: {e}"]
    finally:
        #Always close the file handle
        if file_handle is not None:
            file_handle.close()
