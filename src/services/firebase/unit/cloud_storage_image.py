import io
import os
from typing import Optional, Tuple

from PIL import Image

from src.config.settings import bucket


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
        error_message = f"画像データの送信中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


if __name__ == "__main__":
    import asyncio

    # スクリプトの場所を基準としたパスを生成
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "sample.png")
    print(f"Loading image from: {image_path}")
    asyncio.run(create_image_url_from_image(Image.open(image_path), "sample.png"))
