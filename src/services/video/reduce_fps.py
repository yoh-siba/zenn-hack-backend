import os
import tempfile

import cv2
from google.genai import types


def reduce_fps_to_10(input_video: types.Video) -> types.Video:
    """
    入力動画のフレームレートを10fpsに変更する関数

    Args:
        input_video (types.Video): Google Generative AIのVideo型オブジェクト

    Returns:
        types.Video: フレームレートが10fpsに変更されたVideo型オブジェクト

    Raises:
        Exception: 動画処理中にエラーが発生した場合
    """
    try:
        # 一時ファイルを作成して入力動画を保存
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_input:
            input_video.save(temp_input.name)
            temp_input_path = temp_input.name

        # 出力用の一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
            temp_output_path = temp_output.name

        # OpenCVで動画を読み込み
        cap = cv2.VideoCapture(temp_input_path)

        # 元動画の情報を取得
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 10fpsに変更するためのフレーム間隔を計算
        target_fps = 10.0
        frame_interval = max(1, int(original_fps / target_fps))

        # 動画書き込み用のVideoWriterを設定
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(
            temp_output_path, fourcc, target_fps, (frame_width, frame_height)
        )

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 指定した間隔でフレームを抽出
            if frame_count % frame_interval == 0:
                out.write(frame)

            frame_count += 1

        # リソースを解放
        cap.release()
        out.release()

        # 処理済み動画をtypes.Videoオブジェクトとして読み込み
        output_video = types.Video.from_file(temp_output_path)

        # 一時ファイルを削除
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)

        return output_video

    except Exception as e:
        # エラーが発生した場合、一時ファイルを削除
        if "temp_input_path" in locals() and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if "temp_output_path" in locals() and os.path.exists(temp_output_path):
            os.unlink(temp_output_path)

        raise Exception(f"フレームレート変更中にエラーが発生しました: {str(e)}")
