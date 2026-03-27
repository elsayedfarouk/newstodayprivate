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
    VIDEO_URL = "https://github.com/elsayedfarouk/public/raw/refs/heads/main/news_videos/20260327/x9RdY6bSVT.mp4"

    # --- Post Video ---
    result = post_video_from_url(
        video_url=VIDEO_URL,
        title="",
        description="""
        Trump says he’ll sign order to pay TSA agents as Congress struggles to reach funding deal', 'date': 'Thu, 26 Mar 2026 22:43:00 GMT', 'summary': "President Trump announced he will sign an order to ensure Transportation Security Administration agents receive pay during the ongoing partial government shutdown. This action comes as Congress continues to struggle to reach a funding agreement, now in its 41st day, causing significant travel delays and financial hardship for federal workers. The White House had considered declaring a national emergency to address the issue, but the president may instead redirect existing funds. Democrats are seeking concessions on immigration enforcement policies, specifically regarding ICE operations, including agent identification and restrictions on raids. Republicans have presented a final offer, but negotiations remain stalled. Airports are experiencing increased TSA worker absences, with over 3,100 callouts Wednesday and nearly 500 officers resigning during the shut
        """
    )

    print(result)


if __name__ == "__main__":
    main()
