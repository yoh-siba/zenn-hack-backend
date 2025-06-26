from datetime import datetime
from io import BytesIO
from typing import Tuple

import requests
from PIL import Image

from src.models.enums import part_of_speech_to_japanese
from src.models.exceptions import ServiceException
from src.models.types import CreateMediaRequest, SetupMediaResponse
from src.services.firebase.schemas.comparison_schema import ComparisonSchema
from src.services.firebase.schemas.media_schema import MediaSchema
from src.services.firebase.unit.cloud_storage_image import (
    create_image_url_from_image,
    create_video_url_from_video,
)
from src.services.firebase.unit.firestore_comparison import create_comparison_doc
from src.services.firebase.unit.firestore_flashcard import (
    update_flashcard_doc_on_comparison_id,
)
from src.services.firebase.unit.firestore_media import (
    create_media_doc,
    update_media_doc_on_media_urls,
)
from src.services.google_ai.generate_modified_other_settings import (
    generate_modified_other_settings,
)
from src.services.google_ai.generate_prompt_for_imagen import generate_prompt_for_imagen
from src.services.google_ai.unit.request_image_editing import (
    request_gemini_image_to_image,
)
from src.services.google_ai.unit.request_imagen import request_imagen_text_to_image
from src.services.google_ai.unit.request_veo import (
    request_image_to_video,
    request_text_to_video,
)
from src.services.video.reduce_fps import reduce_fps_to_10


async def setup_media(
    create_media_request: CreateMediaRequest,
) -> SetupMediaResponse:
    """画像（動画）部分を更新する関数
    使用するAIに応じて、何を生成するかが変わる
    mediaを作成（flashcardのobjectを利用）
    Comparisonを作成
    FlashcardのComparisonIdを設定

    Args:
        create_media_request (CreateMediaRequest): メディア作成リクエスト

    Returns:
        SetupMediaResponse: メディアID、比較ID、メディアURLリストを含むレスポンス

    Raises:
        ServiceException: メディア作成に失敗した場合
    """
    try:
        now = datetime.now()
        # 「その他」の設定部分をプロンプトの形に成形（ない場合も対応済）
        modified_other_settings_result = generate_modified_other_settings(
            other_settings=create_media_request.other_settings
        )

        modified_other_settings = (
            modified_other_settings_result.generated_other_settings
        )
        prompt_token_count_o = modified_other_settings_result.prompt_token_count
        candidates_token_count_o = modified_other_settings_result.candidates_token_count
        total_token_count_o = modified_other_settings_result.total_token_count

        joined_user_prompt = "\n".join(
            [create_media_request.user_prompt, modified_other_settings]
        )
        replaced_prompt = (
            joined_user_prompt.replace("{word}", create_media_request.word)
            .replace("{pos}", part_of_speech_to_japanese(create_media_request.pos))
            .replace("{translation}", create_media_request.translation)
            .replace("{example_jpn}", create_media_request.example_jpn)
            .replace("{explanation}", create_media_request.explanation)
            .replace("{modified_other_settings}", modified_other_settings)
        )  # 画像生成用のプロンプトを生成
        result = generate_prompt_for_imagen(_content=replaced_prompt)
        (
            generated_prompt,
            prompt_token_count_p,
            candidates_token_count_p,
            total_token_count_p,
        ) = (
            result.generated_prompt,
            result.prompt_token_count,
            result.candidates_token_count,
            result.total_token_count,
        )

        if not generated_prompt:
            raise ServiceException("プロンプトの生成に失敗しました", "external_api")

        generated_medias = []
        if create_media_request.generation_type == "text-to-image":
            generated_medias = request_imagen_text_to_image(
                _prompt=generated_prompt,
                _number_of_images=1,
                _aspect_ratio="1:1",  # アスペクト比を1:1に設定
                _person_generation="ALLOW_ADULT"
                if create_media_request.allow_generating_person
                else "DONT_ALLOW",  # 人物生成を許可しない
            )
            if not generated_medias:
                raise ValueError("No images generated")
        elif create_media_request.generation_type == "image-to-image":
            # 入力画像を取得
            if not create_media_request.input_media_urls:
                raise ValueError("image-to-image requires input_media_urls")

            response = requests.get(create_media_request.input_media_urls[0])
            input_image = Image.open(BytesIO(response.content))

            # 画像編集を実行
            generated_image = request_gemini_image_to_image(
                _prompt=generated_prompt,
                _image=input_image,
            )
            generated_medias = [generated_image]
            if not generated_medias:
                raise ValueError("No images generated")
        elif (
            create_media_request.generation_type == "text-to-video"
            or create_media_request.generation_type == "image-to-video"
        ):
            generated_video = (
                request_text_to_video(
                    _prompt=generated_prompt,
                    _person_generation="ALLOW_ADULT"
                    if create_media_request.allow_generating_person
                    else "DONT_ALLOW",
                )
                if create_media_request.generation_type == "text-to-video"
                else request_image_to_video(
                    _prompt=generated_prompt,
                    _image_url=create_media_request.input_media_urls[0],
                    _person_generation="ALLOW_ADULT"
                    if create_media_request.allow_generating_person
                    else "DONT_ALLOW",
                )
            )
            if not generated_video:
                raise ValueError(
                    "No videos generated"
                )  # 生成された動画のフレームレートを10fpsに変更
            try:
                processed_video_bytes = reduce_fps_to_10(generated_video)
                generated_medias = [processed_video_bytes]
            except Exception as e:
                # エラー時は元の動画を使用
                generated_medias = [generated_video]
        else:
            raise NotImplementedError(
                f"生成タイプ '{create_media_request.generation_type}' はサポートされていません。"
            )

        media_id = await create_media_doc(
            media_instance=MediaSchema(
                flashcard_id=create_media_request.flashcard_id,
                meaning_id=create_media_request.meaning_id,
                media_urls=[],
                generation_type=create_media_request.generation_type,
                template_id=create_media_request.template_id,
                user_prompt=create_media_request.user_prompt,
                generated_prompt=generated_prompt,
                input_media_urls=create_media_request.input_media_urls,
                prompt_token_count=prompt_token_count_o + prompt_token_count_p,
                candidates_token_count=candidates_token_count_o
                + candidates_token_count_p,
                total_token_count=total_token_count_o + total_token_count_p,
                created_by=create_media_request.flashcard_id,
                created_at=now,
                updated_at=now,
            )
        )  # 生成されたメディアをFirestorageに保存して、URLを取得
        media_url_list = []
        for media in generated_medias:
            if (
                create_media_request.generation_type == "text-to-video"
                or create_media_request.generation_type == "image-to-video"
            ):
                # 動画の場合
                media_url = await create_video_url_from_video(
                    media,
                    f"{create_media_request.word}/{create_media_request.meaning_id}/{create_media_request.flashcard_id}/{media_id}.mp4",
                )
            else:
                # 画像の場合
                media_url = await create_image_url_from_image(
                    media,
                    f"{create_media_request.word}/{create_media_request.meaning_id}/{create_media_request.flashcard_id}/{media_id}.png",
                )
            media_url_list.append(media_url)
        await update_media_doc_on_media_urls(
            media_id=media_id, media_urls=media_url_list
        )
        comparison_id = await create_comparison_doc(
            comparison_instance=ComparisonSchema(
                flashcard_id=create_media_request.flashcard_id,
                old_media_id=create_media_request.old_media_id,
                new_media_id=media_id,
                is_selected_new="",
                created_at=now,
                updated_at=now,
            )
        )
        await update_flashcard_doc_on_comparison_id(
            flashcard_id=create_media_request.flashcard_id, comparison_id=comparison_id
        )
        return SetupMediaResponse(
            comparison_id=comparison_id,
            media_id=media_id,
            media_urls=media_url_list
        )
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"メディア作成中にエラーが発生しました: {str(e)}", "general"
        )
