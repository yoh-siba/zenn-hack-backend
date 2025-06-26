from typing import Literal

from src.models.exceptions import ServiceException
from src.services.firebase.unit.cloud_storage_image import create_image_url_from_image
from src.services.google_ai.unit.request_imagen import request_imagen_text_to_image


async def generate_and_store_image(
    _prompt: str,
    _person_generation: Literal["DONT_ALLOW", "ALLOW_ADULT"],
    _word: str,
    _pos: str,
    _meaning: str,
    _flashcard_id: str,
) -> list[str]:
    """画像を生成してストレージに保存する関数

    Args:
        _prompt (str): 画像生成用のプロンプト
        _person_generation (Literal["DONT_ALLOW", "ALLOW_ADULT"]): 人物生成の許可設定
        _word (str): 単語
        _pos (str): 品詞
        _meaning (str): 意味
        _flashcard_id (str): フラッシュカードID

    Returns:
        list[str]: 生成された画像URLのリスト

    Raises:
        ServiceException: 画像生成または保存に失敗した場合
    """
    try:
        generated_images = request_imagen_text_to_image(
            _prompt=_prompt,
            _number_of_images=1,
            _aspect_ratio="1:1",  # アスペクト比を1:1に設定
            _person_generation=_person_generation,  # 人物生成を許可しない
        )
        if not generated_images:
            raise ServiceException("画像の生成に失敗しました", "external_api")

        # 生成された画像をFirestorageに保存して、URLを取得
        image_url_list = []
        for image in generated_images:
            image_url = await create_image_url_from_image(
                image,
                f"{_word}/{_pos}/{_meaning}/{_flashcard_id}.png",
            )
            image_url_list.append(image_url)

        return image_url_list

    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"画像生成・保存中にエラーが発生しました: {str(e)}", "general"
        )


if __name__ == "__main__":
    import asyncio

    async def main():
        # テスト用の単語
        test_word = "account"
        try:
            flascard_id = await generate_and_store_image(
                test_word,
                "DONT_ALLOW",
                "account",
                "noun",
                "a record of financial expenditure",
                "flashcard_123",
            )
            print(
                f"単語 '{test_word}' のセットアップに成功しました。生成されたflascard_id: {flascard_id}"
            )
        except ServiceException as se:
            print(f"単語 '{test_word}' のセットアップに失敗しました。エラー: {se.message}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {str(e)}")

    # 非同期関数を実行
    asyncio.run(main())
