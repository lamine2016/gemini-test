import os
import requests
from google import genai

# --- Gemini ayarı ---
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_news(topic):
    """Gemini ile özgün haber üretir"""
    chat = client.chats.create(model="models/gemini-1.0-pro")
    response = chat.send_message(f"{topic} hakkında özgün bir haber yaz.")
    return f"{topic} Haberi", response.text

# --- Blogger ayarı ---
BLOG_ID = os.getenv("BLOGGER_SITE_ID")
TOKEN = os.getenv("BLOGGER_TOKEN")

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

    for topic in topics[:5]:  # günde 5 haber
        title, content = generate_news(topic)
        print("Üretilen Haber:", title)
        publish_to_blogger(title, content)

for m in client.models.list():
    print(m.name, m.supported_methods)

