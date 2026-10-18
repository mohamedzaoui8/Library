from authlib.integrations.base_client.errors import OAuthError
from fastapi import APIRouter, HTTPException, Request
from starlette.responses import RedirectResponse

from app.core.oauth import oauth

router = APIRouter(prefix="/auth/google", tags=["Google Auth"])


@router.get("/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
    )


@router.get("/callback", name="google_callback")
async def google_callback(request: Request):
    # Google قد يعيد خطأ إذا رفض المستخدم تسجيل الدخول.
    if request.query_params.get("error"):
        raise HTTPException(
            status_code=400,
            detail="Google login was cancelled or denied.",
        )

    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(
            status_code=401,
            detail="Google authentication failed.",
        ) from None

    userinfo = token.get("userinfo")

    if not userinfo:
        raise HTTPException(
            status_code=401,
            detail="Google did not return verified user information.",
        )

    return {
        "message": "Google authentication succeeded",
        "google_sub": userinfo.get("sub"),
        "email": userinfo.get("email"),
        "email_verified": userinfo.get("email_verified"),
        "name": userinfo.get("name"),
        "picture": userinfo.get("picture"),
    }