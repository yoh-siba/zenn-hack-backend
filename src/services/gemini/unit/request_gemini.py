from src.config.settings import google_client, GOOGLE_GEMINI_MODEL
from pydantic import BaseModel

class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[str]


def get_gemini_response_json(_contents:str, _schema:BaseModel) -> None:
    try:
        response = google_client.models.generate_content(
            model= GOOGLE_GEMINI_MODEL,
            contents=_contents,
            config={
            "response_mime_type": "application/json",
            "response_schema": _schema
        },
    )
        # Use the response as a JSON string.
        print(response.text)
        return response.parsed
    except Exception as e:
        print(e)
        return None

def get_gemini_response(_contents:str) -> None:
    """
    args:
        _contents (str): コンテンツ
    """
    model = google_client.GenerativeModel(GOOGLE_GEMINI_MODEL)
    response = model.generate_content(_contents)
    print(response.text)


if __name__ == "__main__":
    contents = "Explain how AI works in a few words"
    
    # Geminiのレスポンスを取得
    get_gemini_response(contents)

