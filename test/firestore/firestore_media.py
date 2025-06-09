import time
from datetime import datetime

from src.services.firebase.schemas.media_schema import MediaSchema
from src.services.firebase.unit.firestore_media import (
    create_media_doc,
    read_media_docs,
    update_media_doc,
)


def test_firestore_media_functions():
    try:
        # テスト用のメディアデータを作成
        test_media = [
            MediaSchema(
                media_id="media_001",
                flashcard_id="flash_001",
                meaning_id="meaning_001",
                media_urls=["https://example.com/media1.jpg"],
                generation_type="image",
                template_id="template_001",
                user_prompt="テスト用プロンプト1",
                generated_prompt="生成されたプロンプト1",
                input_media_urls=["https://example.com/input1.jpg"],
                prompt_token_count=100,
                candidates_token_count=50,
                total_token_count=150,
                created_by="user_001",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            MediaSchema(
                media_id="media_002",
                flashcard_id="flash_002",
                meaning_id="meaning_002",
                media_urls=["https://example.com/media2.jpg"],
                generation_type="image",
                template_id="template_002",
                user_prompt="テスト用プロンプト2",
                generated_prompt="生成されたプロンプト2",
                input_media_urls=["https://example.com/input2.jpg"],
                prompt_token_count=120,
                candidates_token_count=60,
                total_token_count=180,
                created_by="user_001",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            MediaSchema(
                media_id="media_003",
                flashcard_id="flash_003",
                meaning_id="meaning_003",
                media_urls=["https://example.com/media3.jpg"],
                generation_type="image",
                template_id="template_003",
                user_prompt="テスト用プロンプト3",
                generated_prompt="生成されたプロンプト3",
                input_media_urls=["https://example.com/input3.jpg"],
                prompt_token_count=90,
                candidates_token_count=45,
                total_token_count=135,
                created_by="user_001",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        media_ids = []
        print("\n=== テスト開始 ===")

        # 1. 複数のデータの作成
        print("\n1. 複数のデータの作成")
        try:
            for test_media_item in test_media:
                is_success, error, created_media_id = create_media_doc(test_media_item)
                if not is_success:
                    raise Exception(error)
                media_ids.append(created_media_id)
                print(f"作成したデータ: {test_media_item.to_dict()}")
                print(f"生成されたmedia_id: {created_media_id}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ作成中にエラーが発生しました: {str(e)}")
            raise

        # 2. 複数データの一括読み取り
        print("\n2. 複数データの一括読み取り")
        try:
            read_results, error = read_media_docs(media_ids)
            if error:
                raise Exception(error)
            if read_results:
                print(f"読み取ったデータ数: {len(read_results)}")
                for media in read_results:
                    print(f"読み取ったデータ: {media.to_dict()}")
            else:
                print("データが見つかりませんでした")
        except Exception as e:
            print(f"データ読み取り中にエラーが発生しました: {str(e)}")
            raise

        # 3. 最初のデータの更新
        print("\n3. 最初のデータの更新")
        try:
            test_media[0].user_prompt = "更新されたプロンプト1"
            test_media[0].generated_prompt = "更新された生成プロンプト1"
            test_media[0].updated_at = datetime.now()
            is_success, error = update_media_doc(media_ids[0], test_media[0])
            if not is_success:
                raise Exception(error)
            print(f"更新したデータ: {test_media[0].to_dict()}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ更新中にエラーが発生しました: {str(e)}")
            raise

        # 4. 更新後の全データの一括読み取り
        print("\n4. 更新後の全データの一括読み取り")
        try:
            updated_results, error = read_media_docs(media_ids)
            if error:
                raise Exception(error)
            if updated_results:
                print(f"更新後のデータ数: {len(updated_results)}")
                for media in updated_results:
                    print(f"更新後のデータ: {media.to_dict()}")
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
    test_firestore_media_functions()
