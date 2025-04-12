from core.models import Product, Category, CartOrder, CartOrderProducts, ProductImages, ProductReview, Address


def default(request):
    categories = Category.objects.all()

    address = ""
    
    if request.user.is_authenticated:
        address = Address.objects.filter(user=request.user)

    return {
        'categories': categories,
        'address': address,
    }
