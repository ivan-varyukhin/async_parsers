import time
import aiofiles
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os


async def write_file(session, url, name_img, semaphore):
    async with semaphore:
        async with aiofiles.open(f"images/{name_img}", mode='wb') as f:
            async with session.get(url) as response:
                async for x in response.content.iter_chunked(2048):
                    await f.write(x)
            print(f'Изображение сохранено {name_img}')

async def main(url):
    shema = "https://parsinger.ru/asyncio/aiofile/3/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            img_urls = []
            tasks = []
            soup = BeautifulSoup(await resp.text(), 'lxml')
            links1 = [shema + x['href'] for x in soup.find_all('a')]
            links2 = []

            for link in links1:
                shema2 = '/'.join(link.split('/')[:-1])
                async with session.get(link) as resp2:
                    soup2 = BeautifulSoup(await resp2.text(), 'lxml')
                    links2.extend([shema2 + '/' + x['href'] for x in soup2.find_all('a')])

            for link in links2:
                async with session.get(link) as resp3:
                    soup3 = BeautifulSoup(await resp3.text(), 'lxml')
                    img_urls.extend([x['src'] for x in soup3.find_all('img')])

            for link in set(img_urls):
                name_img = link.split('/')[-1]
                semaphore = asyncio.Semaphore(100)
                task = asyncio.create_task(write_file(session, link, name_img, semaphore))
                tasks.append(task)
            await asyncio.gather(*tasks)

def get_folder_size(filepath, size=0):
    for root, dirs, files in os.walk(filepath):
        for f in files:
            size += os.path.getsize(os.path.join(root, f))
    return size


url = "https://parsinger.ru/asyncio/aiofile/3/index.html"

start = time.perf_counter()
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main(url))

print(f'Cохранено изображений {len(os.listdir("images/"))} за {round(time.perf_counter() - start, 3)} сек')
print(f"Размер файлов: {get_folder_size('images/')} байт")