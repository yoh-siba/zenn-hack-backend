import json
from datetime import datetime
from pathlib import Path

from src.models.types import ModifiedOtherSettingsByGemini
from src.services.google_ai.unit.request_gemini import request_gemini_json


def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def generate_modified_other_settings(
    other_settings: list[str],
) -> ModifiedOtherSettingsByGemini:
    try:
        content = """
            あなたはLLMのプロンプトエンジニアです。
            以下の理想の文章の形式の指示を参照し、以下の文章の形式を修正したものを出力してください。
            出力はマークダウン記法のstr型で返してください。

            ### 理想の文章の形式
            - 項目名は一言にし、マークダウン記法の「### 」で始める
            - 各項目の内容は、その項目の下に改行して記述する
            - 各項目の内容が複雑な場合はマークダウン記法の「- 」で箇条書きにする

            ### 修正したい文章
        """
        if len(other_settings) == 0:
            result = ModifiedOtherSettingsByGemini(
                generated_other_settings="",
                prompt_token_count=0,
                candidates_token_count=0,
                total_token_count=0,
            )
            return result
        input_content = content + "\n" + "\n".join(other_settings)
        generated_other_settings, token_info = request_gemini_json(
            _contents=input_content, _schema=str
        )
        if generated_other_settings is None:
            raise ValueError("Response is None")
        result = ModifiedOtherSettingsByGemini(
            generated_other_settings=generated_other_settings,
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
    other_settings = [
        "猫は三毛猫にしてください。",
        "背景は和風な家の中にして、扇風機も入れてください。",
        "見た人がほっこりするような雰囲気にしてください。",
    ]

    result = generate_modified_other_settings(other_settings)
    if result is None:
        print("No translation generated.")
    print("Generated other settings: ")
    print(result)
    print("type(result):", type(result))
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{current_time}_prompt.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2,
            default=datetime_handler,
        )
    print(f"Translation saved to: {output_file}")
