from typing import Optional, Tuple

from src.config.settings import db
from src.services.firebase.schemas.user_schema import UserSchema


async def create_user_doc(
    user_instance: UserSchema,
) -> Tuple[bool, Optional[str], Optional[str]]:
    try:
        doc_ref = db.collection("users")
        new_doc = doc_ref.add(user_instance.to_dict())
        return True, None, new_doc[1].id
    except Exception as e:
        error_message = f"ユーザーデータの作成中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


async def update_user_doc(
    user_id: str, user_instance: UserSchema
) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("users").document(user_id)
        doc_ref.update(user_instance.to_dict())
        return True, None
    except Exception as e:
        error_message = f"ユーザーデータの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


async def read_user_doc(user_id: str) -> Tuple[Optional[UserSchema], Optional[str]]:
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return UserSchema.from_dict(doc.to_dict()), None
        return None, "指定されたユーザーが見つかりません"
    except Exception as e:
        error_message = f"ユーザーデータの読み込み中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return None, error_message


async def read_user_docs(user_ids: list[str]) -> Tuple[list[UserSchema], Optional[str]]:
    try:
        if not user_ids:
            return [], "ユーザーIDが指定されていません"

        docs = await db.collection("users").where("__name__", "in", user_ids).get()
        users = []
        for doc in docs:
            users.append(UserSchema.from_dict(doc.to_dict()))
        return users, None
    except Exception as e:
        error_message = (
            f"ユーザーデータの一括読み込み中にエラーが発生しました: {str(e)}"
        )
        print(f"\n{error_message}")
        return [], error_message
