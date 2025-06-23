import os

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, storage
from google import genai

# 定数
GOOGLE_GEMINI_MODEL = "gemini-2.0-flash"
GOOGLE_GEMINI_IMAGE_EDITING_MODEL = "gemini-2.0-flash-preview-image-generation"
GOOGLE_IMAGEN_MODEL = "imagen-3.0-generate-002"
GOOGLE_VEO_MODEL = "veo-2.0-generate-001"

# 環境変数の読み込み
load_dotenv()

# APIキーの設定
WORDS_API_KEY = os.getenv("WORDS_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai_client = genai.Client(api_key=GOOGLE_API_KEY)


# Use a service account.
service_account_path = (
    "/src/config/serviceAccount.json"
    if os.getenv("DEPLOY_ENV") == "production"
    else "serviceAccount.json"
)
cred = credentials.Certificate(service_account_path)

app = firebase_admin.initialize_app(
    cred, {"storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")}
)

db = firestore.client()

bucket = storage.bucket()
