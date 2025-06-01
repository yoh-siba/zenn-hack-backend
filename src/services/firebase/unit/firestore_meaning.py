from typing import Optional, Tuple

from src.config.settings import db
from src.services.firebase.schemas.meaning_schema import MeaningSchema


async def create_meaning_doc(
    meaning_instance: MeaningSchema,
) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        doc_ref = db.collection("meanings")
        new_doc = doc_ref.add(meaning_instance.to_dict())
        return True, None, new_doc[1].id
    except Exception as e:
        error_message = f"意味の作成中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


async def update_meaning_doc(
    meaning_id: str, meaning_instance: MeaningSchema
) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("meanings").document(meaning_id)
        doc_ref.update(meaning_instance.to_dict())
        return True, None
    except Exception as e:
        error_message = f"意味の更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def read_meaning_doc(
    meaning_id: str,
) -> Tuple[Optional[MeaningSchema], Optional[str]]:
    try:
        doc_ref = db.collection("meanings").document(meaning_id)
        doc = doc_ref.get()
        if doc.exists:
            return MeaningSchema.from_dict(doc.to_dict()), None
        return None, "指定された意味が見つかりません"
    except Exception as e:
        error_message = f"意味の読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return None, error_message


async def read_meaning_docs(
    meaning_ids: list[str],
) -> Tuple[list[MeaningSchema], Optional[str]]:
    try:
        if not meaning_ids:
            return [], "意味IDが指定されていません"

        docs = (
            await db.collection("meanings").where("__name__", "in", meaning_ids).get()
        )
        meanings = []
        for doc in docs:
            meanings.append(MeaningSchema.from_dict(doc.to_dict()))
        return meanings, None
    except Exception as e:
        error_message = f"意味の一括読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return [], error_message
