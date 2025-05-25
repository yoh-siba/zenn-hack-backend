from pydantic import BaseModel

from src.config.settings import GOOGLE_GEMINI_MODEL, google_client


def request_gemini_json(_contents: str, _schema: BaseModel) -> BaseModel:
    try:
        response = google_client.models.generate_content(
            model=GOOGLE_GEMINI_MODEL,
            contents=_contents,
            config={
                "response_mime_type": "application/json",
                "response_schema": _schema,
            },
        )
        return response.parsed
    except Exception as e:
        print(e)
        return None


def request_gemini_text(_contents: str) -> None:
    """
    args:
        _contents (str): コンテンツ
    """
    try:
        model = google_client.GenerativeModel(GOOGLE_GEMINI_MODEL)
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

    recipe = request_gemini_json(contents, list[Recipe])
    print(recipe)
