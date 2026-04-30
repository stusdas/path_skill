from pypdf import PdfReader


def read_pdf_file(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        texts = []
        for i, page in enumerate(reader.pages[:20]):
            texts.append(f"--- PDF第{i+1}页 ---\n{page.extract_text() or ''}")
        if len(reader.pages) > 20:
            texts.append("[PDF页数过多，仅保留前20页]")
        return "\n".join(texts)
    except Exception:
        return ""
