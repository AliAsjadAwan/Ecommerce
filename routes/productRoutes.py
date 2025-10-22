from fastapi import APIRouter, Query, status
from controllers.productController import (
    search_products_controller,
    get_product_reviews_controller,
    post_product_review_controller
)
from models.review import Review

router = APIRouter(prefix="/products")

# Route 1 — Search Products
# Example: GET /products/search?query=&minPrice=&maxPrice=&category=&page=&limit=&sort=&budget=
@router.get("/search")
async def search_products(
    query: str = Query(default="", description="Search query for products"),
    minPrice: float = Query(default=None, description="Minimum price filter"),
    maxPrice: float = Query(default=None, description="Maximum price filter"),
    category: str = Query(default=None, description="Category filter"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort: str = Query(default="relevance", description="Sort by: relevance, price_asc, price_desc, popularity"),
    budget: float = Query(default=None, description="Budget for price relevance")
):
    """
    Search products with filters, pagination, and sorting
    """
    return search_products_controller(
        query=query,
        min_price=minPrice,
        max_price=maxPrice,
        category=category,
        page=page,
        limit=limit,
        sort=sort,
        budget=budget
    )


# Route 2 — Get Product Reviews
# Example: GET /products/{product_id}/reviews
@router.get("/{product_id}/reviews")
async def get_product_reviews(product_id: str):
    """
    Get all reviews for a specific product
    """
    return get_product_reviews_controller(product_id)


# Route 3 — Post Product Review
# Example: POST /products/{product_id}/reviews
@router.post("/{product_id}/reviews", status_code=status.HTTP_201_CREATED)
async def post_product_review(product_id: str, review: Review):
    """
    Add a new review for a product
    """
    return post_product_review_controller(product_id, review)
