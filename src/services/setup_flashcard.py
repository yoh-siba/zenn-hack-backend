from typing import Optional, Tuple

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


async def setup_word_and_meaning(
    word: str,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """単語とその意味の生成＆格納用の関数
        WordsAPIでベース取得 -> 解説・コアミーニング生成 -> 意味リスト生成 -> データ格納
        TODO: プロンプトを修正（https://ai.google.dev/gemini-api/docs/image-generation?hl=ja#imagen-prompt-guide）
    Args:
        word (str): 設定したい単語

    Returns:
        Tuple[bool, Optional[str], Optional[str]]:
            - 成功/失敗を示すブール値
            - エラーメッセージ（成功時はNone）
            - 作成された単語のID（失敗時はNone）
    """
    try:
        is_exist = await read_word_id_by_word(word)
        if is_exist:
            raise ValueError(f"単語 '{word}' は既に存在します。")
        # WordsAPIから単語情報を取得
        words_api_response: WordsAPIResponse = await request_words_api(word)

        content = f"""
        英単語「{word}」について、解説文とコアミーニングを生成してください。
        explanationには、以下に示すような解説文を生成してください。
        core_meaningには、以下の例のような、全ての意味を包括するコアミーニングを生成してください。
        コアミーニングが無い場合は無くていいです。


        ### 解説文の説明
        以下のいずれかで50字程度の文章にして。
        1. 単語の語源や、その単語がよく使われるシチュエーションなどの豆知識
        2. 単語の覚え方（例：swimはスイスイ泳ぐ）
        （注意点）英単語の意味を羅列しないで。


        ### コアミーニングの例（「run」場合）
        ある方向に，連続して，（すばやくなめらかに）動く
        """
        word_instance = generate_explanation_and_core_meaning(word, content)
        if word_instance is None:
            raise ValueError("WordSchema is None")
        # MeaningSchema用のコンテンツを作成
        content = f"""
        英単語「{word}」の英語の各定義（以下のデータのdefinition）の値について、それぞれ対応する一言の簡潔な日本語訳を考えてください。
        日本語に訳した際、同じ意味になる場合は、その重複は除いてください。
        definition_engには、definitionの値をそのまま入れてください。
        definition_jpnには、考えた日本語訳を入れてください。
        posには、以下のデータのpartOfSpeechの値をそのまま入れてください。
        pronunciationには、以下のデータのpronunciationの値をそのまま入れてください。
        example_engには、examplesの最初の要素を、example_jpnにはその日本語訳を入れてください。
        rankには、そのdefinitionの重要度を考慮して、rankを1から5の整数で設定してください。

        ### 例（「run」場合）
        definitionが「move fast by using one's feet, with one foot off the ground at any given time」なら、意味は「走る」
        「走る」はrunの意味として最も一般的な意味なので、rankは1に設定。


        ### データ
        {words_api_response.get("results", {})}

        ### 発音データ
        {words_api_response.get("pronunciation", {})}
        """
        print(f"\n単語「{word}」の翻訳を生成中...")
        meanings_instance = generate_translation(content)

        print("翻訳完了。WordとMeaningをFirestoreに保存")

        success, error, word_id, meaning_id_list = await create_word_and_meaning(
            word_instance, meanings_instance
        )
        if not success:
            return False, error, None
        print("WordとMeaningの保存に成功。画像生成用プロンプトを生成中...")
        # 代表となる単語の意味情報を取得
        main_meaning = meanings_instance[0] if meanings_instance else None
        content = f"""
        あなたは画像生成AIでイラストを生成するためのプロンプトエンジニアです。
        英単語「{word}」の{main_meaning.pos}としての意味「{main_meaning.definition}」を表現するために、
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
        print(f"\n生成されたプロンプト: {generated_prompt.generated_prompt}")

        ##TODO: 画像生成処理を追加する
        generated_images = request_imagen_text_to_image(
            generated_prompt.generated_prompt,
            _number_of_images=1,
            _aspect_ratio="1:1",  # アスペクト比を1:1に設定
            _person_generation="ALLOW_ADULT",  # 人物生成を許可しない
        )

        image_url_list = []
        for image in generated_images:
            success, error, image_url = await create_image_url_from_image(
                image, f"{word}.png"
            )
            if not success:
                raise ValueError("画像のURL取得に失敗しました", error)
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
            userPrompt="",
            generated_prompt=generated_prompt.generated_prompt,
            input_media_urls=None,  # 入力メディアURLはNone
            prompt_token_count=generated_prompt.prompt_token_count,
            candidates_token_count=generated_prompt.candidates_token_count,
            total_token_count=generated_prompt.total_token_count,
            created_by="default",  # 作成者はシステム
            created_at=word_instance.created_at,
            updated_at=word_instance.updated_at,
        )

        success, error, media_id = await create_media_doc(media_instance)
        if not success:
            return False, error, None

        print("Mediaの保存に成功。Flashcardのセットアップ中...")
        flashcard_instance = FlashcardSchema(
            word_id=word_id,
            using_meaning_list=meaning_id_list[:5],
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
        success, error, flashcard_id = await create_flashcard_doc(flashcard_instance)
        if not success:
            return False, error, None

        print("Flashcardの保存に成功。Mediaの更新中...")
        media_instance = MediaSchema(
            flashcard_id=flashcard_id,
            meaning_id=meaning_id_list[0],  # 最初の意味を使用
            media_urls=image_url_list,
            generation_type="imagen",
            template_id=None,  # TODO: テンプレートIDを設定する
            userPrompt="",
            generated_prompt=generated_prompt.generated_prompt,
            input_media_urls=None,  # 入力メディアURLはNone
            prompt_token_count=generated_prompt.prompt_token_count,
            candidates_token_count=generated_prompt.candidates_token_count,
            total_token_count=generated_prompt.total_token_count,
            created_by="default",  # 作成者はシステム
            created_at=word_instance.created_at,
            updated_at=word_instance.updated_at,
        )

        success, error = await update_media_doc(
            media_id=media_id, media_instance=media_instance
        )
        if not success:
            return False, error, None

        return True, None, flashcard_id

    except Exception as e:
        error_message = f"単語のセットアップ中にエラーが発生しました: {str(e)}"
        print(f"\n{error_message}")
        return False, error_message, None


if __name__ == "__main__":
    import asyncio

    async def main():
        # テスト用の単語
        test_word = "account"
        success, error, flascard_id = await setup_word_and_meaning(test_word)
        if success:
            print(
                f"単語 '{test_word}' のセットアップに成功しました。生成されたflascard_id: {flascard_id}"
            )
        else:
            print(f"単語 '{test_word}' のセットアップに失敗しました。エラー: {error}")

    # 非同期関数を実行
    asyncio.run(main())
