from src.config.settings import google_client, GOOGLE_GEMINI_MODEL

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

