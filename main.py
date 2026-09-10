import os
import requests
from google import genai

# --- Ortam Değişkenleri ---
BLOG_ID = os.getenv("BLOGGER_SITE_TR_ID")
REFRESH_TOKEN = os.getenv("BLOGGER_TOKEN_TR")
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_access_token():
    """Refresh Token'dan yeni bir Access Token üretir."""
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

def generate_news():
    """Gemini API kullanarak haber başlığı ve HTML içeriği üretir."""
    if not GEMINI_API_KEY:
        print("Hata: GEMINI_API_KEY bulunamadı!")
        return None, None

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = (
        "Güncel ve ilgi çekici bir teknoloji/gündem haberi yaz.\n"
        "Çıktı tam olarak şu formatta olmalı:\n"
        "BAŞLIK: [Haber Başlığı]\n"
        "İÇERİK: [Haberin HTML formatındaki gövdesi, <p> ve <h2> etiketleri kullan]"
    )
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text
        title = text.split("BAŞLIK:")[1].split("İÇERİK:")[0].strip()
        content = text.split("İÇERİK:")[1].strip()
        return title, content
    except Exception as e:
        print("İçerik üretilirken veya ayrıştırılırken hata oluştu:", e)
        return None, None

def publish_to_blogger(title, content):
    """Üretilen haberi Blogger'a gönderir."""
    access_token = get_access_token()
    if not BLOG_ID or not access_token:
        print("Hata: BLOGGER_SITE_TR_ID veya Access Token eksik!")
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
    title, content = generate_news()
    if title and content:
        publish_to_blogger(title, content)
    else:
        print("Haber içeriği oluşturulamadığı için işlem iptal edildi.")
