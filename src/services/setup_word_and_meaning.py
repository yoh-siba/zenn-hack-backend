from typing import Optional, Tuple

from src.models.types import WordsAPIResponse
from src.services.firestore.create_word_and_meaning import create_word_and_meaning
from src.services.google_ai.generate_explanation_and_core_meaning import (
    generate_explanation_and_core_meaning,
)
from src.services.google_ai.generate_translation import generate_translation
from src.services.words_api.request_words_api import request_words_api


async def setup_word_and_meaning(
    word: str,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """単語とその意味をセットアップする関数

    Args:
        word (str): セットアップする単語

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 作成された単語のID（失敗時はNone）
    """
    try:
        # WordsAPIから単語情報を取得
        words_api_response: WordsAPIResponse = await request_words_api(word)

        content = f"""
        英単語「{word}」について、解説文とコアミーニングを生成してください。
        explanationには、以下に示すような解説文を生成してください。
        core_meaningには、以下の例のような、全ての意味を包括するコアミーニングを生成してください。
        コアミーニングが無い場合は無くていいです。


        ### 解説文の説明
        以下のいずれかで50字程度の文章にして。
        1. 単語の語源や、その単語がよく使われるシチュエーションなどの豆知識
        2. 単語の覚え方（例：swimはスイスイ泳ぐ）
        （注意点）英単語の意味を羅列しないで。


        ### コアミーニングの例（「run」場合）
        ある方向に，連続して，（すばやくなめらかに）動く
        """
        word_instance = generate_explanation_and_core_meaning("account", content)
        if word_instance is None:
            raise ValueError("WordSchema is None")
        # MeaningSchema用のコンテンツを作成
        content = f"""
        英単語「{word}」の英語の各定義（以下のデータのdefinition）の値について、それぞれ対応する一言の簡潔な日本語訳を考えてください。
        日本語に訳した際、同じ意味になる場合は、その重複は除いてください。
        definition_engには、definitionの値をそのまま入れてください。
        definition_jpnには、考えた日本語訳を入れてください。
        posには、以下のデータのpartOfSpeechの値をそのまま入れてください。
        pronunciationには、以下のデータのpronunciationの値をそのまま入れてください。
        example_engには、examplesの最初の要素を、example_jpnにはその日本語訳を入れてください。
        rankには、そのdefinitionの重要度を考慮して、rankを1から5の整数で設定してください。

        ### 例（「run」場合）
        definitionが「move fast by using one's feet, with one foot off the ground at any given time」なら、意味は「走る」
        「走る」はrunの意味として最も一般的な意味なので、rankは1に設定。


        ### データ
        {words_api_response.get("results", {})}

        ### 発音データ
        {words_api_response.get("pronunciation", {})}
        """
        print(f"\n単語「{word}」の翻訳を生成中...")
        meanings_instance = generate_translation(content)

        print("翻訳完了。WordとMeaningをFirestoreに保存")

        success, error, word_id = await create_word_and_meaning(
            word_instance, meanings_instance
        )
        return success, error, word_id

    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


if __name__ == "__main__":
    import asyncio

    async def main():
        # テスト用の単語
        test_word = "account"
        success, error, word_id = await setup_word_and_meaning(test_word)
        if success:
            print(
                f"単語 '{test_word}' のセットアップに成功しました。生成されたword_id: {word_id}"
            )
        else:
            print(f"単語 '{test_word}' のセットアップに失敗しました。エラー: {error}")

    # 非同期関数を実行
    asyncio.run(main())
