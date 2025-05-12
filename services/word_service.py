import requests
from config.settings import WORDS_API_KEY
from models.types import WordData

def request_words_api(word: str) -> WordData:
    """
    Words APIを使用して単語の情報を取得する
    
    Args:
        word (str): 検索する英単語
        
    Returns:
        WordData: 単語の情報
    """
    url = f"https://wordsapiv1.p.mashape.com/words/{word}"
    headers = {
        "X-Mashape-Key": WORDS_API_KEY,
        "X-Mashape-Host": "wordsapiv1.p.mashape.com"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching word data: {response.status_code}") 