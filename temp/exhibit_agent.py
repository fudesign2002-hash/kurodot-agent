import os
import requests
from flask import Flask, send_file
from google import genai
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 載入 .env 檔案
load_dotenv()

app = Flask(__name__)
api_key = os.getenv("GEMINI_API_KEY")

def generate_poster_text(exhibit_data):
    """將 API 取得的 JSON 丟給 Gemini，產出海報文字"""
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    我有一個展覽的 JSON 資料如下：
    {exhibit_data}
    
    請幫我根據以上資料，產生一份適合放在「展覽海報」上的精簡且吸引人的文字。
    回覆時請不要包含任何 markdown，直接給我純文字，內容包含以下幾點：
    1. 展覽主標題 (吸引人的短句)
    2. 展覽副標或簡介 (1-2句)
    3. 展出日期與時間 (精簡)
    4. 展出地點 (精簡)
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini 發生錯誤: {e}")
        return "無法生成海報內容，請確認 Gemini 狀態。"

@app.route('/poster')
def create_poster():
   # 1. 以假資料暫代 API 發生 Exception 或 401 狀態
    api_url = "https://beta.app.kurodot.io/api/exhibit?id=bauhaus-blueprint-qevdv"
    try:
        req = requests.get(api_url)
        # 如果不是 200 或解析 json 失敗，則使用預設的假資料
        if req.status_code == 200:
            data = req.json()
        else:
            print("API 需要驗證或失敗，使用假資料進行測試。")
            data = {
                "title": "包浩斯百年紀念特展 Bauhaus Concept",
                "description": "這是一場探索包浩斯設計如何重塑現代建築與藝術的特展。呈現從德國魏瑪到柏林的經典家具、建築藍圖及工業設計。",
                "date": "2026/05/10 - 2026/08/20",
                "location": "台北市立美術館一樓展廳",
                "tags": ["設計", "建築", "包浩斯"]
            }
    except Exception as e:
        print("讀取 API 失敗，使用假資料進行測試。")
        data = {
            "title": "包浩斯百年紀念特展 Bauhaus Concept",
            "description": "這是一場探索包浩斯設計如何重塑現代建築與藝術的特展。呈現從德國魏瑪到柏林的經典家具、建築藍圖及工業設計。",
            "date": "2026/05/10 - 2026/08/20",
            "location": "台北市立美術館一樓展廳",
            "tags": ["設計", "建築", "包浩斯"]
        }
        
    # 2. 呼叫 Gemini 幫助撰寫文案
    poster_text = generate_poster_text(data)
    
    # 3. 建立 PDF 海報 (儲存暫存檔)
    pdf_filename = "poster.pdf"
    
    # 這裡示範使用 reportlab 快速建立一個 PDF
    # 註冊中文字體 (Noto Sans CJK TC) 確保中文可以正常顯示
    pdfmetrics.registerFont(TTFont('NotoSansCJK', 'NotoSansCJKtc-Regular.otf'))
    
    c = canvas.Canvas(pdf_filename)
    c.setFont("NotoSansCJK", 24)
    c.drawString(50, 750, "Exhibition Poster (AI Generated)")
    
    c.setFont("NotoSansCJK", 12)
    y_position = 700
    
    # 將 Gemini 回覆的一大段字切分成多行顯示
    for line in poster_text.split('\n'):
        if line.strip():
            c.drawString(50, y_position, line.strip())
            y_position -= 20
        
    c.save()
    
    # 回傳 PDF 檔案
    return send_file(pdf_filename, as_attachment=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)