from datetime import datetime
from typing import Optional, Tuple

from src.config.settings import db
from src.services.firebase.schemas.flashcard_schema import (
    FlashcardSchema,
    FlashcardSchemaWithId,
)


async def create_flashcard_doc(
    flashcard_instance: FlashcardSchema,
) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        doc_ref = db.collection("flashcards")
        new_doc = doc_ref.add(flashcard_instance.to_dict())
        return True, None, new_doc[1].id
    except Exception as e:
        error_message = f"フラッシュカードの作成中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


async def update_flashcard_doc(
    flashcard_id: str, flashcard_instance: FlashcardSchema
) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update(flashcard_instance.to_dict())
        return True, None
    except Exception as e:
        error_message = f"フラッシュカードの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def read_flashcard_doc(
    flashcard_id: str,
) -> Tuple[Optional[FlashcardSchema], Optional[str]]:
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


async def read_flashcard_docs(
    flashcard_ids: list[str],
) -> Tuple[list[FlashcardSchemaWithId], Optional[str]]:
    try:
        if not flashcard_ids:
            return [], "フラッシュカードIDが指定されていません"

        docs = db.collection("flashcards").where("__name__", "in", flashcard_ids).get()
        flashcards = []
        for doc in docs:
            flashcard_instance = doc.to_dict()
            flashcard_instance["flashcard_id"] = doc.id
            flashcard = FlashcardSchemaWithId.from_dict(flashcard_instance)
            flashcards.append(flashcard)
        return flashcards, None
    except Exception as e:
        error_message = (
            f"フラッシュカードの一括読み込み中にエラーが発生しました: {str(e)}"
        )
        print(f"\n{error_message}")
        return [], error_message


async def update_flashcard_doc_on_memo(
    flashcard_id: str, memo: str
) -> Tuple[bool, Optional[str]]:
    try:
        now = datetime.now()
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update({"memo": memo, "updatedAt": now})
        return True, None
    except Exception as e:
        error_message = f"フラッシュカードの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def update_flashcard_doc_on_check_flag(
    flashcard_id: str, check_flag: bool
) -> Tuple[bool, Optional[str]]:
    try:
        now = datetime.now()
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update({"checkFlag": check_flag, "updatedAt": now})
        return True, None
    except Exception as e:
        error_message = f"フラッシュカードの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def update_flashcard_doc_on_using_meaning_id_list(
    flashcard_id: str, using_meaning_id_list: list[str]
) -> Tuple[bool, Optional[str]]:
    try:
        now = datetime.now()
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update({"usingMeaningIdList": using_meaning_id_list, "updatedAt": now})
        return True, None
    except Exception as e:
        error_message = f"フラッシュカードの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def update_flashcard_doc_on_comparison_id(
    flashcard_id: str, comparison_id: str
) -> Tuple[bool, Optional[str]]:
    try:
        now = datetime.now()
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update({"comparisonId": comparison_id, "updatedAt": now})
        return True, None
    except Exception as e:
        error_message = f"フラッシュカードの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def update_flashcard_doc_on_comparison_id_and_current_media(
    flashcard_id: str, comparison_id: str | None, current_media_id: str
) -> Tuple[bool, Optional[str]]:
    try:
        now = datetime.now()
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update(
            {
                "comparisonId": comparison_id,
                "currentMediaId": current_media_id,
                "updatedAt": now,
            }
        )
        return True, None
    except Exception as e:
        error_message = f"フラッシュカードの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def copy_flashcard_doc(
    flashcard_id: str,
    user_id: str,
) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        now = datetime.now()
        if not flashcard_id:
            return False, "フラッシュカードIDが指定されていません", None

        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc = doc_ref.get()
        if doc.exists:
            flashcard_instance = doc.to_dict()
            flashcard_instance["createdAt"] = now
            flashcard_instance["updatedAt"] = now
            flashcard_instance["createdBy"] = user_id
            new_doc = db.collection("flashcards").add(flashcard_instance)
            return True, None, new_doc[1].id
        else:
            return False, f"フラッシュカードID {flashcard_id} が見つかりません", None

    except Exception as e:
        error_message = f"フラッシュカードのコピー中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


async def copy_flashcard_docs(
    flashcard_ids: list[str], user_id: str
) -> Tuple[bool, Optional[str], list[str]]:
    try:
        now = datetime.now()
        if not flashcard_ids:
            return False, "フラッシュカードIDが指定されていません", []
        new_flashcard_ids = []
        for flashcard_id in flashcard_ids:
            doc_ref = db.collection("flashcards").document(flashcard_id)
            doc = doc_ref.get()
            if doc.exists:
                flashcard_instance = doc.to_dict()
                flashcard_instance["createdAt"] = now
                flashcard_instance["updatedAt"] = now
                flashcard_instance["createdBy"] = user_id
                new_doc = db.collection("flashcards").add(flashcard_instance)
                new_flashcard_ids.append(new_doc[1].id)
            else:
                return False, f"フラッシュカードID {flashcard_id} が見つかりません", []

        return True, None, new_flashcard_ids
    except Exception as e:
        error_message = f"フラッシュカードのコピー中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, []


async def read_flashcard_by_word_id(
    word_id: str,
) -> Tuple[Optional[FlashcardSchemaWithId], Optional[str]]:
    try:
        docs = (
            db.collection("flashcards")
            .where("wordId", "==", word_id)
            .where("createdBy", "==", "default")
            .get()
        )
        if not docs:
            return None, "指定された単語IDのフラッシュカードが見つかりません"

        flashcard_instance = docs[0].to_dict()
        flashcard_instance["flashcard_id"] = docs[0].id
        return FlashcardSchemaWithId.from_dict(flashcard_instance), None
    except Exception as e:
        error_message = f"フラッシュカードの読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return None, error_message
