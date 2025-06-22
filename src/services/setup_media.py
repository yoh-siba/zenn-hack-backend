from datetime import datetime
from typing import Optional, Tuple

from fastapi import HTTPException

from src.models.enums import part_of_speech_to_japanese
from src.models.types import CreateMediaRequest
from src.services.firebase.schemas.comparison_schema import ComparisonSchema
from src.services.firebase.schemas.media_schema import MediaSchema
from src.services.firebase.unit.cloud_storage_image import create_image_url_from_image
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
from src.services.google_ai.unit.request_imagen import request_imagen_text_to_image
from src.services.google_ai.unit.request_veo_text_to_video import (
    request_text_to_video,
)


async def setup_media(
    create_media_request: CreateMediaRequest,
) -> Tuple[bool, Optional[str], Optional[str], Optional[str], Optional[str]]:
    """画像（動画）部分を更新する関数
    使用するAIに応じて、何を生成するかが変わる
    mediaを作成（flashcardのobjectを利用）
    Comparisonを作成
    FlashcardのComparisonIdを設定

    Args:
        word (str): セットアップする単語

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 作成された単語のID（失敗時はNone）
            - 作成されたComparisonのID（失敗時はNone）
            - 作成されたメディアのURLリスト（失敗時はNone）
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
        )
        # 画像生成用のプロンプトを生成
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
            raise HTTPException(
                status_code=500, detail="プロンプトの生成に失敗しました。"
            )
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
        elif create_media_request.generation_type == "text-to-video":
            generated_medias = request_text_to_video(
                _prompt=generated_prompt,
                _person_generation="ALLOW_ADULT"
                if create_media_request.allow_generating_person
                else "DONT_ALLOW",
            )
            if not generated_medias:
                raise ValueError("No videos generated")
        elif create_media_request.generation_type == "text-to-image":
            ## TODO: テキストから画像生成の実装
            raise NotImplementedError("テキストから画像生成はまだ実装されていません。")
        success, error, media_id = await create_media_doc(
            media_instance=MediaSchema(
                flashcard_id=create_media_request.flashcard_id,
                meaning_id=create_media_request.meaning_id,
                media_urls=[],
                generation_type="text-to-image",
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
        )
        if not success:
            raise HTTPException(status_code=500, detail=error)
        # 生成された画像をFirestorageに保存して、URLを取得
        media_url_list = []
        for media in generated_medias:
            success, error, media_url = await create_image_url_from_image(
                media,
                f"{create_media_request.word}/{create_media_request.meaning_id}/{create_media_request.flashcard_id}/{media_id}.png",
            )
            if not success:
                raise ValueError("画像のURL取得に失敗しました", error)
            media_url_list.append(media_url)
        success, error = await update_media_doc_on_media_urls(
            media_id=media_id, media_urls=media_url_list
        )
        if not success:
            raise HTTPException(status_code=500, detail=error)
        success, error, comparison_id = await create_comparison_doc(
            comparison_instance=ComparisonSchema(
                flashcard_id=create_media_request.flashcard_id,
                old_media_id=create_media_request.old_media_id,
                new_media_id=media_id,
                is_selected_new="",
                created_at=now,
                updated_at=now,
            )
        )
        if not success:
            raise HTTPException(status_code=500, detail=error)
        success, error = await update_flashcard_doc_on_comparison_id(
            flashcard_id=create_media_request.flashcard_id, comparison_id=comparison_id
        )
        if not success:
            raise HTTPException(status_code=500, detail=error)
        return True, None, media_id, comparison_id, media_url_list
    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None, None, None
