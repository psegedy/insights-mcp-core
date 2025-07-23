from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749 import OAuth2Token
import httpx
from typing import Any

TOKEN_ENDPOINT = (
    "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"
)
HCC_API_BASE = "https://console.redhat.com/api"
USER_AGENT = "insights-mcp/1.0"


class InsightsOAuth2Client(AsyncOAuth2Client):
    def __init__(self, refresh_token: str):
        token_dict = {"refresh_token": refresh_token}
        token = OAuth2Token(token_dict)
        headers = {"User-Agent": USER_AGENT}
        super().__init__(
            "rhsm-api", token=token, token_endpoint=TOKEN_ENDPOINT, headers=headers
        )

    async def _api_call(self, fn, *args, **kwargs) -> dict[str, Any]:
        if "access_token" not in self.token or self.token.is_expired():
            await self.refresh_token()
        try:
            response = await fn(*args, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return {
                "Unexpected HTTP status code": f"{response.status_code}, content: {response.content}"
            }
        except Exception as exc:
            return {"Unhadled error": str(exc)}


class InsightsClient:
    def __init__(self, refresh_token: str):
        self.client = InsightsOAuth2Client(refresh_token)

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None, **kwargs
    ) -> dict[str, Any]:
        url = f"{HCC_API_BASE}/{endpoint}"
        return await self.client._api_call(self.client.get, url=url, params=params, **kwargs)

    async def post(
        self, endpoint: str, json: dict[str, Any] | None = None, **kwargs
    ) -> dict[str, Any]:
        url = f"{HCC_API_BASE}/{endpoint}"
        return await self.client._api_call(self.client.post, url=url, json=json, **kwargs)
