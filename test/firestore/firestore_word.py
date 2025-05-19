from datetime import datetime
import time
from src.schemas.words_schema import WordsSchema
from src.services.firestore.firestore_word import create_word_schema, update_word_schema, read_word_schema

def test_firestore_word_functions():
    try:
        test_word = WordsSchema(
            word="テスト単語",
            meaning_id_list=["meaning_001", "meaning_002"],
            core_meaning="テストの意味",
            explanation="これはテスト用の説明文です。",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        word_id = ""
        print("\n=== テスト開始 ===")
        
        # 1. データの作成
        print("\n1. データの作成")
        try:
            is_success, error, created_word_id = create_word_schema(test_word)
            if not is_success:
                raise Exception(error)
            word_id = created_word_id
            print(f"作成したデータ: {test_word.to_dict()}")
            print(f"生成されたword_id: {word_id}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ作成中にエラーが発生しました: {str(e)}")
            raise

        # 2. データの読み取り
        print("\n2. データの読み取り")
        try:
            read_result, error = read_word_schema(word_id)
            if error:
                raise Exception(error)
            if read_result:
                print(f"読み取ったデータ: {read_result.to_dict()}")
            else:
                print("データが見つかりませんでした")
        except Exception as e:
            print(f"データ読み取り中にエラーが発生しました: {str(e)}")
            raise

        # 3. データの更新
        print("\n3. データの更新")
        try:
            test_word.word = "更新された単語"
            test_word.core_meaning = "更新された意味"
            test_word.updated_at = datetime.now()
            is_success, error = update_word_schema(word_id, test_word)
            if not is_success:
                raise Exception(error)
            print(f"更新したデータ: {test_word.to_dict()}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ更新中にエラーが発生しました: {str(e)}")
            raise

        # 4. 更新後のデータの読み取り
        print("\n4. 更新後のデータの読み取り")
        try:
            updated_result, error = read_word_schema(word_id)
            if error:
                raise Exception(error)
            if updated_result:
                print(f"更新後のデータ: {updated_result.to_dict()}")
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