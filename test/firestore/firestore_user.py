import time
from datetime import datetime

from src.services.firebase.schemas.user_schema import UserSchema
from src.services.firebase.unit.firestore_user import (
    create_user_doc,
    read_user_docs,
    update_user_doc,
)


def test_firestore_user_functions():
    try:
        # テスト用のユーザーデータを作成
        test_users = [
            UserSchema(
                email="test1@example.com",
                user_name="テストユーザー1",
                flashcard_id_list=["flash_001", "flash_002"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            UserSchema(
                email="test2@example.com",
                user_name="テストユーザー2",
                flashcard_id_list=["flash_003"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            UserSchema(
                email="test3@example.com",
                user_name="テストユーザー3",
                flashcard_id_list=["flash_004", "flash_005", "flash_006"],
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        user_ids = []
        print("\n=== テスト開始 ===")

        # 1. 複数のデータの作成
        print("\n1. 複数のデータの作成")
        try:
            for test_user in test_users:
                is_success, error, created_user_id = create_user_doc(test_user)
                if not is_success:
                    raise Exception(error)
                user_ids.append(created_user_id)
                print(f"作成したデータ: {test_user.to_dict()}")
                print(f"生成されたuser_id: {created_user_id}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ作成中にエラーが発生しました: {str(e)}")
            raise

        # 2. 複数データの一括読み取り
        print("\n2. 複数データの一括読み取り")
        try:
            read_results, error = read_user_docs(user_ids)
            if error:
                raise Exception(error)
            if read_results:
                print(f"読み取ったデータ数: {len(read_results)}")
                for user in read_results:
                    print(f"読み取ったデータ: {user.to_dict()}")
            else:
                print("データが見つかりませんでした")
        except Exception as e:
            print(f"データ読み取り中にエラーが発生しました: {str(e)}")
            raise

        # 3. 最初のデータの更新
        print("\n3. 最初のデータの更新")
        try:
            test_users[0].user_name = "更新されたテストユーザー1"
            test_users[0].flashcard_id_list.append("flash_007")
            test_users[0].updated_at = datetime.now()
            is_success, error = update_user_doc(user_ids[0], test_users[0])
            if not is_success:
                raise Exception(error)
            print(f"更新したデータ: {test_users[0].to_dict()}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ更新中にエラーが発生しました: {str(e)}")
            raise

        # 4. 更新後の全データの一括読み取り
        print("\n4. 更新後の全データの一括読み取り")
        try:
            updated_results, error = read_user_docs(user_ids)
            if error:
                raise Exception(error)
            if updated_results:
                print(f"更新後のデータ数: {len(updated_results)}")
                for user in updated_results:
                    print(f"更新後のデータ: {user.to_dict()}")
            else:
                print("更新後のデータが見つかりませんでした")
        except Exception as e:
            print(f"更新後のデータ読み取り中にエラーが発生しました: {str(e)}")
            raise

        print("\n=== テスト成功 ===")

    except Exception as e:
        print("\n=== テスト失敗 ===")
        print(f"エラーが発生しました: {str(e)}")
        raise


if __name__ == "__main__":
    test_firestore_user_functions()
