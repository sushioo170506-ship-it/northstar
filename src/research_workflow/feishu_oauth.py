"""User OAuth helpers for personal Feishu documents without tenant admin tokens."""

from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable


DEFAULT_SCOPES = (
    "offline_access",
    "docx:document",
    "docx:document.block:convert",
    "sheets:spreadsheet",
)


class FeishuOAuthClient:
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        redirect_uri: str,
        *,
        base_url: str = "https://open.feishu.cn",
        transport: Callable[
            [str, str, dict[str, Any], dict[str, str]], dict[str, Any]
        ] | None = None,
    ) -> None:
        if not app_id or not app_secret or not redirect_uri:
            raise ValueError("飞书OAuth需要app_id、app_secret和redirect_uri")
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.base_url = base_url.rstrip("/")
        self.transport = transport

    def authorization_url(
        self,
        *,
        scopes: tuple[str, ...] = DEFAULT_SCOPES,
        state: str | None = None,
    ) -> tuple[str, str]:
        state = state or secrets.token_urlsafe(24)
        query = urllib.parse.urlencode(
            {
                "client_id": self.app_id,
                "redirect_uri": self.redirect_uri,
                "scope": " ".join(scopes),
                "response_type": "code",
                "state": state,
            }
        )
        return (
            "https://accounts.feishu.cn/open-apis/authen/v1/authorize?" + query,
            state,
        )

    def exchange_code(self, code: str) -> dict[str, Any]:
        if not code.strip():
            raise ValueError("OAuth授权码不能为空")
        return self._token_request(
            {
                "grant_type": "authorization_code",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
        )

    def refresh(self, refresh_token: str) -> dict[str, Any]:
        if not refresh_token.strip():
            raise ValueError("refresh_token不能为空")
        return self._token_request(
            {
                "grant_type": "refresh_token",
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "refresh_token": refresh_token,
            }
        )

    def _token_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        path = "/open-apis/authen/v2/oauth/token"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        if self.transport:
            response = self.transport("POST", path, payload, headers)
        else:
            request = urllib.request.Request(
                self.base_url + path,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as opened:
                    response = json.loads(opened.read().decode("utf-8"))
            except (urllib.error.URLError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"飞书OAuth请求失败: {exc}") from exc
        if response.get("code", 0) != 0:
            raise RuntimeError(
                f"飞书OAuth失败 code={response.get('code')}: "
                f"{response.get('msg', 'unknown error')}"
            )
        data = response.get("data", response)
        if not data.get("access_token"):
            raise RuntimeError("飞书OAuth响应缺少access_token")
        return data
