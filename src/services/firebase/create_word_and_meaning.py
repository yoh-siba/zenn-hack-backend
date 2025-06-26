from typing import Tuple

from src.models.exceptions.service_exception import ServiceException
from src.services.firebase.schemas.meaning_schema import MeaningSchema
from src.services.firebase.schemas.word_schema import WordSchema
from src.services.firebase.unit.firestore_meaning import create_meaning_doc
from src.services.firebase.unit.firestore_word import create_word_doc, update_word_doc


async def create_word_and_meaning(
    word_instance: WordSchema,
    meanings_instance: list[MeaningSchema],
) -> Tuple[str, list[str]]:
    """単語とその意味をFirestoreに作成する関数
    Args:
        word_instance (WordSchema): 作成する単語のインスタンス
            meaning_id_listは空の配列でOK（関数内で自動的に設定されます）
        meanings_instance (list[MeaningSchema]): 作成する意味のインスタンスのリスト

    Returns:
        Tuple[str, list[str]]: 作成された単語のIDと意味のIDリスト

    Raises:
        ServiceException: 単語または意味の作成に失敗した場合
    """
    try:
        # 単語をwordsコレクションに追加
        word_id = await create_word_doc(word_instance)

        # 意味をmeaningsコレクションに追加し、IDを収集
        meaning_id_list = []
        for meaning in meanings_instance:
            meaning.word_id = word_id
            meaning_id = await create_meaning_doc(meaning)
            meaning_id_list.append(meaning_id)

        # 単語ドキュメントを更新してmeaning_id_listを設定
        word_instance.meaning_id_list = meaning_id_list
        await update_word_doc(word_id, word_instance)

        return word_id, meaning_id_list
    except ServiceException:
        raise
    except Exception as e:
        raise ServiceException(
            f"単語と意味の作成中に予期せぬエラーが発生しました: {str(e)}", "general"
        )
