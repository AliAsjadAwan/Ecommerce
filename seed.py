import os
import json
from dotenv import load_dotenv
from configure.db import connect_db, get_db
from datetime import datetime

load_dotenv()

# Get data directory
data_dir = os.path.join(os.path.dirname(__file__), 'data')

def run():
    try:
        # Connect to Ecommerce database
        db = connect_db()
        
        # Get collections
        products_collection = db['products']
        users_collection = db['users']
        orders_collection = db['orders']
        reviews_collection = db['reviews']

        # Read files
        products_file = os.path.join(data_dir, 'products.json')
        users_file = os.path.join(data_dir, 'users.json')
        
        with open(products_file, 'r', encoding='utf-8') as f:
            prod_data = json.load(f)

        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)

        # Clear collections
        products_collection.delete_many({})
        users_collection.delete_many({})
        orders_collection.delete_many({})
        reviews_collection.delete_many({})
        
        print("[OK] Collections cleared")

        # Add timestamps to products if not present
        for product in prod_data:
            if 'createdAt' not in product:
                product['createdAt'] = datetime.utcnow()
            if 'rating' not in product:
                product['rating'] = 0.0
            if 'ratingCount' not in product:
                product['ratingCount'] = 0

        # Add timestamps to users if not present
        for user in users_data:
            if 'createdAt' not in user:
                user['createdAt'] = datetime.utcnow()

        # Insert products and users
        products_result = products_collection.insert_many(prod_data)
        users_result = users_collection.insert_many(users_data)
        
        products_ids = products_result.inserted_ids
        users_ids = users_result.inserted_ids

        print(f"[OK] Products inserted: {len(products_ids)}")
        print(f"[OK] Users inserted: {len(users_ids)}")

        # Create a sample order: user 0 buys product 0 and 1
        if len(users_ids) > 0 and len(products_ids) >= 2:
            # Fetch the first two products to get their details
            product1 = products_collection.find_one({'_id': products_ids[0]})
            product2 = products_collection.find_one({'_id': products_ids[1]})
            
            sample_order = {
                'user': users_ids[0],
                'items': [
                    {
                        'product': str(products_ids[0]),
                        'name': product1.get('name'),
                        'price': product1.get('price'),
                        'quantity': 1
                    },
                    {
                        'product': str(products_ids[1]),
                        'name': product2.get('name'),
                        'price': product2.get('price'),
                        'quantity': 2
                    }
                ],
                'totalCost': product1.get('price', 0) * 1 + product2.get('price', 0) * 2,
                'status': 'placed',
                'createdAt': datetime.utcnow()
            }
            
            order_result = orders_collection.insert_one(sample_order)
            print(f"[OK] Sample order created: {order_result.inserted_id}")

        # Create text index on products for search functionality
        try:
            products_collection.create_index([
                ('name', 'text'),
                ('description', 'text'),
                ('brand', 'text')
            ])
            print("[OK] Text index created on products collection")
        except Exception as e:
            print(f"[NOTE] Index creation note: {e}")

        print("\n[SUCCESS] Seed complete! Database: Ecommerce")
        
    except FileNotFoundError as e:
        print(f"[ERROR] Seed error: Data file not found - {e}")
        print(f"   Make sure {data_dir} contains products.json and users.json")
        exit(1)
    except Exception as err:
        print(f"[ERROR] Seed error: {err}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    run()
