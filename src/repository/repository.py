import logging
from src.core.settings import settings
from src.repository.mongo_client import mongo_client
from src.schemas.product import Product

logger = logging.getLogger(__name__)


class ProductRepository:
    
    def __init__(self):
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            self._collection = mongo_client.get_collection(settings.collection_name)
        return self._collection

    async def save_product(self, product: Product):
        try:
            product_dict = product.model_dump()

            # Разная логика поиска для товаров с артикулом и без
            if product.article != 'Нет данных':
                # Товары с артикулом - ищем по артикулу
                search_criterion = {"article": product.article}
                log_id = product.article
            else:
                # Товары без артикула - ищем по названию + URL
                purchase_url = ""
                if product.suppliers and product.suppliers[0].supplier_offers:
                    purchase_url = product.suppliers[0].supplier_offers[0].purchase_url
                
                search_criterion = {
                    "title": product.title,
                    "article": "Нет данных"
                }
                
                # Добавляем URL в критерии если есть
                if purchase_url:
                    search_criterion["suppliers.supplier_offers.purchase_url"] = purchase_url
                
                log_id = f"'{product.title[:30]}...'"

            # Проверяем существование
            existing = await self.collection.find_one(search_criterion)

            if existing:
                await self.collection.update_one(
                    search_criterion,
                    {"$set": product_dict}
                )
                logger.info(f"Обновлен: {log_id}")
            else:
                await self.collection.insert_one(product_dict)
                logger.info(f"Сохранен: {log_id}")

        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")

    async def get_products_count(self) -> int:
        """Возвращает общее количество товаров"""
        
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Ошибка подсчета товаров: {e}")
            return 0

    async def get_products_without_article_count(self) -> int:
        """Возвращает количество товаров без артикула"""
        
        try:
            return await self.collection.count_documents({"article": "Нет данных"})
        except Exception as e:
            logger.error(f"Ошибка подсчета товаров без артикула: {e}")
            return 0