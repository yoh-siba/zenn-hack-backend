import json
from datetime import datetime
from pathlib import Path

import aiohttp

from src.config.settings import WORDS_API_KEY
from src.models.types import WordsAPIResponse


def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


async def request_words_api(word: str) -> WordsAPIResponse:
    """
    Words APIを使用して単語の情報を取得する

    Args:
        word (str): 検索する英単語

    Returns:
        WordData: 単語の情報
    """
    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}"
    headers = {
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
        "X-RapidAPI-Key": WORDS_API_KEY,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Error fetching word data: {response.status}")


if __name__ == "__main__":
    import asyncio

    async def main():
        test_word = "account"
        try:
            word_data = await request_words_api(test_word)
            print(f"単語 '{test_word}' のデータ: {word_data}")

            output_dir = Path(__file__).parent.parent / "google_ai" / "output"
            output_dir.mkdir(exist_ok=True)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"{current_time}_word_api.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    word_data,
                    f,
                    ensure_ascii=False,
                    indent=2,
                    default=datetime_handler,
                )
            print(f"Word API data saved to: {output_file}")
        except Exception as e:
            print(f"エラー: {str(e)}")

    asyncio.run(main())
