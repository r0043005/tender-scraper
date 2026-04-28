import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

async def scrape_tenders():
    print("正在啟動瀏覽器...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        url = "https://web.pcc.gov.tw/prkms/tender/common/basic/indexTenderBasic"
        print(f"正在前往: {url}")
        
        try:
            # 增加等待時間
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            print(f"目前頁面標題: {await page.title()}")

            # 確保檔案至少會被建立
            if not os.path.exists("tenders.json"):
                with open("tenders.json", "w", encoding="utf-8") as f:
                    json.dump([], f)

            print("嘗試使用 JavaScript 強制觸發查詢按鈕...")
            # 直接在頁面執行查詢函數，避開所有定位問題
            await page.evaluate("() => { if(typeof basicTenderSearch === 'function') { basicTenderSearch(); } else { document.getElementById('basicTenderSearchId').click(); } }")

            # 等待結果表格載入
            print("等待搜尋結果...")
            try:
                # 增加等待時間至 60 秒，政府網站有時很慢
                await page.wait_for_selector("#print_area", timeout=60000)
            except:
                print("搜尋結果未出現，可能需要更多時間或查無資料。")
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
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_tenders())
