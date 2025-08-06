import re
import logging
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.core.settings import settings
from src.scrapers.scraper import PageScraper


logger = logging.getLogger(__name__)


class CategoryPageParser:
    '''Парсер ссылок на товары'''
     
    def __init__(self):
        
        self.scraper = PageScraper()
        
    async def get_page_count(self, url: str) -> int:
        '''Определяет количество страниц в категории'''
        
        logger.debug(f"Определение количества страниц для: {url}")
        
        html = await self.scraper.scrape_page(url)
        
        pattern = r'page=(\d+)'
        matches = re.findall(pattern, html)
        
        if matches:
            return max(int(match) for match in matches)
            logger.info(f"Найдено страниц: {max_page}")
        else:
            logger.info("Пагинация не найдена, возвращаем 1 страницу")
            return 1
    
    async def create_page_links(self, url: str) -> List[str]:
        '''Создает ссылки на все страницы категории'''
        
        pages = []
        page_count = await self.get_page_count(url)
        
        logger.info(f"Создание ссылок для {page_count} страниц")
        
        for page_number in range(1, page_count + 1):
            if page_number == 1:
                pages.append(url)
            else:
                pages.append(f'{url}?page={page_number}')  
        
        logger.debug(f"Создано ссылок на страницы: {len(pages)}")    
        return pages
    
    async def get_product_links(self, url: str) -> List[str]:  
        '''Извлекает ссылки на товары со страницы категории'''
        
        logger.debug(f"Извлечение товаров с: {url}")
        
        html = await self.scraper.scrape_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        product_links = set()
        
        item_blocks = soup.find_all('div', class_ = 'product-card')
        logger.debug(f"Найдено блоков товаров: {len(item_blocks)}")
        
        for block in item_blocks:
            title_links = block.find_all('a')
            for link in title_links:
                href = link.get('href')
                if href and href.startswith('products/'):
                    full_url = urljoin(settings.base_url, href)
                    product_links.add(full_url)
        
        products_list = sorted(list(product_links))
        logger.info(f"Найдено товаров: {len(products_list)}")
        
        return products_list