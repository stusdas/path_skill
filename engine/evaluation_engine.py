from memory.case_store import list_cases


def summarize_cases() -> dict:
    cases = list_cases()
    return {
        "case_count": len(cases),
        "questions": [c.get("question", "") for c in cases[-10:]],
    }
