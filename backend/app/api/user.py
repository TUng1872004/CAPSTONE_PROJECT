import select
from urllib import request
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
import jwt
import requests
from google.auth.transport import requests as grequests
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from pydantic import BaseModel, Field
from typing import Annotated, List, Optional
from datetime import datetime
from llama_index.core.base.llms.types import MessageRole
from google.oauth2 import id_token

from app.schema.user import ALGORITHM, SECRET_KEY, Token
from dotenv import load_dotenv

from app.core.dependencies import MinIOServiceDep, UserServiceDep

load_dotenv()
import os
from app.core.config import settings

router = APIRouter(prefix="/api/user", tags=["user"])


class GoogleLoginRequest(BaseModel):
    code: str = Field(
        ..., description="The authorization code received from Google OAuth"
    )


security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload  # contains user_id, email, etc.
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/secure-endpoint")
async def secure_endpoint(user=Depends(verify_token)):
    return {"msg": f"Hello {user['email']}, welcome back!"}


@router.post("/login/google")
async def login_with_google(request: GoogleLoginRequest, user_service: UserServiceDep):
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET

    try:
        if not client_id or not client_secret:
            raise HTTPException(status_code=500, detail="Missing OAuth credentials")

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": request.code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": "postmessage",  # for use with PKCE and SPA
            "grant_type": "authorization_code",
        }

        response = requests.post(token_url, data=payload, timeout=10)
        token_data = response.json()
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Google token error: {token_data.get('error', 'Unknown error')}",
            )

        if "error" in token_data:
            raise HTTPException(
                status_code=400,
                detail=f"Google OAuth error: {token_data['error']} - {token_data.get('error_description', '')}",
            )

        # Extract the id_token (JWT with user profile info)
        if "id_token" not in token_data:
            raise HTTPException(
                status_code=400,
                detail=f"No id_token in response. Available keys: {list(token_data.keys())}",
            )

        google_user_info = user_service.verify_google_id_token(
            token_data["id_token"], token_data["access_token"]
        )

        user = await user_service.create_or_update_user(google_user_info)

        user_data = {
            "user_id": str(user.id),  # Convert MongoDB ObjectId to string
            "email": user.email,
            "name": user.full_name,
            "google_id": user.google_id,
        }

        my_app_token = user_service.create_jwt_token(user_data)

        return {
            "access_token": my_app_token,
            "token_type": "Bearer",
            "user": {
                "id": user_data["user_id"],
                "email": user_data["email"],
                "name": user_data["name"],
                "picture": user.picture,
            },
        }

    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Google OAuth request timed out")
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502, detail=f"Google OAuth request error: {str(e)}"
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Invalid token audience")
    except jwt.InvalidIssuedAtError:
        raise HTTPException(status_code=401, detail="Invalid token issued at time")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# {data: "xin choa"}
@router.get("/chat-history")
async def get_chat_history(user_service: UserServiceDep, user=Depends(verify_token)):
    user_id = user["user_id"]
    chats = await user_service.get_user_chat_history(user_id)
    return {"chats": chats}


@router.get("/chat-history/{session_id}")
async def get_chat_detail(session_id: str, user_service: UserServiceDep):
    chat = await user_service.get_user_chat_detail(session_id)
    return {"chat": chat}


@router.post("/uploads")
async def upload_file(
    user_service: UserServiceDep,
    group: str = Form(...),
    session_id: str = Form(None),
    files: List[UploadFile] = File(...),
    user=Depends(verify_token),
):
    user_id = user["user_id"]
    # lưu file lên minio, trả về ids
    video_id_video_url_thumbnail_url_s3_url_obj = await user_service.add_videos_to_user(
        user_id, files, group, session_id
    )
    video_ids_video_url_obj = [
        {"video_id": str(vid), "video_url": s3_url}
        for vid, video_url, thumb_url, s3_url in video_id_video_url_thumbnail_url_s3_url_obj
    ]
    # bảo ingestion ingest mấy video có id đó
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://localhost:8000/api/uploads/",
                json={"videos": video_ids_video_url_obj, "user_id": user_id},
            )
    except Exception as e:
        logging.error(f"Error notifying ingestion service: {e}")

    return {"msg": "File uploaded successfully"}


@router.get("/groups")
async def get_user_groups(user_service: UserServiceDep, user=Depends(verify_token)):
    user_id = user["user_id"]
    groups = await user_service.get_user_groups(user_id)
    return {"groups": groups}


# get user video base on group
@router.get("/videos")
async def get_user_videos(
    user_service: UserServiceDep,
    group: str = Query(...),
    session_id: str = Query(...),
    user=Depends(verify_token),
):
    videos = await user_service.get_user_videos(group, session_id)
    return {"videos": videos}

@router.post("/videos/select")
async def select_videos(
    user_service: UserServiceDep,
    data: dict,
    user=Depends(verify_token),
):
    session_id = data.get("session_id")
    video_ids = data.get("video_ids", [])
    
    await user_service.select_videos(session_id, video_ids)
    return {"msg": "Videos selected"}

@router.post("/groups/create")
async def create_user_group(
    user_service: UserServiceDep, data: dict, user=Depends(verify_token)
):
    user_id = user["user_id"]
    group_name = data.get("group_name", "New Group")
    new_group = await user_service.create_user_group(user_id, group_name)
    print("🎉🎉🎉 Created group:", new_group)
    return {"group": new_group}


@router.delete("/groups/{group_id}/delete")
async def delete_group(
    group_id: str, user_service: UserServiceDep, user=Depends(verify_token)
):
    user_id = user["user_id"]
    await user_service.delete_group(group_id)
    return {"msg": "Group deleted"}


@router.delete("/videos/delete")
async def delete_videos(
    user_service: UserServiceDep,
    data: dict,
    user=Depends(verify_token),
):
    video_ids = data.get("video_ids", [])
    await user_service.delete_videos(video_ids)
    return {"msg": "Videos deleted"}
