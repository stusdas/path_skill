import csv
from parsers.text_parser import read_text_file


def read_csv_file(file_path: str) -> str:
    try:
        rows = []
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                rows.append(", ".join(row))
                if i >= 49:
                    rows.append("[CSV内容过长，仅保留前50行]")
                    break
        return "\n".join(rows)
    except Exception:
        return read_text_file(file_path)
