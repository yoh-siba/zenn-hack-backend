from datetime import datetime
import time
from src.schemas.flashcard_schema import FlashcardSchema
from src.services.firestore.firestore_flashcard import create_flashcard_doc, update_flashcard_doc, read_flashcard_doc, read_flashcard_docs

def test_firestore_flashcard_functions():
    try:
        # テスト用のフラッシュカードデータを作成
        test_flashcards = [
            FlashcardSchema(
                word_id="word_001",
                using_meaning_list=["meaning_001", "meaning_002"],
                memo="テスト用メモ1",
                media_id_list=["media_001", "media_002"],
                current_media_id="media_001",
                comparison_id=None,
                created_by="user_001",
                version=1,
                check_flag=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            FlashcardSchema(
                word_id="word_002",
                using_meaning_list=["meaning_003"],
                memo="テスト用メモ2",
                media_id_list=["media_003"],
                current_media_id="media_003",
                comparison_id="word_001",
                created_by="user_001",
                version=1,
                check_flag=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            FlashcardSchema(
                word_id="word_003",
                using_meaning_list=["meaning_004", "meaning_005"],
                memo="テスト用メモ3",
                media_id_list=["media_004", "media_005"],
                current_media_id="media_004",
                comparison_id=None,
                created_by="user_001",
                version=1,
                check_flag=False,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        flashcard_ids = []
        print("\n=== テスト開始 ===")
        
        # 1. 複数のデータの作成
        print("\n1. 複数のデータの作成")
        try:
            for test_flashcard in test_flashcards:
                is_success, error, created_flashcard_id = create_flashcard_doc(test_flashcard)
                if not is_success:
                    raise Exception(error)
                flashcard_ids.append(created_flashcard_id)
                print(f"作成したデータ: {test_flashcard.to_dict()}")
                print(f"生成されたflashcard_id: {created_flashcard_id}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ作成中にエラーが発生しました: {str(e)}")
            raise

        # 2. 複数データの一括読み取り
        print("\n2. 複数データの一括読み取り")
        try:
            read_results, error = read_flashcard_docs(flashcard_ids)
            if error:
                raise Exception(error)
            if read_results:
                print(f"読み取ったデータ数: {len(read_results)}")
                for flashcard in read_results:
                    print(f"読み取ったデータ: {flashcard.to_dict()}")
            else:
                print("データが見つかりませんでした")
        except Exception as e:
            print(f"データ読み取り中にエラーが発生しました: {str(e)}")
            raise

        # 3. 最初のデータの更新
        print("\n3. 最初のデータの更新")
        try:
            test_flashcards[0].memo = "更新されたメモ"
            test_flashcards[0].check_flag = True
            test_flashcards[0].version = 2
            test_flashcards[0].updated_at = datetime.now()
            is_success, error = update_flashcard_doc(flashcard_ids[0], test_flashcards[0])
            if not is_success:
                raise Exception(error)
            print(f"更新したデータ: {test_flashcards[0].to_dict()}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ更新中にエラーが発生しました: {str(e)}")
            raise

        # 4. 更新後の全データの一括読み取り
        print("\n4. 更新後の全データの一括読み取り")
        try:
            updated_results, error = read_flashcard_docs(flashcard_ids)
            if error:
                raise Exception(error)
            if updated_results:
                print(f"更新後のデータ数: {len(updated_results)}")
                for flashcard in updated_results:
                    print(f"更新後のデータ: {flashcard.to_dict()}")
            else:
                print("更新後のデータが見つかりませんでした")
        except Exception as e:
            print(f"更新後のデータ読み取り中にエラーが発生しました: {str(e)}")
            raise

        print("\n=== テスト成功 ===")

    except Exception as e:
        print(f"\n=== テスト失敗 ===")
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    test_firestore_flashcard_functions() 