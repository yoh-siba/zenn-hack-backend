import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google import genai

# 定数
GOOGLE_GEMINI_MODEL = "gemini-2.0-flash"
GOOGLE_IMAGEN_MODEL = "imagen-3.0-generate-002"

# 環境変数の読み込み
load_dotenv()

# APIキーの設定
WORDS_API_KEY = os.getenv('WORDS_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
google_client = genai.Client(api_key=GOOGLE_API_KEY)

# Use a service account.
cred = credentials.Certificate('serviceAccount.json')

app = firebase_admin.initialize_app(cred)

db = firestore.client()