import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# APIキーの設定
WORDS_API_KEY = os.getenv('WORDS_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS') 