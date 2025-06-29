from datetime import datetime

from src.models.exceptions.service_exception import ServiceException
from src.models.types import SetUpUserRequest
from src.services.firebase.schemas.user_schema import UserSchema
from src.services.firebase.unit.firestore_flashcard import copy_flashcard_docs
from src.services.firebase.unit.firestore_user import create_user_doc


async def setup_user(
    _user: SetUpUserRequest,
) -> None:
    """
    DBにUserObjectをセットアップする関数
    Args:
        _user (SetUpUserRequest): 設定したいユーザー

    Raises:
        ServiceException: ユーザーのセットアップに失敗した場合
    """
    try:
        now = datetime.now()
        # TODO: デフォルトのフラッシュカードIDを最終版にカスタマイズ
        default_flashcard_ids = [
            "IMG5iGYPazwiqahf7VZL",
            "T4aaxF1o8BXtQHYBeocq",
            "eqtxae39Ibh8aAi8ZKV0",
            "uz3gQHMDtlsEwXPM9Ppj",
            "y5HMvmu2xt6FpnmAI4dl",
        ]
        new_flashcard_ids = await copy_flashcard_docs(
            flashcard_ids=default_flashcard_ids, user_id=_user.user_id
        )

        user_instance = UserSchema(
            email=_user.email,
            user_name=_user.user_name,
            flashcard_id_list=new_flashcard_ids,
            created_at=now,
            updated_at=now,
        )
        await create_user_doc(
            user_id=_user.user_id, user_instance=user_instance
        )
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"ユーザーのセットアップ中に予期せぬエラーが発生しました: {str(e)}",
            "general",
        )


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
            try:
                await setup_user(test_user)
                print(f"ユーザー '{test_user.email}' のセットアップに成功しました。")
            except ServiceException as se:
                print(
                    f"ユーザー '{test_user.email}' のセットアップに失敗しました。エラー: {se.message}"
                )
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {str(e)}")

    # 非同期関数を実行
    asyncio.run(main())
