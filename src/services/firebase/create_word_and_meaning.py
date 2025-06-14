from typing import Optional, Tuple

from src.services.firebase.schemas.meaning_schema import MeaningSchema
from src.services.firebase.schemas.word_schema import WordSchema
from src.services.firebase.unit.firestore_meaning import create_meaning_doc
from src.services.firebase.unit.firestore_word import create_word_doc, update_word_doc


async def create_word_and_meaning(
    word_instance: WordSchema,
    meanings_instance: list[MeaningSchema],
) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """単語とその意味をFirestoreに作成する関数
    Args:
        word_instance (WordSchema): 作成する単語のインスタンス
            meaning_id_listは空の配列でOK（関数内で自動的に設定されます）
        meanings_instance (list[MeaningSchema]): 作成する意味のインスタンスのリスト

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 作成された単語のID（失敗時はNone）
            - 作成された意味のIDリスト（失敗時はNone）
    """
    try:
        # 単語をwordsコレクションに追加
        success, error, word_id = await create_word_doc(word_instance)
        if not success:
            print(f"\n単語の作成に失敗しました: {error}")
            return False, error, None, None

        # 意味をmeaningsコレクションに追加し、IDを収集
        print(f"\n単語 '{word_instance.word}' の意味を作成中...")
        meaning_id_list = []
        for meaning in meanings_instance:
            meaning.word_id = word_id
            success, error, meaning_id = await create_meaning_doc(meaning)
            if not success:
                print(f"\n意味の作成に失敗しました: {error}")
                return False, error, None, None
            meaning_id_list.append(meaning_id)

        # 単語ドキュメントを更新してmeaning_id_listを設定
        word_instance.meaning_id_list = meaning_id_list
        success, error = await update_word_doc(word_id, word_instance)
        if not success:
            print(f"\n単語の更新に失敗しました: {error}")
            return False, error, None, None
        return True, None, word_id, meaning_id_list
    except Exception as e:
        error_message = f"単語の作成中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None
