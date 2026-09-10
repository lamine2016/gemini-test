import os
import requests

# --- Blogger Ayarı ---
BLOG_ID = os.getenv("BLOGGER_SITE_TR_ID")
REFRESH_TOKEN = os.getenv("BLOGGER_TOKEN_TR")
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

def get_access_token():
    """Refresh Token'den Access Token üretir."""
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    r = requests.post(url, data=data)
    if r.status_code == 200:
        return r.json().get("access_token")
    else:
        print("Access Token alınamadı:", r.text)
        return None

def publish_to_blogger(title, content):
    """Üretilen haberi Blogger'a gönderir."""
    access_token = get_access_token()
    if not BLOG_ID or not access_token:
        print("Hata: BLOGGER_SITE_TR_ID veya BLOGGER_TOKEN_TR eksik!")
        return

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "kind": "blogger#post",
        "title": title,
        "content": content
    }

    r = requests.post(url, headers=headers, json=data)
    if r.status_code == 200:
        print("Haber başarıyla yayınlandı:", r.json().get("url"))
    else:
        print("Haber yayınlanamadı:", r.status_code, r.text)

if __name__ == "__main__":
    # Burada test amaçlı bir gönderi yapabilirsin
    publish_to_blogger("Test Başlık", "Bu bir test içeriğidir.")
