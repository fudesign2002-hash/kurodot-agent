import os
from flask import Flask
from google import genai
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數 (本地測試用)
load_dotenv()

app = Flask(__name__)
api_key = os.getenv("GEMINI_API_KEY")

@app.route('/')
def hello():
    if not api_key:
        return "❌ 找不到 GEMINI_API_KEY，請確認環境變數有正確設定。", 500
        
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='請用繁體中文回覆我："Hello World！這是一個與 Gemini 串接到 Cloud Run 的測試。"'
        )
        return f"<h1>✅ 來自 Gemini 的回覆：</h1><p>{response.text}</p>"
    except Exception as e:
        return f"❌ 發生錯誤：{str(e)}", 500

if __name__ == "__main__":
    # Cloud Run 會將 PORT 環境變數傳進來
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
