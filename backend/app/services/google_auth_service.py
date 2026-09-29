import urllib.request
import json
from typing import Optional, Dict
from app.config import settings

import urllib.request
import json
from typing import Optional, Dict
from app.config import settings

def verify_google_id_token(token: str) -> Optional[Dict[str, str]]:
    """
    Verifies Google OAuth token (supports both ID Token JWTs and OAuth2 Access Tokens).
    """
    if not token:
        return None

    # 1. Try native google.oauth2 id_token verification if token is a JWT
    if token.count(".") == 2:
        try:
            from google.oauth2 import id_token as google_id_token
            from google.auth.transport import requests as google_requests

            request = google_requests.Request()
            client_id = settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
            
            id_info = google_id_token.verify_oauth2_token(token, request, audience=client_id)

            return {
                "google_id": id_info.get("sub"),
                "email": id_info.get("email"),
                "full_name": id_info.get("name"),
                "avatar_url": id_info.get("picture"),
                "email_verified": id_info.get("email_verified", True),
            }
        except Exception as e:
            print(f"[GOOGLE AUTH] Native ID token verify failed: {e}. Trying HTTP fallbacks...")

        # Try Google TokenInfo HTTP endpoint for ID token
        try:
            url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if "sub" in data and "email" in data:
                        return {
                            "google_id": data.get("sub"),
                            "email": data.get("email"),
                            "full_name": data.get("name"),
                            "avatar_url": data.get("picture"),
                            "email_verified": data.get("email_verified") == "true" or data.get("email_verified") is True,
                        }
        except Exception as ex:
            print(f"[GOOGLE AUTH] Tokeninfo id_token error: {ex}")

    # 2. Try Google UserInfo endpoint (Works for both Access Tokens & ID Tokens)
    try:
        url = "https://www.googleapis.com/oauth2/v3/userinfo"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if "sub" in data and "email" in data:
                    print(f"[GOOGLE AUTH] Verified token via Google UserInfo endpoint for {data.get('email')}")
                    return {
                        "google_id": data.get("sub"),
                        "email": data.get("email"),
                        "full_name": data.get("name"),
                        "avatar_url": data.get("picture"),
                        "email_verified": data.get("email_verified", True),
                    }
    except Exception as ex:
        print(f"[GOOGLE AUTH] Userinfo endpoint error: {ex}")

    # 3. Try TokenInfo access_token query fallback
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?access_token={token}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if "sub" in data and "email" in data:
                    return {
                        "google_id": data.get("sub"),
                        "email": data.get("email"),
                        "full_name": data.get("name"),
                        "avatar_url": data.get("picture"),
                        "email_verified": data.get("email_verified") == "true" or data.get("email_verified") is True,
                    }
    except Exception as ex:
        print(f"[GOOGLE AUTH] Tokeninfo access_token error: {ex}")

    return None

