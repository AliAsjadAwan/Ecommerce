# 🛒 E-Commerce Marketplace Backend (FastAPI + MongoDB + PyMongo)

## 📘 Overview

This project is a **backend system for an e-commerce marketplace** similar to Amazon.
It supports **product management, user orders, reviews, and intelligent search** features including
**keyword search, fuzzy similarity search, and hybrid ranking** (based on similarity, popularity, and price relevance).

---

## 🚀 Features

* **Product Management**: Create, read, update, and search products.
* **User Management**: Manage users and their orders.
* **Order Handling**: Track orders with items, quantities, total price, and timestamps.
* **Reviews**: Users can post and view product reviews.
* **Search Functionality**:
  * Keyword Search (e.g., "laptop")
  * Fuzzy/Similarity Search (e.g., "hp leptop" → "HP Laptop")
  * Hybrid Ranking (Similarity + Popularity + Price Closeness)

---

## 🧩 Tech Stack

| Component   | Technology                       |
| ------------ | -------------------------------- |
| Runtime     | Python 3.13.9                    |
| Framework   | FastAPI                          |
| Database    | MongoDB (PyMongo Driver)         |
| Validation  | Pydantic 2.10.0+                 |
| Server      | Uvicorn (ASGI)                   |
| Search      | MongoDB Text Index + Fuzzy Logic |
| Environment | `.env` for configuration         |
| API Testing | Postman / Swagger UI             |

---

## 🗂️ Project Structure

```
.
├───configure
│   └───db.py                 # MongoDB connection management
├───controllers
│   ├───orderController.py    # Order business logic & aggregations
│   ├───productController.py  # Product search & reviews logic
│   └───userController.py     # User orders logic
├───data
│   ├───products.json         # Sample product data
│   └───users.json           # Sample user data
├───models
│   ├───order.py             # Order Pydantic models
│   ├───product.py           # Product Pydantic models
│   ├───review.py            # Review Pydantic models
│   └───user.py              # User Pydantic models
├───routes
│   ├───orderRoutes.py       # Order API endpoints
│   ├───productRoutes.py     # Product API endpoints
│   └───userRoutes.py        # User API endpoints
├───main.py                  # FastAPI application entry point
├───seed.py                  # Database seeder script
├───requirements.txt         # Python dependencies
├───README.md                # Project documentation
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone or Create Folder

```bash
mkdir ecommerce
cd ecommerce
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
```

**Activate it:**
- **Windows PowerShell**: `.venv\Scripts\activate`
- **Linux/Mac**: `source .venv/bin/activate`

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
```
fastapi>=0.115.0
uvicorn>=0.32.0
pymongo>=4.10.0
pydantic>=2.10.0
pydantic[email]
python-dotenv
```

### 4️⃣ Create a `.env` file (Optional)

```bash
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=Ecommerce
PORT=8000
```

### 5️⃣ Run MongoDB (if using locally)

```bash
mongod
```

### 6️⃣ Seed the Database

```bash
python seed.py
```

This will:
- Clear existing collections
- Insert 40+ sample products and users
- Create a sample order
- **Create text index** for search functionality

### 7️⃣ Start the Server

```bash
python main.py
```

✅ Server will run on:
**[http://localhost:8000](http://localhost:8000)**

### 8️⃣ View Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🧠 API Endpoints

| Method | Endpoint | Description |
| ------- | --------------------------------- | ----------------------------------- |
| **GET**  | `/products/search?query=&budget=` | Keyword + Fuzzy + Hybrid Search     |
| **GET**  | `/products/{id}/reviews`           | Get all reviews for a product       |
| **POST** | `/products/{id}/reviews`           | Add a new review to a product       |
| **GET**  | `/users/{id}/orders`               | Fetch all orders of a specific user |
| **GET**  | `/orders/{id}`                     | Get order details by ID             |
| **GET**  | `/orders/top-products`             | Top 5 products by category (30 days)|

---

## 🔍 Hybrid Search Logic

The `/products/search` endpoint combines multiple ranking signals:

| Factor | Weight | Description |
| ------- | ------ | -------------------------------------------- |
| **Text Similarity** | 0.4 | How close the name/description matches query |
| **Popularity** | 0.4 | Based on total purchases (from Orders) |
| **Price Relevance** | 0.2 | How close product price is to user's budget |

**Formula:**

```
finalScore = 0.4 * similarity + 0.4 * popularity + 0.2 * priceScore
```

Products are sorted in descending order of `finalScore`.

**Implementation:**
> See `controllers/productController.py` → `search_products_controller()`

---

## 📊 Aggregation Example

To find **Top 5 most frequently purchased products (by category) in the last month**:

```js
db.orders.aggregate([
 { $match: { createdAt: { $gte: new Date(new Date() - 30 * 24 * 60 * 60 * 1000) } } },
 { $unwind: "$items" },
 { $group: { _id: "$items.product", totalSold: { $sum: "$items.quantity" } } },
 { $lookup: { from: "products", localField: "_id", foreignField: "_id", as: "product" } },
 { $unwind: "$product" },
 { $group: { _id: "$product.category", topProducts: { $push: { name: "$product.name", sold: "$totalSold" } } } },
 { $project: { topProducts: { $slice: ["$topProducts", 5] } } }
]);
```

**Endpoint:** `GET /orders/top-products`

---

## 🧪 Testing APIs in Postman

1. **Start the server**

   ```
   python main.py
   ```

2. **In Postman**, test APIs:

| Name | Example Request | Description |
| ----- | --------------------------------------------------------------------- | ------------------ |
| **Search - Basic** | `http://localhost:8000/products/search?query=laptop` | Keyword search |
| **Search - Fuzzy** | `http://localhost:8000/products/search?query=hp%20leptop` | Fuzzy search |
| **Search - Hybrid** | `http://localhost:8000/products/search?query=laptop&budget=60000` | Hybrid Search |
| **User Orders** | `GET http://localhost:8000/users/{user_id}/orders` | Orders of one user |
| **Product Reviews** | `GET http://localhost:8000/products/{product_id}/reviews` | Get reviews |
| **Top Products** | `GET http://localhost:8000/orders/top-products` | Top products analytics |

**📖 Full Testing Guide:** See [POSTMAN_GUIDE.md](POSTMAN_GUIDE.md)

---

## 📚 Bonus Feature (Hybrid Search)

Hybrid ranking combines:

* **Similarity** (Text relevance via MongoDB text search)
* **Popularity** (Sales count from orders aggregation)
* **Price closeness** to user's budget

> Implemented in `controllers/productController.py`
> under the `/products/search` API.

**Search Parameters:**
- `query` - Search keyword
- `minPrice` / `maxPrice` - Price range filters
- `category` - Category filter
- `budget` - For price relevance scoring
- `sort` - Sort by: `relevance`, `price_asc`, `price_desc`, `popularity`
- `page` / `limit` - Pagination

---

## 🐛 Troubleshooting

### Port Already in Use (Error 10048)
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual number)
taskkill /F /PID <PID>

# Restart server
python main.py
```

### MongoDB Connection Error
- Ensure MongoDB is running: `mongod`
- Check connection in `configure/db.py`
- Default: `mongodb://localhost:27017`

### Missing Dependencies
```powershell
pip install --upgrade -r requirements.txt
```

### Search Not Working
- Make sure you ran `python seed.py` to create text index
- Text index is required on products collection

---

## 🔑 Key Features Implemented

✅ **FastAPI** with auto-generated interactive docs  
✅ **MongoDB** integration with PyMongo driver  
✅ **Pydantic** models for request/response validation  
✅ **Text Search** with MongoDB text indexes  
✅ **Hybrid Ranking** (similarity + popularity + price)  
✅ **Aggregation Pipelines** for analytics  
✅ **ObjectId Serialization** handling  
✅ **Clean Architecture** with controllers, routes, models  
✅ **Error Handling** with proper HTTP status codes  
✅ **CORS Support** and async endpoints  

---

## 🗄️ Database Collections

### `products`
- **Fields**: name, description, category, brand, price, stock, rating, ratingCount
- **Indexes**: Text index on `name`, `description`, `brand`

### `users`
- **Fields**: name, email, address, phone

### `orders`
- **Fields**: user (ref), items (array of {product, quantity, price}), totalCost, status, createdAt

### `reviews`
- **Fields**: user (ref), product (ref), rating (1-5), text, createdAt

---

## 👨‍💻 Author

**Abdul Moiz Bhatti**  
E-commerce Backend Design — Internal Exam Project  
Built using **FastAPI, Python, PyMongo, and MongoDB**.

---

## 📄 License

MIT License - Free to use for educational and learning purposes.
