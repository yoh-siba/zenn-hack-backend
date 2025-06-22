import time
from io import BytesIO
from typing import Literal

import requests
from google.genai import types
from PIL import Image

from src.config.settings import GOOGLE_VEO_MODEL, genai_client


def request_text_to_video(
    _prompt: str,
    _person_generation: Literal["DONT_ALLOW", "ALLOW_ADULT"],
) -> types.Video:
    """
    args:
        _prompt (str): 画像生成用プロンプト
        _person_generation (Literal): 人物生成の許可設定
    returns:
        types.Video: 生成された動画オブジェクト
    raises:
        Exception: APIリクエスト中にエラーが発生した場合
    """
    try:
        operation = genai_client.models.generate_videos(
            model=GOOGLE_VEO_MODEL,
            prompt=_prompt,
            config=types.GenerateVideosConfig(
                person_generation=_person_generation,
                aspect_ratio="16:9",  # "16:9" or "9:16"
                duration_seconds=5,  # 5~8
                number_of_videos=1,
            ),
        )

        # 動画生成の進行状況をポーリング
        while not operation.done:
            time.sleep(20)
            operation = genai_client.operations.get(operation)

        # 動画をダウンロードして保存
        video_objects = []
        for n, generated_video in enumerate(operation.response.generated_videos):
            video_objects.append(generated_video.video)
        print("video_objects：", video_objects)
        return video_objects[0]

    except Exception as e:
        print(f"エラーの詳細: {str(e)}")
        raise Exception(f"動画生成中にエラーが発生しました: {str(e)}")


def request_image_to_video(
    _prompt: str,
    _image_url: str,
    _person_generation: Literal["DONT_ALLOW", "ALLOW_ADULT"],
) -> types.Video:
    """
    args:
        _prompt (str): 画像生成用プロンプト
        image_url (str): 画像のURL
        _person_generation (Literal): 人物生成の許可設定
    returns:
        types.Video: 生成された動画オブジェクト
    raises:
        Exception: APIリクエスト中にエラーが発生した場合
    """
    try:
        # URLから画像を取得してImage.Imageオブジェクトに変換
        print(f"画像URLにアクセス中: {_image_url}")
        response = requests.get(_image_url)
        response.raise_for_status()

        print("HTTPレスポンス情報:")
        print(f"  ステータスコード: {response.status_code}")
        print(f"  コンテンツサイズ: {len(response.content)} bytes")
        print(f"  コンテンツタイプ: {response.headers.get('content-type', 'unknown')}")

        if len(response.content) == 0:
            raise Exception("取得した画像データが空です")

        # 画像をロード
        image_bytes = BytesIO(response.content)
        image = Image.open(image_bytes)

        print("画像情報:")
        print(f"  サイズ: {image.size}")
        print(f"  モード: {image.mode}")
        print(f"  フォーマット: {image.format}")

        # 画像が有効かテスト
        try:
            image.verify()
            # verify後は画像が使えなくなるので再ロード
            image_bytes.seek(0)
            image = Image.open(image_bytes)
            print("画像の検証: 成功")
        except Exception as verify_error:
            print(f"画像の検証エラー: {verify_error}")
            raise Exception(f"無効な画像ファイルです: {verify_error}")

        # RGBモードに変換（APIが要求する可能性があるため）
        if image.mode != "RGB":
            print(f"画像を{image.mode}からRGBに変換中...")
            image = image.convert("RGB")
            print("RGB変換完了")

        # Google AI APIに適した形式で画像を準備
        # 画像をバイト形式で再保存（APIが期待する形式）
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        # types.Imageオブジェクトを作成
        image_part = types.Image(
            image_bytes=img_byte_arr.getvalue(), mime_type="image/png"
        )
        print("API用画像オブジェクト作成完了")
        print(f"画像バイトサイズ: {len(img_byte_arr.getvalue())} bytes")

        operation = genai_client.models.generate_videos(
            model=GOOGLE_VEO_MODEL,
            prompt=_prompt,
            image=image_part,
            config=types.GenerateVideosConfig(
                person_generation=_person_generation,
                aspect_ratio="16:9",  # "16:9" or "9:16"
                duration_seconds=5,  # 5~8
                number_of_videos=1,
            ),
        )

        print(f"Operation作成完了: {operation}")
        print(f"Operation done状態: {operation.done}")
        print(f"Operation name: {getattr(operation, 'name', 'なし')}")

        # 動画生成の進行状況をポーリング
        while not operation.done:
            time.sleep(20)
            operation = genai_client.operations.get(operation)
            print(f"更新されたOperation done状態: {operation.done}")

        print("動画生成完了!")
        print(f"Operation response: {operation.response}")

        # responseがNoneでないことを確認
        if operation.response is None:
            raise Exception(
                "API応答が空です (operation.response is None)"
            )  # generated_videosがあることを確認
        if not hasattr(operation.response, "generated_videos"):
            raise Exception("API応答にgenerated_videosがありません")

        generated_videos = operation.response.generated_videos

        # 安全性フィルタリングのチェック
        if generated_videos is None:
            print("operation.response", operation.response)

            # RAI (Responsible AI) フィルタリングの確認
            rai_filtered_count = getattr(
                operation.response, "rai_media_filtered_count", 0
            )
            rai_filtered_reasons = getattr(
                operation.response, "rai_media_filtered_reasons", []
            )

            if rai_filtered_count > 0:
                reasons_text = ", ".join(rai_filtered_reasons)
                print(
                    f"安全性フィルタリング: {rai_filtered_count}個の動画がブロックされました"
                )
                print(f"理由: {reasons_text}")

                # より詳細なエラーメッセージを提供
                if "people/face generation" in reasons_text.lower():
                    raise Exception(
                        f"人物/顔生成の安全設定により動画生成がブロックされました。"
                        f"プロンプトを調整するか、人物を含まない内容に変更してください。"
                        f"詳細: {reasons_text}"
                    )
                else:
                    raise Exception(
                        f"安全性設定により動画生成がブロックされました ({rai_filtered_count}個)。"
                        f"理由: {reasons_text}"
                    )
            else:
                raise Exception("generated_videosがNoneです（理由不明）")

        print(
            f"Generated videos count: {len(generated_videos) if generated_videos else 0}"
        )

        # 動画をダウンロードして保存
        video_objects = []
        for n, generated_video in enumerate(generated_videos):
            print(f"Video {n}: {generated_video}")
            if hasattr(generated_video, "video") and generated_video.video is not None:
                video_objects.append(generated_video.video)
            else:
                print(f"Warning: Video {n} has no video attribute or is None")

        if not video_objects:
            raise Exception("有効な動画オブジェクトが見つかりませんでした")

        print("video_objects：", video_objects)
        return video_objects[0]

    except Exception as e:
        print(f"エラーの詳細: {str(e)}")
        raise Exception(f"動画生成中にエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    prompt = "Panning wide shot of a calico kitten sleeping in the sunshine"
    video_object = request_text_to_video(prompt, "DONT_ALLOW")

    # 同階層に生成された動画ファイルを保存
    file_path = "video.mp4"
    video_object.save(file_path)
    print(f"生成された動画ファイル: {file_path}")
