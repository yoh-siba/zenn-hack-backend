from typing import Optional, Tuple

from fastapi import HTTPException

from src.models.types import FlashcardResponse, WordResponse
from src.services.firebase.unit.firestore_flashcard import (
    read_flashcard_docs,
)
from src.services.firebase.unit.firestore_meaning import read_meaning_docs
from src.services.firebase.unit.firestore_media import read_media_doc
from src.services.firebase.unit.firestore_user import read_user_doc
from src.services.firebase.unit.firestore_word import read_word_doc


async def get_flashcard_list(
    user_id: str,
) -> Tuple[bool, Optional[str], Optional[FlashcardResponse]]:
    """Flashcardを取得する関数

    Args:
        user_id (str): ユーザーのID

    Returns:
        Tuple[bool, Optional[str], Optional[FlashcardResponse]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 取得したFlashcardのリスト（失敗時はNone）
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
        flashcard_responses = []
        for flashcard in flashcards:
            word, error = await read_word_doc(flashcard.word_id)
            if error:
                raise HTTPException(status_code=500, detail=error)
            word_response = word.to_dict()
            word_response["wordId"] = flashcard.word_id
            meanings, error = await read_meaning_docs(flashcard.using_meaning_id_list)
            if error:
                raise HTTPException(status_code=500, detail=error)
            media, error = await read_media_doc(flashcard.current_media_id)
            if error:
                raise HTTPException(status_code=500, detail=error)
            flashcard = FlashcardResponse(
                flashcard_id=flashcard.flashcard_id,
                word=WordResponse.from_dict(word_response),
                meanings=meanings,
                media=media,
                memo=flashcard.memo,
                version=flashcard.version,
                check_flag=flashcard.check_flag,
            )
            flashcard_responses.append(flashcard)
        return True, None, flashcard_responses
    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None
