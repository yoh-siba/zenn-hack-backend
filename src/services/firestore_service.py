from google.cloud import firestore
from models.types import Translations

def save_to_firestore(translations: Translations, word: str) -> None:
    """
    翻訳結果をFirestoreに保存する
    
    Args:
        translations (Translations): 翻訳結果の配列
        word (str): 元の英単語
    """
    db = firestore.Client()
    
    # 単語ドキュメントの参照
    word_ref = db.collection('words').document(word)
    
    # データの保存
    word_ref.set({
        'word': word,
        'translations': translations,
        'created_at': firestore.SERVER_TIMESTAMP
    }) 