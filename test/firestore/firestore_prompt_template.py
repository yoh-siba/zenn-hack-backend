from datetime import datetime
import time
from src.schemas.prompt_template_schema import PromptTemplateSchema
from src.services.firestore.firestore_prompt_template import create_prompt_template_doc, update_prompt_template_doc, read_prompt_template_doc, read_prompt_template_docs

def test_firestore_prompt_template_functions():
    try:
        # テスト用のプロンプトテンプレートデータを作成
        test_templates = [
            PromptTemplateSchema(
                templateId="template_001",
                name="画像生成テンプレート1",
                description="単語の意味を表す画像を生成するためのテンプレート1",
                generationType="image",
                promptText="以下の単語の意味を表す画像を生成してください：{word}\n意味：{meaning}",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            PromptTemplateSchema(
                templateId="template_002",
                name="画像生成テンプレート2",
                description="単語の例文を表す画像を生成するためのテンプレート2",
                generationType="image",
                promptText="以下の例文を表す画像を生成してください：{example}\n単語：{word}",
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            PromptTemplateSchema(
                templateId="template_003",
                name="画像生成テンプレート3",
                description="単語の関連性を表す画像を生成するためのテンプレート3",
                generationType="image",
                promptText="以下の単語の関連性を表す画像を生成してください：{word}\n関連語：{related_words}",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        template_ids = []
        print("\n=== テスト開始 ===")
        
        # 1. 複数のデータの作成
        print("\n1. 複数のデータの作成")
        try:
            for test_template in test_templates:
                is_success, error, created_template_id = create_prompt_template_doc(test_template)
                if not is_success:
                    raise Exception(error)
                template_ids.append(created_template_id)
                print(f"作成したデータ: {test_template.to_dict()}")
                print(f"生成されたtemplate_id: {created_template_id}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ作成中にエラーが発生しました: {str(e)}")
            raise

        # 2. 複数データの一括読み取り
        print("\n2. 複数データの一括読み取り")
        try:
            read_results, error = read_prompt_template_docs(template_ids)
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

        # 3. 最初のデータの更新
        print("\n3. 最初のデータの更新")
        try:
            test_templates[0].name = "更新された画像生成テンプレート1"
            test_templates[0].description = "更新された説明文1"
            test_templates[0].promptText = "更新されたプロンプトテキスト：{word}\n意味：{meaning}\n追加情報：{additional_info}"
            test_templates[0].updated_at = datetime.now()
            is_success, error = update_prompt_template_doc(template_ids[0], test_templates[0])
            if not is_success:
                raise Exception(error)
            print(f"更新したデータ: {test_templates[0].to_dict()}")
            # Firestoreの同期を待つ
            time.sleep(2)
        except Exception as e:
            print(f"データ更新中にエラーが発生しました: {str(e)}")
            raise

        # 4. 更新後の全データの一括読み取り
        print("\n4. 更新後の全データの一括読み取り")
        try:
            updated_results, error = read_prompt_template_docs(template_ids)
            if error:
                raise Exception(error)
            if updated_results:
                print(f"更新後のデータ数: {len(updated_results)}")
                for template in updated_results:
                    print(f"更新後のデータ: {template.to_dict()}")
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
    test_firestore_prompt_template_functions() 