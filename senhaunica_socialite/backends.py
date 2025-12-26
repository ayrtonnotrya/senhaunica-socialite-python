import os
from typing import Optional, Any
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest
from .client import SenhaUnicaClient

User = get_user_model()

class SenhaUnicaBackend(ModelBackend):
    """
    Custom Authentication Backend for Senha Unica USP.
    """

    def authenticate(self, request: HttpRequest, oauth_token: str = None, oauth_token_secret: str = None, oauth_verifier: str = None, **kwargs: Any) -> Optional[AbstractBaseUser]:
        """
        Authenticates the user using the OAuth 1.0a credentials.

        Args:
            request: The HTTP request.
            oauth_token: The generic Request Token (from step 1).
            oauth_token_secret: The Request Token Secret (stored in session).
            oauth_verifier: The verification code returned by USP.

        Returns:
            The authenticated User object or None.
        """
        if not oauth_token or not oauth_verifier or not oauth_token_secret:
            return None

        # Load credentials from env
        key = os.getenv("SENHAUNICA_KEY")
        secret = os.getenv("SENHAUNICA_SECRET")
        # Callback URL is needed for the client init, though arguably not used in access_token step
        # depending on strictness. We pass it for consistency.
        callback = os.getenv("SENHAUNICA_CALLBACK_URL", "http://localhost:8000/callback")
        callback_id = os.getenv("SENHAUNICA_CALLBACK_ID")
        env = os.getenv("SENHAUNICA_ENV", "prod")

        if not key or not secret:
            # If credentials are missing, we cannot proceed
            return None

        client = SenhaUnicaClient(key, secret, callback, callback_id=callback_id, env=env)

        try:
            # 1. Exchange Request Token for Access Token
            token_resp = client.fetch_access_token(oauth_token, oauth_token_secret, oauth_verifier)
            access_token = token_resp['oauth_token']
            access_token_secret = token_resp['oauth_token_secret']

            # 2. Fetch User Info
            user_info = client.get_user_info(access_token, access_token_secret)
            
            # Map USP response keys (based on 'wsusuario' verification)
            # Keys found: loginUsuario, nomeUsuario, emailPrincipalUsuario, emailUspUsuario
            codpes = user_info.get('loginUsuario') or user_info.get('codpes')
            
            if not codpes:
                return None

            # 3. Get or Create User
            # We treat 'codpes' as the username
            user, created = User.objects.get_or_create(username=str(codpes))
            
            # Update fields
            user.first_name = user_info.get('nomeUsuario') or user_info.get('nompes', '')
            user.email = user_info.get('emailPrincipalUsuario') or user_info.get('emailUspUsuario') or user_info.get('email', '')
            user.save()

            return user

        except Exception:
            return None
