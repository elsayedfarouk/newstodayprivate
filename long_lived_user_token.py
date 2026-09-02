import requests

# ==============================
# CONFIG (replace these values)
# ==============================
APP_ID = "4016070761858145"
APP_SECRET = "6ce6912ab08634a30af262e6fe449319"
SHORT_LIVED_USER_TOKEN = "EAA5EmFcnRGEBRCv6eC0RHhwIcK0RJs2ZCYFRs1KZBCRnl3QmyblyKP4zUlayZBnWXZCX3rFNUbDFQ4MpS6sKpUjTtZAGIs1DGf9avGuVYCZBsJMwFh1HNrVHXYhOIRolUbxRNaOGsDDvWmksEDGiNPFeXmZAt3l5fZAtH3H5nQAl6wkZAPP49znXcx2UgDMjY9qpPrlJ6vnZAPapYzh3Aq0T1nBjHFzCNN43sIWY0K"

# ==============================
# STEP 1: Get long-lived user token
# ==============================
def get_long_lived_user_token():
    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": SHORT_LIVED_USER_TOKEN,
    }

    res = requests.get(url, params=params)
    data = res.json()

    if "access_token" not in data:
        raise Exception(f"Error getting long-lived token: {data}")

    return data["access_token"]


# ==============================
# STEP 2: Get page access token
# ==============================
def get_page_access_token(long_lived_token):
    url = "https://graph.facebook.com/v19.0/me/accounts"
    params = {
        "access_token": long_lived_token
    }

    res = requests.get(url, params=params)
    data = res.json()

    if "data" not in data:
        raise Exception(f"Error getting pages: {data}")

    pages = []
    for page in data["data"]:
        pages.append({
            "name": page["name"],
            "id": page["id"],
            "access_token": page["access_token"]
        })

    return pages


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    try:
        print("Getting long-lived user token...")
        long_token = get_long_lived_user_token()
        print("Success!\n")

        print("Getting page access tokens...")
        pages = get_page_access_token(long_token)

        for p in pages:
            print(f"Page: {p['name']}")
            print(f"Page ID: {p['id']}")
            print(f"Access Token: {p['access_token']}")
            print("-" * 40)

    except Exception as e:
        print("Error:", e)