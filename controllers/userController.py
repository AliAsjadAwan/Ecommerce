from bson import ObjectId
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

# GET /users/{user_id}/orders
def get_user_orders_controller(user_id: str):
    try:
        db = get_db()
        orders_collection = db['orders']
        products_collection = db['products']
        
        # Find all orders for the user
        orders = list(orders_collection.find({'user': ObjectId(user_id)}).sort([('createdAt', -1)]))
        
        # Populate product details for each order
        for order in orders:
            if 'items' in order:
                for item in order['items']:
                    if 'product' in item:
                        # Get product details
                        product_id = item['product'] if isinstance(item['product'], ObjectId) else ObjectId(item['product'])
                        product = products_collection.find_one(
                            {'_id': product_id},
                            {'name': 1, 'brand': 1, 'price': 1}
                        )
                        if product:
                            item['product'] = convert_objectids(product)
        
        # Convert all ObjectIds to strings
        orders = convert_objectids(orders)
        
        return orders
    except Exception as err:
        print(f"Error in get_user_orders_controller: {err}")
        raise HTTPException(status_code=500, detail=str(err))