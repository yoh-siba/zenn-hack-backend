import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import google.generativeai as genai


# 定数
GOOGLE_GEMINI_MODEL = "gemini-2.0-flash"

# 環境変数の読み込み
load_dotenv()

# APIキーの設定
WORDS_API_KEY = os.getenv('WORDS_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
google_client = genai

# Use a service account.
cred = credentials.Certificate('serviceAccount.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()