"""
Integration tests for the register -> login -> me authentication flow.

These hit the real FastAPI app (via httpx.AsyncClient + ASGITransport) and a
real SQLite database (see conftest.py), so they exercise the full stack:
routers -> services -> repositories -> ORM models -> password hashing -> JWT.
"""


async def test_register_new_user_succeeds(client):
    payload = {
        "email": "jane.doe@example.com",
        "username": "janedoe",
        "full_name": "Jane Doe",
        "password": "supersecret123",
    }

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert data["is_active"] is True
    # The response model must never leak the password / hash.
    assert "password" not in data
    assert "hashed_password" not in data


async def test_register_duplicate_email_is_rejected(client):
    payload = {
        "email": "duplicate@example.com",
        "username": "firstuser",
        "password": "supersecret123",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    payload["username"] = "seconduser"  # different username, same email
    second = await client.post("/api/v1/auth/register", json=payload)

    assert second.status_code == 409


async def test_register_weak_password_is_rejected(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "username": "weakuser", "password": "123"},
    )

    # Pydantic's min_length=6 constraint on UserCreate.password
    assert response.status_code == 422


async def test_login_with_correct_credentials_returns_jwt(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "supersecret123",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "supersecret123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str) and len(data["access_token"]) > 20


async def test_login_with_wrong_password_is_rejected(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "username": "wrongpassuser",
            "password": "supersecret123",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "not-the-password"},
    )

    assert response.status_code == 401


async def test_login_with_unknown_email_is_rejected(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )

    assert response.status_code == 401


async def test_me_without_token_is_rejected(client):
    response = await client.get("/api/v1/auth/me")

    # FastAPI's HTTPBearer returns 403 when no Authorization header is sent.
    assert response.status_code == 403


async def test_me_with_invalid_token_is_rejected(client):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


async def test_me_with_valid_token_returns_current_user(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "username": "meuser",
            "full_name": "Me User",
            "password": "supersecret123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "supersecret123"},
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["username"] == "meuser"
