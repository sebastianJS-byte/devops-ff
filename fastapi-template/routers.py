import json
from fastapi import APIRouter, HTTPException, status
from typing import List
from .models import Product, ProductCreate

router = APIRouter()

DB_FILE = "app/db.json"


def read_db() -> List[Product]:
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return [Product(**item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_db(products: List[Product]):
    with open(DB_FILE, "w") as f:
        json.dump([p.model_dump() for p in products], f, indent=2)


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}


@router.get("/products", response_model=List[Product])
def get_products():
    return read_db()


@router.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    products = read_db()
    product = next((p for p in products if p.id == product_id), None)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(product_create: ProductCreate):
    products = read_db()
    new_id = max([p.id for p in products]) + 1 if products else 1
    new_product = Product(id=new_id, **product_create.model_dump())
    products.append(new_product)
    write_db(products)
    return new_product


@router.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, product_update: ProductCreate):
    products = read_db()
    product_index = next((i for i, p in enumerate(products) if p.id == product_id), None)

    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")

    updated_product = Product(id=product_id, **product_update.model_dump())
    products[product_index] = updated_product
    write_db(products)
    return updated_product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    products = read_db()
    product_to_delete = next((p for p in products if p.id == product_id), None)

    if product_to_delete is None:
        raise HTTPException(status_code=404, detail="Product not found")

    products.remove(product_to_delete)
    write_db(products)
    return