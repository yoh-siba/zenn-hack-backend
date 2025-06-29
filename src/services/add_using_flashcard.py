from src.models.exceptions import ServiceException
from src.models.types import SetUpUserRequest
from src.services.firebase.unit.firestore_flashcard import copy_flashcard_doc
from src.services.firebase.unit.firestore_user import (
    update_user_doc_add_using_flashcard,
)


async def add_using_flashcard(
    _user_id: str,
    _flashcard_id: str,
) -> None:
    """
    ユーザーにフラッシュカードを追加する関数

    Args:
        _user_id (str): ユーザーID
        _flashcard_id (str): 追加するフラッシュカードID

    Raises:
        ServiceException: フラッシュカードの追加に失敗した場合
    """
    try:
        new_flashcard_id = await copy_flashcard_doc(
            flashcard_id=_flashcard_id, user_id=_user_id
        )
        await update_user_doc_add_using_flashcard(
            user_id=_user_id, flashcard_id=new_flashcard_id
        )
    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"フラッシュカードの追加中にエラーが発生しました: {str(e)}", "general"
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
                await add_using_flashcard(test_user)
                print(f"ユーザー '{test_user.email}' のセットアップに成功しました。")
            except ServiceException as se:
                print(f"ユーザー '{test_user.email}' のセットアップに失敗しました。エラー: {se.message}")
            except Exception as e:
                print(f"予期せぬエラーが発生しました: {str(e)}")

    # 非同期関数を実行
    asyncio.run(main())
