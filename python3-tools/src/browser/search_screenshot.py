from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=200)
        page = browser.new_page()

        page.goto("https://www.baidu.com/", wait_until="domcontentloaded")

        # 尝试用 JS 填写（绕过 hidden 限制）
        page.evaluate("""() => {
            const el = document.querySelector("input[name='wd']");
            if (el) el.value = "Playwright 自动化";
        }""")
        page.press("input[name='wd']", "Enter")

        page.wait_for_selector("#content_left")
        page.screenshot(path="baidu_search.png")

        print("✅ 已完成搜索并保存截图：baidu_search.png")
        browser.close()


if __name__ == "__main__":
    main()
