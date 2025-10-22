from bson import ObjectId
from datetime import datetime
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

# Search products controller
def search_products_controller(query: str, min_price: float, max_price: float, 
                               category: str, page: int, limit: int, sort: str, budget: float):
    try:
        db = get_db()
        products_collection = db['products']
        orders_collection = db['orders']
        
        skip = (page - 1) * limit

        # 1) Try text search
        if query:
            results = list(products_collection.find(
                {"$text": {"$search": query}}, 
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(200))
        else:
            # if no query, return recent products
            results = list(products_collection.find().sort([("createdAt", -1)]).limit(200))

        # 2) apply filters
        filtered = [p for p in results if (
            (min_price is None or p['price'] >= min_price) and
            (max_price is None or p['price'] <= max_price) and
            (category is None or p['category'] == category)
        )]

        # Get product IDs for popularity calculation
        prod_ids = [p['_id'] for p in filtered]
        
        # Convert to both formats to handle different storage types
        prod_ids_obj = [pid if isinstance(pid, ObjectId) else ObjectId(pid) for pid in prod_ids if pid]
        prod_ids_str = [str(pid) for pid in prod_ids]

        pop_map = {}
        if prod_ids_obj:
            # Try matching with ObjectId
            pop_agg = orders_collection.aggregate([
                {"$match": {"items.product": {"$in": prod_ids_obj}}},
                {"$unwind": "$items"},
                {"$match": {"items.product": {"$in": prod_ids_obj}}},
                {"$group": {"_id": "$items.product", "totalSold": {"$sum": "$items.quantity"}}}
            ])
            for item in pop_agg:
                pop_map[str(item['_id'])] = item['totalSold']
            
            # Also try matching with string format
            pop_agg_str = orders_collection.aggregate([
                {"$match": {"items.product": {"$in": prod_ids_str}}},
                {"$unwind": "$items"},
                {"$match": {"items.product": {"$in": prod_ids_str}}},
                {"$group": {"_id": "$items.product", "totalSold": {"$sum": "$items.quantity"}}}
            ])
            for item in pop_agg_str:
                pop_map[str(item['_id'])] = item.get('totalSold', 0) + pop_map.get(str(item['_id']), 0)

        max_pop = max([0] + list(pop_map.values()))

        # 4) attach metadata and compute a final score
        enriched = []
        for p in filtered:
            # Convert all ObjectIds to strings
            p = convert_objectids(p)
            pop = pop_map.get(p['_id'], 0)
            sim = p.get('score', 0) / 10 if p.get('score') else 0.5
            pop_score = pop / max_pop if max_pop else 0
            price_score = 1 - abs(p['price'] - budget) / max(budget, 1) if budget else 1
            final_score = 0.4 * sim + 0.4 * pop_score + 0.2 * price_score
            enriched.append({**p, "popularity": pop, "simScore": sim, "finalScore": final_score})

        # 5) sort results
        if sort == 'price_asc':
            enriched.sort(key=lambda x: x['price'])
        elif sort == 'price_desc':
            enriched.sort(key=lambda x: x['price'], reverse=True)
        elif sort == 'popularity':
            enriched.sort(key=lambda x: x['popularity'], reverse=True)
        else:
            enriched.sort(key=lambda x: x.get('finalScore', 0), reverse=True)

        paged = enriched[skip:skip + limit]

        return {
            "page": page,
            "limit": limit,
            "total": len(enriched),
            "results": paged
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

# Get product reviews controller
def get_product_reviews_controller(product_id: str):
    try:
        db = get_db()
        reviews_collection = db['reviews']
        
        reviews = list(reviews_collection.find({"product": ObjectId(product_id)})
                       .sort([("createdAt", -1)]))
        
        # Convert all ObjectIds to strings recursively
        reviews = convert_objectids(reviews)
        
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Post product review controller
def post_product_review_controller(product_id: str, review_data):
    try:
        db = get_db()
        products_collection = db['products']
        reviews_collection = db['reviews']
        
        review = {
            "user": review_data.user,
            "product": ObjectId(product_id),
            "rating": review_data.rating,
            "text": review_data.text,
            "createdAt": datetime.utcnow()
        }
        result = reviews_collection.insert_one(review)

        # Update the product's rating
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if product:
            new_count = (product.get('ratingCount', 0)) + 1
            old_rating = product.get('rating', 0)
            old_count = product.get('ratingCount', 0)
            new_rating = ((old_rating * old_count) + review_data.rating) / new_count
            products_collection.update_one(
                {"_id": ObjectId(product_id)}, 
                {"$set": {"rating": new_rating, "ratingCount": new_count}}
            )

        return {"_id": str(result.inserted_id), "message": "Review added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
