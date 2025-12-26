import os
import pytest
from senhaunica_socialite.client import SenhaUnicaClient

def test_client_initialization_dev_env():
    """
    Test if client initializes with correct DEV URLs.
    """
    client = SenhaUnicaClient("key", "secret", "http://callback", env="dev")
    assert client.authorize_url == SenhaUnicaClient.USP_Authorize_URL_DEV
    assert client.request_token_url == SenhaUnicaClient.USP_Request_Token_URL_DEV

def test_client_initialization_prod_env():
    """
    Test if client initializes with correct PROD URLs (default).
    """
    client = SenhaUnicaClient("key", "secret", "http://callback", env="prod")
    assert client.authorize_url == SenhaUnicaClient.USP_Authorize_URL_PROD

def test_env_file_loading():
    """
    Test if .env.testing is being loaded correctly by pytest.
    """
    # SENHAUNICA_KEY is set in .env.testing as 'test_key_placeholder'
    assert os.getenv('SENHAUNICA_KEY') == 'test_key_placeholder'
