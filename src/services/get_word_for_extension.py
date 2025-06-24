from typing import Optional, Tuple

from fastapi import HTTPException

from src.models.types import WordForExtensionResponse, WordResponse
from src.services.firebase.unit.firestore_flashcard import (
    read_flashcard_by_word_id,
)
from src.services.firebase.unit.firestore_meaning import read_meaning_docs
from src.services.firebase.unit.firestore_media import read_media_doc
from src.services.firebase.unit.firestore_word import get_word_id_by_word, read_word_doc


async def get_word_for_extension(
    word: str,
) -> Tuple[bool, Optional[str], Optional[WordForExtensionResponse]]:
    """Flashcardを取得する関数

    Args:
        user_id (str): ユーザーのID

    Returns:
        Tuple[bool, Optional[str], Optional[WordForExtensionResponse]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 取得したFlashcardのリスト（失敗時はNone）
    """
    try:
        word_id = await get_word_id_by_word(word)
        if not word_id:
            raise HTTPException(status_code=404, detail="Word not found")

        flashcard, error = await read_flashcard_by_word_id(word_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        word, error = await read_word_doc(word_id)
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
        word_for_extension_response = WordForExtensionResponse(
            message="setup word for extension successfully",
            flashcard_id=flashcard.flashcard_id,
            word=WordResponse.from_dict(word_response),
            meanings=meanings,
            media=media,
        )
        return True, None, word_for_extension_response
    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None
