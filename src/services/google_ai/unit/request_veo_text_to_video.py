import time
from typing import Literal

from google.genai import types

from src.config.settings import GOOGLE_VEO_MODEL, genai_client


def request_text_to_video(
    _prompt: str,
    _person_generation: Literal["DONT_ALLOW", "ALLOW_ADULT"],
) -> list[types.Video]:
    """
    args:
        _prompt (str): 画像生成用プロンプト
        _person_generation (Literal): 人物生成の許可設定
    returns:
        list[types.Video]: 生成された動画オブジェクトのリスト
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
            ),
        )

        # 動画生成の進行状況をポーリング
        while not operation.done:
            time.sleep(20)
            operation = genai_client.operations.get(operation)

        # 動画をダウンロードして保存
        video_objects = []
        for n, generated_video in enumerate(operation.response.generated_videos):
            genai_client.files.download(file=generated_video.video)
            video_objects.append(generated_video.video)

        return video_objects

    except Exception as e:
        print(f"エラーの詳細: {str(e)}")
        raise Exception(f"動画生成中にエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    prompt = "Panning wide shot of a calico kitten sleeping in the sunshine"
    video_objects = request_text_to_video(prompt, "DONT_ALLOW")

    # 同階層に生成された動画ファイルを保存
    for n, video_object in enumerate(video_objects):
        file_path = f"video{n}.mp4"
        video_object.save(file_path)
        print(f"生成された動画ファイル: {file_path}")
