from src.services.firebase.unit.firestore_prompt_template import (
    read_prompt_template_docs,
)


def test_firestore_prompt_template_functions():
    try:
        print("\n=== テスト開始 ===")

        # 1. 全データの一括読み取り
        print("\n1. 全データの一括読み取り")
        try:
            read_results, error = read_prompt_template_docs()
            if error:
                raise Exception(error)
            if read_results:
                print(f"読み取ったデータ数: {len(read_results)}")
                for template in read_results:
                    print(f"読み取ったデータ: {template.to_dict()}")
            else:
                print("データが見つかりませんでした")
        except Exception as e:
            print(f"データ読み取り中にエラーが発生しました: {str(e)}")
            raise

        print("\n=== テスト成功 ===")

    except Exception as e:
        print("\n=== テスト失敗 ===")
        print(f"エラーが発生しました: {str(e)}")
        raise


if __name__ == "__main__":
    test_firestore_prompt_template_functions()
