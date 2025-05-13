import google.generativeai as genai
from config.settings import GOOGLE_API_KEY
from models.types import WordInstance, Translations
import json
from typing import List
from pydantic import BaseModel
from enum import Enum

# Google APIキーの設定
genai.configure(api_key=GOOGLE_API_KEY)

class PartOfSpeech(str, Enum):
    NOUN = "noun"
    VERB = "verb"
    ADVERB = "adverb"
    ADJECTIVE = "adjective"

class Translation(BaseModel):
    word: str
    part_of_speech: PartOfSpeech
    definition: str
    japanese_meaning: str
    english_example: str
    japanese_example: str

class TranslationResponse(BaseModel):
    translations: List[Translation]

def translate_and_prioritize(word_instance: WordInstance) -> Translations:
    """
    Geminiを使用して定義と例文を日本語に翻訳し、優先順位付けを行う
    
    Args:
        definitions (Definitions): 定義と例文のペアの配列
        
    Returns:
        Translations: 優先順位付けされた翻訳結果
    """
    word = word_instance["word"]
    defs_and_examples = word_instance["defs_and_examples"]
    # Geminiへのプロンプト作成
    prompt = f"""以下の英単語「{word}」の定義と例文を、英単語帳で使用する優先度の高い順に日本語に翻訳してください。
各項目について、英単語、品詞（noun, verb, adverb, adjectiveのいずれか）、定義、日本語の意味、英語の例文、日本語の例文の形式で返してください。

入力：
"""
    
    for i, def_pair in enumerate(defs_and_examples, 1):
        prompt += f"{i}. Definition: {def_pair['definition']}\n"
        prompt += f"   Example: {def_pair['example']}\n\n"
    
    # Gemini API呼び出し
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,
            candidate_count=1
        ),
        response_mime_type="application/json",
        response_schema=TranslationResponse
    )
    
    # レスポンスの解析と整形
    try:
        # Pydanticモデルとしてパース
        result: TranslationResponse = response.parsed
        return result.translations
    except Exception as e:
        # エラー処理
        print(f"レスポンスのパースに失敗しました: {str(e)}")
        print("生のレスポンス:", response.text)
        return [] 