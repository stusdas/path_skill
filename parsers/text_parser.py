def read_text_file(file_path: str) -> str:
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    return ""
