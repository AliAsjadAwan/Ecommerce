# main.py
from fastapi import FastAPI
from dotenv import load_dotenv
from configure.db import connect_db
from routes.productRoutes import router as product_router
from routes.userRoutes import router as user_router
from routes.orderRoutes import router as order_router

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Ecommerce API",
    description="E-commerce platform API with product search, orders, and reviews",
    version="1.0.0"
)

# Connect to MongoDB (Ecommerce database)
connect_db()

# Include routers
app.include_router(product_router, tags=["Products"])
app.include_router(user_router, tags=["Users"])
app.include_router(order_router, tags=["Orders"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Ecommerce API",
        "database": "Ecommerce",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
