"""Verificar el token recibido; no consultar ni administrar usuarios de Clerk."""

import jwt
from jwt import PyJWKClient

from app.errors import ApiError, ErrorCode
from app.settings import Settings
from app.users import UserIdentity


class SessionAuthenticator:
    def __init__(self, settings: Settings) -> None:
        self._issuer = settings.clerk_issuer
        self._public_key = settings.clerk_jwt_key
        self._origins = settings.clerk_authorized_parties or settings.cors_origins
        self._allowed_users = settings.allowed_clerk_user_ids
        self._jwks = None
        if self._issuer:
            self._jwks = PyJWKClient(f"{self._issuer}/.well-known/jwks.json", timeout=10)

    def verify(self, token: str) -> UserIdentity:
        if self._issuer is None:
            raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE)

        claims = self._verify_signature_and_dates(token)
        subject = claims["sub"]
        session_id = claims["sid"]
        has_session_identity = (
            isinstance(subject, str) and subject.startswith("user_")
            and isinstance(session_id, str) and session_id.startswith("sess_")
        )
        has_authorized_origin = claims.get("azp") in self._origins
        has_active_session = claims.get("sts") != "pending"
        if not (has_session_identity and has_authorized_origin and has_active_session):
            raise ApiError(ErrorCode.INVALID_SESSION)
        if self._allowed_users and subject not in self._allowed_users:
            raise ApiError(ErrorCode.FORBIDDEN)
        return UserIdentity(issuer=self._issuer, subject=subject)

    def _verify_signature_and_dates(self, token: str) -> dict:
        try:
            key = self._signing_key(token)
            return jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                issuer=self._issuer,
                options={
                    "require": ["iss", "sub", "sid", "exp", "nbf", "iat"],
                    "verify_aud": False,
                },
            )
        except (jwt.PyJWKClientConnectionError, jwt.InvalidKeyError):
            raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE) from None
        except (jwt.PyJWTError, ValueError, TypeError):
            raise ApiError(ErrorCode.INVALID_SESSION) from None

    def _signing_key(self, token: str):
        if self._public_key:
            return self._public_key.get_secret_value()
        if self._jwks is None:
            raise ApiError(ErrorCode.PROVIDER_UNAVAILABLE)
        return self._jwks.get_signing_key_from_jwt(token).key
