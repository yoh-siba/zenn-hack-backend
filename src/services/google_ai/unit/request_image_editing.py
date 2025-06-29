from io import BytesIO

from google.genai import types
from PIL import Image

from src.config.settings import GOOGLE_GEMINI_IMAGE_EDITING_MODEL, genai_client


def request_gemini_image_to_image(
    _prompt: str,
    _image: Image.Image,
) -> Image.Image:
    """
    args:
        _prompt (str): 画像生成用プロンプト
    returns:
        Image.Image: 生成された画像
    raises:
        Exception: APIリクエスト中にエラーが発生した場合
    """
    try:
        response = genai_client.models.generate_content(
            model=GOOGLE_GEMINI_IMAGE_EDITING_MODEL,
            contents=[_prompt, _image],
            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
        )

        if response is None:
            raise Exception(
                "APIからの応答がNoneです。認証情報やAPIの設定を確認してください。"
            )  # レスポンスの構造を確認
        if not hasattr(response, "candidates") or not response.candidates:
            raise Exception("APIの応答にcandidatesが含まれていません。")

        images = []

        for candidate in response.candidates:
            if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                has_text_description = False
                for i, part in enumerate(candidate.content.parts):
                    print(
                        f"Part {i}: inline_data = {part.inline_data is not None}, text = {part.text is not None}"
                    )
                    if part.text is not None:
                        has_text_description = True
                    elif part.inline_data is not None:
                        try:
                            image = Image.open(BytesIO(part.inline_data.data))
                            # テキスト説明がある場合のみ、その後の画像を生成画像として扱う
                            if has_text_description:
                                images.append(image)
                        except Exception as img_error:
                            print(f"  画像の読み込みエラー: {img_error}")

        if not images:
            raise Exception(
                f"生成された画像がありません。プロンプトの内容を確認してください。\nプロンプト: {_prompt}"
            )

        # 最後の画像（最新の生成画像）を返す
        return images[-1]
    except Exception as e:
        print(f"エラーの詳細: {str(e)}")
        raise Exception(f"画像生成中にエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    prompt = "以下の指示に従って画像を更新して\n## 修正点: 豚をペンギンに変換して"
    try:
        # 元画像を読み込み
        original_image = Image.open("src/services/google_ai/unit/image.png")
        print(f"元画像サイズ: {original_image.size}")

        edited_image = request_gemini_image_to_image(prompt, original_image)

        # 結果画像を保存（デバッグ用）
        edited_image.save("src/services/google_ai/unit/result_image.png")
        print("結果画像を result_image.png として保存しました")

        # 元画像と結果画像のサイズを比較
        if edited_image.size != original_image.size:
            print(
                f"⚠️  画像サイズが変更されました: {original_image.size} → {edited_image.size}"
            )
        else:
            print(f"画像サイズは同じです: {edited_image.size}")

        print("画像生成完了！画像を表示します...")
        edited_image.show()
    except Exception as e:
        print(f"実行エラー: {e}")
