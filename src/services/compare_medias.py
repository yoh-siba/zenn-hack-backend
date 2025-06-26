from src.models.exceptions import ServiceException
from src.models.types import CompareMediasRequest
from src.services.firebase.unit.firestore_comparison import (
    update_comparison_doc_on_is_selected_new,
)
from src.services.firebase.unit.firestore_flashcard import (
    update_flashcard_doc_on_comparison_id_and_current_media,
)


async def compare_medias(
    compare_medias_request: CompareMediasRequest,
) -> None:
    """比較結果を反映する関数
    currentMediaId:newを選ばれたら新しいメディアを生成し、oldを選ばれたらそのまま
    comparisonIdはnullに変える
    Comparisonのis_selected_newを更新する

    Args:
        compare_medias_request (CompareMediasRequest): 比較結果リクエスト

    Raises:
        ServiceException: 比較結果の更新に失敗した場合
    """
    try:
        await update_flashcard_doc_on_comparison_id_and_current_media(
            flashcard_id=compare_medias_request.flashcard_id,
            comparison_id=None,
            current_media_id=compare_medias_request.new_media_id
            if compare_medias_request.is_selected_new
            else compare_medias_request.old_media_id,
        )
        await update_comparison_doc_on_is_selected_new(
            comparison_id=compare_medias_request.comparison_id,
            is_selected_new=compare_medias_request.is_selected_new,
        )
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"比較結果の更新中にエラーが発生しました: {str(e)}", "general"
        )
