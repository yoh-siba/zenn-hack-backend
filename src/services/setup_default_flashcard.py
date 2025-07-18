from src.models.exceptions import ServiceException
from src.models.types import WordsAPIResponse
from src.services.firebase.create_word_and_meaning import create_word_and_meaning
from src.services.firebase.schemas.flashcard_schema import FlashcardSchema
from src.services.firebase.schemas.media_schema import MediaSchema
from src.services.firebase.unit.cloud_storage_image import create_image_url_from_image
from src.services.firebase.unit.firestore_flashcard import create_flashcard_doc
from src.services.firebase.unit.firestore_media import (
    create_media_doc,
    update_media_doc,
)
from src.services.firebase.unit.firestore_word import read_word_id_by_word
from src.services.google_ai.generate_explanation_and_core_meaning import (
    generate_explanation_and_core_meaning,
)
from src.services.google_ai.generate_prompt_for_imagen import generate_prompt_for_imagen
from src.services.google_ai.generate_translation import generate_translation
from src.services.google_ai.unit.request_imagen import request_imagen_text_to_image
from src.services.words_api.request_words_api import request_words_api


async def setup_default_flashcard(
    word: str,
) -> str:
    """デフォルトフラッシュカードをセットアップする関数
    WordsAPIでベース取得 -> 解説・コアミーニング生成 -> 意味リスト生成 -> データ格納

    Args:
        word (str): 設定したい単語

    Returns:
        str: 作成されたフラッシュカードID

    Raises:
        ServiceException: フラッシュカードのセットアップに失敗した場合
    """
    try:
        is_exist = await read_word_id_by_word(word)
        if is_exist:
            raise ServiceException(f"単語 '{word}' は既に存在します", "conflict")

        # WordsAPIから単語情報を取得
        try:
            words_api_response: WordsAPIResponse = await request_words_api(word)
        except Exception:
            raise ServiceException(
                f"意味の取得に失敗しました。入力された英単語には対応できません。単語: '{word}'",
                "external_api",
            )
        print(f"WordsAPI response for word '{word}': {words_api_response}")

        # MeaningSchema用のコンテンツを作成
        content = f"""
        英単語「{word}」の英語の各定義（以下のデータのdefinition）の値について、それぞれ対応する一言の簡潔な日本語訳を考えてください。
        日本語に訳した際、同じ意味になる場合は、その重複は除いてください。
        definition_engには、definitionの値をそのまま入れてください。
        definition_jpnには、考えた日本語訳を入れてください。
        日本語訳はできるだけ簡潔にし、補足説明部分は「（）」でくくることで、どこが単語の意味なのかを明確にしてください。
        日本語訳は、example_jpnで使ったものと同様の表現を使用してください。
        posには、以下のデータのpartOfSpeechを参考にしつつ、[noun, pronoun, intransitiveVerb, transitiveVerb, adjective, adverb, auxiliaryVerb, article, interjection, conjunction, preposition]のいずれかを入れてください。
        pronunciationには、以下のデータのpronunciationの値をそのまま入れてください。
        example_engには、examplesの最初の要素を、example_jpnにはその日本語訳を入れてください。
        examplesが空の場合は、簡単な例文を考えて、example_engとexample_jpnにそれぞれ入れてください。
        rankには、そのdefinitionの重要度を考慮して、rankを1（重要度高い）から5（重要度低い）の整数で設定してください。

        ### 例（「run」場合）
        definitionが「move fast by using one's feet, with one foot off the ground at any given time」なら、意味は「走る」
        「走る」はrunの意味として最も一般的な意味なので、rankは1に設定。


        ### データ
        {words_api_response.get("results", {})}

        ### 発音データ
        {words_api_response.get("pronunciation", {})}
        """
        # 単語の翻訳を生成
        meanings_instance = generate_translation(content)
        if meanings_instance is None:
            raise ValueError("MeaningsSchema is None")
        print(f"Generated meanings for word '{word}': {meanings_instance}")
        content = f"""
        英単語「{word}」について、解説文とコアミーニングを生成してください。
        explanationには、以下に示すような解説文を生成してください。
        core_meaningには、以下の例のような、全ての意味を包括する50字以内の大まかな意味かNULLを入力してください。
    

        ### 解説文の説明
        以下の優先順位で50字程度の文章にして。
        1. 単語の覚え方（例：swimは「スイスイ泳ぐ」と覚えよう）
        2. その単語がよく使われるシチュエーション、類義語などの豆知識
        3. 単語の語源や由来
        （注意点）英単語の意味を羅列しないで。


        ### コアミーニングの例（「run」場合）
        ある方向に，連続して，（すばやくなめらかに）動く

        ### 単語の意味
        {[{meaning.pos, meaning.translation} for meaning in meanings_instance]}
        """
        # contentを生成
        word_instance = generate_explanation_and_core_meaning(word, content)
        if word_instance is None:
            raise ValueError("WordSchema is None")
        print(f"Generated word instance for '{word}': {word_instance}")
        # WordとMeaningをFirestoreに保存

        word_id, meaning_id_list = await create_word_and_meaning(
            word_instance, meanings_instance
        )
        # 画像生成用プロンプトを生成
        # 代表となる単語の意味情報を取得
        main_meaning = meanings_instance[0] if meanings_instance else None
        content = f"""
        あなたは画像生成AIでイラストを生成するためのプロンプトエンジニアです。
        英単語「{word}」の{main_meaning.pos}としての意味「{main_meaning.translation}」を表現するために、
        text-to-imageモデルのImagenに入力する英語のプロンプトを考えてください。

        ### 良いプロンプトの書き方のコツ
        Style, Subject, Context and Backgroundから成り、意味のあるキーワードと修飾子を使用したシンプルかつ明確な文。
        （例）A sketch of a modern apartment building surrounded by skyscrapers

        ### 画像の特徴
        以下の例文を表現した画像
        {main_meaning.example_eng}
        """
        generated_prompt = generate_prompt_for_imagen(content)
        if generated_prompt is None:
            raise ValueError("Generated prompt is None")
        # プロンプトを生成済み

        ##TODO: 画像生成処理を追加する
        generated_images = request_imagen_text_to_image(
            generated_prompt.generated_prompt,
            _number_of_images=1,
            _aspect_ratio="1:1",  # アスペクト比を1:1に設定
            _person_generation="ALLOW_ALL",  # 人物生成を許可しない
        )

        image_url_list = []
        for image in generated_images:
            image_url = await create_image_url_from_image(
                image,
                f"_default/{word}/{main_meaning.pos}/{main_meaning.translation}.png",
            )
            image_url_list.append(image_url)

        ## TODO: Mediaの保存処理を追加する
        if not generated_images:
            raise ValueError("No images generated")
        media_instance = MediaSchema(
            flashcard_id="",  # 後で更新する
            meaning_id=meaning_id_list[0],
            media_urls=image_url_list,
            generation_type="text-to-image",
            template_id=None,  # TODO: テンプレートIDを設定する
            user_prompt="",
            generated_prompt=generated_prompt.generated_prompt,
            input_media_urls=None,  # 入力メディアURLはNone
            prompt_token_count=generated_prompt.prompt_token_count,
            candidates_token_count=generated_prompt.candidates_token_count,
            total_token_count=generated_prompt.total_token_count,
            created_by="default",  # 作成者はシステム
            created_at=word_instance.created_at,
            updated_at=word_instance.updated_at,
        )

        media_id = await create_media_doc(media_instance)

        # Flashcardのセットアップ
        flashcard_instance = FlashcardSchema(
            word_id=word_id,
            using_meaning_id_list=meaning_id_list[:5],
            memo="",
            media_id_list=[media_id],  # 後で更新される
            current_media_id=media_id,
            comparison_id="",  # 後で更新される
            created_by="default",
            version=0,
            check_flag=False,
            created_at=word_instance.created_at,
            updated_at=word_instance.updated_at,
        )
        flashcard_id = await create_flashcard_doc(flashcard_instance)

        # Mediaの更新
        media_instance = MediaSchema(
            flashcard_id=flashcard_id,
            meaning_id=meaning_id_list[0],  # 最初の意味を使用
            media_urls=image_url_list,
            generation_type="imagen",
            template_id=None,  # TODO: テンプレートIDを設定する
            user_prompt="",
            generated_prompt=generated_prompt.generated_prompt,
            input_media_urls=None,  # 入力メディアURLはNone
            prompt_token_count=generated_prompt.prompt_token_count,
            candidates_token_count=generated_prompt.candidates_token_count,
            total_token_count=generated_prompt.total_token_count,
            created_by="default",  # 作成者はシステム
            created_at=word_instance.created_at,
            updated_at=word_instance.updated_at,
        )

        await update_media_doc(media_id=media_id, media_instance=media_instance)

        return flashcard_id

    except ServiceException:
        raise  # 再発生
    except Exception as e:
        raise ServiceException(
            f"デフォルトフラッシュカードのセットアップ中にエラーが発生しました: {str(e)}",
            "general",
        )


if __name__ == "__main__":
    import asyncio

    async def main():
        # 学習用の単語（30単語）
        # test_word_list = [
        #     # 基本単語
        #     "apple",
        #     "book",
        #     "cat",
        #     "dog",
        #     "house",
        #     "water",
        #     "food",
        #     "time",
        #     "work",
        #     "family",
        #     # 中級単語
        #     "challenge",
        #     "opportunity",
        #     "environment",
        #     "communication",
        #     "education",
        #     "experience",
        #     "knowledge",
        #     "research",
        #     "decision",
        #     "solution",
        #     # 上級単語
        #     "achievement",
        #     "responsibility",
        #     "investigation",
        #     "development",
        #     "collaboration",
        #     "perspective",
        #     "innovation",
        #     "sustainable",
        #     "significant",
        #     "magnificent",
        #     # 動詞
        #     "create",
        #     "analyze",
        #     "improve",
        #     "establish",
        #     "examine",
        #     # 形容詞
        #     "incredible",
        #     "essential",
        #     "effective",
        #     "comprehensive",
        #     "extraordinary",
        # ]
        test_word_list = ["candidate"]
        for test_word in test_word_list:
            try:
                flashcard_id = await setup_default_flashcard(test_word)
                print(f"フラッシュカードのセットアップに成功: {flashcard_id}")
            except ServiceException as se:
                print(
                    f"フラッシュカードのセットアップに失敗: {se.message} ({se.error_type})"
                )

    # 非同期関数を実行
    asyncio.run(main())
