from typing import Optional

from src.config.settings import db
from src.models.exceptions import ServiceException
from src.models.types import MediaResponse
from src.services.firebase.schemas.media_schema import MediaSchema


async def create_media_doc(
    media_instance: MediaSchema,
) -> str:
    try:
        doc_ref = db.collection("medias")
        new_doc = doc_ref.add(media_instance.to_dict())
        return new_doc[1].id
    except Exception as e:
        raise ServiceException(
            f"メディアデータの作成中にエラーが発生しました: {str(e)}", "external_api"
        )


async def update_media_doc(media_id: str, media_instance: MediaSchema) -> None:
    try:
        doc_ref = db.collection("medias").document(media_id)
        doc_ref.update(media_instance.to_dict())
    except Exception as e:
        raise ServiceException(
            f"メディアデータの更新中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_media_doc(
    media_id: str,
) -> Optional[MediaResponse]:
    try:
        doc_ref = db.collection("medias").document(media_id)
        doc = doc_ref.get()
        if doc.exists:
            media_instance = doc.to_dict()
            media_instance["media_id"] = doc.id
            return MediaResponse.from_dict(media_instance)
        raise ServiceException("指定されたメディアデータが見つかりません", "not_found")
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"メディアデータの読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def read_media_docs(
    media_ids: list[str],
) -> list[MediaSchema]:
    try:
        if not media_ids:
            raise ServiceException("メディアデータIDが指定されていません", "validation")

        docs = await db.collection("medias").where("__name__", "in", media_ids).get()
        media_list = []
        for doc in docs:
            media_list.append(MediaSchema.from_dict(doc.to_dict()))
        return media_list
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"メディアデータの一括読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def update_media_doc_on_media_urls(media_id: str, media_urls: list[str]) -> None:
    try:
        doc_ref = db.collection("medias").document(media_id)
        doc_ref.update({"mediaUrls": media_urls})
    except Exception as e:
        raise ServiceException(
            f"メディアデータの更新中にエラーが発生しました: {str(e)}", "external_api"
        )
