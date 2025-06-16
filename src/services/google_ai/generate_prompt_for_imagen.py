import json
from datetime import datetime
from pathlib import Path

from src.models.types import PromptForImagenByGemini
from src.services.google_ai.unit.request_gemini import request_gemini_json


def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def generate_prompt_for_imagen(_content: str) -> PromptForImagenByGemini:
    try:
        response, token_info = request_gemini_json(
            _contents=_content, _schema=PromptForImagenByGemini
        )
        if response is None:
            raise ValueError("Response is None")
        result = PromptForImagenByGemini(
            generated_prompt=response.generated_prompt,
            prompt_token_count=token_info.prompt_token_count,
            candidates_token_count=token_info.candidates_token_count,
            total_token_count=token_info.total_token_count,
        )
        return result
    except Exception as e:
        print(e)
        raise ValueError("画像生成用プロンプトの生成に失敗しました") from e


if __name__ == "__main__":
    # Example usage
    content = """
あなたは画像生成AIでイラストを生成するためのプロンプトエンジニアです。
英単語「run」の動詞としての意味「走る」を表現するために、
text-to-imageモデルのImagenに入力する英語のプロンプトを考えてください。

### 良いプロンプトの書き方のコツ
Style, Subject, Context and Backgroundから成り、意味のあるキーワードと修飾子を使用したシンプルかつ明確な文。
（例）A sketch of a modern apartment building surrounded by skyscrapers

### 画像の特徴
- 動きのある躍動感のある表現
- 人物が走っている様子を中心に
- 自然な風景や都市の背景
- 明るく活気のある雰囲気
- スピード感を表現する動的な構図
"""

    result = generate_prompt_for_imagen(content)

    if result is None:
        print("No translation generated.")
    print(f"Generated prompt: {result.generated_prompt}")
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{current_time}_prompt.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            result.to_dict(),
            f,
            ensure_ascii=False,
            indent=2,
            default=datetime_handler,
        )
    print(f"Translation saved to: {output_file}")
