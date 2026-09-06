import os

api_key = os.environ.get("GEMINI_API_KEY", "YOK")
print("Gemini API Key:", api_key)
def generate_news():
    title = "Bugün Almanya’da Ekonomi Gelişmeleri"
    content = (
        "Almanya’da bugün açıklanan ekonomik veriler, "
        "enflasyonun %3 seviyesinde olduğunu gösterdi. "
        "Uzmanlar enerji fiyatlarının etkisini tartışıyor."
    )
    return title, content
