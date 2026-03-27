# import requests
#
# page_id = "1019688641230557"
#
# video_url = "https://github.com/elsayedfarouk/public/raw/refs/heads/main/news_videos/20260207/0LUF1Aqk9M.mp4"
#
# endpoint = f"https://graph.facebook.com/v19.0/{page_id}/videos"
#
# data = {
#     'access_token': access_token,
#     'file_url': video_url,
#     'description': 'Video posted from URL',
#     'title': 'My Video Title'
# }
#
# response = requests.post(endpoint, data=data)
#
# print(response.status_code)
# print(response.json())


import requests
import os
from dotenv import load_dotenv


def post_video_from_url(video_url: str,
                        title: str = "", description: str = "") -> dict:
    """
    Post a video to a Facebook Page using a public video URL.
    """

    page_id = "1019688641230557"
    access_token = os.getenv("token_facebook")

    endpoint = f"https://graph.facebook.com/v19.0/{page_id}/videos"

    payload = {
        "access_token": access_token,
        "file_url": video_url,
        "title": title,
        "description": description,
    }

    response = requests.post(endpoint, data=payload)

    # --- Simple Success / Fail Check ---
    if "id" in response:
        print("✅ Video posted successfully!")
        print("Video ID:", response["id"])
    else:
        print("❌ Failed to post video.")
        print("Error:", response)

    return response.json()


def main():
    # --- Config ---
    VIDEO_URL = "https://github.com/elsayedfarouk/public/raw/refs/heads/main/news_videos/20260207/0LUF1Aqk9M.mp4"

    # --- Post Video ---
    result = post_video_from_url(
        video_url=VIDEO_URL,
        title="My Video Title",
        description="Uploaded via Python 🎬"
    )

    print(result)


if __name__ == "__main__":
    main()
