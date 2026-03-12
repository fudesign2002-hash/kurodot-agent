import os
from google import genai
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# 初始化 Gemini Client
api_key = os.getenv("GEMINI_API_KEY")

def main():
    if not api_key:
        print("❌ 找不到 GEMINI_API_KEY，請確認環境變數 (.env) 已經設定好。")
        return
        
    client = genai.Client(api_key=api_key)
    print("🚀 正在呼叫 Gemini API...")
    try:
        # 呼叫 Gemini 模型
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='請用繁體中文回覆我："Hello World！這是一個與 Gemini 串接的測試。"'
        )
        print("\n✅ 來自 Gemini 的回覆：")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
    except Exception as e:
        print(f"\n❌ 發生錯誤：{str(e)}")

if __name__ == "__main__":
    main()