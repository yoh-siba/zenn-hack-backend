from src.config.settings import db
from src.schemas.word_schema import WordSchema, MeaningSchema

def test_firestore_word() -> None:
    """
    Words APIのテストを実行する
    
    Args:
        word (str): テストする英単語
    """
    try:
        doc_ref = db.collection("test_words")
        example_word = WordSchema(
            wordId="1",
            word="example",
            core_meaning="example",
            explanation="example",
            meaning_list=[MeaningSchema(
                meaningId="1",
                pos="noun",
                definition="example",
                pronunciation="example",
                example_eng="example",
                example_jpn="example",
                rank=1,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            )]
        )
        doc_ref.add(example_word.to_dict())

    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")


if __name__ == "__main__":
    test_firestore_word()