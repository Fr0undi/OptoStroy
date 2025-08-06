import re
import logging
from typing import List, Optional

from bs4 import BeautifulSoup

from src.core.settings import settings
from src.scrapers.scraper import PageScraper
from src.schemas.product import Product, Supplier, SupplierOffer, PriceInfo, Attribute


logger = logging.getLogger(__name__)


class ProductPropertyParser:
    '''Парсер для извлечения информации о товаре'''
    
    def __init__(self):
        self.scraper = PageScraper()
        
    async def parse_product(self, url: str) -> Optional[Product]:
        '''Парсит страницу товара, возвращая объект Product'''
        
        logger.info(f"Парсинг товара: {url}")
        
        html = await self.scraper.scrape_page(url)
        if not html:
            logger.error(f"Не удалось получить HTML: {url}")            
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Извлекаем основную информацию о товарах
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        article = self._extract_article(soup)
        brand = self._extract_brand(soup)
        country_of_origin = self._extract_country(soup)
        category = self._extract_category(soup)
        
        if article is None:
            article = 'Нет данных'
            
        # Извлекаем атрибуты
        attributes = self._extract_attributes(soup)
        
        # Извлекаем информацию о поставщике
        suppliers = self._extract_supplier_info(soup, url)
        
        return Product(
            title = title,
            description = description,
            article = article or 'Нет данных',
            brand = brand,
            country_of_origin = country_of_origin,
            category = category,
            attributes = attributes,
            suppliers = suppliers
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        '''Извлекает название товара'''
        
        # Ищем название товара в основных заголовах
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text(strip = True)        
        
        # Ищем название товара в navigation
        nav_title = soup.find('li', class_ = 'breadcrumb-item active')
        if nav_title:
            return nav_title.get_text(strip = True)
        
        # Ищем название товара в meta-тегах
        meta_title = soup.find('meta', {'itemprop': 'name'})
        if meta_title and meta_title.get('content'):
            return meta_title.get('content')       
        
        return 'Нет данных'
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        '''Извлекает описание товара'''
        
        # Ищем таб описания
        desc_tab = soup.find('div', {'id': 'tab-description'})
        if desc_tab:
            # Ищем первый параграф с описанием
            first_paragraph = desc_tab.find('p')
            if first_paragraph:
                description = first_paragraph.get_text(strip = True)
                if description:
                    return description
        
        # Ищем в основном блоке описание товара
        desc_block = soup.find('div', {'class': 'product__description'})
        if desc_block:
            desc_text = desc_block.get_text(strip = True)
            if desc_text:
                return desc_text       
        
        # Ищем в основном блоке описание под тегом 'p'
        desc_block_p = soup.find('div', {'class': 'product__description'})
        if desc_block_p:
            desc_paragraph = desc_block_p.find('p')
            if desc_paragraph:
                desc_text = desc_paragraph.get_text(strip = True)
                if desc_text:
                    return desc_text
        
        # Ищем в основном блоке описание под тегом 'span'
        desc_block_span = soup.find('div', {'class': 'product__description'})
        if desc_block:
            desc_paragraph = desc_block_span.find('span')
            if desc_paragraph:
                desc_text = desc_paragraph.get_text(strip = True)
                if desc_text:
                    return desc_text
                    
        return 'Нет данных'
    
    def _extract_article(self, soup: BeautifulSoup) -> str:
        '''Извлекает артикул товара'''
        
        # Поиск в основном блоке в span
        sku_span = soup.find('span', class_='variant-sku')
        if sku_span:
            article = sku_span.get_text(strip=True)
            if article and article.strip():
                return article
        
        # Поиск в основном блоке в li
        article_block = soup.find('li', class_='sku sku-show')
        if article_block:
            art_span = article_block.find('span')
            if art_span:
                article = art_span.get_text(strip=True)
                if article and article.strip():
                    return article
        
        # Поиск в meta-тегах
        meta_sku = soup.find('meta', {'itemprop': 'sku'})
        if meta_sku and meta_sku.get('content'):
            article = meta_sku.get('content').strip()
            if article:
                return article
    
        return 'Нет данных'
    
    def _extract_brand(self, soup: BeautifulSoup) -> str:
        '''Извлекает бренд товара'''
        
        # Ищем в основном блоке
        brand_block = soup.find('ul', class_ = 'product__meta')
        if brand_block:
            brand_a = brand_block.find('a')
            if brand_a:
                brand = brand_a.get_text(strip = True)
                if brand and brand.strip():
                    return brand
        
        # Ищем в meta-тегах       
        div_brand = soup.find('div', itemprop = 'brand')
        if div_brand:
            meta_brand = div_brand.find('meta', {'itemprop': 'brand'})
            if meta_brand and meta_brand.get('content'):
                return meta_brand.get('content')
        
        return 'Нет данных'
    
    def _extract_country(self, soup: BeautifulSoup) -> str:
        '''Извлекает страну происхождения'''
        
        tabs_spec = soup.find('div', class_ = 'spec')
        if tabs_spec:
            tabs_sec = tabs_spec.find('div', class_ = 'spec__section')
            if tabs_sec:
                rows = tabs_sec.find_all('div', class_ = 'spec__row')
                for row in rows:
                    name_cell = row.find('div', class_ = 'spec__name')
                    value_cell = row.find('div', class_ = 'spec__value')
                    if name_cell and value_cell:
                        name = name_cell.get_text(strip = True)
                        if name == 'Страна происхождения:':
                            return value_cell.get_text(strip = True)
        
        return 'Нет данных'
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        '''Извлекает категорию товара'''
        
        # Ищем в page-header__breadcrumb
        breadcrumb = soup.find('ol', {'class': 'breadcrumb'})
        if breadcrumb:
            breadcrumb_items = breadcrumb.find_all('li', {'class': 'breadcrumb-item'})
            
            # Собираем все категории, исключая "Главная" и сам товар
            categories = []
            for item in breadcrumb_items:
                if 'active' not in item.get('class', []):
                    link = item.find('a')
                    if link:
                        category = link.get_text(strip = True)
                        if category and category != 'Главная':
                            categories.append(category)
            
            # Возращаем последнюю категорию товара
            if categories:
                return categories[-1]
        
        # Ищем категорию в meta-тегах
        meta_category = soup.find('meta', {'itemprop': 'category'})
        if meta_category and meta_category.get('content'):
            category_chain = meta_category.get('content')
            parts = category_chain.split('/')
            last_category = parts[-1].strip()
            if last_category:
                return last_category
        
        return 'Нет данных'

    def _extract_attributes(self, soup: BeautifulSoup) -> List[Attribute]:
        '''Извлекает атрибуты товара, избегая дублирование'''
        
        
        attributes = []
        seen_attributes = set()
        
        # Извлечённые ранее характеристики
        excluded_attributes = {
            'название', 'описание', 'артикул', 'категория', 'цена', 'стоимость',
            'наличие', 'в наличии', 'бренд', 'марка', 'страна происхождения'
        }
        
        # Ищем блоки характеристик: в табе спецификации и других местах
        specs_to_check = []
        
        # Основной таб спецификации
        spec_tab = soup.find('div', {'id': 'tab-specification'})
        if spec_tab:
            spec_section = spec_tab.find('div', class_='spec__section')
            if spec_section:
                specs_to_check.append(spec_section)
        
        # Альтернативные места
        alternative_specs = soup.find_all('div', class_='spec')
        for spec_block in alternative_specs:
            spec_section = spec_block.find('div', class_='spec__section')
            if spec_section and spec_section not in specs_to_check:
                specs_to_check.append(spec_section)
        
        # Обрабатываем все найденные блоки характеристик
        for spec_section in specs_to_check:
            rows = spec_section.find_all('div', class_='spec__row')
            
            for row in rows:
                name_elem = row.find('div', class_='spec__name')
                value_elem = row.find('div', class_='spec__value')
                
                if name_elem and value_elem:
                    # Извлекаем название характеристики
                    name = name_elem.get_text(strip=True)
                    
                    # Извлекаем значение характеристики
                    # Проверяем есть ли ссылка внутри значения
                    value_link = value_elem.find('a')
                    if value_link:
                        value = value_link.get_text(strip=True)
                    else:
                        value = value_elem.get_text(strip=True)
                    
                    if name and value:
                        name_clean = name.rstrip(':').strip()
                        name_lower = name_clean.lower().strip()   
                        
                        # Пропускаем исключенные характеристики
                        if name_lower in excluded_attributes:
                            continue
                        
                        # Пропускаем дубликаты
                        if name_lower in seen_attributes:
                            continue
                        
                        attributes.append(Attribute(attr_name = name_clean, attr_value = value))
                        seen_attributes.add(name_lower)
    
        return attributes  
   
    def _extract_price(self, soup: BeautifulSoup) -> float:
        '''Извлекает цену товара'''
        
        # Ищем цену в основном блоке товара
        price_block = soup.find('div', class_ = 'product__prices')
        if price_block:
            new_price = price_block.find('span', class_ = 'new-price')
            if new_price:
                new_price_text = new_price.get_text(strip = True)
                
                price_match = re.search(r'(\d{1,3}(?:\s\d{3})*(?:[,\.]\d{2})?)', new_price_text)
                if price_match:
                    price_str = price_match.group(1).replace(' ', '').replace(',', '.')
                    try:
                        return float(price_str)
                    except ValueError:
                        pass
        
            # В случае отсутствия new-price - ищем в old-price        
            old_price = price_block.find('span', class_ = 'old-price')
            if old_price:
                old_price_text = old_price.get_text(strip = True)
                
                price_match = re.search(r'(\d{1,3}(?:\s\d{3})*(?:[,\.]\d{2})?)', old_price_text)
                if price_match:
                    price_str = price_match.group(1).replace(' ', '').replace(',', '.')
                    try:
                        price_value_float = float(price_str)
                        # Проверяем что цена больше 0
                        if price_value_float > 0:
                            return price_value_float
                    except ValueError:
                        pass
        
        # Ищем цену в блоке с атритбутом data-price
        checked_variant = soup.find('input', class_='variant-radio checked')
        if not checked_variant:
            checked_variant = soup.find('input', {'checked': True})
            
        if checked_variant:
            data_price = checked_variant.get('data-price')
            if data_price:
                price_match = re.search(r'(\d{1,3}(?:\s\d{3})*(?:[,\.]\d{2})?)', data_price)
                if price_match:
                    price_str = price_match.group(1).replace(' ', '').replace(',', '.')
                    try:
                        return float(price_str)
                    except ValueError:
                        pass

        # Ищем в meta-тегах
        meta_price = soup.find('meta', {'itemprop': 'price'})
        if meta_price and meta_price.get('content'):
             price_text = meta_price.get('content')
             price_match = re.search(r'(\d{1,3}(?:\s\d{3})*(?:[,\.]\d{2})?)', price_text)
             if price_match:
                 price_str = price_match.group(1).replace(' ', '').replace(',', '.')
                 try:
                     return float(price_str)
                 except ValueError:
                     pass
        
        return 0.0
             
    def _extract_stock(self, soup: BeautifulSoup) -> str:
        '''Извлекает информацию о наличии товара'''
        
        # Ищем в основном блоке товара
        stock_block  = soup.find('ul', class_ = 'product__meta')
        if stock_block:
            stock_info = stock_block.find('span', class_ = 'text-success')
            if stock_info:
                return stock_info.get_text(strip = True)       
         
            availability_item = stock_block.find('li', class_='product__meta-availability')  #ПРОВЕРИТЬ ПРИ ТЕСТЕ НАДО БУДЕТ
            if availability_item:
                status_span = availability_item.find('span')
                if status_span:
                    return status_span.get_text(strip=True)
         
        return 'Нет данных'   
            
    def _extract_supplier_info(self, soup: BeautifulSoup, page_url: str) -> List[Supplier]:
        '''Извлекает информацию о поставщике'''
        
        price = self._extract_price(soup)
        stock = self._extract_stock(soup)
        
        price_info = PriceInfo(qnt = 1, discount = 0, price = price)
        
        supplier_offer = SupplierOffer(
            price = [price_info],
            stock = stock,
            purchase_url = page_url
        )
        
        supplier = Supplier(
            supplier_name = 'ОптоСтрой',
            supplier_phone = '8 (499) 455-50-75; 8 (800) 500-61-72',
            supplier_address = 'Москва, 41км Строительный рынок',
            supplier_description = 'Оптово-розничный магазин строительных материалов',
            supplier_offers = [supplier_offer]
        )
        
        return [supplier]      