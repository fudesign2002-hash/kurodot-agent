import json

def get_valid_images(artworks):
    """從作品列表中尋找適合的平面圖檔，並回傳 (作品標題, 網址, 媒材) 的列表"""
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
    valid_artworks = []
    
    for art in artworks:
        url = art.get('artworkFile', '')
        if any(ext in url.lower() for ext in valid_extensions):
            title = art.get('title', 'Untitled')
            medium = art.get('medium', 'Digital')
            date = art.get('date', '')
            valid_artworks.append({
                'title': title,
                'url': url,
                'medium': medium,
                'date': date
            })
    return valid_artworks

def generate_booklet(json_filepath, output_html):
    with open(json_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    exhibition = data.get('exhibition', {})
    artworks = data.get('artworks', [])
    stats = data.get('stats', {})
    
    # Exhibition details
    title = exhibition.get('title', 'UNTITLED')
    subtitle = exhibition.get('subtitle', '')
    artist = exhibition.get('artist', 'Unknown')
    overview = exhibition.get('overview', '').replace('\n', '<br>')
    venue = exhibition.get('venue', 'TBA')
    
    # Artwork images
    valid_artworks = get_valid_images(artworks)
    cover_image = valid_artworks[0]['url'] if valid_artworks else 'https://via.placeholder.com/800x1200?text=No+Cover'
    
    # Stats details (from Umami)
    pageviews = stats.get('pageviews', 0)
    visitors = stats.get('visitors', 0)
    visits = stats.get('visits', 0)
    totaltime = stats.get('totaltime', 0) 
    # Optional: convert total time to minutes or hours
    total_time_mins = round(totaltime / 60)
    
    # Artwork Gallery HTML Generation (Page 3)
    gallery_html = ""
    # Select up to 4 artworks for the gallery page
    for art in valid_artworks[1:5]: 
        gallery_html += f"""
        <div class="art-card">
            <div class="art-img" style="background-image: url('{art['url']}')"></div>
            <div class="art-info">
                <h3>{art['title']}</h3>
                <p>{art['medium']} | {art['date']}</p>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Exhibition Booklet</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,700;1,400&family=Montserrat:wght@300;400;600;700&display=swap');
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            background-color: #e0e0e0;
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: 'Montserrat', sans-serif;
            padding: 40px;
            gap: 40px;
        }}
        
        /* A4 Page Styling */
        .page {{
            width: 210mm;
            height: 297mm;
            background-color: #ffffff;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            position: relative;
            overflow: hidden;
            flex-shrink: 0;
            page-break-after: always;
        }}

        @media print {{
            body {{ background-color: #ffffff; padding: 0; gap: 0; }}
            .page {{ box-shadow: none; margin: 0; }}
        }}

        /* --- PAGE 1: COVER --- */
        .page-cover {{
            display: flex;
            flex-direction: column;
        }}
        .cover-img {{
            flex: 7;
            background-image: url('{cover_image}');
            background-size: cover;
            background-position: center;
        }}
        .cover-text {{
            flex: 3;
            background-color: #111;
            color: #fff;
            padding: 40px 50px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .cover-text h1 {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 80px;
            line-height: 0.9;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .cover-text h2 {{
            font-size: 18px;
            font-weight: 300;
            letter-spacing: 2px;
            color: #b0b0b0;
            margin-bottom: 30px;
        }}
        .cover-text h3 {{
            border-top: 1px solid #fff;
            padding-top: 20px;
            font-size: 20px;
            letter-spacing: 4px;
            text-transform: uppercase;
        }}

        /* --- PAGE 2: OVERVIEW --- */
        .page-overview {{
            padding: 80px;
            display: flex;
            flex-direction: column;
        }}
        .section-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 50px;
            margin-bottom: 20px;
            border-bottom: 2px solid #111;
            padding-bottom: 10px;
        }}
        .overview-content {{
            font-size: 16px;
            line-height: 2;
            column-count: 2;
            column-gap: 40px;
            text-align: justify;
            margin-top: 20px;
        }}

        /* --- PAGE 3: GALLERY --- */
        .page-gallery {{
            padding: 60px;
            display: flex;
            flex-direction: column;
        }}
        .gallery-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-gap: 30px;
            margin-top: 30px;
            flex: 1;
        }}
        .art-card {{
            display: flex;
            flex-direction: column;
            border: 1px solid #eee;
            padding: 10px;
        }}
        .art-img {{
            flex: 1;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            min-height: 250px;
            margin-bottom: 15px;
        }}
        .art-info h3 {{ font-size: 16px; margin-bottom: 5px; }}
        .art-info p {{ font-size: 12px; color: #666; }}

        /* --- PAGE 4: IMPACT (STATS) --- */
        .page-stats {{
            background-color: #111;
            color: #fff;
            padding: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .page-stats .section-title {{
            color: #fff;
            border-bottom: 2px solid #444;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-gap: 40px;
            margin-top: 50px;
        }}
        .stat-box {{
            background: #222;
            padding: 40px;
            text-align: center;
            border-radius: 8px;
        }}
        .stat-num {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 60px;
            color: #ff4757;
            margin-bottom: 10px;
        }}
        .stat-label {{
            font-size: 14px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #aaa;
        }}

        /* --- PAGE 5: BACK COVER --- */
        .page-back {{
            background-color: #f8f8f8;
            padding: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}
        .back-title {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 40px;
            margin-bottom: 20px;
        }}
        .venue-info {{
            font-size: 18px;
            letter-spacing: 2px;
            color: #555;
            margin-bottom: 40px;
        }}
        .logo {{
            width: 100px;
            height: 100px;
            border: 2px solid #111;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            letter-spacing: 2px;
        }}

    </style>
</head>
<body>

    <!-- PAGE 1: COVER -->
    <div class="page page-cover">
        <div class="cover-img"></div>
        <div class="cover-text">
            <h1>{title}</h1>
            <h2>{subtitle}</h2>
            <h3>By {artist}</h3>
        </div>
    </div>

    <!-- PAGE 2: OVERVIEW -->
    <div class="page page-overview">
        <h2 class="section-title">The Exhibition</h2>
        <div class="overview-content">
            {overview}
        </div>
    </div>

    <!-- PAGE 3: SELECTED WORKS -->
    <div class="page page-gallery">
        <h2 class="section-title">Selected Works</h2>
        <div class="gallery-grid">
            {gallery_html}
        </div>
    </div>

    <!-- PAGE 4: DIGITAL IMPACT (UMAMI STATS) -->
    <div class="page page-stats">
        <h2 class="section-title">Digital Impact</h2>
        <p style="margin-top: 20px; color: #ccc; font-size: 18px;">Exhibition analytics & visitor engagement tracking.</p>
        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-num">{pageviews:,}</div>
                <div class="stat-label">Page Views</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">{visitors:,}</div>
                <div class="stat-label">Unique Visitors</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">{visits:,}</div>
                <div class="stat-label">Total Sessions</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">{total_time_mins:,}</div>
                <div class="stat-label">Total Time (Mins)</div>
            </div>
        </div>
    </div>

    <!-- PAGE 5: BACK COVER -->
    <div class="page page-back">
        <h2 class="back-title">{title}</h2>
        <div class="venue-info">📍 Hosted at: {venue}</div>
        <div class="logo">KURO</div>
    </div>

</body>
</html>
"""

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 成功生成 {title} 的展覽小冊子 (5頁)")
    print(f"✅ 已整合 Umami 流量分析資料 ({pageviews} pageviews, {visitors} visitors)")
    print(f"✅ 已輸出至 '{output_html}'")

if __name__ == '__main__':
    generate_booklet("exhibition_data.json", "booklet.html")
