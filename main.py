from datetime import datetime

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

from src.models.exceptions import ServiceException
from src.models.types import (
    AddUsingFlashcardRequest,
    CompareMediasRequest,
    CreateDefaultFlashcardRequest,
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
    WordForExtensionResponseModel,
)
from src.services.add_using_flashcard import add_using_flashcard
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
from src.services.get_word_for_extension import get_word_for_extension
from src.services.setup_default_flashcard import setup_default_flashcard
from src.services.setup_media import setup_media
from src.services.setup_user import setup_user

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://zenn-hack-backend.web.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# エラータイプとHTTPステータスコードのマッピング
ERROR_TYPE_TO_HTTP_STATUS = {
    "not_found": 404,
    "validation": 400,
    "permission": 403,
    "conflict": 409,
    "external_api": 502,
    "general": 500,
}


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
        user_instance = await read_user_doc(userId)
        if not user_instance:
            raise HTTPException(
                status_code=404, detail="指定されたユーザーは存在しません"
            )
        user_response = user_instance.to_dict()
        user_response["user_id"] = userId
        return {
            "message": "User retrieved successfully",
            "user": UserResponse.from_dict(user_response).to_dict(),
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        await setup_user(user)
        return {"message": "User setup successful"}
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        await update_user_doc(user_id=user.user_id, user_instance=user)
        return {"message": "User update successful", "userId": user.user_id}
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class AddUsingFlashcardResponseModel(BaseModel):
    message: str


@app.put(
    "/user/add/usingFlashcard",
    description="ユーザが使用するフラッシュカードの追加用エンドポイント",
    response_model=AddUsingFlashcardResponseModel,
)
async def add_using_flashcard_endpoint(
    _user: dict = Body(
        ...,
        example={
            "userId": "12345",
            "flashcardId": "67890",
        },
    ),
):
    try:
        user = AddUsingFlashcardRequest.from_dict(_user)
        await add_using_flashcard(user.user_id, user.flashcard_id)
        return {"message": "User update successful"}
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        await delete_user_doc(user_id=user_id)
        # TODO: ユーザーの使用したFlashcardを削除する処理を実装
        return {"message": "User delete successful"}
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        flashcard_responses = await get_flashcard_list(user_id)
        return {
            "message": "Flashcards retrieved successfully",
            "flashcards": [flashcard.to_dict() for flashcard in flashcard_responses],
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        await update_flashcard_doc_on_check_flag(
            flashcard_id=update_flag_request.flashcard_id,
            check_flag=update_flag_request.check_flag,
        )
        return {"message": "Check flag updated successfully"}
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        await update_flashcard_doc_on_memo(
            flashcard_id=update_memo_request.flashcard_id, memo=update_memo_request.memo
        )
        return {"message": "Flashcard memo update successful"}
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        await update_flashcard_doc_on_using_meaning_id_list(
            flashcard_id=create_meaning_request.flashcard_id,
            using_meaning_id_list=create_meaning_request.using_meaning_id_list,
        )
        return {"message": "Using meaning ID list updated successfully"}
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateDefaultFlashcardResponseModel(BaseModel):
    message: str
    flashcardId: str


@app.post(
    "/flashcard/create",
    description="デフォルトフラッシュカード作成用エンドポイント",
    response_model=CreateDefaultFlashcardResponseModel,
)
async def create_default_flashcard_endpoint(
    _request: dict = Body(
        ...,
        example={
            "word": "example",
        },
    ),
):
    try:
        create_flashcard_request = CreateDefaultFlashcardRequest.from_dict(_request)
        print(
            f"Received request to create default flashcard for word: {create_flashcard_request.word}"
        )
        flashcard_id = await setup_default_flashcard(create_flashcard_request.word)
        return {
            "message": "Default flashcard created successfully",
            "flashcardId": flashcard_id,
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateMediaResponseModel(BaseModel):
    message: str
    comparisonId: str
    newMediaId: str
    newMediaUrls: list[str]


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
            "translation": "猫",
            "exampleJpn": "猫がマットの上に座っていました。",
            "explanation": "しばしば犬と対比される小型の哺乳類で、一般的にペットとして飼われる。",
            "coreMeaning": "無ければNullで",
            "generationType": "text-to-image",
            "templateId": "template_001",
            "userPrompt": "あなたは画像生成AIでイラストを生成するための～",
            "otherSettings": ["猫の種類は三毛猫にしてください。", "無ければNullでで"],
            "allowGeneratingPerson": True,
            "inputMediaUrls": ["http://example.com/image1.jpg", "無ければNullで"],
        },
    ),
):
    try:
        create_media_request = CreateMediaRequest.from_dict(_request)
        setup_result = await setup_media(create_media_request=create_media_request)
        return {
            "message": "Flashcard comparison ID updated successfully",
            "comparisonId": setup_result.comparison_id,
            "newMediaId": setup_result.media_id,
            "newMediaUrls": setup_result.media_urls,
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GetNoComparedMediasResponseModel(BaseModel):
    message: str
    comparisons: list[NotComparedMediaResponseModel]


@app.get(
    "/comparison/{userId}",
    description="未比較のメディア一括取得用エンドポイント",
    response_model=GetNoComparedMediasResponseModel,
)
async def get_comparison_endpoint(userId: str):
    try:
        user_id = userId
        media_list = await get_not_compared_media_list(user_id=user_id)
        return {
            "message": "Not compared medias retrieved successfully",
            "comparisons": [media.to_dict() for media in media_list],
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CompareMediasResponseModel(BaseModel):
    message: str


@app.put(
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
        print(f"Received comparison request: {compare_medias_request}")
        await compare_medias(compare_medias_request=compare_medias_request)
        return {"message": "Flashcard comparison ID updated successfully"}
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        word_instance = await read_word_doc(word_id=word_id)
        if not word_instance:
            raise HTTPException(
                status_code=404, detail="指定された単語が見つかりません"
            )
        if len(word_instance.meaning_id_list) == 0:
            raise HTTPException(
                status_code=404, detail="この単語には意味が登録されていません。"
            )
        meanings = await read_meaning_docs(meaning_ids=word_instance.meaning_id_list)
        if not meanings:
            raise HTTPException(status_code=404, detail="意味が見つかりません")
        return {
            "message": "Meanings retrieved successfully",
            "meanings": [meaning.to_dict() for meaning in meanings],
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        template_list = await read_prompt_template_docs()
        return {
            "message": "User templates retrieved successfully",
            "templates": [template.to_dict() for template in template_list],
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        template_id = await create_prompt_template_doc(
            template_instance=template_instance
        )
        return {
            "message": "Template created successfully",
            "templateId": template_id,
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
        await update_prompt_template_doc(
            template_id=update_template_request.template_id,
            template_instance=template_instance,
        )
        return {
            "message": "Template updated successfully",
        }
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid request format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/word/{word}",
    description="単語の詳細情報取得用エンドポイント",
    response_model=WordForExtensionResponseModel,
)
async def get_word_for_extension_endpoint(word: str):
    try:
        word_response = await get_word_for_extension(word)
        return word_response.to_dict()
    except ServiceException as se:
        status_code = ERROR_TYPE_TO_HTTP_STATUS.get(se.error_type, 500)
        raise HTTPException(status_code=status_code, detail=se.message)
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
