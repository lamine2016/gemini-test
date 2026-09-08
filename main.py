import os
import requests
import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_news(topic):
    """Gemini ile özgün haber üretir."""
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"{topic} hakkında ilgi çekici ve özgün bir haber yaz."
        )
        return f"{topic} Haberi", response.text
    except Exception as e:
        print(f"[{topic}] için haber üretilirken hata oluştu: {e}")
        return None, None

# --- Blogger Ayarı ---
BLOG_ID = os.getenv("BLOGGER_SITE_ID")
TOKEN = os.getenv("BLOGGER_TOKEN")

def publish_to_blogger(title, content):
    """Üretilen haberi Blogger'a gönderir."""
    if not BLOG_ID or not TOKEN:
        print("Hata: BLOGGER_SITE_ID veya BLOGGER_TOKEN ortam değişkeni eksik!")
        return

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"title": title, "content": content}

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code in [200, 201]:
            print(f" Success: '{title}' Blogger'da başarıyla yayınlandı.")
        else:
            print(f" Error ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"Blogger'a erişirken hata oluştu: {e}")

if __name__ == "__main__":
    topics = ["Ekonomi", "Spor", "Kültür-Sanat", "Kadın", "Sağlık", "Bilim"]

    for topic in topics[:5]:
        print(f"\n--- {topic} için haber üretiliyor ---")
        title, content = generate_news(topic)
        if title and content:
            publish_to_blogger(title, content)
        else:
            print(f"[{topic}] için haber içeriği üretilemediği için atlanıyor.")
