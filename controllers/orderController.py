from datetime import datetime, timedelta
from bson.objectid import ObjectId
from fastapi import HTTPException
from configure.db import get_db

# Helper function to convert all ObjectIds in a document to strings
def convert_objectids(doc):
    """Recursively convert all ObjectId instances to strings in a document"""
    if isinstance(doc, dict):
        return {k: convert_objectids(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [convert_objectids(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    else:
        return doc

# =============================
# GET /orders/{order_id}
# =============================
def get_order_by_id_controller(order_id: str):
    try:
        db = get_db()
        orders_collection = db['orders']
        users_collection = db['users']
        products_collection = db['products']
        
        order = orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # populate user fields (name, email)
        user_id = order.get('user')
        if user_id:
            user = users_collection.find_one({"_id": ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id}, {"name": 1, "email": 1})
            if user:
                order['user'] = user

        # populate items.product fields (name, brand, price)
        for item in order.get('items', []):
            product_id = item.get('product')
            if product_id:
                # Convert to ObjectId if it's a string
                if isinstance(product_id, str):
                    product_id = ObjectId(product_id)
                product = products_collection.find_one(
                    {"_id": product_id}, 
                    {"name": 1, "brand": 1, "price": 1}
                )
                if product:
                    item['product'] = product

        # Convert all ObjectIds to strings
        order = convert_objectids(order)
        
        return order
    except HTTPException:
        raise
    except Exception as err:
        print(f"Error in get_order_by_id_controller: {err}")
        raise HTTPException(status_code=500, detail=str(err))


# =============================
# GET /orders/top-products
# Aggregation: Top 5 most frequently purchased products in last month, grouped by category
# =============================
def get_top_products_by_category_controller():
    try:
        db = get_db()
        orders_collection = db['orders']
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        pipeline = [
            {
                "$match": {
                    "createdAt": {"$gte": thirty_days_ago}
                }
            },
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.product",
                    "totalSold": {"$sum": "$items.quantity"}
                }
            },
            {
                "$lookup": {
                    "from": "products",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "product"
                }
            },
            {"$unwind": "$product"},
            {
                "$group": {
                    "_id": "$product.category",
                    "topProducts": {
                        "$push": {
                            "name": "$product.name",
                            "sold": "$totalSold"
                        }
                    }
                }
            },
            {
                "$project": {
                    "topProducts": {"$slice": ["$topProducts", 5]}
                }
            }
        ]

        result = list(orders_collection.aggregate(pipeline))
        
        # Convert ObjectIds to strings
        result = convert_objectids(result)
        
        return result
    except Exception as err:
        print(f"Error in get_top_products_by_category_controller: {err}")
        raise HTTPException(status_code=500, detail=str(err))