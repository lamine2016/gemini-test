import os
import google.genai as genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))



def generate_news(topic):
    """Gemini ile özgün haber üretir."""
    try:
        # Hızlı ve güncel yanıtlar için gemini-2.5-flash modeli önerilir.
        # Daha detaylı içerikler için "gemini-2.5-pro" da kullanabilirsiniz.
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{topic} hakkında ilgi çekici ve özgün bir haber yaz."
        )
        return f"{topic} Haberi", response.text
    except Exception as e:
        print(f"[{topic}] için haber üretilirken hata oluştu: {e}")
        return None, None


# --- Blogger Ayarı ---
BLOG_ID = os.getenv("BLOGGER_SITE_ID")  # Secret'tan geliyor
TOKEN = os.getenv("BLOGGER_TOKEN")      # Secret'tan geliyor


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
    data = {
        "title": title,
        "content": content
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f" Success: '{title}' Blogger'da başarıyla yayınlandı.")
        else:
            print(f" Error ({response.status_code}): Blogger yayını başarısız. Yanıt: {response.text}")
    except Exception as e:
        print(f"Blogger'a erişirken hata oluştu: {e}")


if __name__ == "__main__":
    topics = ["Ekonomi", "Spor", "Kültür-Sanat", "Kadın", "Sağlık", "Bilim"]

    for topic in topics[:5]:  # Günde 5 haber
        print(f"\n--- {topic} için haber üretiliyor ---")
        title, content = generate_news(topic)

        if title and content:
            publish_to_blogger(title, content)
        else:
            print(f"[{topic}] için haber içeriği üretilemediği için atlanıyor.")
