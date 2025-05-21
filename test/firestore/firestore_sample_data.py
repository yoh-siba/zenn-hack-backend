from datetime import datetime
import time
from src.schemas.meaning_schema import MeaningSchema
from src.schemas.word_schema import WordSchema
from src.schemas.media_schema import MediaSchema
from src.schemas.comparison_schema import ComparisonSchema
from src.schemas.flashcard_schema import FlashcardSchema
from src.services.firestore.firestore_meaning import create_meaning_doc
from src.services.firestore.create_word_and_meaning import create_word_doc
from src.services.firestore.firestore_media import create_media_doc
from src.services.firestore.firestore_comparison import create_comparison_doc
from src.services.firestore.firestore_flashcard import create_flashcard_doc

def test_firestore_sample_data():
    try:
        print("\n=== サンプルデータ格納テスト開始 ===")
        
        # 1. Meaningデータの作成
        print("\n1. Meaningデータの作成")
        meaning = MeaningSchema(
            pos="名詞",
            definition="テストの定義",
            pronunciation="てすと",
            example_eng="This is a test example.",
            example_jpn="これはテスト例文です。",
            rank=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        is_success, error, meaning_id = create_meaning_doc(meaning)
        if not is_success:
            raise Exception(error)
        print(f"作成したMeaningデータ: {meaning.to_dict()}")
        print(f"生成されたmeaning_id: {meaning_id}")
        time.sleep(2)

        # 2. Wordデータの作成
        print("\n2. Wordデータの作成")
        word = WordSchema(
            word="テスト",
            meaning_id_list=[meaning_id],
            core_meaning="テストの核心的な意味",
            explanation="これはテストの説明です。",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        is_success, error, word_id = create_word_doc(word)
        if not is_success:
            raise Exception(error)
        print(f"作成したWordデータ: {word.to_dict()}")
        print(f"生成されたword_id: {word_id}")
        time.sleep(2)

        # 3. Mediaデータの作成
        print("\n3. Mediaデータの作成")
        media = MediaSchema(
            media_id="media_001",
            flashcard_id="",  # 後で更新
            meaning_id=meaning_id,
            media_urls=["https://example.com/test.jpg"],
            generation_type="image",
            template_id=None,
            userPrompt="テストの画像を生成してください",
            generated_prompt="A test image showing the concept of testing",
            input_media_urls=None,
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        is_success, error, media_id = create_media_doc(media)
        if not is_success:
            raise Exception(error)
        print(f"作成したMediaデータ: {media.to_dict()}")
        print(f"生成されたmedia_id: {media_id}")
        time.sleep(2)

        # 4. Comparisonデータの作成
        print("\n4. Comparisonデータの作成")
        comparison = ComparisonSchema(
            flashcard_id="",  # 後で更新
            oldMedia_id="old_media_001",
            new_media_id=media_id,
            selected=media_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        is_success, error, comparison_id = create_comparison_doc(comparison)
        if not is_success:
            raise Exception(error)
        print(f"作成したComparisonデータ: {comparison.to_dict()}")
        print(f"生成されたcomparison_id: {comparison_id}")
        time.sleep(2)

        # 5. Flashcardデータの作成
        print("\n5. Flashcardデータの作成")
        flashcard = FlashcardSchema(
            word_id=word_id,
            using_meaning_list=[meaning_id],
            memo="テスト用のメモ",
            media_id_list=[media_id],
            current_media_id=media_id,
            comparison_id=comparison_id,
            created_by="test_user",
            version=1,
            check_flag=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        is_success, error, flashcard_id = create_flashcard_doc(flashcard)
        if not is_success:
            raise Exception(error)
        print(f"作成したFlashcardデータ: {flashcard.to_dict()}")
        print(f"生成されたflashcard_id: {flashcard_id}")

        print("\n=== サンプルデータ格納テスト成功 ===")
        print("\n生成されたID一覧:")
        print(f"meaning_id: {meaning_id}")
        print(f"word_id: {word_id}")
        print(f"media_id: {media_id}")
        print(f"comparison_id: {comparison_id}")
        print(f"flashcard_id: {flashcard_id}")

    except Exception as e:
        print(f"\n=== サンプルデータ格納テスト失敗 ===")
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    test_firestore_sample_data() 