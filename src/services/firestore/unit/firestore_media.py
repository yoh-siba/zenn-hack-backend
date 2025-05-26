from typing import Optional, Tuple

from src.config.settings import db
from src.services.firestore.schemas.media_schema import MediaSchema


async def create_media_doc(
    media_instance: MediaSchema,
) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        doc_ref = db.collection("media")
        new_doc = doc_ref.add(media_instance.to_dict())
        return True, None, new_doc[1].id
    except Exception as e:
        error_message = f"メディアデータの作成中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


async def update_media_doc(
    media_id: str, media_instance: MediaSchema
) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("media").document(media_id)
        doc_ref.update(media_instance.to_dict())
        return True, None
    except Exception as e:
        error_message = f"メディアデータの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def read_media_doc(media_id: str) -> Tuple[Optional[MediaSchema], Optional[str]]:
    try:
        doc_ref = db.collection("media").document(media_id)
        doc = doc_ref.get()
        if doc.exists:
            return MediaSchema.from_dict(doc.to_dict()), None
        return None, "指定されたメディアデータが見つかりません"
    except Exception as e:
        error_message = f"メディアデータの読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return None, error_message


async def read_media_docs(
    media_ids: list[str],
) -> Tuple[list[MediaSchema], Optional[str]]:
    try:
        if not media_ids:
            return [], "メディアデータIDが指定されていません"

        docs = await db.collection("media").where("__name__", "in", media_ids).get()
        media_list = []
        for doc in docs:
            media_list.append(MediaSchema.from_dict(doc.to_dict()))
        return media_list, None
    except Exception as e:
        error_message = (
            f"メディアデータの一括読み込み中にエラーが発生しました: {str(e)}"
        )
        print(f"\n{error_message}")
        return [], error_message
