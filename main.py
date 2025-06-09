import json

from fastapi import Body, FastAPI, HTTPException
from pydantic import ValidationError

from src.models.types import (
    CreateMediaRequest,
    FlashcardResponse,
    SetUpUserRequest,
    UpdateFlagRequest,
    UpdateMemoRequest,
    UpdateUserRequest,
    UpdateUsingMeaningsRequest,
)
from src.services.firebase.create_word_and_meaning import create_word_and_meaning
from src.services.firebase.unit.firestore_flashcard import (
    read_flashcard_docs,
    update_flashcard_doc_on_check_flag,
    update_flashcard_doc_on_memo,
    update_flashcard_doc_on_using_meaning_id_list,
)
from src.services.firebase.unit.firestore_meaning import read_meaning_docs
from src.services.firebase.unit.firestore_media import read_media_doc
from src.services.firebase.unit.firestore_user import read_user_doc, update_user_doc
from src.services.firebase.unit.firestore_word import read_word_doc
from src.services.setup_flashcard import setup_flashcard
from src.services.setup_media import setup_media
from src.services.setup_user import setup_user
from src.services.words_api import request_words_api

app = FastAPI()


@app.get("/")
async def root():
    """
    Root endpoint to check server status.
    """
    return {"message": "Hello World"}


@app.get("/word/{word}", description="Retrieve word information and translations.")
async def get_word(word: str):
    """
    Fetches word data from Words API, translates it, and stores it in Firestore.

    Args:
        word (str): The word to retrieve information for.

    Returns:
        dict: Translated word data.
    """
    try:
        word_data = request_words_api(word)
        translated_data = setup_flashcard(word_data)
        create_word_and_meaning(translated_data)
        return translated_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/user/{userId}", description="Retrieve user information by user ID.")
async def get_user_endpoint(userId: str):
    """
    Fetches user data from Firestore.

    Args:
        userId (str): The ID of the user to retrieve.

    Returns:
        dict: User data.
    """
    try:
        user_instance, error = await read_user_doc(userId)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not user_instance:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        return {
            "message": "User retrieved successfully",
            "user": user_instance.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/setup", description="Set up a new user.")
async def setup_user_endpoint(_user: dict = Body(...)):
    """
    Registers a new user in Firestore.

    Args:
        _user (dict): User data for registration.

    Returns:
        dict: Success message and user ID.
    """
    try:
        user = SetUpUserRequest.from_json(json.dumps(_user))
        success, error, user_id = await setup_user(user)
        if success:
            return {"message": "User setup successful", "userId": user_id}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/user/update", description="Update user information.")
async def update_user_endpoint(_user: dict = Body(...)):
    """
    Updates user information in Firestore.

    Args:
        _user (dict): Updated user data.

    Returns:
        dict: Success message and user ID.
    """
    try:
        user = UpdateUserRequest.from_json(json.dumps(_user))
        success, error = await update_user_doc(
            user_id=user.user_id,
            user_instance=user
        )
        if success:
            return {"message": "User update successful", "userId": user.user_id}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/flashcard/{userId}", description="Retrieve flashcards for a user.")
async def get_flashcards_endpoint(userId: str):
    """
    Fetches flashcards associated with a user from Firestore.

    Args:
        userId (str): The ID of the user whose flashcards to retrieve.

    Returns:
        dict: User's flashcards data.
    """
    try:
        user_id = userId
        user_instance, error = await read_user_doc(user_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not user_instance:
            raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
        # 登録単語が0の場合はフロント側で処理（エラーではない）
        if len(user_instance.flashcard_id_list) == 0:
            return []
        flashcards, error = await read_flashcard_docs(user_instance.flashcard_id_list)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not flashcards:
            raise HTTPException(status_code=404, detail="このユーザーのフラッシュカードが見つかりません")
        flashcard_responses = []
        i = 0
        for flashcard in flashcards:
            word, error = await read_word_doc(flashcard.word_id)
            if error:
                raise HTTPException(status_code=500, detail=error)
            meanings, error = await read_meaning_docs(flashcard.using_meaning_id_list)
            if error:
                raise HTTPException(status_code=500, detail=error) 
            media, error = await read_media_doc(flashcard.current_media_id)
            if error:
                raise HTTPException(status_code=500, detail=error)
            flashcard = FlashcardResponse(
                flashcard_id=flashcard.flashcard_id,
                word=word,
                meanings=meanings,
                media=media,
                memo=flashcard.memo,
                version=flashcard.version,
                check_flag=flashcard.check_flag,
            )
            flashcard_responses.append(flashcard.to_dict())
            i += 1
        return {
            "message": "Flashcards retrieved successfully",
            "flashcards": flashcard_responses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/flashcard/update/checkFlag", description="Update the check flag of a flashcard.")
async def update_check_flag_endpoint(_request: dict = Body(...)):
    """
    Updates the check flag for a specific flashcard.

    Args:
        _request (dict): Request data containing flashcard ID and check flag.

    Returns:
        dict: Success message.
    """
    try:
        # リクエストボディの型を確認
        update_flag_request = UpdateFlagRequest.from_dict(_request)
        success, error = await update_flashcard_doc_on_check_flag(
            flashcard_id=update_flag_request.flashcard_id,
            check_flag=update_flag_request.check_flag
        )
        if success:
            return {"message": "Flashcard update successful"}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/flashcard/update/memo", description="Update the memo of a flashcard.")
async def update_flashcard_memo_endpoint(_request: dict = Body(...)):
    """
    Updates the memo for a specific flashcard.

    Args:
        _request (dict): Request data containing flashcard ID and memo.

    Returns:
        dict: Success message.
    """
    try:
        update_memo_request = UpdateMemoRequest.from_dict(_request)
        success, error = await update_flashcard_doc_on_memo(
            flashcard_id=update_memo_request.flashcard_id,
            memo=update_memo_request.memo
        )
        if error:
            raise HTTPException(status_code=500, detail=error)
        if success:
            return {"message": "Flashcard memo update successful"}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/flashcard/update/usingMeaningIdList", description="Update the list of meanings used by a flashcard.")
async def update_using_meaning_id_list_endpoint(_request: dict = Body(...)):
    """
    Updates the list of meanings associated with a specific flashcard.

    Args:
        _request (dict): Request data containing flashcard ID and meaning ID list.

    Returns:
        dict: Success message.
    """
    try:
        create_meaning_request = UpdateUsingMeaningsRequest.from_dict(_request)
        success, error = await update_flashcard_doc_on_using_meaning_id_list(
            flashcard_id=create_meaning_request.flashcard_id,
            using_meaning_id_list=create_meaning_request.using_meaning_id_list
        )
        if error:
            raise HTTPException(status_code=500, detail=error)
        if success:
            return {"message": "Meaning updated successfully"}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/media/create", description="Set up media for a flashcard.")
async def setup_media_endpoint(_request: dict = Body(...)):
    """
    新しいメディアの生成（プロンプトの生成＆画像・動画生成）
    メディアColへ格納
    ComparisonsColへ格納
    フラッシュカードColのcomparisonIdを更新
    〇〇を返す（Flashcard？currentMediaId?）
    Args:
        _request (dict): Request data containing flashcard and media information.

    Returns:
        dict: Success message and flashcard ID.
    """
    try:
        create_media_request = CreateMediaRequest.from_dict(_request)
        success, error, media_id = await setup_media(
            create_media_request=create_media_request
        )
        if error:
            raise HTTPException(status_code=500, detail=error)
        if success:
            return {"message": "Flashcard comparison ID updated successfully"}

    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/meaning/{wordId}")
async def get_meanings_endpoint(wordId: str):
    try:
        word_id = wordId
        word_instance, error = await read_word_doc(word_id =word_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if len(word_instance.meaning_id_list) == 0:
            raise HTTPException(status_code=404, detail="この単語には意味が登録されていません。")
        meanings, error = await read_meaning_docs(meaning_ids=word_instance.meaning_id_list)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not meanings:
            raise HTTPException(status_code=404, detail="意味が見つかりません")
        return {
            "message": "Meanings retrieved successfully",
            "meanings": [meaning.to_dict() for meaning in meanings]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







# プロンプトのテンプレート全取得API
@app.get("/template")
async def get_template_endpoint():
    try:
       raise HTTPException(status_code=500, detail="このAPIはまだ実装されていません。")
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# プロンプトのテンプレート更新API
@app.put("/template/update")
async def update_template_endpoint(_request: dict = Body(...)):
    try:
        # update_template_request = UpdateTemplateRequest.from_dict(_request)
        raise HTTPException(status_code=500, detail="このAPIはまだ実装されていません。")
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#  エラー報告の仕様を整理したうえで実装
# 単語の意味追加API（注：ユーザーごとの意味追加APIとは別）
@app.post("/apply/add_meaning")
async def apply_add_meaning_endpoint(_request: dict = Body(...)):
    try:
    #    add_meaning_request = ApplyAddMeaningRequest.from_dict(_request)
       raise HTTPException(status_code=500, detail="このAPIはまだ実装されていません。")
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#  エラー報告の仕様を整理したうえで実装
# 単語の意味追加API（注：ユーザーごとの意味追加APIとは別）
@app.post("/apply/modify_meaning")
async def apply_modify_meaning_endpoint(_request: dict = Body(...)):
    try:
        # modify_meaning_request = ApplyModifyMeaningRequest.from_dict(_request)
        raise HTTPException(status_code=500, detail="このAPIはまだ実装されていません。")
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

