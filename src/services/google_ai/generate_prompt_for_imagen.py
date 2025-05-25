from src.services.google_ai.unit.request_imagen import request_gemini_text_to_image


# TODO: ImageGen用のプロンプトを作成するためのAPIリクエストを行う

def generate_prompt_for_image_gen(_prompt:str) -> dict:
    try:
        request_gemini_text_to_image(_prompt, 1, "1:1", "DONT_ALLOW")
        return {}
    except Exception as e:
        print(e)
        return None