from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]


class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool



@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}



@app.post("/products", status_code=201)
def add_product(product: Product):

    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="Product with this name already exists")

    new_id = max(p["id"] for p in products) + 1 if products else 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


@app.get("/products/audit")
def audit_products():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": len(in_stock_products),
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):

    if discount_percent < 1 or discount_percent > 99:
        raise HTTPException(status_code=400, detail="discount_percent must be between 1 and 99")

    updated_products = []

    for p in products:
        if p["category"].lower() == category.lower():
            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price
            updated_products.append({"name": p["name"], "price": new_price})

    if not updated_products:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated_products),
        "products": updated_products
    }



@app.get("/products/{product_id}")
def get_product(product_id: int):

    for p in products:
        if p["id"] == product_id:
            return p

    raise HTTPException(status_code=404, detail="Product not found")



@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for p in products:

        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {"message": "Product updated", "product": p}

    raise HTTPException(status_code=404, detail="Product not found")



@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for p in products:

        if p["id"] == product_id:
            products.remove(p)
            return {"message": f"Product '{p['name']}' deleted"}

    raise HTTPException(status_code=404, detail="Product not found")