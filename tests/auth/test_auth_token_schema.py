from auth.application.schemas import TokenResponse


def test_token_response_can_include_refresh_token_for_mobile_clients():
    response = TokenResponse(
        access_token="access",
        refresh_token="refresh",
        expires_in=900,
    )

    assert response.model_dump()["refresh_token"] == "refresh"
