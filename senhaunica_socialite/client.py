import urllib.parse
from typing import Dict, Any, Optional
from authlib.integrations.requests_client import OAuth1Session

class SenhaUnicaClient:
    """
    Client for interacting with USP's OAuth 1.0a provider (Senha Unica).
    """

    # Prod URLs
    USP_Authorize_URL_PROD = "https://uspdigital.usp.br/wsusuario/oauth/authorize"
    USP_Request_Token_URL_PROD = "https://uspdigital.usp.br/wsusuario/oauth/request_token"
    USP_Access_Token_URL_PROD = "https://uspdigital.usp.br/wsusuario/oauth/access_token"
    USP_User_Info_URL_PROD = "https://uspdigital.usp.br/wsusuario/oauth/usuariousp"

    # Dev URLs
    USP_Authorize_URL_DEV = "https://dev.uspdigital.usp.br/wsusuario/oauth/authorize"
    USP_Request_Token_URL_DEV = "https://dev.uspdigital.usp.br/wsusuario/oauth/request_token"
    USP_Access_Token_URL_DEV = "https://dev.uspdigital.usp.br/wsusuario/oauth/access_token"
    USP_User_Info_URL_DEV = "https://dev.uspdigital.usp.br/wsusuario/oauth/usuariousp"

    def __init__(self, consumer_key: str, consumer_secret: str, callback_url: str, callback_id: str = None, env: str = "prod"):
        """
        Initializes the Senha Unica Client.

        Args:
            consumer_key: The OAuth Consumer Key.
            consumer_secret: The OAuth Consumer Secret.
            callback_url: The URL to redirect back to after authorization.
            callback_id: The USP Callback ID (required for Authorize URL).
            env: The environment ('prod' or 'dev').
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.callback_url = callback_url
        self.callback_id = callback_id
        self.env = env.lower()

        # Set endpoints based on environment
        if self.env == "dev":
            self.authorize_url = self.USP_Authorize_URL_DEV
            self.request_token_url = self.USP_Request_Token_URL_DEV
            self.access_token_url = self.USP_Access_Token_URL_DEV
            self.user_info_url = self.USP_User_Info_URL_DEV
        else:
            self.authorize_url = self.USP_Authorize_URL_PROD
            self.request_token_url = self.USP_Request_Token_URL_PROD
            self.access_token_url = self.USP_Access_Token_URL_PROD
            self.user_info_url = self.USP_User_Info_URL_PROD
    
    def _get_session(self, token: Optional[str] = None, token_secret: Optional[str] = None) -> OAuth1Session:
        return OAuth1Session(
            self.consumer_key,
            self.consumer_secret,
            token=token,
            token_secret=token_secret,
            redirect_uri=self.callback_url
        )

    def fetch_request_token(self) -> Dict[str, str]:
        """
        Fetches the initial Request Token.
        Handles the non-JSON, query-encoded string response from USP manually.
        """
        session = self._get_session()
        # Authlib `fetch_request_token` automatically parses form-urlencoded responses
        # into a dictionary (oauth_token, oauth_token_secret, etc.)
        return session.fetch_request_token(self.request_token_url)

    def get_authorization_url(self, request_token: str) -> str:
        """
        Generates the full authorization URL for the user to visit.
        """
        session = self._get_session(token=request_token)
        # USP specific: callback_id must be appended to the authorize URL
        kwargs = {}
        if self.callback_id:
            kwargs['callback_id'] = self.callback_id
            
        return session.create_authorization_url(self.authorize_url, **kwargs)

    def fetch_access_token(self, request_token: str, request_token_secret: str, verifier: str) -> Dict[str, str]:
        """
        Exchanges the Verifier for the final Access Token.
        """
        session = self._get_session(token=request_token, token_secret=request_token_secret)
        # Authlib automatically handles the verifier when calling fetch_access_token if passed in url or body
        # Usually we pass verifier via parse_authorization_response or manually
        session.parse_authorization_response(f"https://example.com/?oauth_verifier={verifier}")
        return session.fetch_access_token(self.access_token_url)

    def get_user_info(self, access_token: str, access_token_secret: str) -> Dict[str, Any]:
        """
        Fetches the user profile from the USP API protected resource.
        Post request required, strictly signed.
        """
        session = self._get_session(token=access_token, token_secret=access_token_secret)
        # USP endpoint expects POST
        resp = session.post(self.user_info_url)
        resp.raise_for_status()
        return resp.json()
