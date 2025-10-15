import requests
from playwright import async_api
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
from config import PROFILE_PATH,USER_AGENT,TARGET_URL,SEARCH,TARGET_POST_NUMBER,SAVE_POST
import json
import os
import shutil
async def get_img_post(page,file_path):
    try:
        img_list=[]
        await page.wait_for_load_state()
        await page.wait_for_timeout(5000)
        soup=BeautifulSoup(await page.content(),'lxml')
        root_div=soup.find("div",attrs={"class":"swiper-wrapper"})
        if root_div is not None:
            div_list=root_div.find_all("div",attrs={"class":"note-slider-img xhs-webplayer xhsplayer xhsplayer-pc"})
            if div_list is not None:
                for div in div_list:
                    img=div.find("img")
                    img_list.append(img["src"])
        # 存在可以抓取的图片资源
        if len(img_list)>0:
            for url in img_list:
                req=requests.get(url)
                # 如果获取图片成功
                if req.status_code==200:
                    if not os.path.exists(file_path+"/img"):
                        os.mkdir(file_path+"/img")
                    with open(file_path+"/img/"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".jpg","wb") as f:
                        f.write(req.content)
    except Exception as err:
        print(f"爬取图片资源错误{err}")
async def catch_video(response):
    try:
        url=response.url
        if ".mp4" in url:
            req=requests.get(url)
            if req.status_code==200:
                with open("temporary/"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".mp4","wb") as f:
                    f.write(req.content)
    except Exception as err:
        print(f"监听抓取视频错误{err}")
# 该函数不做爬取处理将临时文件夹中存放的文件移动到指定文件夹中
async def get_video_post(file_path):
    try:
        if not os.path.exists(file_path+"/video"):
            os.mkdir(file_path+"/video")
        for file in os.listdir("temporary/"):
            target_path=os.path.join(file_path+"/video",file)
            now_path=os.path.join("temporary/",file)
            shutil.move(now_path,target_path)
        return True
    except Exception as err:
        print(f"爬取视频资源错误{err}")
async def get_text_post(page,file_path):
    try:
        await page.wait_for_load_state()
        await page.wait_for_timeout(5000)
        soup=BeautifulSoup(await page.content(),'lxml')
        root_div=soup.find("div",attrs={"class":"note-scroller"})
        if root_div is not None:
            title_div=root_div.find("div",attrs={"id":"detail-title","class":"title"})
            content_div=root_div.find("div",attrs={"id":"detail-desc","class":"desc"})
            with open(file_path+"/text.txt","w",encoding="utf-8") as f:
                json.dump({
                    "title":title_div.text if title_div is not None else "",
                    "content":content_div.text if content_div is not None else "",
                },f,ensure_ascii=False,indent=4)
        return True
    except Exception as err:
        print(f"爬取文本失败{err}")
async def detail(page):
    try:
        # 以时间戳来定义文件名称
        file_path=SAVE_POST+"/"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # 创建目录
        os.mkdir(file_path)
        # 定义默认函数开启监听（独立线程处理）
        handler = lambda r: asyncio.create_task(catch_video(r))
        page.on("response",handler)
        await page.wait_for_load_state()
        await page.wait_for_timeout(5000)
        await get_img_post(page,file_path)
        await get_text_post(page,file_path)
        # 退出详情页爬虫移除监听
        page.remove_listener("response",handler)
        back_button=page.locator("div[class='close-circle']")
        # 监听移除后处理视频内容
        await get_video_post(file_path)
        await back_button.click()
        await page.wait_for_load_state()
        await page.wait_for_timeout(5000)

        await asyncio.sleep(30)
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