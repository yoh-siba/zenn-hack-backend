import json
from datetime import datetime
from pathlib import Path

from src.models.types import ExplanationByGemini
from src.services.firebase.schemas.word_schema import WordSchema
from src.services.google_ai.unit.request_gemini import request_gemini_json


def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def generate_explanation_and_core_meaning(_word: str, _content: str) -> WordSchema:
    try:
        response, token_info = request_gemini_json(
            _contents=_content, _schema=ExplanationByGemini
        )
        if response is None:
            raise ValueError("Response is None")
        result = WordSchema(
            word=_word,
            meaning_id_list=[],  # 後で更新される
            core_meaning=response.core_meaning,
            explanation=response.explanation,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return result
    except Exception as e:
        print(e)
        raise ValueError("翻訳の生成に失敗しました") from e


if __name__ == "__main__":
    # Example usage
    content = """
英単語「account」について、解説文とコアミーニングを生成してください。
explanationには、以下に示すような解説文を生成してください。
core_meaningには、以下の例のような、全ての意味を包括するコアミーニングを生成してください。
コアミーニングが無い場合は無くていいです。


### 解説文の説明
以下のいずれかで50字程度の文章にして。
1. 単語の語源や、その単語がよく使われるシチュエーションなどの豆知識
2. 単語の覚え方（例：swimはスイスイ泳ぐ）
（注意点）英単語の意味を羅列しないで。


### コアミーニングの例（「run」場合）
ある方向に，連続して，（すばやくなめらかに）動く
"""
    result = generate_explanation_and_core_meaning("account", content)

    if result is None:
        print("No translation generated.")
    # 出力ディレクトリの作成
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    # 現在時刻をファイル名に使用
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{current_time}_explanation.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            result.to_dict(),
            f,
            ensure_ascii=False,
            indent=2,
            default=datetime_handler,
        )
    print(f"Translation saved to: {output_file}")
