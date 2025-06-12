import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

BASE_URL = "http://test"

# @pytest.mark.asyncio
# async def test_get_user_success():
#     # 正常系: 存在するユーザーIDでユーザー情報を取得する
#     async with AsyncClient( base_url=BASE_URL) as ac:
#         response = await ac.get("/user/valid_user_id")
#     assert response.status_code == 200
#     assert response.json()["message"] == "User retrieved successfully"

@pytest.mark.asyncio
async def test_get_user_not_found():
    # 異常系: 存在しないユーザーIDで404エラーを確認する
    response = client.get("/user/invalid_user_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "ユーザーが見つかりません"

# @pytest.mark.asyncio
# async def test_setup_user_success():
#     # 正常系: 新規ユーザーを登録する
#     payload = {"email": "test@example.com", "displayName": "Test User"}
#     response = client.post("/user/setup", json=payload)
#     assert response.status_code == 200
#     assert response.json()["message"] == "User setup successful"

# @pytest.mark.asyncio
# async def test_setup_user_duplicate_email():
#     # 異常系: 既存のメールアドレスで400エラーを確認する
#     payload = {"email": "duplicate@example.com", "displayName": "Duplicate User"}
#     response = client.post("/user/setup", json=payload)
#     assert response.status_code == 400
#     assert "このメールアドレスは既に登録されています。" in response.json()["detail"]

# @pytest.mark.asyncio
# async def test_update_user_success():
#     # 正常系: ユーザー情報を更新する
#     payload = {"userId": "valid_user_id", "email": "updated@example.com", "displayName": "Updated User"}
#     response = client.put("/user/update", json=payload)
#     assert response.status_code == 200
#     assert response.json()["message"] == "User update successful"

# @pytest.mark.asyncio
# async def test_update_user_not_found():
#     # 異常系: 存在しないユーザーIDで404エラーを確認する
#     payload = {"userId": "invalid_user_id", "email": "updated@example.com", "displayName": "Updated User"}
#     response = client.put("/user/update", json=payload)
#     assert response.status_code == 404
#     assert response.json()["detail"] == "ユーザーが見つかりません"

# @pytest.mark.asyncio
# async def test_get_flashcards_success():
#     # 正常系: ユーザーのフラッシュカード一覧を取得する
#     response = client.get("/flashcard/valid_user_id")
#     assert response.status_code == 200
#     assert response.json()["message"] == "Flashcards retrieved successfully"

# @pytest.mark.asyncio
# async def test_get_flashcards_not_found():
#     # 異常系: 存在しないユーザーIDで404エラーを確認する
#     response = client.get("/flashcard/invalid_user_id")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "ユーザーが見つかりません"

# @pytest.mark.asyncio
# async def test_update_flashcard_memo_success():
#     # 正常系: フラッシュカードのメモを更新する
#     payload = {"flashcardId": "valid_flashcard_id", "memo": "Updated memo"}
#     response = client.put("/flashcard/update/memo", json=payload)
#     assert response.status_code == 200
#     assert response.json()["message"] == "Flashcard memo update successful"

# @pytest.mark.asyncio
# async def test_update_flashcard_memo_not_found():
#     # 異常系: 存在しないフラッシュカードIDで404エラーを確認する
#     payload = {"flashcardId": "invalid_flashcard_id", "memo": "Updated memo"}
#     response = client.put("/flashcard/update/memo", json=payload)
#     assert response.status_code == 404
#     assert response.json()["detail"] == "フラッシュカードが見つかりません"
