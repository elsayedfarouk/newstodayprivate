import os
from pathlib import Path
import mimetypes
import requests
from zernio import Zernio
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

ZERNIO_API_KEY = os.getenv("ZERNIO_API_KEY")
TIKTOK_ACCOUNT_ID = "6a7b7b3f77555aae01cd37d0"


def upload_media_zernio(file_path: Path, api_key: str) -> str:
    """
    Upload a media file using Zernio's presigned URL endpoint (supports up to 5GB).
    """
    file_size = file_path.stat().st_size
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        content_type = "video/mp4"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "filename": file_path.name,
        "contentType": content_type,
        "size": file_size,
    }

    # 1. Request presigned upload URL
    presign_res = requests.post(
        "https://zernio.com/api/v1/media/presign",
        headers=headers,
        json=payload,
    )
    presign_res.raise_for_status()
    presign_data = presign_res.json()

    upload_url = presign_data["uploadUrl"]
    public_url = presign_data["publicUrl"]

    # 2. PUT file bytes to cloud storage
    with open(file_path, "rb") as f:
        upload_res = requests.put(
            upload_url,
            data=f,
            headers={"Content-Type": content_type},
        )
        upload_res.raise_for_status()

    return public_url


def resolve_tiktok_account_id(api_key: str, identifier: str = None) -> str:
    """
    Resolve the 24-character Zernio accountId for TikTok.
    If identifier is already a 24-char hex ID, returns it directly.
    Otherwise, queries Zernio API for connected TikTok accounts.
    """
    # If already a 24-character hex ObjectId
    if identifier and len(identifier) == 24 and all(c in "0123456789abcdefABCDEF" for c in identifier):
        return identifier

    headers = {"Authorization": f"Bearer {api_key}"}
    res = requests.get("https://zernio.com/api/v1/accounts", headers=headers)
    res.raise_for_status()
    data = res.json()
    accounts = data.get("accounts", [])

    tiktok_accounts = [acc for acc in accounts if acc.get("platform") == "tiktok"]

    if not tiktok_accounts:
        all_platforms = [f"{a.get('platform')}: {a.get('username', a.get('_id'))}" for a in accounts]
        raise ValueError(
            f"No connected TikTok accounts found in Zernio. "
            f"Connected accounts: {all_platforms or 'None'}. "
            f"Please connect your TikTok account in the Zernio dashboard."
        )

    # Match by username if provided
    if identifier:
        clean_id = identifier.lstrip("@").lower()
        for acc in tiktok_accounts:
            username = (acc.get("username") or "").lstrip("@").lower()
            if username == clean_id or acc.get("_id") == identifier:
                print(f"Matched TikTok account: @{acc.get('username')} (ID: {acc.get('_id')})")
                return acc["_id"]

    # Default to first TikTok account if no exact match or identifier was empty
    selected = tiktok_accounts[0]
    print(f"Using TikTok account: @{selected.get('username')} (ID: {selected.get('_id')})")
    return selected["_id"]


def publish_tiktok_video(
    video_path: str,
    caption: str,
    tiktok_account_id: str = None,
    as_draft: bool = False,
):
    """
    Upload a local video to Zernio and publish it to TikTok.
    If TikTok direct posting is at capacity and as_draft is False, it will automatically fallback to draft mode.
    """

    video_file = Path(video_path)

    if not video_file.exists():
        raise FileNotFoundError(f"Video not found: {video_file}")

    if not video_file.is_file():
        raise ValueError(f"Not a file: {video_file}")

    if not ZERNIO_API_KEY:
        raise ValueError("ZERNIO_API_KEY is not set in environment or .env file.")

    client = Zernio(api_key=ZERNIO_API_KEY)

    # 1. Resolve TikTok 24-character accountId
    resolved_account_id = resolve_tiktok_account_id(ZERNIO_API_KEY, tiktok_account_id)

    # 2. Upload video
    print(f"Uploading: {video_file} ({video_file.stat().st_size / (1024 * 1024):.2f} MB)")

    video_url = upload_media_zernio(video_file, ZERNIO_API_KEY)

    print(f"Uploaded successfully:")
    print(video_url)

    # 3. Create TikTok post
    mode_text = "Creator Inbox Draft" if as_draft else "Direct Post"
    print(f"Publishing to TikTok ({mode_text})...")

    tiktok_settings = {
        "privacy_level": "PUBLIC_TO_EVERYONE",
        "allow_comment": True,
        "allow_duet": True,
        "allow_stitch": True,
        "content_preview_confirmed": True,
        "express_consent_given": True,
    }
    if as_draft:
        tiktok_settings["draft"] = True

    result = client.posts.create_post(
        content=caption,
        media_items=[
            {
                "type": "video",
                "url": video_url,
            }
        ],
        platforms=[
            {
                "platform": "tiktok",
                "accountId": resolved_account_id,
            }
        ],
        tiktok_settings=tiktok_settings,
        publish_now=True,
    )

    post = result.get("post", result)
    status = post.get("status")
    print(f"Post ID: {post.get('_id')}")
    print(f"Status: {status}")

    # Check for platform-specific errors or capacity issues
    platforms_info = post.get("platforms", [])
    has_capacity_error = False
    for p in platforms_info:
        if p.get("error"):
            err = p.get("error")
            print(f"Platform {p.get('platform')} error: {err}")
            if "capacity" in err.lower() or "creator inbox" in err.lower():
                has_capacity_error = True

    # Fallback to draft mode if direct posting hit capacity
    if status == "failed" and has_capacity_error and not as_draft:
        print("\nTikTok direct posting is at capacity. Retrying as Creator Inbox Draft...")
        tiktok_settings["draft"] = True
        retry_result = client.posts.create_post(
            content=caption,
            media_items=[
                {
                    "type": "video",
                    "url": video_url,
                }
            ],
            platforms=[
                {
                    "platform": "tiktok",
                    "accountId": resolved_account_id,
                }
            ],
            tiktok_settings=tiktok_settings,
            publish_now=True,
        )
        post = retry_result.get("post", retry_result)
        print(f"Retry Post ID: {post.get('_id')}")
        print(f"Retry Status: {post.get('status')}")
        print("Note: Delivered to your TikTok app Creator Inbox. Open TikTok to finalize and post!")

    if post.get("platformPostUrl"):
        print(f"Live URL: {post.get('platformPostUrl')}")

    return post


if __name__ == "__main__":

    publish_tiktok_video(
        video_path=r"news_videos/20260902/Tesa4pfEyV.mp4",
        caption="Successfully structured news data for 'Credo's Optical Bet: Is a $600M+ Revenue Opportunity Taking Shape?'",
        tiktok_account_id=TIKTOK_ACCOUNT_ID,
        as_draft=True,  # Set to True for Creator Inbox delivery when TikTok direct post capacity is full
    )