from src.config.settings import google_client, GOOGLE_IMAGEN_MODEL
from google.genai import types
from PIL import Image
from io import BytesIO
from typing import Literal

def request_gemini_text_to_image(_prompt:str, _number_of_images:int, _aspect_ratio:str, _person_generation:Literal["DONT_ALLOW", "ALLOW_ADULT"]) -> list[Image.Image]:
    """
    args:
        _prompt (str): 画像生成用プロンプト
        _number_of_images (int): 生成する画像の数
    returns:
        list[Image.Image]: 生成された画像のリスト
    raises:
        Exception: APIリクエスト中にエラーが発生した場合
    """
    try:
        print(f"APIリクエスト開始: プロンプト={_prompt}, 画像数={_number_of_images}, アスペクト比={_aspect_ratio}")
        
        response = google_client.models.generate_images(
            model= GOOGLE_IMAGEN_MODEL,
            prompt=_prompt,
            config=types.GenerateImagesConfig(
                number_of_images= _number_of_images,
                aspect_ratio= _aspect_ratio,
                person_generation= _person_generation
            ),
        )
        
        if response is None:
            raise Exception("APIからの応答がNoneです。認証情報やAPIの設定を確認してください。")
            
        if not hasattr(response, 'generated_images'):
            raise Exception(f"APIの応答にgenerated_imagesが含まれていません。応答内容: {response}")
            
        if not response.generated_images:
            raise Exception("生成された画像がありません。プロンプトの内容を確認してください。")
            
        images = []
        for generated_image in response.generated_images:
            image = Image.open(BytesIO(generated_image.image.image_bytes))
            images.append(image)
            image.show()
        return images
    except Exception as e:
        print(f"エラーの詳細: {str(e)}")
        raise Exception(f"画像生成中にエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    prompt = ('Robot holding a red skateboard')
    request_gemini_text_to_image(prompt, 1, "1:1", "DONT_ALLOW")

