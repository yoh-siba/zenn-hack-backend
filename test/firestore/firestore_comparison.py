from datetime import datetime
import time
from src.schemas.comparison_schema import ComparisonSchema
from src.services.firestore.firestore_comparison import create_comparison_doc, update_comparison_doc, read_comparison_doc, read_comparison_docs

def test_firestore_comparison_functions():
    try:
        # テスト用の比較データを作成
        test_comparisons = [
            ComparisonSchema(
                comparisonId="comp_001",
                flashcardId="flash_001",
                oldMediaId="media_001",
                newMediaId="media_002",
                selected="old",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ComparisonSchema(
                comparisonId="comp_002",
                flashcardId="flash_002",
                oldMediaId="media_003",
                newMediaId="media_004",
                selected="new",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            ComparisonSchema(
                comparisonId="comp_003",
                flashcardId="flash_003",
                oldMediaId="media_005",
                newMediaId="media_006",
                selected="old",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        comparison_ids = []
        print("\n=== テスト開始 ===")
        
        # 1. 複数のデータの作成
        print("\n1. 複数のデータの作成")
        try:
            for test_comparison in test_comparisons:
                is_success, error, created_comparison_id = create_comparison_doc(test_comparison)
                if not is_success:
                    raise Exception(error)
                comparison_ids.append(created_comparison_id)
                print(f"作成したデータ: {test_comparison.to_dict()}")
                print(f"生成されたcomparison_id: {created_comparison_id}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ作成中にエラーが発生しました: {str(e)}")
            raise

        # 2. 複数データの一括読み取り
        print("\n2. 複数データの一括読み取り")
        try:
            read_results, error = read_comparison_docs(comparison_ids)
            if error:
                raise Exception(error)
            if read_results:
                print(f"読み取ったデータ数: {len(read_results)}")
                for comparison in read_results:
                    print(f"読み取ったデータ: {comparison.to_dict()}")
            else:
                print("データが見つかりませんでした")
        except Exception as e:
            print(f"データ読み取り中にエラーが発生しました: {str(e)}")
            raise

        # 3. 最初のデータの更新
        print("\n3. 最初のデータの更新")
        try:
            test_comparisons[0].selected = "new"
            test_comparisons[0].updated_at = datetime.now()
            is_success, error = update_comparison_doc(comparison_ids[0], test_comparisons[0])
            if not is_success:
                raise Exception(error)
            print(f"更新したデータ: {test_comparisons[0].to_dict()}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ更新中にエラーが発生しました: {str(e)}")
            raise

        # 4. 更新後の全データの一括読み取り
        print("\n4. 更新後の全データの一括読み取り")
        try:
            updated_results, error = read_comparison_docs(comparison_ids)
            if error:
                raise Exception(error)
            if updated_results:
                print(f"更新後のデータ数: {len(updated_results)}")
                for comparison in updated_results:
                    print(f"更新後のデータ: {comparison.to_dict()}")
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
    test_firestore_comparison_functions() 