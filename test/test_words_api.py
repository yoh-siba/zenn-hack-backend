import json
import sys

from src.services.word_service import request_words_api


def test_words_api(word: str) -> None:
    """
    Words APIのテストを実行する

    Args:
        word (str): テストする英単語
    """
    try:
        print(f"\n=== Words API テスト: '{word}' ===\n")

        # APIリクエスト実行
        print("1. APIリクエスト実行中...")
        word_data = request_words_api(word)

        # 結果の表示
        print("\n2. 取得したデータ:")
        print(json.dumps(word_data, indent=2, ensure_ascii=False))

        # データ構造の検証
        print("\n3. データ構造の検証:")
        print(f"- 単語: {word_data['word']}")
        print(f"- 音節数: {word_data['syllables']['count']}")
        print(f"- 発音: {word_data['pronunciation']['all']}")
        print(f"- 使用頻度: {word_data['frequency']}")
        print(f"- 定義数: {len(word_data['results'])}")

        # 各定義の詳細表示
        print("\n4. 定義の詳細:")
        for i, result in enumerate(word_data["results"], 1):
            print(f"\n定義 {i}:")
            print(f"- 品詞: {result['partOfSpeech']}")
            print(f"- 意味: {result['definition']}")
            if result.get("examples"):
                print(f"- 例文: {result['examples'][0]}")
            if result.get("synonyms"):
                print(f"- 類義語: {', '.join(result['synonyms'])}")

        print(f"\n=== テスト完了: '{word}' ===\n")

    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    # コマンドライン引数から単語を取得、なければデフォルト値を使用
    test_word = sys.argv[1] if len(sys.argv) > 1 else "example"
    test_words_api(test_word)
