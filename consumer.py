import os
import asyncio
import aiohttp
from dotenv import load_dotenv
import aio_pika
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

load_dotenv()

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
QUEUE_NAME = os.getenv("QUEUE_NAME")

TIMEOUT = 10


async def fetch_page(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as e:
        print(f"Ошибка загрузки страницы {url}: {e}")
        return None


async def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        link_text = a_tag.get_text(strip=True) or "No text"
        full_url = urljoin(base_url, href)
        parsed_base = urlparse(base_url)
        parsed_url = urlparse(full_url)
        if parsed_base.netloc == parsed_url.netloc:
            links.add((full_url, link_text))
    return links


async def publish_to_queue(channel, link):
    await channel.default_exchange.publish(
        aio_pika.Message(body=link.encode()),
        routing_key=QUEUE_NAME,
    )


async def process_message(channel, url):
    async with aiohttp.ClientSession() as session:
        html = await fetch_page(session, url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            page_title = soup.title.string.strip() if soup.title else "No title"
            print(f"Обработка страницы: {page_title} ({url})")
            links = await extract_links(html, url)
            for link_url, link_text in links:
                print(f"Найдена ссылка: {link_text} ({link_url})")
                await publish_to_queue(channel, link_url)


async def consume():
    connection = await aio_pika.connect_robust(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        login=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD,
    )
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)

        print("Ожидание сообщений...")

        while True:
            try:
                message = await queue.get(timeout=TIMEOUT)
                async with message.process():
                    url = message.body.decode()
                    await process_message(channel, url)
            except aio_pika.exceptions.QueueEmpty:
                print(f"Нет сообщений в течение {TIMEOUT} секунд. Остановка консумера.")
                break

if __name__ == "__main__":
    asyncio.run(consume())
