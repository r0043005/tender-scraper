import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

async def scrape_tenders():
    print("正在啟動瀏覽器...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 增加視窗大小確保按鈕不會因為響應式設計而隱藏
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        url = "https://web.pcc.gov.tw/prkms/tender/common/basic/indexTenderBasic"
        print(f"正在前往: {url}")
        
        try:
            # 增加等待時間並使用 commit 確保頁面載入
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            print(f"目前頁面標題: {await page.title()}")

            # 嘗試多種方式定位查詢按鈕
            print("正在尋找查詢按鈕...")
            # 根據使用者提供的 HTML 結構，使用 ID 定位最準確
            search_button = page.locator("#basicTenderSearchId")
            
            # 檢查是否存在，如果不存在則使用文字定位備援
            if await search_button.count() == 0:
                print("找不到 #basicTenderSearchId，嘗試使用文字定位...")
                search_button = page.get_by_text("查詢", exact=True).first

            # 等待按鈕出現、可見且可用
            await search_button.wait_for(state="visible", timeout=15000)
            print("點擊查詢按鈕...")
            await search_button.click()

            # 等待結果表格載入
            print("等待搜尋結果...")
            try:
                await page.wait_for_selector("#print_area", timeout=30000)
            except:
                print("搜尋結果表格 (#print_area) 未出現，可能是查無資料或網站回應慢。")
                # 即使沒資料也產生空檔案，避免 Git 報錯
                with open("tenders.json", "w", encoding="utf-8") as f:
                    json.dump([], f)
                return

            # 抓取表格行
            rows = await page.locator("#print_area table tr").all()
            tenders_data = []
            
            for row in rows[1:]:
                cols = await row.locator("td").all_inner_text()
                if len(cols) >= 7:
                    link_element = row.locator("td a").first
                    detail_url = ""
                    if await link_element.count() > 0:
                        href = await link_element.get_attribute("href")
                        if href:
                            detail_url = "https://web.pcc.gov.tw" + href if href.startswith("/") else href

                    item = {
                        "agency_name": cols[1].strip(),
                        "tender_id": cols[2].strip(),
                        "tender_name": cols[3].strip(),
                        "procurement_nature": cols[4].strip(),
                        "category": cols[5].strip(),
                        "publish_date": cols[6].strip(),
                        "deadline": cols[7].strip() if len(cols) > 7 else "",
                        "detail_url": detail_url
                    }
                    tenders_data.append(item)
            
            print(f"成功抓取 {len(tenders_data)} 筆標案資料。")

            with open("tenders.json", "w", encoding="utf-8") as f:
                json.dump(tenders_data, f, ensure_ascii=False, indent=4)
            
            print("資料已成功儲存至 tenders.json")

        except Exception as e:
            print(f"發生錯誤: {e}")
            # 確保即使發生錯誤也會產生一個空的 JSON，防止 Git add 報錯
            if not os.path.exists("tenders.json"):
                with open("tenders.json", "w", encoding="utf-8") as f:
                    json.dump([], f)
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_tenders())
