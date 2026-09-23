import os
import requests
from google import genai

# --- Ortam Değişkenleri ---
BLOG_ID_TR = os.getenv("BLOGGER_SITE_TR_ID")
BLOG_ID_DE = os.getenv("BLOGGER_SITE_DE_ID")
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
    try:
        r = requests.post(url, data=data, timeout=30)
        r.raise_for_status()
        return r.json().get("access_token")
    except Exception as e:
        print("Access Token alınamadı:", e)
        return None

def generate_news(topic, lang="tr"):
    """Gemini API kullanarak kategoriye göre haber üretir."""
    if not GEMINI_API_KEY:
        print("Hata: GEMINI_API_KEY bulunamadı!")
        return None, None, None, None

    client = genai.Client(api_key=GEMINI_API_KEY)

    if lang == "tr":
        prompt = (
            f"{topic} kategorisinde güncel ve özgün bir haber yaz.\n"
            "Çıktı tam olarak şu formatta olmalı:\n"
            "BAŞLIK: [Haber Başlığı]\n"
            "META: [150 karakterlik meta açıklama]\n"
            "ETİKETLER: [5 tane haberle ilgili etiket, virgülle ayrılmış]\n"
            "İÇERİK: [Haberin HTML formatındaki gövdesi, <p> ve <h2> etiketleri kullan]"
        )
    elif lang == "de":
        prompt = (
            f"Schreibe einen aktuellen und originellen Nachrichtenartikel über {topic}.\n"
            "Das Ergebnis muss genau in folgendem Format sein:\n"
            "BAŞLIK: [Artikelüberschrift]\n"
            "META: [Meta-Beschreibung mit 150 Zeichen]\n"
            "ETİKETLER: [5 relevante Schlagwörter, durch Komma getrennt]\n"
            "İÇERİK: [Artikeltext im HTML-Format mit <p> und <h2>]"
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
        print("İçerik üretilirken hata oluştu:", e)
        return None, None, None, None

def publish_to_blogger(blog_id, title, content, labels=None, meta_description=None):
    """Üretilen haberi Blogger'a gönderir."""
    access_token = get_access_token()
    if not blog_id or not access_token:
        print("Hata: BLOGGER_SITE_ID veya Access Token eksik!")
        return

    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"
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
        clean_labels = [lbl.strip() for lbl in labels if lbl.strip()]
        data["labels"] = clean_labels
    if meta_description:
        safe_meta = meta_description.strip()[:150]
        if safe_meta:
            data["customMetaDescription"] = safe_meta

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            print("Haber başarıyla yayınlandı:", r.json().get("url"))
        else:
            print("Haber yayınlanamadı:", r.status_code, r.text)
    except Exception as e:
        print("Blogger API çağrısında hata:", e)

if __name__ == "__main__":
    topics_tr = [
        "Türkiye Süper Lig Haberleri", "Hollywood", "Türkiye Hava Durumu", "Ankara Haberleri"
    ]
    topics_de = [
        "Deutschland Wirtschaft", "Gesundheit Nachrichten", "Deutschland Politik", "Deutschland Wetter"
    ]

    for topic in topics_tr:
    print(f"\n--- {topic} için haber üretiliyor ---")
    title, content, meta, labels = generate_news(topic, lang="tr")
    if title and content:
        publish_to_blogger(BLOG_ID_TR, title, content, labels=labels, meta_description=meta)

for topic in topics_de:
    print(f"\n--- {topic} für Nachrichten wird erstellt ---")
    title, content, meta, labels = generate_news(topic, lang="de")
    if title and content:
        publish_to_blogger(BLOG_ID_DE, title, content, labels=labels, meta_description=meta)

