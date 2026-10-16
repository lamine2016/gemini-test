import os
import requests
import feedparser
from google import genai

# ----------------------
# AYARLAR
# ----------------------

BLOG_ID_TR = os.getenv("BLOGGER_SITE_TR_ID")

REFRESH_TOKEN = os.getenv("BLOGGER_TOKEN_TR")
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MAX_POSTS = 8

RSS_FEEDS = [
    "https://www.ntv.com.tr/teknoloji.rss",
    "https://www.haberturk.com/rss/magazin.xml",
    "https://www.haberturk.com/rss/kultur-sanat.xml"
]

BLOCKED_WORDS = [
    "cumhurbaşkanı",
    "seçim",
    "parti",
    "tbmm",
    "chp",
    "ak parti",
    "mhp",
    "bakan",
    "siyasi",
    "politik"
]

# ----------------------
# ACCESS TOKEN
# ----------------------

def get_access_token():

    url = "https://oauth2.googleapis.com/token"

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }

    try:

        response = requests.post(
            url,
            data=data,
            timeout=30
        )

        response.raise_for_status()

        return response.json()["access_token"]

    except Exception as e:

        print("Token hatası:", e)

        return None

# ----------------------
# BLOGGER
# ----------------------

def publish_to_blogger(
    title,
    content,
    labels,
    meta_description
):

    access_token = get_access_token()

    if not access_token:
        return

    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID_TR}/posts/"

    payload = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": labels,
        "customMetaDescription": meta_description[:150]
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        print(
            "Yayın sonucu:",
            response.status_code
        )

    except Exception as e:

        print(
            "Blogger gönderim hatası:",
            e
        )

# ----------------------
# SİYASET FİLTRESİ
# ----------------------

def is_blocked(text):

    text = text.lower()

    return any(
        word in text
        for word in BLOCKED_WORDS
    )

# ----------------------
# RSS
# ----------------------

def get_rss_news():

    news = []

    for feed_url in RSS_FEEDS:

        try:

            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:

                title = getattr(
                    entry,
                    "title",
                    ""
                )

                summary = getattr(
                    entry,
                    "summary",
                    ""
                )

                if not title:
                    continue

                news.append({
                    "title": title,
                    "summary": summary
                })

        except Exception as e:

            print(
                "RSS okuma hatası:",
                e
            )

    return news

# ----------------------
# GEMINI
# ----------------------

def generate_news(
    source_title,
    source_text
):

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    prompt = f"""
Sen profesyonel bir haber editörüsün.

Aşağıdaki haberi yeniden yorumlayarak
özgün bir haber oluştur.

KAYNAK BAŞLIK:

{source_title}

KAYNAK METİN:

{source_text}

KURALLAR:

- En az 600 kelime yaz.
- Tamamen yeni başlık oluştur.
- Haber dili kullan.
- Kopyala yapıştır yapma.
- En az 3 adet h2 başlığı kullan.
- SEO uyumlu yaz.
- Magazin, teknoloji, spor veya kültür sanat haberi formatında yaz.
- Sonuç bölümü ekle.
- HTML üret.

ÇIKTI FORMATI:

BAŞLIK:
META:
ETİKETLER:
İÇERİK:
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text

        title = text.split(
            "BAŞLIK:"
        )[1].split(
            "META:"
        )[0].strip()

        meta = text.split(
            "META:"
        )[1].split(
            "ETİKETLER:"
        )[0].strip()

        labels = text.split(
            "ETİKETLER:"
        )[1].split(
            "İÇERİK:"
        )[0].strip().split(",")

        content = text.split(
            "İÇERİK:"
        )[1].strip()

        return (
            title,
            content,
            meta,
            labels
        )

    except Exception as e:

        print(
            "Gemini hatası:",
            e
        )

        return (
            None,
            None,
            None,
            None
        )

# ----------------------
# MAIN
# ----------------------

if __name__ == "__main__":

    rss_news = get_rss_news()

    published = 0

    for item in rss_news:

        if published >= MAX_POSTS:
            break

        source_text = (
            item["title"] +
            "\n\n" +
            item["summary"]
        )

        if is_blocked(source_text):
            continue

        print(
            f"İşleniyor: {item['title']}"
        )

        title, content, meta, labels = generate_news(
            item["title"],
            source_text
        )

        if not title:
            continue

        publish_to_blogger(
            title,
            content,
            labels,
            meta
        )

        published += 1

    print(
        f"Toplam yayınlanan haber: {published}"
    )
