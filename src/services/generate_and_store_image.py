from typing import Literal, Optional, Tuple

from src.services.firebase.unit.cloud_storage_image import create_image_url_from_image
from src.services.google_ai.unit.request_imagen import request_imagen_text_to_image


async def generate_and_store_image(
    _prompt: str,
    _person_generation: Literal["DONT_ALLOW", "ALLOW_ADULT"],
    _word: str,
    _pos: str,
    _meaning: str,
    _flashcard_id: str,
) -> Tuple[bool, Optional[str], Optional[list[str]]]:
    """単語とその意味の生成＆格納用の関数
        WordsAPIでベース取得 -> 解説・コアミーニング生成 -> 意味リスト生成 -> データ格納
    Args:
        _prompt (str): 画像生成用のプロンプト
        _person_generation (Literal["DONT_ALLOW", "ALLOW_ADULT"]): 人物生成の許可設定

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 画像のURL
    """
    try:
        generated_images = request_imagen_text_to_image(
            _prompt=_prompt,
            _number_of_images=1,
            _aspect_ratio="1:1",  # アスペクト比を1:1に設定
            _person_generation=_person_generation,  # 人物生成を許可しない
        )
        if not generated_images:
            raise ValueError("No images generated")

        # 生成された画像をFirestorageに保存して、URLを取得
        image_url_list = []
        for image in generated_images:
            success, error, image_url = await create_image_url_from_image(
                image,
                f"{_word}/{_pos}/{_meaning}/{_flashcard_id}.png",
            )
            if not success:
                raise ValueError("画像のURL取得に失敗しました", error)
            image_url_list.append(image_url)

        return True, None, image_url_list

    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


if __name__ == "__main__":
    import asyncio

    async def main():
        # テスト用の単語
        test_word = "account"
        success, error, flascard_id = await generate_and_store_image(
            test_word,
            "DONT_ALLOW",
            "account",
            "noun",
            "a record of financial expenditure",
            "flashcard_123",
        )
        if success:
            print(
                f"単語 '{test_word}' のセットアップに成功しました。生成されたflascard_id: {flascard_id}"
            )
        else:
            print(f"単語 '{test_word}' のセットアップに失敗しました。エラー: {error}")

    # 非同期関数を実行
    asyncio.run(main())
