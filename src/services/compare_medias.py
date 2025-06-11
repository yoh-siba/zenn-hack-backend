from typing import Optional, Tuple

from fastapi import HTTPException

from src.models.types import CompareMediasRequest
from src.services.firebase.unit.firestore_comparison import (
    update_comparison_doc_on_is_selected_new,
)
from src.services.firebase.unit.firestore_flashcard import (
    update_flashcard_doc_on_comparison_id_and_current_media,
)


async def compare_medias(
    compare_media_request: CompareMediasRequest,
) -> Tuple[bool, Optional[str]]:
    """比較結果を反映する関数
    currentMediaId:newを選ばれたら新しいメディアを生成し、oldを選ばれたらそのまま
    comparisonIdはnullに変える
    Comparisonのis_selected_newは
    """
    try:
        success, error = await update_flashcard_doc_on_comparison_id_and_current_media(
            flashcard_id=compare_media_request.flashcard_id,
            comparison_id=None,
            current_media_id=compare_media_request.new_media_id if compare_media_request.is_selected_new else compare_media_request.old_media_id,
        )
        if not success:
            raise HTTPException(status_code=500, detail=error)
        success, error = await update_comparison_doc_on_is_selected_new(
            comparison_id=compare_media_request.comparison_id,
            is_selected_new=compare_media_request.is_selected_new)
        if not success:
            raise HTTPException(status_code=500, detail=error)  
        return True, None
    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message