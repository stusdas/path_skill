import os
from pathlib import Path
from typing import Dict, List

from parsers.code_parser import read_code_file
from parsers.csv_parser import read_csv_file
from parsers.docx_parser import read_docx_file
from parsers.json_parser import read_json_file
from parsers.pdf_parser import read_pdf_file
from parsers.text_parser import read_text_file
from core.config import PROCESSED_DIR
from core.utils import dump_json

TEXT_EXTS = {".txt", ".md", ".log", ".xml", ".yaml", ".yml"}
CODE_EXTS = {".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs", ".sql"}


def read_file_by_type(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext in TEXT_EXTS:
        return read_text_file(file_path)
    if ext == ".json":
        return read_json_file(file_path)
    if ext == ".csv":
        return read_csv_file(file_path)
    if ext == ".docx":
        return read_docx_file(file_path)
    if ext == ".pdf":
        return read_pdf_file(file_path)
    if ext in CODE_EXTS:
        return read_code_file(file_path)
    return ""


def scan_folder(folder_path: str) -> List[Dict]:
    if not os.path.isdir(folder_path):
        raise ValueError("资料文件夹路径无效")
    results = []
    for root, _, files in os.walk(folder_path):
        for name in files:
            path = os.path.join(root, name)
            content = read_file_by_type(path).strip()
            if not content:
                continue
            item = {
                "file_name": name,
                "file_type": Path(path).suffix.lower().lstrip("."),
                "source_path": path,
                "content": content,
            }
            results.append(item)
            dump_json(PROCESSED_DIR / f"{len(results):03d}_{name}.json", item)
    return results
