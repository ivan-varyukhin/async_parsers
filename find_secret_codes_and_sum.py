import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup

domain = 'https://parsinger.ru/asyncio/create_soup/1/'
link_list = []
res = []

def get_soup(url):
    resp = requests.get(url=url)
    return BeautifulSoup(resp.text, 'lxml')

def get_urls(soup):
    links = soup.find('div', class_='item_card').find_all('a')
    for link in links:
        link_list.append(domain + link['href'])

async def get_data(session, link):
    async with session.get(url=link) as response:
        resp = await response.text()
        soup = BeautifulSoup(resp, 'lxml')
        try:
            res.append(int(soup.find('body').text))
        except:
            pass
        
async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for link in link_list:
            task = asyncio.create_task(get_data(session, link))
            tasks.append(task)
        await asyncio.gather(*tasks)

url = 'https://parsinger.ru/asyncio/create_soup/1/index.html'
soup = get_soup(url)
get_urls(soup)


# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
print(sum(res))