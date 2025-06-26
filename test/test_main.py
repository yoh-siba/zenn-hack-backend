from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# 正常系：ルートエンドポイントが正しく動作する場合
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


################################################
############## ユーザー関連のテスト ##############
################################################


# 正常系：新しいユーザーをセットアップする場合
def test_user_setup():
    response = client.post(
        "/user/setup",
        json={"userId": "sampleId", "email": "sample@sample.com", "userName": "山田"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User setup successful"}


# 異常系：無効なリクエストボディで新しいユーザーをセットアップする場合
def test_user_setup_invalid_body():
    response = client.post(
        "/user/setup",
        json={"userId": "", "email": "invalid_email", "userName": ""},
    )
    assert response.status_code == 502
    # バリデーションエラーが発生する場合


# 正常系：指定したユーザーIDでユーザー情報を取得する場合
def test_get_user():
    response = client.get("/user/sampleId")
    assert response.status_code == 200


# 異常系：無効なユーザーIDでユーザー情報を取得する場合
def test_get_user_invalid_id():
    response = client.get("/user/invalid_id")
    assert response.status_code == 500
    assert response.json() == {"detail": "指定されたユーザーは存在しません"}


# 正常系：既存のユーザー情報を更新する場合
def test_user_update():
    response = client.put(
        "/user/update",
        json={
            "userId": "sampleId",
            "email": "sample@sample.com",
            "userName": "山田2",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "User update successful",
    }


# 異常系：無効なリクエストボディで既存のユーザー情報を更新する場合
def test_user_update_invalid_body():
    response = client.put(
        "/user/update",
        json={"userId": "", "email": "invalid_email", "userName": ""},
    )
    assert response.status_code == 502
    # バリデーションエラーが発生する場合


# 正常系：指定したユーザーIDでユーザー情報を取得する場合
def test_get_user2():
    response = client.get("/user/sampleId")
    assert response.status_code == 200


# 正常系：指定したユーザーIDでユーザーを削除する場合
def test_delete_user():
    response = client.delete("/user/sampleId")
    assert response.status_code == 200
    assert response.json() == {"message": "User delete successful"}


# 異常系：削除済みのユーザーIDでユーザーを削除できない場合
def test_delete_user2():
    response = client.delete("/user/sampleId")
    assert response.status_code == 404
    assert response.json() == {"detail": "指定されたユーザーは存在しません"}


# 異常系：削除済みのユーザーIDでユーザー情報が取得できない場合
def test_get_user3():
    response = client.get("/user/sampleId")
    assert response.status_code == 500
    assert response.json() == {"detail": "指定されたユーザーは存在しません"}


##############################################
######### フラッシュカード関連のテスト #########
##############################################


# # 正常系：指定したユーザーIDでフラッシュカード一覧を取得する場合
# def test_get_flashcards():
#     response = client.get("/flashcard/U0R53LJvpZOCdvVDbUYF")
#     assert response.status_code == 200
#     assert response.json() == {
#         "message": "Flashcards retrieved successfully",
#         "flashcards": [],
#     }

# # 正常系：指定したユーザーIDでユーザー情報を取得する場合
# def test_get_user2():
#     response = client.get("/user/sampleId")
#     assert response.status_code == 200
#     assert response.json() == {
#         "message": "User retrieved successfully",
#         "user": {
#             "userId": "sampleId",
#             "email": "sample@sample.com",
#             "userName": "山田",
#             "flashcardIdList": [
#                 "U0R53LJvpZOCdvVDbUYF",
#                 "iota2j31aw9opZXXEQAy",
#                 "qTZ97Xx6lF3rldphGOBS",
#                 "qiRQwQhwuokaclEG4c37",
#                 "tlqZh0L3POx6cFzpBpo3",
#             ],
#         },
#     }


# # 異常系：無効なユーザーIDでフラッシュカード一覧を取得する場合
# def test_get_flashcards_invalid_id():
#     response = client.get("/flashcard/invalid_id")
#     assert response.status_code == 500
#     # assert response.json() == {"detail": "Invalid user ID"}


# # 正常系：フラッシュカードのチェックフラグを更新する場合
# def test_update_check_flag():
#     response = client.put(
#         "/flashcard/update/checkFlag",
#         json={"flashcardId": "U0R53LJvpZOCdvVDbUYF", "checkFlag": True},
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Check flag updated successfully"}


# # 異常系：無効なリクエストボディでフラッシュカードのチェックフラグを更新する場合
# def test_update_check_flag_invalid_body():
#     response = client.put(
#         "/flashcard/update/checkFlag",
#         json={"flashcardId": "", "checkFlag": "invalid_flag"},
#     )
#     assert response.status_code == 500
#     # assert response.json() == {"detail": "Invalid request format"}


# # 正常系：フラッシュカードのメモを更新する場合
# def test_update_memo():
#     response = client.put(
#         "/flashcard/update/memo",
#         json={
#             "flashcardId": "U0R53LJvpZOCdvVDbUYF",
#             "memo": "更新されたメモ内容",
#         },
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Flashcard memo update successful"}


# # 異常系：無効なリクエストボディでフラッシュカードのメモを更新する場合
# def test_update_memo_invalid_body():
#     response = client.put(
#         "/flashcard/update/memo",
#         json={"flashcardId": "", "memo": ""},
#     )
#     assert response.status_code == 500
#     # assert response.json() == {"detail": "Invalid request format"}


# # 正常系：フラッシュカードの意味IDリストを更新する場合
# def test_update_using_meaning_id_list():
#     response = client.put(
#         "/flashcard/update/usingMeaningIdList",
#         json={
#             "flashcardId": "U0R53LJvpZOCdvVDbUYF",
#             "usingMeaningIdList": ["L35JDrI7sVIrkhxNulsE"],
#         },
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Using meaning ID list updated successfully"}


# # 異常系：無効なリクエストボディでフラッシュカードの意味IDリストを更新する場合
# def test_update_using_meaning_id_list_invalid_body():
#     response = client.put(
#         "/flashcard/update/usingMeaningIdList",
#         json={"flashcardId": "", "usingMeaningIdList": []},
#     )
#     assert response.status_code == 500
#     # assert response.json() == {"detail": "Invalid request format"}


# # 正常系：新しいメディアを作成する場合
# def test_media_create():
#     response = client.post(
#         "/media/create",
#         json={
#             "flashcardId": "created_flashcard_id",
#             "oldMediaId": "67890",
#             "meaningId": "54321",
#             "generationType": "text-to-image",
#             "templateId": "template_001",
#             "userPrompt": "Generate an image of a cat",
#             "allowGeneratingPerson": True,
#             "inputMediaUrls": [],
#         },
#     )
#     assert response.status_code == 200
#     assert response.json() == {
#         "message": "Media created successfully",
#         "media_id": "new_media_id",
#     }


# # 異常系：無効なリクエストボディで新しいメディアを作成する場合
# def test_media_create_invalid_body():
#     response = client.post(
#         "/media/create",
#         json={
#             "flashcardId": "",
#             "oldMediaId": "",
#             "meaningId": "",
#             "generationType": "",
#             "templateId": "",
#             "userPrompt": "",
#             "allowGeneratingPerson": False,
#             "inputMediaUrls": [],
#         },
#     )
#     assert response.status_code == 500
#     # assert response.json() == {"detail": "Invalid request format"}


# # 正常系：指定したユーザーIDで比較データを取得する場合
# def test_comparison_get():
#     response = client.post("/comparison/cergU7H1N7gRnzZmiZcC")
#     assert response.status_code == 200
#     assert response.json() == {
#         "message": "Comparison data retrieved successfully",
#         "medias": [],
#     }


# # 異常系：無効なユーザーIDで比較データを取得する場合
# def test_comparison_get_invalid_id():
#     response = client.post("/comparison/invalid_id")
#     assert response.status_code == 500
#     # assert response.json() == {"detail": "Invalid user ID"}


# # 正常系：比較結果を更新する場合
# def test_comparison_update():
#     response = client.post(
#         "/comparison/update",
#         json={
#             "flashcardId": "U0R53LJvpZOCdvVDbUYF",
#             "comparisonId": "comparison_id",
#             "oldMediaId": "67890",
#             "newMediaId": "54321",
#             "isSelectedNew": True,
#         },
#     )
#     assert response.status_code == 200
#     assert response.json() == {"message": "Comparison updated successfully"}


# # 異常系：無効なリクエストボディで比較結果を更新する場合
# def test_comparison_update_invalid_body():
#     response = client.post(
#         "/comparison/update",
#         json={
#             "flashcardId": "",
#             "comparisonId": "",
#             "oldMediaId": "",
#             "newMediaId": "",
#             "isSelectedNew": False,
#         },
#     )
#     assert response.status_code == 500
#     # assert response.json() == {"detail": "Invalid request format"}
