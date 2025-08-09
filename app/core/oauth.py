"""
NAVER OAuth implementation
"""
import httpx
from typing import Optional, Dict, Any
import os
from urllib.parse import urlencode

class NaverOAuth:
    """NAVER OAuth 2.0 client"""
    
    def __init__(self):
        self.client_id = os.getenv("NAVER_CLIENT_ID", "3q7_Du8DrgEwtopgzVgZ")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("NAVER_REDIRECT_URI", "http://49.50.130.173:8080/v1/auth/naver/login")
        self.auth_url = "https://nid.naver.com/oauth2.0/authorize"
        self.token_url = "https://nid.naver.com/oauth2.0/token"
        self.profile_url = "https://openapi.naver.com/v1/nid/me"
    
    def get_authorization_url(self, state: str) -> str:
        """
        Get NAVER OAuth authorization URL
        
        Args:
            state: Random state string for CSRF protection
            
        Returns:
            Authorization URL
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state
        }
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def get_access_token(self, code: str, state: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from NAVER
            state: State parameter for validation
            
        Returns:
            Token response or None if failed
        """
        params = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "state": state
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    return data
        
        return None
    
    async def get_user_profile(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile from NAVER
        
        Args:
            access_token: NAVER access token
            
        Returns:
            User profile or None if failed
        """
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.profile_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("resultcode") == "00":
                    return data.get("response")
        
        return None