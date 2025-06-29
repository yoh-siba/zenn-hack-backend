from datetime import datetime
from typing import Optional

from src.config.settings import db
from src.models.exceptions import ServiceException
from src.services.firebase.schemas.flashcard_schema import (
    FlashcardSchema,
    FlashcardSchemaWithId,
)


async def create_flashcard_doc(
    flashcard_instance: FlashcardSchema,
) -> str:
    try:
        doc_ref = db.collection("flashcards")
        new_doc = doc_ref.add(flashcard_instance.to_dict())
        return new_doc[1].id
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードの作成中にエラーが発生しました: {str(e)}", "external_api"
        )


async def update_flashcard_doc(
    flashcard_id: str, flashcard_instance: FlashcardSchema
) -> None:
    try:
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update(flashcard_instance.to_dict())
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードの更新中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_flashcard_doc(
    flashcard_id: str,
) -> Optional[FlashcardSchema]:
    try:
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc = doc_ref.get()
        if doc.exists:
            return FlashcardSchema.from_dict(doc.to_dict())
        raise ServiceException(
            "指定されたフラッシュカードが見つかりません", "not_found"
        )
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードの読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def read_flashcard_docs(
    flashcard_ids: list[str],
) -> list[FlashcardSchemaWithId]:
    try:
        if not flashcard_ids:
            raise ServiceException(
                "フラッシュカードIDが指定されていません", "validation"
            )

        docs = db.collection("flashcards").where("__name__", "in", flashcard_ids).get()
        flashcards = []
        for doc in docs:
            flashcard_instance = doc.to_dict()
            flashcard_instance["flashcard_id"] = doc.id
            flashcard = FlashcardSchemaWithId.from_dict(flashcard_instance)
            flashcards.append(flashcard)
        return flashcards
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードの一括読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def update_flashcard_doc_on_memo(flashcard_id: str, memo: str) -> None:
    try:
        now = datetime.now()
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update({"memo": memo, "updatedAt": now})
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードのメモ更新中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def update_flashcard_doc_on_check_flag(
    flashcard_id: str, check_flag: bool
) -> None:
    try:
        now = datetime.now()
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update({"checkFlag": check_flag, "updatedAt": now})
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードのチェックフラグ更新中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def update_flashcard_doc_on_using_meaning_id_list(
    flashcard_id: str, using_meaning_id_list: list[str]
) -> None:
    try:
        now = datetime.now()
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update({"usingMeaningIdList": using_meaning_id_list, "updatedAt": now})
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードの意味ID更新中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def update_flashcard_doc_on_comparison_id(
    flashcard_id: str, comparison_id: str
) -> None:
    try:
        now = datetime.now()
        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc_ref.update({"comparisonId": comparison_id, "updatedAt": now})
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードの更新中にエラーが発生しました: {str(e)}", "external_api"
        )


async def update_flashcard_doc_on_comparison_id_and_current_media(
    flashcard_id: str, comparison_id: str | None, current_media_id: str
) -> None:
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
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードの比較ID・メディアID更新中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def copy_flashcard_doc(
    flashcard_id: str,
    user_id: str,
) -> str:
    try:
        now = datetime.now()
        if not flashcard_id:
            raise ServiceException(
                "フラッシュカードIDが指定されていません", "validation"
            )

        doc_ref = db.collection("flashcards").document(flashcard_id)
        doc = doc_ref.get()
        if doc.exists:
            flashcard_instance = doc.to_dict()
            flashcard_instance["createdAt"] = now
            flashcard_instance["updatedAt"] = now
            flashcard_instance["createdBy"] = user_id
            new_doc = db.collection("flashcards").add(flashcard_instance)
            return new_doc[1].id
        else:
            raise ServiceException(
                f"フラッシュカードID {flashcard_id} が見つかりません", "not_found"
            )

    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードのコピー中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def copy_flashcard_docs(flashcard_ids: list[str], user_id: str) -> list[str]:
    try:
        now = datetime.now()
        if not flashcard_ids:
            raise ServiceException(
                "フラッシュカードIDが指定されていません", "validation"
            )
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
                raise ServiceException(
                    f"フラッシュカードID {flashcard_id} が見つかりません", "not_found"
                )

        return new_flashcard_ids
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードの一括コピー中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def read_flashcard_by_word_id(
    word_id: str,
) -> Optional[FlashcardSchemaWithId]:
    try:
        docs = (
            db.collection("flashcards")
            .where("wordId", "==", word_id)
            .where("createdBy", "==", "default")
            .get()
        )
        if not docs:
            raise ServiceException(
                "指定された単語IDのフラッシュカードが見つかりません", "not_found"
            )

        flashcard_instance = docs[0].to_dict()
        flashcard_instance["flashcard_id"] = docs[0].id
        return FlashcardSchemaWithId.from_dict(flashcard_instance)
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"単語IDによるフラッシュカード読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )
