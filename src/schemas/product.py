from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class PriceInfo(BaseModel):
    qnt: int = 1
    discount: float = 0
    price: float


class SupplierOffer(BaseModel):
    price: List[PriceInfo]
    stock: str = 'Нет данных'
    delivery_time: str = 'Нет данных'
    package_info: str = 'Нет данных'
    purchase_url: str
    
    
class Supplier(BaseModel):
    dealer_id: str = 'Нет данных'
    supplier_name: str = 'ОптоСтрой'
    supplier_tel: str = '8 (499) 455-50-75; 8 (800) 500-61-72'
    supplier_address: str = 'Москва, 41км Строительный рынок'
    supplier_description: str = 'Описание отсутствует'
    supplier_offers: List[SupplierOffer] = Field(default_factory = list)


class Attribute(BaseModel):
    attr_name: str
    attr_value: str


class Product(BaseModel):
    title: str
    description: str
    article: Optional[str] = 'Нет данных'
    brand: str = 'Нет данных'
    country_of_origin: str = 'Нет данных'
    warranty_months: str = 'Нет данных'
    category: str = 'Нет данных'
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%d.%m.%Y %H:%M")
    )
    attributes: List[Attribute] = Field(default_factory=list)
    suppliers: List[Supplier] = Field(default_factory=list)
    
    @validator('article', pre=True)
    def validate_article(cls, v):
        if v is None or v == '':
            return 'Нет данных'
        return v
