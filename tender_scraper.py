import asyncio
import json
import os
from playwright.async_api import async_playwright

async def scrape_tenders():
    print("正在啟動瀏覽器...")
    async with async_playwright() as p:
        # 啟動瀏覽器 (使用 headless=True 表示不顯示視窗，若要看過程可改為 False)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        url = "https://web.pcc.gov.tw/prkms/tender/common/basic/indexTenderBasic"
        print(f"正在前往: {url}")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # 點擊「查詢」按鈕 (不輸入關鍵字預設查詢最近標案)
            print("點擊查詢按鈕...")
            search_button = page.locator("input[value='查詢']")
            await search_button.click()

            # 等待結果表格載入
            print("等待搜尋結果...")
            # 根據網站結構，結果通常位於一個 table 中，我們等待該表格出現
            await page.wait_for_selector("#print_area", timeout=30000)

            # 抓取表格行
            # 排除表頭，選取資料行
            rows = await page.locator("#print_area table tr").all()
            
            tenders_data = []
            
            # 第一行通常是表頭，從第二行開始解析
            for row in rows[1:]:
                cols = await row.locator("td").all_inner_text()
                
                # 確保欄位數量正確 (初步過濾掉無效行)
                if len(cols) >= 7:
                    # 抓取詳情頁連結 (通常在案號或案名欄位中)
                    link_element = row.locator("td a").first
                    detail_url = ""
                    if await link_element.count() > 0:
                        href = await link_element.get_attribute("href")
                        if href:
                            detail_url = "https://web.pcc.gov.tw" + href if href.startswith("/") else href

                    item = {
                        "agency_name": cols[1].strip(),        # 機關名稱
                        "tender_id": cols[2].strip(),          # 標案案號
                        "tender_name": cols[3].strip(),        # 標案名稱
                        "procurement_nature": cols[4].strip(), # 招標方式
                        "category": cols[5].strip(),           # 採購性質
                        "publish_date": cols[6].strip(),       # 公告日期
                        "deadline": cols[7].strip() if len(cols) > 7 else "", # 截止投標
                        "detail_url": detail_url
                    }
                    tenders_data.append(item)
            
            print(f"成功抓取 {len(tenders_data)} 筆標案資料。")

            # 存成 JSON 檔案
            with open("tenders.json", "w", encoding="utf-8") as f:
                json.dump(tenders_data, f, ensure_ascii=False, indent=4)
            
            print("資料已成功儲存至 tenders.json")

        except Exception as e:
            print(f"發生錯誤: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_tenders())
