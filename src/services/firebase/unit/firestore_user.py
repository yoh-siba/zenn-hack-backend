from typing import Optional

from src.config.settings import db
from src.models.exceptions import ServiceException
from src.services.firebase.schemas.user_schema import UserSchema


async def create_user_doc(
    user_id: str,
    user_instance: UserSchema,
) -> None:
    try:
        doc_ref = db.collection("users")
        existing_docs = doc_ref.where("email", "==", user_instance.email).get()
        if existing_docs:
            raise ServiceException(
                "このメールアドレスは既に登録されています", "conflict"
            )
        new_doc_ref = doc_ref.document(user_id)
        new_doc_ref.set(user_instance.to_dict())
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"ユーザーデータの作成中にエラーが発生しました: {str(e)}", "external_api"
        )


async def update_user_doc(user_id: str, user_instance: UserSchema) -> None:
    try:
        doc_ref = db.collection("users").document(user_id)
        doc_ref.update(user_instance.to_dict())
    except Exception as e:
        raise ServiceException(
            f"ユーザーデータの更新中にエラーが発生しました: {str(e)}", "external_api"
        )


async def read_user_doc(user_id: str) -> Optional[UserSchema]:
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            user_instance = UserSchema.from_dict(doc.to_dict())
            return user_instance
        return None
    except Exception as e:
        raise ServiceException(
            f"ユーザーデータの読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def read_user_docs(user_ids: list[str]) -> list[UserSchema]:
    try:
        if not user_ids:
            raise ServiceException("ユーザーIDが指定されていません", "validation")

        docs = await db.collection("users").where("__name__", "in", user_ids).get()
        users = []
        for doc in docs:
            users.append(UserSchema.from_dict(doc.to_dict()))
        return users
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"ユーザーデータの一括読み込み中にエラーが発生しました: {str(e)}",
            "external_api",
        )


async def delete_user_doc(user_id: str) -> None:
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise ServiceException("指定されたユーザーは存在しません", "not_found")
        doc_ref.delete()
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"ユーザーデータの削除中にエラーが発生しました: {str(e)}", "external_api"
        )


async def update_user_doc_add_using_flashcard(user_id: str, flashcard_id: str) -> None:
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise ServiceException("指定されたユーザーは存在しません", "not_found")

        user_data = doc.to_dict()
        flashcard_ids = user_data.get("flashcardIdList", [])
        if flashcard_id not in flashcard_ids:
            flashcard_ids.append(flashcard_id)
            user_data["flashcardIdList"] = flashcard_ids
            doc_ref.update(user_data)
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"ユーザーデータの更新中にエラーが発生しました: {str(e)}", "external_api"
        )
