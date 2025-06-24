from typing import Optional, Tuple

from src.models.types import SetUpUserRequest
from src.services.firebase.unit.firestore_flashcard import copy_flashcard_doc
from src.services.firebase.unit.firestore_user import (
    update_user_doc_add_using_flashcard,
)


async def add_using_flashcard(
    _user_id: str,
    _flashcard_id: str,
) -> Tuple[bool, Optional[str]]:
    """
    DBにUserObjectをセットアップする関数
    Args:
        _user (UserSchema): 設定したいユーザー

    Returns:
        Tuple[bool, Optional[str]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 作成されたユーザーのID（失敗時はNone）
    """
    try:
        success, error_message, new_flashcard_id = await copy_flashcard_doc(
            flashcard_id=_flashcard_id
        )
        success, error_message = await update_user_doc_add_using_flashcard(
            user_id=_user_id, flashcard_id=new_flashcard_id
        )
        if not success:
            print(f"\nユーザーのセットアップに失敗しました: {error_message}")
            return False, error_message
        return True, None
    except Exception as e:
        error_message = f"ユーザーのセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message


if __name__ == "__main__":
    import asyncio

    async def main():
        # テスト用のユーザー
        test_user_list = [
            SetUpUserRequest(
                email="test2@example.com",
                user_name="test2",
            ),
        ]
        for test_user in test_user_list:
            print(f"\nユーザー '{test_user.email}' のセットアップ")
            success, error, user_id = await add_using_flashcard(test_user)
            if success:
                print(
                    f"ユーザー '{test_user.email}' のセットアップに成功しました。生成されたユーザーID: {user_id}"
                )
            else:
                print(
                    f"ユーザー '{test_user.email}' のセットアップに失敗しました。エラー: {error}"
                )

    # 非同期関数を実行
    asyncio.run(main())
