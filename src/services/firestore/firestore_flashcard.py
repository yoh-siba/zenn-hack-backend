from src.schemas.flashcard_schema import FlashcardSchema
from src.config.settings import db
from typing import Optional, Tuple

def create_flashcard_doc(flashcard_instance: FlashcardSchema) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        doc_ref = db.collection("flashcards")
        new_doc = doc_ref.add(flashcard_instance.to_dict())
        return True, None, new_doc[1].id
    except Exception as e:
        error_message = f"フラッシュカードの作成中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None

def update_flashcard_doc(flashcard_id: str, flashcard_instance: FlashcardSchema) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update(flashcard_instance.to_dict())
        return True, None
    except Exception as e:
        error_message = f"フラッシュカードの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message

def read_flashcard_doc(flashcard_id: str) -> Tuple[Optional[FlashcardSchema], Optional[str]]:
    try:
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc = doc_ref.get()
        if doc.exists:
            return FlashcardSchema.from_dict(doc.to_dict()), None
        return None, "指定されたフラッシュカードが見つかりません"
    except Exception as e:
        error_message = f"フラッシュカードの読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return None, error_message

def read_flashcard_docs(flashcard_ids: list[str]) -> Tuple[list[FlashcardSchema], Optional[str]]:
    try:
        if not flashcard_ids:
            return [], "フラッシュカードIDが指定されていません"
            
        docs = db.collection("flashcards").where("__name__", "in", flashcard_ids).get()
        flashcards = []
        for doc in docs:
            flashcards.append(FlashcardSchema.from_dict(doc.to_dict()))
        return flashcards, None
    except Exception as e:
        error_message = f"フラッシュカードの一括読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return [], error_message 