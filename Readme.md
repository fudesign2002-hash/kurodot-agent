# 🎨 Kurodot AI: Multi-Agent Curatorial Orchestrator
一個基於 Gemini 1.5 Pro 打造的次世代多代理人策展系統。它將複雜的數位展覽策展流程自動化，透過「AI 策展工作坊」的多代理人協作架構，將原始展覽數據與視覺靈感，轉化為專業、高品質的策展設計資產。


## Interactive UI: AI Curation Canvas | 核心視覺：AI 策展工作坊
採用「畫布 (Canvas)」設計，使用者Chief Curator （首席策展人）透過「便利貼」與團隊溝通。每種顏色代表一個專業領域，確保任務邊界清晰。

### Workflow / 協同工作流程
0. #fefefe Note (未指派):
Drop an idea or a URL. The Project Manager will intervene, parse the data, and automatically dispatch downstream tasks.

1. #f1a456 Project Manager (project-manager.py):
收集原始創意或解析 URL。若任務未指派，PM 會介入解析數據並自動分派任務。
Drop an idea or a URL. The Project Manager will intervene, parse the data, and automatically dispatch downstream tasks.

2. #ce538a VI Designer (vi-designer.py):
讀取參考圖語義，利用 Imagen 3 生成展覽主視覺、配色方案與設計元素。
Strict visual, color, and image generation instructions.

3. #87e5e7 Editor (editor.py):
將結構化數據（JSON）轉化為流暢的策展論述、作品賞析，並提供高品質的中英雙語轉譯。
Strict tone, translation, and narrative instructions.

4. #5062c8 Data Analyst (analyst.py):
對接 Umami API 分析即時流量，識別最受歡迎的作品，為策展提供數據支持。
Data interpretation instructions.

5. #272a3a Tech Producer (tech-producer.py):
負責檔案格式輸出（PDF, SVG, JPG, PNG）。搞定檔案封裝、Google Cloud Storage 存儲。


## 🌟 Technical Highlights: Domain Isolation | 技術亮點：代理人邊界感

專案核心實驗點在於：證明多代理人系統可以像人類專業團隊一樣，在不破壞他人成果的前提下，進行高度並行的協同工作。

* **Prompt Sharding (獨立約束):** Every agent has strict Boundary Constraints to prevent overstepping. 
* **Non-Interference (不干擾原則):** When the Editor modifies text, the Tech Producer locks visual assets. When the VI Designer alters styles, text remains Read-Only.
* **Version Control (分開控管):** Each Agent maintains its own state branch. The final merge happens only during the Tech Production phase.



開發指令!!!!!重要, 絕對遵守
所有角色的agent的功能只寫在自己的.py檔裡面, 不能開新檔案
designer要確保所有文字顯示正常, 不能超出外匡, 有正確的padding,
editor只能改文字不能改design
pm要可以分派任務
tech要可以輸出不同格式檔案 jpg,png,pdf, svg
每次完成更新告訴我新的版本號碼我可以知道有沒有讀到舊的
ui 全英文
自動檢查不可以出現錯誤, 有就修好(index):762 Uncaught SyntaxError: Unexpected token '}' (at (index):762:9)


整理ui非常簡單,
有sticky note
agent按鈕列
agent狀態列
畫布 在畫面中央