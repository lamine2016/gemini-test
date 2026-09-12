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

def generate_news(topic):
    """Gemini API kullanarak kategoriye göre haber başlığı, içerik, meta açıklama ve etiketler üretir."""
    if not GEMINI_API_KEY:
        print("Hata: GEMINI_API_KEY bulunamadı!")
        return None, None, None, None

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = (
        f"{topic} kategorisinde güncel ve özgün bir haber yaz.\n"
        "Çıktı tam olarak şu formatta olmalı:\n"
        "BAŞLIK: [Haber Başlığı]\n"
        "META: [150 karakterlik meta açıklama]\n"
        "ETİKETLER: [5 tane haberle ilgili etiket, virgülle ayrılmış]\n"
        "İÇERİK: [Haberin HTML formatındaki gövdesi, <p> ve <h2> etiketleri kullan]"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        text = response.text
        title = text.split("BAŞLIK:")[1].split("META:")[0].strip()
        meta = text.split("META:")[1].split("ETİKETLER:")[0].strip()
        labels = text.split("ETİKETLER:")[1].split("İÇERİK:")[0].strip().split(",")
        content = text.split("İÇERİK:")[1].strip()
        return title, content, meta, labels
    except Exception as e:
        print("İçerik üretilirken veya ayrıştırılırken hata oluştu:", e)
        return None, None, None, None

def publish_to_blogger(title, content, labels=None, meta_description=None):
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

    if labels:
        data["labels"] = labels
    if meta_description:
        data["customMetaDescription"] = meta_description

    r = requests.post(url, headers=headers, json=data)
    if r.status_code == 200:
        print("Haber başarıyla yayınlandı:", r.json().get("url"))
    else:
        print("Haber yayınlanamadı:", r.status_code, r.text)

if __name__ == "__main__":
    topics = ["Ekonomi", "Spor", "Teknoloji", "Sağlık"]

    for topic in topics:
        print(f"\n--- {topic} için haber üretiliyor ---")
        title, content, meta, labels = generate_news(topic)
        if title and content:
            publish_to_blogger(title, content, labels=labels, meta_description=meta)
        else:
            print(f"[{topic}] için haber üretilemedi.")
