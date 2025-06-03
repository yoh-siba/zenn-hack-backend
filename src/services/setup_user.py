from datetime import datetime
from typing import Optional, Tuple

from src.models.types import NewUser
from src.services.firebase.schemas.user_schema import UserSchema
from src.services.firebase.unit.firestore_user import create_user_doc


async def setup_user(
    _user: NewUser,
) -> Tuple[bool, Optional[str], Optional[str]]:
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
        print(f"\nユーザーのセットアップを開始: {_user.email}")
        now = datetime.now()
        user_instance = UserSchema(
            email=_user.email,
            display_name=_user.display_name,
           flashcard_id_list=[],
           created_at=now,
            updated_at=now,
        )
        success, error_message, user_id = await create_user_doc(user_instance)
        if not success:
            print(f"\nユーザーのセットアップに失敗しました: {error_message}")
            return False, error_message, None
        # ユーザーのセットアップが成功
        return True, None, user_id
    except Exception as e:
        error_message = f"ユーザーのセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


if __name__ == "__main__":
    import asyncio

    async def main():
        # テスト用のユーザー
        test_user_list = [
            NewUser(
                email="test1@example.com",
                display_name="test1",
            ),
        ]
        for test_user in test_user_list:
            print(f"\nユーザー '{test_user.email}' のセットアップ")
            success, error, user_id = await setup_user(test_user)
            if success:
                print(
                    f"ユーザー '{test_user.email}' のセットアップに成功しました。生成されたユーザーID: {user_id}"
                )
            else:
                print(f"ユーザー '{test_user.email}' のセットアップに失敗しました。エラー: {error}")

    # 非同期関数を実行
    asyncio.run(main())
