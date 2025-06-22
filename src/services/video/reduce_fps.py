import os
import tempfile

import cv2
from google.genai import types

from src.config.settings import genai_client


def reduce_fps_to_10(input_video: types.Video) -> bytes:
    """
    入力動画のフレームレートを10fpsに変更する関数

    Args:
        input_video (types.Video): Google Generative AIのVideo型オブジェクト

    Returns:
        bytes: フレームレートが10fpsに変更された動画のバイトデータ

    Raises:
        Exception: 動画処理中にエラーが発生した場合
    """
    try:
        # 一時ファイルを作成して入力動画を保存
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_input:
            temp_input_path = temp_input.name

        # 動画データを取得（URIの場合はダウンロード、video_bytesがある場合はそれを使用）
        if input_video.video_bytes:
            video_data = input_video.video_bytes
        elif input_video.uri:
            # genai_clientを使用して認証されたダウンロードを実行
            video_data = genai_client.files.download(file=input_video)
        else:
            raise ValueError(
                "動画データまたはURIが見つかりません"
            )  # 動画データを一時ファイルに書き込み
        with open(temp_input_path, "wb") as f:
            f.write(video_data)

        # 出力用の一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
            temp_output_path = temp_output.name

        # OpenCVで動画を読み込み
        cap = cv2.VideoCapture(temp_input_path)

        if not cap.isOpened():
            raise ValueError(
                f"OpenCVで動画ファイルを開けませんでした: {temp_input_path}"
            )

        # 元動画の情報を取得
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if original_fps <= 0 or frame_width <= 0 or frame_height <= 0:
            raise ValueError(
                f"無効な動画パラメータ: FPS={original_fps}, Size={frame_width}x{frame_height}"
            )  # 10fpsに変更するためのフレーム間隔を計算
        target_fps = 10.0
        frame_interval = max(1, int(original_fps / target_fps))
        # 動画書き込み用のVideoWriterを設定（H.264コーデック）
        fourcc = cv2.VideoWriter_fourcc(*"avc1")  # H.264コーデック
        out = cv2.VideoWriter(
            temp_output_path, fourcc, target_fps, (frame_width, frame_height)
        )

        if not out.isOpened():
            raise ValueError("VideoWriterの初期化に失敗しました")

        frame_count = 0
        written_frames = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 指定した間隔でフレームを抽出
            if frame_count % frame_interval == 0:
                out.write(frame)
                written_frames += 1
                # if written_frames % 10 == 0:
                #     print(f"[DEBUG] 処理中... 書き込みフレーム数: {written_frames}")

            frame_count += 1

        # リソースを解放
        cap.release()
        out.release()

        # 出力ファイルの存在確認
        if not os.path.exists(temp_output_path):
            raise ValueError(f"出力ファイルが作成されませんでした: {temp_output_path}")

        output_file_size = os.path.getsize(temp_output_path)

        if output_file_size == 0:
            raise ValueError("出力ファイルのサイズが0バイトです")

        # 処理済み動画をバイトデータとして読み込み
        with open(temp_output_path, "rb") as f:
            output_video_bytes = f.read()

        # ファイルサイズの検証
        if len(output_video_bytes) != output_file_size:
            raise ValueError(
                f"ファイル読み込みサイズが不一致: 期待値={output_file_size}, 実際={len(output_video_bytes)}"
            )

        # 一時ファイルを削除
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)

        return output_video_bytes

    except Exception as e:
        # エラーが発生した場合、一時ファイルを削除
        if "temp_input_path" in locals() and os.path.exists(temp_input_path):
            os.unlink(temp_input_path)
        if "temp_output_path" in locals() and os.path.exists(temp_output_path):
            os.unlink(temp_output_path)

        raise Exception(f"フレームレート変更中にエラーが発生しました: {str(e)}")
