from typing import Optional, Tuple

from src.config.settings import db
from src.services.firebase.schemas.user_schema import UserSchema


async def create_user_doc(
    user_id: str,
    user_instance: UserSchema,
) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("users")
        existing_docs = doc_ref.where("email", "==", user_instance.email).get()
        if existing_docs:
            error_message = "このメールアドレスは既に登録されています。"
            print(f"\n{error_message}")
            return False, error_message, None
        new_doc_ref = doc_ref.document(user_id)
        new_doc_ref.set(user_instance.to_dict())
        return True, None
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
            user_instance = UserSchema.from_dict(doc.to_dict())
            return user_instance, None
        return None, "指定されたユーザーは存在しません"
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


async def delete_user_doc(user_id: str) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            return False, "指定されたユーザーは存在しません"
        doc_ref.delete()
        return True, None
    except Exception as e:
        error_message = "ユーザーデータの削除中にエラーが発生しました"
        print(f"\n{error_message}: {str(e)}")
        return False, error_message


async def update_user_doc_add_using_flashcard(
    user_id: str, flashcard_id: str
) -> Tuple[bool, Optional[str]]:
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()
        if not doc.exists:
            return False, "指定されたユーザーは存在しません"

        user_data = doc.to_dict()
        flashcard_ids = user_data.get("flashcardIdList", [])
        if flashcard_id not in flashcard_ids:
            flashcard_ids.append(flashcard_id)
            user_data["flashcardIdList"] = flashcard_ids
            doc_ref.update(user_data)

        return True, None
    except Exception as e:
        error_message = f"ユーザーデータの更新中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message
