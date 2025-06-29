from src.models.exceptions import ServiceException
from src.models.types import GetNotComparedMediaResponse
from src.services.firebase.unit.firestore_comparison import read_comparison_doc
from src.services.firebase.unit.firestore_flashcard import (
    read_flashcard_docs,
)
from src.services.firebase.unit.firestore_media import read_media_doc
from src.services.firebase.unit.firestore_user import read_user_doc


async def get_not_compared_media_list(
    user_id: str,
) -> list[GetNotComparedMediaResponse]:
    """未比較メディア一覧を取得する関数

    Args:
        user_id (str): ユーザーのID

    Returns:
        list[GetNotComparedMediaResponse]: 未比較メディアのリスト

    Raises:
        ServiceException: ユーザーが見つからない場合、または処理に失敗した場合
    """
    try:
        user_instance = await read_user_doc(user_id)
        if not user_instance:
            raise ServiceException("指定されたユーザーは存在しません", "not_found")
        # 登録単語が0の場合はフロント側で処理（エラーではない）
        if len(user_instance.flashcard_id_list) == 0:
            return []
        flashcards = await read_flashcard_docs(user_instance.flashcard_id_list)
        if not flashcards:
            raise ServiceException(
                "このユーザーのフラッシュカードが見つかりません", "not_found"
            )
        media_responses = []
        for flashcard in flashcards:
            if not flashcard.comparison_id:
                continue  # 比較IDがない場合はスキップ
            # 比較IDがある場合のみ処理
            comparison = await read_comparison_doc(flashcard.comparison_id)
            if not comparison:
                raise ServiceException(f"比較ID {flashcard.comparison_id} が見つかりません", "not_found")
            new_media = await read_media_doc(comparison.new_media_id)
            if not new_media:
                raise ServiceException(f"メディアID {comparison.new_media_id} が見つかりません", "not_found")
            media_response = GetNotComparedMediaResponse(
                flashcard_id=flashcard.flashcard_id,
                comparison_id=flashcard.comparison_id,
                new_media_id=new_media.media_id,
                new_media_urls=new_media.media_urls,
            )
            media_responses.append(media_response)
        return media_responses
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"未比較メディア一覧の取得中にエラーが発生しました: {str(e)}", "general"
        )
