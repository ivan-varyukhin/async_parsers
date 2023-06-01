import time
import aiofiles
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import os


async def write_file(session, url, name_img):
    async with aiofiles.open(f"images/{name_img}", mode='wb') as f:
        async with session.get(url) as response:
            async for x in response.content.iter_chunked(2048):
                await f.write(x)
        print(f'Изображение сохранено {name_img}')

async def main(url):
    shema = "https://parsinger.ru/asyncio/aiofile/2/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            links = [shema + x['href'] for x in soup.find_all('a')]
            img_urls = []
            tasks = []
            for link in links:
                async with session.get(link) as resp2:
                    soup2 = BeautifulSoup(await resp2.text(), 'lxml')
                    img_urls.extend([x['src'] for x in soup2.find_all('img')])
            for link in img_urls:
                name_img = link.split('/')[-1]
                task = asyncio.create_task(write_file(session, link, name_img))
                tasks.append(task)
            await asyncio.gather(*tasks)

def get_folder_size(filepath, size=0):
    for root, dirs, files in os.walk(filepath):
        for f in files:
            size += os.path.getsize(os.path.join(root, f))
    return size


url = "https://parsinger.ru/asyncio/aiofile/2/index.html"
start = time.perf_counter()
# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main(url))

print(f'Cохранено изображений {len(os.listdir("images/"))} за {round(time.perf_counter() - start, 3)} сек')
print(f"Размер файлов: {get_folder_size('images/')} байт")