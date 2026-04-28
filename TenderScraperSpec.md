# 政府採購招標平台爬蟲開發規格書 (Specification)

## 1. 專案概述
本專案旨在開發一個自動化爬蟲工具，用於從「政府採購網」抓取招標公告資訊。該平台是台灣政府採購案的核心發布管道，包含工程、財物及勞務各類標案。

*   **目標網址**: [政府採購網 - 招標查詢](https://web.pcc.gov.tw/prkms/tender/common/basic/indexTenderBasic)
*   **主要目標**: 自動化執行查詢、解析結果列表，並視需求進入詳情頁抓取細部規格。

## 2. 技術架構建議
由於目標網站高度依賴 JavaScript 進行頁面渲染與分頁，建議採用以下技術棧：

*   **語言**: Python 或 Node.js (TypeScript)
*   **核心工具**:
    *   **瀏覽器自動化**: Playwright (首選，速度快且 API 現代化) 或 Selenium。
    *   **解析工具**: BeautifulSoup4 (Python) 或 Cheerio (Node.js) 用於靜態 HTML 片段解析。
    *   **資料儲存**: CSV, JSON 或 資料庫 (PostgreSQL/MongoDB)。

## 3. 抓取欄位定義 (Data Schema)

### 3.1 搜尋結果列表
| 欄位名稱 | 描述 | 範例 |
| :--- | :--- | :--- |
| `agency_name` | 招標機關名稱 | 臺北市政府工務局 |
| `tender_id` | 標案案號 | 112001-A |
| `tender_name` | 標案名稱 | 113年度辦公大樓清潔維護案 |
| `procurement_nature` | 招標方式 | 公開招標 |
| `category` | 採購性質 | 勞務類 |
| `publish_date` | 公告日期 | 2024/04/28 |
| `deadline` | 截止投標日期 | 2024/05/10 17:00 |
| `detail_url` | 詳情頁連結 | https://web.pcc.gov.tw/... |

### 3.2 標案詳情 (進階抓取)
| 欄位名稱 | 描述 | 範例 |
| :--- | :--- | :--- |
| `budget_amount` | 預算金額 | 5,000,000 |
| `location` | 履約地點 | 臺北市 |
| `contact_person` | 聯絡人 | 王小明 |
| `contact_phone` | 聯絡電話 | 02-23456789 |
| `qualification` | 投標廠商資格 | 詳見招標文件 |

## 4. 爬蟲工作流程

1.  **初始化**: 啟動 headless 瀏覽器並導航至目標 URL。
2.  **條件輸入**:
    *   自動填入搜尋關鍵字或選擇日期範圍。
    *   點擊「查詢」按鈕。
3.  **列表抓取**:
    *   等待結果表格加載 (Wait for Selector)。
    *   迭代表格列 (Rows)，提取各欄位資訊。
4.  **分頁處理**:
    *   偵測「下一頁」按鈕狀態。
    *   點擊分頁並等待 AJAX 內容更新。
5.  **深度抓取 (Optional)**: 點擊各標案連結進入詳情頁，抓取詳細預算與規格。
6.  **資料持久化**: 將結果存入指定格式 (如 `data.csv`)。

## 5. 技術挑戰與解決方案

*   **動態內容**: 使用 `page.wait_for_selector()` 確保內容完全載入後再進行解析。
*   **反爬機制**: 
    *   設置隨機的 `User-Agent`。
    *   加入隨機延遲 (`time.sleep` 或 `page.wait_for_timeout`)。
    *   模擬真實用戶行為 (Mouse movement/Click)。
*   **Session 管理**: 該網站可能使用 Session/Cookies 維持查詢狀態，自動化工具需妥善處理 Cookie。
*   **編碼問題**: 確保輸出格式支援 UTF-8 以正確處理繁體中文。

## 6. 注意事項與法律合規
*   **遵守 robots.txt**: 確認網站對爬蟲的限制。
*   **存取頻率**: 避免短時間內發送大量請求，造成伺服器負擔。
*   **資料用途**: 確保抓取的公開資訊僅用於合法合規之分析用途。
