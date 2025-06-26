from src.models.exceptions import ServiceException
from src.models.types import WordForExtensionResponse, WordResponse
from src.services.firebase.unit.firestore_flashcard import (
    read_flashcard_by_word_id,
)
from src.services.firebase.unit.firestore_meaning import read_meaning_docs
from src.services.firebase.unit.firestore_media import read_media_doc
from src.services.firebase.unit.firestore_word import get_word_id_by_word, read_word_doc


async def get_word_for_extension(
    word: str,
) -> WordForExtensionResponse:
    """拡張機能用の単語情報を取得する関数

    Args:
        word (str): 検索する単語

    Returns:
        WordForExtensionResponse: 単語情報と関連データ

    Raises:
        ServiceException: 単語が見つからない場合、または処理に失敗した場合
    """
    try:
        word_id = await get_word_id_by_word(word)
        if not word_id:
            raise ServiceException("指定された単語が見つかりません", "not_found")

        flashcard = await read_flashcard_by_word_id(word_id)
        if not flashcard:
            raise ServiceException("指定された単語IDのフラッシュカードが見つかりません", "not_found")
        word = await read_word_doc(word_id)
        if not word:
            raise ServiceException("指定された単語が見つかりません", "not_found")
        word_response = word.to_dict()
        word_response["wordId"] = flashcard.word_id
        meanings = await read_meaning_docs(flashcard.using_meaning_id_list)
        media = await read_media_doc(flashcard.current_media_id)
        if not media:
            raise ServiceException("指定されたメディアが見つかりません", "not_found")
        word_for_extension_response = WordForExtensionResponse(
            message="setup word for extension successfully",
            flashcard_id=flashcard.flashcard_id,
            word=WordResponse.from_dict(word_response),
            meanings=meanings,
            media=media,
        )
        return word_for_extension_response
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"単語詳細情報の取得中にエラーが発生しました: {str(e)}", "general"
        )
