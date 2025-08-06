from typing import List
from urllib.parse import urljoin
import logging

from bs4 import BeautifulSoup

from src.core.settings import settings
from src.scrapers.scraper import PageScraper


logger = logging.getLogger(__name__)


class StartPageParser:
    '''Парсер категорий товаров из каталога'''
    
    def __init__(self):
        self.scraper = PageScraper()
        
    async def get_categories(self, url: str) -> List[str]:
        '''Извлекает ссылки категорий товаров'''
        
        logger.info(f"Получение категорий с: {url}")
        
        html = await self.scraper.scrape_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        items = soup.find_all('div', class_ = 'category-card__name')
        
        categories = []
        for item in items:
            link = item.find('a')
            if link:
                href = link.get('href')
                if href:
                    full_url = urljoin(settings.base_url, href)
                    categories.append(full_url)
                    
                    logger.debug(f"Найдена категория: {full_url}")
        
        logger.info(f"Всего найдено категорий: {len(categories)}")
            
        return categories