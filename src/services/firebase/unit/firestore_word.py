from typing import Optional

from src.config.settings import db
from src.models.exceptions import ServiceException
from src.services.firebase.schemas.word_schema import WordSchema


async def create_word_doc(
    word_instance: WordSchema,
) -> str:
    try:
        print("word_instance.to_dict():", word_instance.to_dict())
        doc_ref = db.collection("words")
        new_doc = doc_ref.add(word_instance.to_dict())
        return new_doc[1].id
    except Exception as e:
        raise ServiceException(
            f"単語の作成中にエラーが発生しました: {str(e)}", "external_api"
        )


async def update_word_doc(word_id: str, word_instance: WordSchema) -> None:
    try:
        doc_ref = db.collection("words").document(word_id)
        doc_ref.update(word_instance.to_dict())
    except Exception as e:
        raise ServiceException(
            f"単語の更新中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_word_doc(word_id: str) -> Optional[WordSchema]:
    try:
        doc_ref = db.collection("words").document(word_id)
        doc = doc_ref.get()
        if doc.exists:
            word_instance = doc.to_dict()
            word_instance["word_id"] = doc.id
            return WordSchema.from_dict(word_instance)
        return None
    except Exception as e:
        raise ServiceException(
            f"単語の読み込み中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_word_docs(word_ids: list[str]) -> list[WordSchema]:
    try:
        if not word_ids:
            raise ServiceException("単語IDが指定されていません", "validation")

        docs = db.collection("words").where("__name__", "in", word_ids).get()
        words = []
        for doc in docs:
            words.append(WordSchema.from_dict(doc.to_dict()))
        return words
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"単語の一括読み込み中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_word_id_by_word(
    _word: str,
) -> Optional[str]:
    try:
        query = db.collection("words").where("word", "==", _word).limit(1)
        docs = query.get()
        if not docs:
            return None

        doc = docs[0]
        return doc.id

    except Exception as e:
        raise ServiceException(
            f"単語の読み込み中にエラーが発生しました: {str(e)}", "external_api"
        )


async def get_word_id_by_word(
    _word: str,
) -> Optional[str]:
    try:
        query = db.collection("words").where("word", "==", _word).limit(1)
        docs = query.get()
        if not docs:
            return None

        doc = docs[0]
        return doc.id

    except Exception as e:
        raise ServiceException(
            f"単語の読み込み中にエラーが発生しました: {str(e)}", "external_api"
        )
