from typing import Optional, Tuple

from fastapi import HTTPException

from src.models.types import GetNotComparedMediaResponse
from src.services.firebase.unit.firestore_comparison import read_comparison_doc
from src.services.firebase.unit.firestore_flashcard import (
    read_flashcard_docs,
)
from src.services.firebase.unit.firestore_media import read_media_doc
from src.services.firebase.unit.firestore_user import read_user_doc


async def get_not_compared_media_list(
    user_id: str,
) -> Tuple[bool, Optional[str], Optional[list[GetNotComparedMediaResponse]]]:
    """Flashcardを取得する関数

    Args:
        user_id (str): ユーザーのID

    Returns:
        Tuple[bool, Optional[str], Optional[FlashcardResponse]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 取得したMediaのリスト（失敗時はNone）
    """
    try:
        user_instance, error = await read_user_doc(user_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not user_instance:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        # 登録単語が0の場合はフロント側で処理（エラーではない）
        if len(user_instance.flashcard_id_list) == 0:
            return []
        flashcards, error = await read_flashcard_docs(user_instance.flashcard_id_list)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not flashcards:
            raise HTTPException(
                status_code=404, detail="このユーザーのフラッシュカードが見つかりません"
            )
        media_responses = []
        for flashcard in flashcards:
            if not flashcard.comparison_id:
                continue  # 比較IDがない場合はスキップ
            # 比較IDがある場合のみ処理
            comparison, error = await read_comparison_doc(flashcard.comparison_id)
            if error:
                raise HTTPException(status_code=500, detail=error)
            new_media, error = await read_media_doc(comparison.new_media_id)
            if error:
                raise HTTPException(status_code=500, detail=error)
            media_response = GetNotComparedMediaResponse(
                flashcard_id=flashcard.flashcard_id,
                comparison_id=flashcard.comparison_id,
                new_media_urls=new_media.media_urls,
            )
            media_responses.append(media_response)
        return True, None, media_responses
    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None
