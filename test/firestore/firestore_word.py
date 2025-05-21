from datetime import datetime
import time
from src.schemas.word_schema import WordSchema
from src.services.firestore.create_word_and_meaning import create_word_doc, update_word_doc, read_word_doc, read_word_docs
from src.services.firestore.create_word_and_meaning import create_word_and_meaning

def test_firestore_word_functions():
    try:
        # テスト用の単語データを作成
        test_words = [
            WordSchema(
                word="テスト単語1",
                meaning_id_list=["meaning_001", "meaning_002"],
                core_meaning="テストの意味1",
                explanation="これはテスト用の説明文1です。",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            WordSchema(
                word="テスト単語2",
                meaning_id_list=["meaning_003", "meaning_004"],
                core_meaning="テストの意味2",
                explanation="これはテスト用の説明文2です。",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            WordSchema(
                word="テスト単語3",
                meaning_id_list=["meaning_005", "meaning_006"],
                core_meaning="テストの意味3",
                explanation="これはテスト用の説明文3です。",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        word_ids = []
        print("\n=== テスト開始 ===")
        
        # 1. 複数のデータの作成
        print("\n1. 複数のデータの作成")
        try:
            for test_word in test_words:
                is_success, error, created_word_id = create_word_doc(test_word)
                if not is_success:
                    raise Exception(error)
                word_ids.append(created_word_id)
                print(f"作成したデータ: {test_word.to_dict()}")
                print(f"生成されたword_id: {created_word_id}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ作成中にエラーが発生しました: {str(e)}")
            raise

        # 2. 複数データの一括読み取り
        print("\n2. 複数データの一括読み取り")
        try:
            read_results, error = read_word_docs(word_ids)
            if error:
                raise Exception(error)
            if read_results:
                print(f"読み取ったデータ数: {len(read_results)}")
                for word in read_results:
                    print(f"読み取ったデータ: {word.to_dict()}")
            else:
                print("データが見つかりませんでした")
        except Exception as e:
            print(f"データ読み取り中にエラーが発生しました: {str(e)}")
            raise

        # 3. 最初のデータの更新
        print("\n3. 最初のデータの更新")
        try:
            test_words[0].word = "更新された単語1"
            test_words[0].core_meaning = "更新された意味1"
            test_words[0].updated_at = datetime.now()
            is_success, error = update_word_doc(word_ids[0], test_words[0])
            if not is_success:
                raise Exception(error)
            print(f"更新したデータ: {test_words[0].to_dict()}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ更新中にエラーが発生しました: {str(e)}")
            raise

        # 4. 更新後の全データの一括読み取り
        print("\n4. 更新後の全データの一括読み取り")
        try:
            updated_results, error = read_word_docs(word_ids)
            if error:
                raise Exception(error)
            if updated_results:
                print(f"更新後のデータ数: {len(updated_results)}")
                for word in updated_results:
                    print(f"更新後のデータ: {word.to_dict()}")
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
    test_firestore_word_functions() 
    create_word_and_meaning