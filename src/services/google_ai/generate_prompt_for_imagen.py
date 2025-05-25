import json
from datetime import datetime
from pathlib import Path

from src.models.types import PromptForImagenByGemini
from src.services.firestore.schemas.meaning_schema import MeaningSchema
from src.services.google_ai.unit.request_gemini import request_gemini_json


def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def generate_prompt_for_imagen(_content: str) -> list[MeaningSchema]:
    try:
        response = request_gemini_json(
            _contents=_content, _schema=PromptForImagenByGemini
        )
        if response is None:
            raise ValueError("Response is None")
        if not isinstance(response, list):
            raise ValueError("Response is not a list")
        if len(response) == 0:
            raise ValueError("Response list is empty")
        result = PromptForImagenByGemini(
            meaning_id=response.meaning_id,
            prompt_for_imagen=response.prompt_for_imagen,
        )
        result.sort(key=lambda x: x.rank)
        return result
    except Exception as e:
        print(e)
        raise ValueError("翻訳の生成に失敗しました") from e


if __name__ == "__main__":
    # Example usage
    content = """
あなたは画像生成AIでイラストを生成するためのプロンプトエンジニアです。
英単語「」の動詞としての意味「」を表現するために、
text-to-imageモデルのGeminiに入力する英語のプロンプトを考えてください。

### 良いプロンプトの書き方のコツ
Style, Subject, Context and Backgroundから成り、意味のあるキーワードと修飾子を使用したシンプルかつ明確な文。
（例）A sketch of a modern apartment building surrounded by skyscrapers

### 画像の特徴





"""

    result = generate_prompt_for_imagen(content)
    result.sort(key=lambda x: x.rank)

    if result is None:
        print("No translation generated.")
    # 出力ディレクトリの作成
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    # 現在時刻をファイル名に使用
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{current_time}_word.json"
    # 結果をJSONファイルに出力
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            [meaning.to_dict() for meaning in result],
            f,
            ensure_ascii=False,
            indent=2,
            default=datetime_handler,
        )
    print(f"Translation saved to: {output_file}")
