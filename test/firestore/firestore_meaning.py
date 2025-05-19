from datetime import datetime
import time
from src.schemas.meanings_schema import MeaningSchema
from src.services.firestore.firestore_meaning import create_meaning_doc, update_meaning_doc, read_meaning_doc, read_meaning_docs

def test_firestore_meaning_functions():
    try:
        # テスト用の意味データを作成
        test_meanings = [
            MeaningSchema(
                pos="名詞",
                definition="テストの定義1",
                pronunciation="てすと1",
                example_eng="This is a test example 1.",
                example_jpn="これはテスト例文1です。",
                rank=1,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            MeaningSchema(
                pos="動詞",
                definition="テストの定義2",
                pronunciation="てすと2",
                example_eng="This is a test example 2.",
                example_jpn="これはテスト例文2です。",
                rank=2,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            MeaningSchema(
                pos="形容詞",
                definition="テストの定義3",
                pronunciation="てすと3",
                example_eng="This is a test example 3.",
                example_jpn="これはテスト例文3です。",
                rank=3,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        meaning_ids = []
        print("\n=== テスト開始 ===")
        
        # 1. 複数のデータの作成
        print("\n1. 複数のデータの作成")
        try:
            for test_meaning in test_meanings:
                is_success, error, created_meaning_id = create_meaning_doc(test_meaning)
                if not is_success:
                    raise Exception(error)
                meaning_ids.append(created_meaning_id)
                print(f"作成したデータ: {test_meaning.to_dict()}")
                print(f"生成されたmeaning_id: {created_meaning_id}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ作成中にエラーが発生しました: {str(e)}")
            raise

        # 2. 複数データの一括読み取り
        print("\n2. 複数データの一括読み取り")
        try:
            read_results, error = read_meaning_docs(meaning_ids)
            if error:
                raise Exception(error)
            if read_results:
                print(f"読み取ったデータ数: {len(read_results)}")
                for meaning in read_results:
                    print(f"読み取ったデータ: {meaning.to_dict()}")
            else:
                print("データが見つかりませんでした")
        except Exception as e:
            print(f"データ読み取り中にエラーが発生しました: {str(e)}")
            raise

        # 3. 最初のデータの更新
        print("\n3. 最初のデータの更新")
        try:
            test_meanings[0].definition = "更新された定義1"
            test_meanings[0].example_eng = "This is an updated test example 1."
            test_meanings[0].updated_at = datetime.now()
            is_success, error = update_meaning_doc(meaning_ids[0], test_meanings[0])
            if not is_success:
                raise Exception(error)
            print(f"更新したデータ: {test_meanings[0].to_dict()}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ更新中にエラーが発生しました: {str(e)}")
            raise

        # 4. 更新後の全データの一括読み取り
        print("\n4. 更新後の全データの一括読み取り")
        try:
            updated_results, error = read_meaning_docs(meaning_ids)
            if error:
                raise Exception(error)
            if updated_results:
                print(f"更新後のデータ数: {len(updated_results)}")
                for meaning in updated_results:
                    print(f"更新後のデータ: {meaning.to_dict()}")
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
    test_firestore_meaning_functions() 