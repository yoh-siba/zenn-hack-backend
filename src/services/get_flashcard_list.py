from typing import Optional, Tuple

from src.models.exceptions.service_exception import ServiceException
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
) -> list[FlashcardResponse]:
    """Flashcardを取得する関数

    Args:
        user_id (str): ユーザーのID

    Returns:
        list[FlashcardResponse]: 取得したFlashcardのリスト
        
    Raises:
        ServiceException: フラッシュカード取得に失敗した場合
    """
    try:
        user_instance = await read_user_doc(user_id)
        if not user_instance:
            raise ServiceException("ユーザーが見つかりません", "not_found")
        # 登録単語が0の場合はフロント側で処理（エラーではない）
        if len(user_instance.flashcard_id_list) == 0:
            return []
        flashcards = await read_flashcard_docs(user_instance.flashcard_id_list)
        if not flashcards:
            raise ServiceException("このユーザーのフラッシュカードが見つかりません", "not_found")
        flashcard_responses = []
        for flashcard in flashcards:
            word = await read_word_doc(flashcard.word_id)
            if not word:
                raise ServiceException(f"単語ID {flashcard.word_id} が見つかりません", "not_found")
            word_response = word.to_dict()
            word_response["wordId"] = flashcard.word_id
            meanings = await read_meaning_docs(flashcard.using_meaning_id_list)
            media = await read_media_doc(flashcard.current_media_id)
            if not media:
                raise ServiceException(f"メディアID {flashcard.current_media_id} が見つかりません", "not_found")
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
        return flashcard_responses
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"フラッシュカード一覧の取得中に予期せぬエラーが発生しました: {str(e)}", "general"
        )
