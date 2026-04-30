import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from core.config import CASES_DIR, PROCESSED_DIR, PROFILES_DIR, REPORTS_DIR
from core.llm_client import LLMClient
from engine.decision_engine import DecisionEngine
from engine.profile_engine import ProfileEngine
from parsers.file_router import scan_folder


def clear_dir(path: Path):
    if path.exists():
        for item in path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)


def main():
    clear_dir(PROCESSED_DIR)
    clear_dir(PROFILES_DIR)
    clear_dir(CASES_DIR)
    clear_dir(REPORTS_DIR)

    llm = LLMClient(mock=True)
    file_items = scan_folder(str(ROOT / "examples" / "demo_user_1"))
    profile_engine = ProfileEngine(llm)
    profile = profile_engine.run(file_items, {
        "nickname": "测试用户",
        "occupation": "学生",
        "mbti": "",
        "zodiac": "",
        "attachment_style": "",
        "labels": ["长期主义", "纠结型"],
        "impression": "想避免人生局部最优",
    })
    assert "four_layer_system" in profile
    assert "executive_summary" in profile

    decision_engine = DecisionEngine(llm)
    result = decision_engine.run(profile, "我该选稳定工作还是高成长工作？")
    assert "decomposition" in result
    assert "options" in result
    assert "report" in result and len(result["report"]) > 20
    print("SMOKE_TEST_OK")


if __name__ == "__main__":
    main()
