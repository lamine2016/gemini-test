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

    SPIN_STYLE = """
BAŞLIK:
{Güncel Gelişmeler Açıklandı|Son Durum Belli Oldu|Yeni Rapor Yayımlandı|Dikkat Çeken Ayrıntılar Ortaya Çıktı}

GİRİŞ:
{Uzmanların değerlendirmelerine göre|Son verilere göre|Yapılan açıklamalara göre|Güncel raporlar doğrultusunda}

GELİŞME:
{Konuya ilişkin değerlendirmeler sürüyor.|Yeni bilgiler kamuoyu ile paylaşılmaya devam ediyor.|İlgili gelişmeler yakından takip ediliyor.|Yetkililer süreci yakından izliyor.}

SONUÇ:
{Yeni gelişmelerin önümüzdeki günlerde netleşmesi bekleniyor.|Resmi açıklamaların takip edilmesi tavsiye ediliyor.|Uzmanlar sürecin yakından takip edilmesini öneriyor.|Konu gündemdeki yerini koruyor.}
"""

    if lang == "tr":

        prompt = (
            f"{topic} kategorisinde güncel ve özgün bir haber yaz.\n\n"

            "Aşağıdaki spintax yapısını birebir kullanma.\n"
            "Sadece anlatım çeşitliliğini örnek al.\n\n"

            f"{SPIN_STYLE}\n\n"

            "Kurallar:\n"
            "- Haber dili kullan.\n"
            "- SEO uyumlu yaz.\n"
            "- En az 250 kelime yaz.\n"
            "- Tercihen 350-500 kelime arasında olsun.\n"
            "- Başlık dikkat çekici olsun.\n"
            "- Aynı cümleyi tekrar etme.\n"
            "- Giriş, gelişme ve sonuç bölümleri olsun.\n"
            "- Doğal gazetecilik dili kullan.\n"
            "- HTML formatında üret.\n"
            "- <p> ve <h2> etiketlerini kullan.\n\n"

            "Çıktı tam olarak şu formatta olmalı:\n"
            "BAŞLIK: [Haber Başlığı]\n"
            "META: [150 karakterlik meta açıklama]\n"
            "ETİKETLER: [5 tane haberle ilgili etiket, virgülle ayrılmış]\n"
            "İÇERİK: [HTML haber içeriği]"
        )

    else:

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
            model="gemini-2.5-flash",
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

        title = f"{topic.capitalize()} Gelişmeleri"

        meta = f"{topic} hakkında güncel gelişmeler ve son bilgiler."

        labels = [topic]

        content = f"""
<p>{topic.capitalize()} konusunda güncel bilgiler kamuoyu ile paylaşıldı.</p>

<h2>Son Durum</h2>

<p>Konuya ilişkin gelişmeler yakından takip edilirken yeni açıklamaların gün içerisinde gelmesi bekleniyor.</p>

<p>Uzmanlar ve yetkililer tarafından yapılan değerlendirmeler doğrultusunda vatandaşların resmi kaynakları takip etmeleri öneriliyor.</p>

<h2>Güncel Değerlendirmeler</h2>

<p>Kamuoyunu ilgilendiren gelişmelerin düzenli olarak güncelleneceği belirtilirken konuya ilişkin yeni bilgilerin paylaşılması bekleniyor.</p>
"""

        return title, content, meta, labels

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
        "maç haberleri", "trafik Haberleri", "hava durumu"
    ]
    topics_de = [
        "Deutschland Wirtschaft", "Deutschland Wetter"
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

