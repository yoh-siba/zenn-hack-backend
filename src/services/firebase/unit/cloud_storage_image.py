import io
import os
from typing import Optional, Tuple, Union

from google.genai import types
from PIL import Image

from src.config.settings import bucket, genai_client


async def create_image_url_from_image(
    _image: Image.Image,
    _file_name: str,
) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        img_byte_arr = io.BytesIO()
        _image.save(img_byte_arr, format=_image.format or "PNG")
        img_byte_arr = img_byte_arr.getvalue()

        blob = bucket.blob(_file_name)

        blob.upload_from_string(
            img_byte_arr,
            content_type=f"image/{_image.format.lower() if _image.format else 'png'}",
        )
        print("File {} uploaded to {}.".format(_file_name, _file_name))
        blob.make_public()
        image_url = blob.public_url
        print("image_url:", image_url)
        return True, None, image_url
    except Exception as e:
        error_message = f"Mediaのデータ送信中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


async def create_video_url_from_video(
    _video: Union[types.Video, bytes],
    _file_name: str,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    types.Video形式またはbytes形式の動画をCloud Storageに保存してURLを返す関数

    Args:
        _video (Union[types.Video, bytes]): 保存する動画オブジェクトまたはバイトデータ
        _file_name (str): 保存するファイル名（.mp4拡張子を含む）

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
            - 成功/失敗フラグ
            - エラーメッセージ（成功時はNone）
            - 動画URL（失敗時はNone）
    """
    try:
        # バイト形式の場合はそのまま使用、Video形式の場合はダウンロード
        if isinstance(_video, bytes):
            video_data = _video
        elif isinstance(_video, types.Video):
            # video_bytesがある場合はそれを使用、ない場合はgenai_clientでダウンロード
            if _video.video_bytes:
                video_data = _video.video_bytes
            elif _video.uri:
                # genai_clientを使用して認証されたダウンロードを実行
                print(f"Downloading video from: {_video.uri}")
                video_data = genai_client.files.download(file=_video)
            else:
                raise ValueError("動画データまたはURIが見つかりません")
        else:
            raise ValueError("サポートされていない動画形式です")

        # Cloud Storageに動画をアップロード
        blob = bucket.blob(_file_name)

        blob.upload_from_string(
            video_data,
            content_type="video/mp4",
        )
        print("File {} uploaded to {}.".format(_file_name, _file_name))
        blob.make_public()
        video_url = blob.public_url
        print("video_url:", video_url)
        return True, None, video_url

    except Exception as e:
        error_message = f"動画のデータ送信中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None
        print(f"\n{error_message}")
        return False, error_message, None


if __name__ == "__main__":
    import asyncio

    # スクリプトの場所を基準としたパスを生成
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "sample.png")
    print(f"Loading image from: {image_path}")
    asyncio.run(create_image_url_from_image(Image.open(image_path), "sample.png"))
