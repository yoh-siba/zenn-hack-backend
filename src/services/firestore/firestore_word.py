from src.schemas.words_schema import WordsSchema
from src.config.settings import db
from typing import Optional, Tuple

def create_word_schema(word_instance: WordsSchema) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        doc_ref = db.collection("words")
        new_doc = doc_ref.add(word_instance.to_dict())
        return True, None, new_doc[1].id
    except Exception as e:
        error_message = f"単語の作成中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None

def update_word_schema(word_id: str, word_instance: WordsSchema) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("words").document(word_id)
        doc_ref.update(word_instance.to_dict())
        return True, None
    except Exception as e:
        error_message = f"単語の更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message

def read_word_schema(word_id: str) -> Tuple[Optional[WordsSchema], Optional[str]]:
    try:
        doc_ref = db.collection("words").document(word_id)
        doc = doc_ref.get()
        if doc.exists:
            return WordsSchema.from_dict(doc.to_dict()), None
        return None, "指定された単語が見つかりません"
    except Exception as e:
        error_message = f"単語の読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return None, error_message