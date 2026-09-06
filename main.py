import os
import requests
import google.generativeai as genai

# --- Gemini ayarı ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- Blogger ayarı ---
BLOG_ID = os.getenv("BLOGGER_SITE_ID")   # Blogger blog ID
TOKEN = os.getenv("BLOGGER_TOKEN")       # OAuth2 token

def generate_news(topic):
    """Gemini ile özgün haber üretir"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"{topic} hakkında özgün bir haber yaz.")
    return f"{topic} Haberi", response.text

def publish_to_blogger(title, content):
    """Üretilen haberi Blogger'a gönderir"""
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    data = {
        "title": title,
        "content": content
    }
    response = requests.post(url, headers=headers, json=data)
    print("Blogger response:", response.status_code, response.text)

if __name__ == "__main__":
    topics = ["Ekonomi", "Spor", "Kültür-Sanat", "Kadın", "Sağlık", "Bilim"]

    # Günde 5 haber üret → ilk 5 konuyu seçiyoruz
    for topic in topics[:5]:
        title, content = generate_news(topic)
        print("Üretilen Haber:", title)
        publish_to_blogger(title, content)
