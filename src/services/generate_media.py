from typing import Optional, Tuple


async def generate_media(
    _word: str,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """画像（動画）部分を更新する関数
    使用するAIに応じて、何を生成するかが変わる
    mediaを作成（flashcardのobjectを利用）
    Comparisonを作成
    FlashcardのComparisonIdを設定
    



    Args:
        word (str): セットアップする単語

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 作成された単語のID（失敗時はNone）
    """
    try:
        print(f"\n単語のセットアップを開始: {_word}")
    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


if __name__ == "__main__":
    import asyncio

    async def main():
        # テスト用の単語
        test_word = "account"
        success, error, word_id = await generate_media(test_word)
        if success:
            print(
                f"単語 '{test_word}' のセットアップに成功しました。生成されたword_id: {word_id}"
            )
        else:
            print(f"単語 '{test_word}' のセットアップに失敗しました。エラー: {error}")

    # 非同期関数を実行
    asyncio.run(main())
