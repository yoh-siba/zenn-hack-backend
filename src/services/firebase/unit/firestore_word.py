from typing import Optional, Tuple

from src.config.settings import db
from src.services.firebase.schemas.word_schema import WordSchema


async def create_word_doc(
    word_instance: WordSchema,
) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        doc_ref = db.collection("words")
        new_doc = doc_ref.add(word_instance.to_dict())
        return True, None, new_doc[1].id
    except Exception as e:
        error_message = f"単語の作成中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


async def update_word_doc(
    word_id: str, word_instance: WordSchema
) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("words").document(word_id)
        doc_ref.update(word_instance.to_dict())
        return True, None
    except Exception as e:
        error_message = f"単語の更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def read_word_doc(word_id: str) -> Tuple[Optional[WordSchema], Optional[str]]:
    try:
        doc_ref = db.collection("words").document(word_id)
        doc = doc_ref.get()
        if doc.exists:
            return WordSchema.from_dict(doc.to_dict()), None
        return None, "指定された単語が見つかりません"
    except Exception as e:
        error_message = f"単語の読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return None, error_message


async def read_word_docs(word_ids: list[str]) -> Tuple[list[WordSchema], Optional[str]]:
    try:
        if not word_ids:
            return [], "単語IDが指定されていません"

        docs = db.collection("words").where("__name__", "in", word_ids).get()
        words = []
        for doc in docs:
            words.append(WordSchema.from_dict(doc.to_dict()))
        return words, None
    except Exception as e:
        error_message = f"単語の一括読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return [], error_message
