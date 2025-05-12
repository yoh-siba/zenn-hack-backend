from services.word_service import request_words_api
from services.translation_service import translate_and_prioritize
from services.firestore_service import save_to_firestore
from models.types import Definitions
import json

def main():
    # テストする単語
    test_word = "example"
    
    try:
        print(f"\n=== 単語 '{test_word}' の処理を開始します ===\n")
        
        # 1. Words APIで単語情報を取得
        print("1. Words APIから単語情報を取得中...")
        word_data = request_words_api(test_word)
        print("取得したデータ:")
        print(json.dumps(word_data, indent=2, ensure_ascii=False))
        
        # 2. 定義と例文のペアを作成
        print("\n2. 定義と例文のペアを作成中...")
        definitions = []
        for result in word_data.get('results', []):
            if 'definition' in result and 'examples' in result and result['examples']:
                definitions.append({
                    'definition': result['definition'],
                    'example': result['examples'][0]
                })
        print("作成した定義と例文のペア:")
        print(json.dumps(definitions, indent=2, ensure_ascii=False))
        
        # 3. 翻訳と優先順位付け
        print("\n3. GPTで翻訳と優先順位付けを実行中...")
        translations = translate_and_prioritize(definitions)
        print("翻訳結果:")
        print(json.dumps(translations, indent=2, ensure_ascii=False))
        
        # 4. Firestoreに保存
        print("\n4. Firestoreに保存中...")
        save_to_firestore(translations, test_word)
        print("保存完了！")
        
        print(f"\n=== 単語 '{test_word}' の処理が完了しました ===\n")
        
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main() 