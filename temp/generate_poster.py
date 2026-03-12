import json

def get_best_image_url(artworks):
    """從作品列表中尋找第一個適合用於海報平面的圖檔（排除 .glb 等 3D 模型）"""
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    for art in artworks:
        url = art.get('artworkFile', '')
        # 簡單判斷網址是否包含合法的圖片副檔名
        if any(ext in url.lower() for ext in valid_extensions):
            return url
    return ""

def generate_poster(json_filepath, output_html):
    # 1. 讀取 JSON 資料
    with open(json_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    exhibition = data.get('exhibition', {})
    artworks = data.get('artworks', [])
    
    # 2. 提取需要的展覽資訊
    title = exhibition.get('title', 'UNTITLED EXHIBITION')
    subtitle = exhibition.get('subtitle', '')
    artist = exhibition.get('artist', 'Unknown Artist')
    overview = exhibition.get('overview', '').replace('\n', '<br>')
    venue = exhibition.get('venue', 'TBA')
    
    # 3. 尋找海報主圖 (Cover Image)
    bg_image_url = get_best_image_url(artworks)
    if not bg_image_url:
        bg_image_url = 'https://via.placeholder.com/800x1200?text=No+Image+Available'

    # 4. 生成動態 HTML 內容 (帶有高質感的 CSS 排版)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Poster</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=Playfair+Display:ital@0;1&family=Roboto:wght@300;400&display=swap');
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Roboto', sans-serif;
            padding: 20px;
        }}
        
        .poster-container {{
            width: 800px;
            height: 1131px; /* A4 Ratio */
            background-color: #fff;
            position: relative;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        
        .poster-image {{
            flex: 6;
            background-image: url('{bg_image_url}');
            background-size: cover;
            background-position: center;
            position: relative;
        }}
        
        .poster-content {{
            flex: 4;
            background-color: #1a1a1a;
            color: #ffffff;
            padding: 50px 60px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        .header-section h1 {{
            font-family: 'Oswald', sans-serif;
            font-size: 80px;
            text-transform: uppercase;
            letter-spacing: 5px;
            line-height: 1;
            margin-bottom: 10px;
            color: #ff4757;
        }}
        
        .header-section h2 {{
            font-family: 'Playfair Display', serif;
            font-size: 24px;
            font-style: italic;
            color: #cccccc;
            margin-bottom: 20px;
        }}
        
        .artist-name {{
            font-family: 'Oswald', sans-serif;
            font-size: 20px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #ffffff;
            border-bottom: 2px solid #ff4757;
            display: inline-block;
            padding-bottom: 5px;
            margin-bottom: 30px;
        }}
        
        .overview {{
            font-family: 'Roboto', sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #b3b3b3;
            max-height: 150px;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .footer-section {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            border-top: 1px solid #333;
            padding-top: 20px;
        }}
        
        .venue {{
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #ff4757;
        }}
        
    </style>
</head>
<body>
    <div class="poster-container">
        <!-- 上半部：主視覺圖片 -->
        <div class="poster-image"></div>
        
        <!-- 下半部：展覽資訊排版 -->
        <div class="poster-content">
            <div class="header-section">
                <h1>{title}</h1>
                <h2>{subtitle}</h2>
                <div class="artist-name">By {artist}</div>
                <div class="overview">{overview}</div>
            </div>
            
            <div class="footer-section">
                <div class="venue">📍 Venue: {venue}</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

    # 5. 儲存成為 html
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 成功提取展覽資訊: {title} by {artist}")
    print(f"✅ 成功找到封面圖片: {bg_image_url.split('?')[0].split('%2F')[-1]}")
    print(f"✅海報已生成！請在瀏覽器中打開 '{output_html}' 查看結果。")

if __name__ == '__main__':
    generate_poster("exhibition_data.json", "poster.html")
