import os
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse
from .client import SenhaUnicaClient

def login_init(request: HttpRequest) -> HttpResponse:
    """
    Initiates the OAuth 1.0a flow.
    1. Fetches Request Token.
    2. Stores Request Token Secret in session.
    3. Redirects user to USP Authorization URL.
    """
    key = os.getenv("SENHAUNICA_KEY")
    secret = os.getenv("SENHAUNICA_SECRET")
    callback = os.getenv("SENHAUNICA_CALLBACK_URL", request.build_absolute_uri(reverse('senhaunica_callback')))
    callback_id = os.getenv("SENHAUNICA_CALLBACK_ID")
    env = os.getenv("SENHAUNICA_ENV", "prod")

    if not key or not secret:
        return HttpResponse("Misconfigured Credentials", status=500)

    client = SenhaUnicaClient(key, secret, callback, callback_id=callback_id, env=env)
    
    # 1. Get Request Token
    try:
        resp = client.fetch_request_token()
        oauth_token = resp.get('oauth_token')
        oauth_token_secret = resp.get('oauth_token_secret')
        
        if not oauth_token or not oauth_token_secret:
             return HttpResponse("Failed to obtain Request Token from USP", status=502)

        # 2. Store Secret in Session (Required for Step 3)
        request.session['senhaunica_token_secret'] = oauth_token_secret
        
        # 3. Redirect
        url = client.get_authorization_url(oauth_token)
        
        print(f"DEBUG: ENV used: {env}")
        print(f"DEBUG: Client Callback URL: {client.callback_url}")
        print(f"DEBUG: Request Token Resp: {resp}")
        print(f"DEBUG: Generated Auth URL: {url}")
        
        return redirect(url)

    except Exception as e:
        print(f"DEBUG: Exception: {e}")
        return HttpResponse(f"Error initiating login: {e}", status=502)


def login_callback(request: HttpRequest) -> HttpResponse:
    """
    Handles the callback from USP.
    1. Retrieves verifier and token from Query String.
    2. Retrieves secret from session.
    3. Authenticates using the Backend.
    """
    oauth_verifier = request.GET.get('oauth_verifier')
    oauth_token = request.GET.get('oauth_token')
    oauth_token_secret = request.session.get('senhaunica_token_secret')

    if not oauth_verifier or not oauth_token or not oauth_token_secret:
        return HttpResponse("Invalid Callback Request or Session Expired", status=400)

    # Clean up session
    del request.session['senhaunica_token_secret']

    # Authenticate (delegates to SenhaUnicaBackend)
    user = authenticate(request, oauth_token=oauth_token, oauth_token_secret=oauth_token_secret, oauth_verifier=oauth_verifier)

    if user:
        login(request, user)
        # Redirect to intended next page or home
        return redirect(os.getenv("SENHAUNICA_LOGIN_REDIRECT_URL", "/"))
    else:
        return HttpResponse("Authentication Failed", status=403)
