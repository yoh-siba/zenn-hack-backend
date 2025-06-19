from datetime import datetime

from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel, ValidationError

from src.models.types import (
    CompareMediasRequest,
    CreateMediaRequest,
    CreateTemplateRequest,
    FlashcardResponseModel,
    MeaningResponseModel,
    NotComparedMediaResponseModel,
    SetUpUserRequest,
    TemplatesResponseModel,
    UpdateFlagRequest,
    UpdateMemoRequest,
    UpdateTemplateRequest,
    UpdateUserRequest,
    UpdateUsingMeaningsRequest,
    UserResponse,
    UserResponseModel,
)
from src.services.compare_medias import compare_medias
from src.services.firebase.schemas.prompt_template_schema import PromptTemplateSchema
from src.services.firebase.unit.firestore_flashcard import (
    update_flashcard_doc_on_check_flag,
    update_flashcard_doc_on_memo,
    update_flashcard_doc_on_using_meaning_id_list,
)
from src.services.firebase.unit.firestore_meaning import read_meaning_docs
from src.services.firebase.unit.firestore_prompt_template import (
    create_prompt_template_doc,
    read_prompt_template_docs,
    update_prompt_template_doc,
)
from src.services.firebase.unit.firestore_user import (
    delete_user_doc,
    read_user_doc,
    update_user_doc,
)
from src.services.firebase.unit.firestore_word import read_word_doc
from src.services.get_flashcard_list import get_flashcard_list
from src.services.get_not_compared_media_list import get_not_compared_media_list
from src.services.setup_media import setup_media
from src.services.setup_user import setup_user

app = FastAPI()


@app.get("/")
async def root(description: str = "サーバーの稼働確認用エンドポイント"):
    return {"message": "Hello World"}


class GetUserResponseModel(BaseModel):
    message: str
    user: UserResponseModel


@app.get(
    "/user/{userId}",
    description="ユーザー情報の取得用エンドポイント",
    response_model=GetUserResponseModel,
)
async def get_user_endpoint(userId: str):
    try:
        user_instance, error = await read_user_doc(userId)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not user_instance:
            raise HTTPException(
                status_code=500, detail="指定されたユーザーは存在しません"
            )
        user_response = user_instance.to_dict()
        user_response["user_id"] = userId
        return {
            "message": "User retrieved successfully",
            "user": UserResponse.from_dict(user_response).to_dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SetUpUserResponseModel(BaseModel):
    message: str


@app.post(
    "/user/setup",
    description="新規のユーザー登録用エンドポイント",
    response_model=SetUpUserResponseModel,
)
async def setup_user_endpoint(
    _user: dict = Body(
        ...,
        example={
            "userId": "12345",
            "email": "yamada@yamada.com",
            "userName": "山田",
        },
    ),
):
    try:
        user = SetUpUserRequest.from_dict(_user)
        success, error = await setup_user(user)
        if success:
            return {"message": "User setup successful"}
        else:
            raise HTTPException(status_code=500, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateUserResponseModel(BaseModel):
    message: str


@app.put(
    "/user/update",
    description="ユーザ情報の更新用エンドポイント",
    response_model=UpdateUserResponseModel,
)
async def update_user_endpoint(
    _user: dict = Body(
        ...,
        example={
            "userId": "12345",
            "email": "yamada@yamada.com",
            "userName": "山田",
        },
    ),
):
    try:
        user = UpdateUserRequest.from_dict(_user)
        success, error = await update_user_doc(user_id=user.user_id, user_instance=user)
        if success:
            return {"message": "User update successful", "userId": user.user_id}
        else:
            raise HTTPException(status_code=500, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DeleteUserResponseModel(BaseModel):
    message: str


@app.delete(
    "/user/{userId}",
    description="ユーザ情報の削除用エンドポイント",
    response_model=DeleteUserResponseModel,
)
async def delete_user_endpoint(userId: str):
    try:
        user_id = userId
        success, error = await delete_user_doc(user_id=user_id)
        if success:
            # TODO: ユーザーの使用したFlashcardを削除する処理を実装
            return {"message": "User delete successful"}
        else:
            raise HTTPException(status_code=500, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GetFlashcardsResponseModel(BaseModel):
    message: str
    flashcards: list[FlashcardResponseModel]


@app.get(
    "/flashcard/{userId}",
    description="ユーザのフラッシュカード一覧取得用エンドポイント",
    response_model=GetFlashcardsResponseModel,
)
async def get_flashcards_endpoint(userId: str):
    try:
        user_id = userId
        success, error, flashcard_responses = await get_flashcard_list(user_id)
        if not success:
            raise HTTPException(status_code=500, detail=error)
        return {
            "message": "Flashcards retrieved successfully",
            "flashcards": [flashcard.to_dict() for flashcard in flashcard_responses],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateFlashcardResponseModel(BaseModel):
    message: str


@app.put(
    "/flashcard/update/checkFlag",
    description="フラッシュカードのチェックフラグ更新用エンドポイント",
    response_model=UpdateFlashcardResponseModel,
)
async def update_check_flag_endpoint(
    _request: dict = Body(..., example={"flashcardId": "12345", "checkFlag": True}),
):
    try:
        # リクエストボディの型を確認
        update_flag_request = UpdateFlagRequest.from_dict(_request)
        success, error = await update_flashcard_doc_on_check_flag(
            flashcard_id=update_flag_request.flashcard_id,
            check_flag=update_flag_request.check_flag,
        )
        if success:
            return {"message": "Check flag updated successfully"}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put(
    "/flashcard/update/memo",
    description="フラッシュカードのメモ更新用エンドポイント",
    response_model=UpdateFlashcardResponseModel,
)
async def update_flashcard_memo_endpoint(
    _request: dict = Body(
        ..., example={"flashcardId": "12345", "memo": "新しいメモ内容"}
    ),
):
    try:
        update_memo_request = UpdateMemoRequest.from_dict(_request)
        success, error = await update_flashcard_doc_on_memo(
            flashcard_id=update_memo_request.flashcard_id, memo=update_memo_request.memo
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


@app.put(
    "/flashcard/update/usingMeaningIdList",
    description="フラッシュカードの意味IDリスト更新用エンドポイント",
    response_model=UpdateFlashcardResponseModel,
)
async def update_using_meaning_id_list_endpoint(
    _request: dict = Body(
        ..., example={"flashcardId": "12345", "usingMeaningIdList": ["67890", "54321"]}
    ),
):
    try:
        create_meaning_request = UpdateUsingMeaningsRequest.from_dict(_request)
        success, error = await update_flashcard_doc_on_using_meaning_id_list(
            flashcard_id=create_meaning_request.flashcard_id,
            using_meaning_id_list=create_meaning_request.using_meaning_id_list,
        )
        if error:
            raise HTTPException(status_code=500, detail=error)
        if success:
            return {"message": "Using meaning ID list updated successfully"}
        else:
            raise HTTPException(status_code=400, detail=error)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateMediaResponseModel(BaseModel):
    message: str
    media_id: str


@app.post(
    "/media/create",
    description="フラッシュカード用のメディアを生成するエンドポイント",
    response_model=CreateMediaResponseModel,
)
async def setup_media_endpoint(
    _request: dict = Body(
        ...,
        example={
            "flashcardId": "12345",
            "oldMediaId": "67890",
            "meaningId": "54321",
            "pos": "noun",
            "word": "cat",
            "meaning": "猫",
            "example": "猫がマットの上に座っていました。",
            "explanation": "しばしば犬と対比される小型の哺乳類で、一般的にペットとして飼われる。",
            "coreMeaning": None,
            "generationType": "text-to-image",
            "templateId": "template_001",
            "userPrompt": "あなたは画像生成AIでイラストを生成するための～",
            "otherSettings": ["猫の種類は三毛猫にしてください。"],
            "allowGeneratingPerson": True,
            "inputMediaUrls": [
                "https://example.com/input1.jpg",
            ],
        },
    ),
):
    try:
        create_media_request = CreateMediaRequest.from_dict(_request)
        success, error, media_id = await setup_media(
            create_media_request=create_media_request
        )
        if error:
            raise HTTPException(status_code=500, detail=error)
        if success:
            return {
                "message": "Flashcard comparison ID updated successfully",
                "media_id": media_id,
            }

    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GetNoComparedMediasResponseModel(BaseModel):
    message: str
    medias: list[NotComparedMediaResponseModel]


@app.post(
    "/comparison/{userId}",
    description="未比較のメディア一括取得用エンドポイント",
    response_model=GetNoComparedMediasResponseModel,
)
async def get_comparison_endpoint(userId: str):
    try:
        user_id = userId
        success, error, media_list = await get_not_compared_media_list(user_id=user_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if success:
            return {
                "message": "Not compared medias retrieved successfully",
                "medias": [media.to_dict() for media in media_list],
            }

    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CompareMediasResponseModel(BaseModel):
    message: str


@app.post(
    "/comparison/update",
    description="メディアの比較結果送信用エンドポイント",
    response_model=CompareMediasResponseModel,
)
async def update_comparison_endpoint(
    _request: dict = Body(
        ...,
        example={
            "flashcardId": "12345",
            "comparisonId": "null",
            "oldMediaId": "54321",
            "newMediaId": "67890",
            "isSelectedNew": True,
        },
    ),
):
    try:
        compare_medias_request = CompareMediasRequest.from_dict(_request)
        success, error = await compare_medias(
            compare_medias_request=compare_medias_request
        )
        if error:
            raise HTTPException(status_code=500, detail=error)
        if success:
            return {"message": "Flashcard comparison ID updated successfully"}

    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GetAllMeaningsResponseModel(BaseModel):
    message: str
    meanings: list[MeaningResponseModel]


@app.get(
    "/meaning/{wordId}",
    description="単語の全ての意味一覧取得用エンドポイント",
    response_model=GetAllMeaningsResponseModel,
)
async def get_meanings_endpoint(wordId: str):
    try:
        word_id = wordId
        word_instance, error = await read_word_doc(word_id=word_id)
        if error:
            raise HTTPException(status_code=500, detail=error)
        if len(word_instance.meaning_id_list) == 0:
            raise HTTPException(
                status_code=404, detail="この単語には意味が登録されていません。"
            )
        meanings, error = await read_meaning_docs(
            meaning_ids=word_instance.meaning_id_list
        )
        if error:
            raise HTTPException(status_code=500, detail=error)
        if not meanings:
            raise HTTPException(status_code=404, detail="意味が見つかりません")
        return {
            "message": "Meanings retrieved successfully",
            "meanings": [meaning.to_dict() for meaning in meanings],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GetTemplateResponseModel(BaseModel):
    message: str
    templates: list[TemplatesResponseModel]


# プロンプトのテンプレート全取得API
@app.get(
    "/template",
    description="ユーザのフラッシュカード一覧取得用エンドポイント",
    response_model=GetTemplateResponseModel,
)
async def get_template_endpoint():
    try:
        template_list, error = await read_prompt_template_docs()
        if error:
            raise HTTPException(status_code=500, detail=error)
        return {
            "message": "User templates retrieved successfully",
            "templates": [template_list.to_dict() for template_list in template_list],
        }

    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateTemplateResponseModel(BaseModel):
    message: str
    templateId: str


# プロンプトのテンプレート作成API
@app.post(
    "/template/create",
    description="プロンプトのテンプレート作成用エンドポイント",
    response_model=CreateTemplateResponseModel,
)
async def create_template_endpoint(
    _request: dict = Body(
        ...,
        example={
            "generationType": "text-to-image",
            "target": "例文",
            "preText": "Generate an image of a cat",
        },
    ),
):
    try:
        create_template_request = CreateTemplateRequest.from_dict(_request)
        now = datetime.now()
        template_instance = PromptTemplateSchema(
            generation_type=create_template_request.generation_type,
            target=create_template_request.target,
            pre_text=create_template_request.pre_text,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
        )
        success, error, template_id = await create_prompt_template_doc(
            template_instance=template_instance
        )
        if error:
            raise HTTPException(status_code=500, detail=error)
        if success:
            return {
                "message": "Template created successfully",
                "templateId": template_id,
            }

    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateTemplateResponseModel(BaseModel):
    message: str


# プロンプトのテンプレート更新API
@app.put(
    "/template/update",
    description="プロンプトのテンプレート更新用エンドポイント",
    response_model=UpdateTemplateResponseModel,
)
async def update_template_endpoint(
    _request: dict = Body(
        ...,
        example={
            "templateId": "12345",
            "generationType": "text-to-image",
            "target": "例文",
            "preText": "Generate an image of a cat",
        },
    ),
):
    try:
        update_template_request = UpdateTemplateRequest.from_dict(_request)
        now = datetime.now()
        template_instance = PromptTemplateSchema(
            generation_type=update_template_request.generation_type,
            target=update_template_request.target,
            pre_text=update_template_request.pre_text,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
        )
        success, error = await update_prompt_template_doc(
            template_id=update_template_request.template_id,
            template_instance=template_instance,
        )
        if error:
            raise HTTPException(status_code=500, detail=error)
        if success:
            return {
                "message": "Template updated successfully",
            }
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
