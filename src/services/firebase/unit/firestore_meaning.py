from typing import Optional

from src.config.settings import db
from src.models.exceptions import ServiceException
from src.models.types import MeaningResponse
from src.services.firebase.schemas.meaning_schema import MeaningSchema


async def create_meaning_doc(
    meaning_instance: MeaningSchema,
) -> str:
    try:
        doc_ref = db.collection("meanings")
        new_doc = doc_ref.add(meaning_instance.to_dict())
        return new_doc[1].id
    except Exception as e:
        raise ServiceException(
            f"意味の作成中にエラーが発生しました: {str(e)}", "external_api"
        )


async def update_meaning_doc(meaning_id: str, meaning_instance: MeaningSchema) -> None:
    try:
        doc_ref = db.collection("meanings").document(meaning_id)
        doc_ref.update(meaning_instance.to_dict())
    except Exception as e:
        raise ServiceException(
            f"意味の更新中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_meaning_doc(
    meaning_id: str,
) -> Optional[MeaningSchema]:
    try:
        doc_ref = db.collection("meanings").document(meaning_id)
        doc = doc_ref.get()
        if doc.exists:
            return MeaningSchema.from_dict(doc.to_dict())
        return None
    except Exception as e:
        raise ServiceException(
            f"意味の読み込み中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_meaning_docs(
    meaning_ids: list[str],
) -> list[MeaningResponse]:
    try:
        if not meaning_ids:
            raise ServiceException("意味IDが指定されていません", "validation")
        docs = db.collection("meanings").where("__name__", "in", meaning_ids).get()
        meanings = []
        for doc in docs:
            meaning_instance = doc.to_dict()
            meaning_instance["meaning_id"] = doc.id
            meanings.append(MeaningResponse.from_dict(meaning_instance))
        return meanings
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"意味の一括読み込み中にエラーが発生しました: {str(e)}", "external_api"
        )
