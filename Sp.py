from playwright import async_api
from bs4 import BeautifulSoup
import asyncio
from config import PROFILE_PATH,USER_AGENT,TARGET_URL,SEARCH,TARGET_POST_NUMBER
async def detail(page):
    try:
        await page.wait_for_load_state()
        await page.wait_for_timeout(5000)
        back_button=page.locator("div[class='close-circle']")
        await back_button.click()
        await page.wait_for_load_state()
        await page.wait_for_timeout(5000)

        await asyncio.sleep(10)
    except Exception as err:
        print(f"详情页操作错误{err}")
async def spider(page):
    try:
        # 去重列表
        data_index_list=[]
        await page.wait_for_load_state()
        await page.wait_for_timeout(5000)

        input_box=page.locator('div[class="input-box"]')
        search_input=input_box.locator('input[id="search-input"]')
        search_button=input_box.locator('div[class="search-icon"]')

        await search_input.type(SEARCH,delay=200)
        await search_button.click()

        await page.wait_for_load_state()
        await page.wait_for_timeout(5000)

        main_div = page.locator('div[class="search-layout__main"]')
        # 初始帖子
        date_index=0
        while date_index<TARGET_POST_NUMBER:
            section_dom = main_div.locator(f'section[class="note-item"][data-index="{date_index}"]')
            if not await section_dom.is_visible():
                    await section_dom.scroll_into_view_if_needed()
            # 分析一下是否为帖子 xhs中存在一个问题会在帖子中参杂推荐列表这里过滤一下
            query_note_list_div=section_dom.locator('div[class="query-note-list"]')
            if await query_note_list_div.count()>0:
                date_index += 1
                continue
            await section_dom.click()
            await detail(page)
            date_index+=1
    except Exception as err:
        print(f"爬虫主函数错误{err}")
async def login(page):
    try:

        await page.wait_for_load_state()
        await page.wait_for_timeout(5000)

        login_button=page.locator('text="登录"')

        while await login_button.count()>0:
            print("监测到未登录，请手动登录！")
            print("登录后请输入回车")
            input()

        return True
    except Exception as err:
        print(f"登录错误{err}")
        return False
async def main():
    try:
        async with async_api.async_playwright() as p:
            context = await p.firefox.launch_persistent_context(user_data_dir=PROFILE_PATH,headless=False,user_agent=USER_AGENT)
            await context.add_init_script('init.js')
            page = await context.new_page()
            await page.goto(TARGET_URL)
            if await login(page):
                print("登录成功")
                await spider(page)
            await asyncio.sleep(60)
    except Exception as err:
        print(f"主函数错误")

if __name__ == '__main__':
    asyncio.run(main())