from typing import Tuple

from google.generativeai.types import TokenInfo
from pydantic import BaseModel

from src.config.settings import GOOGLE_GEMINI_MODEL, genai_client


def request_gemini_json(
    _contents: str, _schema: BaseModel
) -> Tuple[BaseModel, TokenInfo]:
    try:
        response = genai_client.models.generate_content(
            model=GOOGLE_GEMINI_MODEL,
            contents=_contents,
            config={
                "response_mime_type": "application/json",
                "response_schema": _schema,
            },
        )
        return response.parsed, response.token_info
    except Exception as e:
        print(e)
        return None, None


def request_gemini_text(_contents: str) -> None:
    """
    args:
        _contents (str): コンテンツ
    """
    try:
        model = genai_client.GenerativeModel(GOOGLE_GEMINI_MODEL)
        response = model.generate_content(_contents)
        print(response.text)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None


if __name__ == "__main__":
    contents = "Explain how AI works in a few words"

    # Geminiのレスポンスを取得
    # request_gemini_text(contents)

    class Recipe(BaseModel):
        recipe_name: str
        ingredients: list[str]

    recipe, token_info = request_gemini_json(contents, list[Recipe])
    print(recipe)
    print(token_info)
