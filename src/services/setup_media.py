from datetime import datetime
from typing import Optional, Tuple

from fastapi import HTTPException

from src.models.types import CreateMediaRequest
from src.services.firebase.schemas.comparison_schema import ComparisonSchema
from src.services.firebase.schemas.media_schema import MediaSchema
from src.services.firebase.unit.firestore_comparison import create_comparison_doc
from src.services.firebase.unit.firestore_flashcard import (
    update_flashcard_doc_on_comparison_id,
)
from src.services.firebase.unit.firestore_media import create_media_doc
from src.services.generate_and_store_image import generate_and_store_image
from src.services.google_ai.generate_prompt_for_imagen import generate_prompt_for_imagen


async def setup_media(
    create_media_request: CreateMediaRequest,
) -> Tuple[bool, Optional[str], Optional[str]]:
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
    """
    try:
        now = datetime.now()
        generated_prompt, prompt_token_count, candidates_token_count, total_token_count = await generate_prompt_for_imagen(create_media_request)
        if not generated_prompt:
            raise HTTPException(status_code=500, detail="プロンプトの生成に失敗しました。")
        image_url = ""
        if create_media_request.generation_type == "text-to-image":
            success, error, image_url = await generate_and_store_image(
                _prompt=generated_prompt,
                _person_generation="ALLOW_ADULT" if create_media_request.allow_generating_person else "DONT_ALLOW"
            )
            if not success:
                raise HTTPException(status_code=500, detail=error)
        elif create_media_request.generation_type == "text-to-video":
            ## TODO: 動画生成の実装
            raise NotImplementedError("動画生成はまだ実装されていません。")
        elif create_media_request.generation_type == "image-to-image":
            ## TODO: 画像から画像生成の実装
            raise NotImplementedError("画像から画像生成はまだ実装されていません。")
        success, error, media_id = await create_media_doc(
            media_instance=MediaSchema(
                flashcard_id=create_media_request.flashcard_id,
                meaning_id=create_media_request.meaning_id,
                media_urls=[image_url],
                generation_type="text-to-image",
                template_id=create_media_request.template_id,
                user_prompt=create_media_request.user_prompt,
                generated_prompt=generated_prompt,
                input_media_urls=create_media_request.input_media_urls,
                prompt_token_count=prompt_token_count,
                candidates_token_count=candidates_token_count,
                total_token_count=total_token_count,
                created_by=create_media_request.flashcard_id,
                created_at=now,
                updated_at=now
            )
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
            flashcard_id=create_media_request.flashcard_id,
            comparison_id=comparison_id
        )
        if not success:
            raise HTTPException(status_code=500, detail=error)
        return True, None, media_id
    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None