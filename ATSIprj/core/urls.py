from django.urls import path, include
from core.views import index, category_list_view, product_list_view, category_product_list_view, product_detail_view, \
    tag_list, ajax_add_review, search_view, add_to_cart, cart_view, delete_item_from_cart, update_cart, checkout_view, \
    payment_completed_view, payment_failed_view, customer_dashboard, order_detail, make_address_default

app_name = "core"

urlpatterns = [
    # Homepage
    path("", index, name="index"),

    # Products
    path("product/", product_list_view, name="product-list"),
    path("product/<pid>", product_detail_view, name="product-detail"),

    # Category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),

    # Tags
    path("product/tag/<tag_slug>/", tag_list, name="tags"),

    # Add Review
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),

    # Search
    path("search/", search_view, name="search"),

    # Add to cart
    path("add-to-cart/", add_to_cart, name="add-to-cart"),

    # Cart Page
    path("cart/", cart_view, name="cart"),

    # Cart Page
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),

    # Update Cart
    path("update-cart/", update_cart, name="update-cart"),

    # Checkout view
    path("checkout/", checkout_view, name="checkout"),

    # Paypal URL
    path('paypal/', include('paypal.standard.ipn.urls')),

    # Paypal payment successful
    path("payment-completed/<int:order_id>/", payment_completed_view, name="payment-completed"),

    # Paypal payment failed
    path("payment-failed/", payment_failed_view, name="payment-failed"),

    # Dashboard URL
    path("dashboard/", customer_dashboard, name="dashboard"),

    # Order Detail
    path("dashboard/order/<int:id>", order_detail, name="order-detail"),

    # Mark address as default
    path("make-default-address/", make_address_default, name="make-default-address"),
]
