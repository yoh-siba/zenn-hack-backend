import openai
from config.settings import OPENAI_API_KEY
from models.types import Definitions, Translations

# OpenAI APIキーの設定
openai.api_key = OPENAI_API_KEY

def translate_and_prioritize(definitions: Definitions) -> Translations:
    """
    GPTを使用して定義と例文を日本語に翻訳し、優先順位付けを行う
    
    Args:
        definitions (Definitions): 定義と例文のペアの配列
        
    Returns:
        Translations: 優先順位付けされた翻訳結果
    """
    # GPTへのプロンプト作成
    prompt = "以下の英単語の定義と例文を、英単語帳で使用する優先度の高い順に日本語に翻訳してください。\n"
    prompt += "各項目について、品詞、日本語の意味、英語の例文、日本語の例文の形式で返してください。\n\n"
    
    for i, def_pair in enumerate(definitions, 1):
        prompt += f"{i}. Definition: {def_pair['definition']}\n"
        prompt += f"   Example: {def_pair['example']}\n\n"
    
    # GPT API呼び出し
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは英語の専門家で、英単語の定義と例文を適切に日本語に翻訳し、優先順位付けができます。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    # レスポンスの解析と整形
    result = []
    content = response.choices[0].message.content
    # ここでGPTの応答を適切な形式にパースする処理を実装
    # 実際の実装では、GPTの応答形式に応じて適切なパース処理が必要
    
    return result 