from django.shortcuts import render, get_object_or_404, redirect
from taggit.models import Tag
from core.models import Product, Category, ProductReview, CartOrder, CartOrderProducts, Address
from django.db.models import Avg
from core.forms import ProductReviewForm
from django.http import JsonResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required

from userauths.models import Profile


def index(request):
    products = Product.objects.filter(featured=True, product_status="published").order_by("title")

    context = {
        "products": products
    }

    return render(request, "core/index.html", context)


def product_list_view(request):
    products = Product.objects.filter(product_status="published")

    context = {
        "products": products
    }

    return render(request, 'core/product-list.html', context)


def category_list_view(request):
    categories = Category.objects.all()

    context = {
        "categories": categories
    }

    return render(request, 'core/category-list.html', context)


def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)

    context = {
        "category": category,
        "products": products,
    }
    return render(request, "core/category-product-list.html", context)


def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    product_image = product.p_images.all()
    related = Product.objects.filter(category=product.category).exclude(pid=pid)

    reviews = ProductReview.objects.filter(product=product).order_by("-date")
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
    review_form = ProductReviewForm()
    make_review = True

    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False

    context = {
        "product": product,
        "product_image": product_image,
        "related": related,
        "reviews": reviews,
        "average_rating": average_rating,
        "review_form": review_form,
        "make_review": make_review,
    }

    return render(request, "core/product-detail.html", context)


def tag_list(request, tag_slug=None):
    products = Product.objects.filter(product_status="published").order_by("title")

    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        products = products.filter(tags__in=[tag])

    context = {
        "products": products,
        "tag": tag,
    }

    return render(request, "core/tag.html", context)


def ajax_add_review(request, pid):
    if not request.user.is_authenticated:
        return 0

    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review=request.GET['review'],
        rating=request.GET['rating'],
    )

    context = {
        'user': user.username,
        'review': request.GET['review'],
        'rating': request.GET['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
        {
            'bool': True,
            'context': context,
            'average_reviews': average_reviews
        }
    )


def search_view(request):
    query = request.GET.get("q")

    products = Product.objects.filter(title__icontains=query).order_by("title")

    context = {
        "products": products,
        "query": query,
    }
    return render(request, "core/search.html", context)


def add_to_cart(request):
    cart_product = {str(request.GET['id']): {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }}

    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data

    else:
        request.session['cart_data_obj'] = cart_product
    return JsonResponse({"data": request.session['cart_data_obj'],
                         'totalcartitems': len(request.session['cart_data_obj'])})


def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {"cart_data": request.session['cart_data_obj'],
                                                  'totalcartitems': len(request.session['cart_data_obj']),
                                                  'cart_total_amount': cart_total_amount})
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")


def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'],
                                                             'totalcartitems': len(request.session['cart_data_obj']),
                                                             'cart_total_amount': cart_total_amount})

    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})


def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data": request.session['cart_data_obj'],
                                                             'totalcartitems': len(request.session['cart_data_obj']),
                                                             'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems': len(request.session['cart_data_obj'])})


@login_required
def checkout_view(request):
    cart_total_amount = 0
    total_amount = 0

    # Checking if cart_data_obj session exists
    if 'cart_data_obj' in request.session:

        # Getting total amount for Paypal Amount
        for p_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * float(item['price'])

        # Create Order Object
        order = CartOrder.objects.create(
            user=request.user,
            price=total_amount
        )

        # Getting total amount for The Cart
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

            cart_order_products = CartOrderProducts.objects.create(
                order=order,
                invoice_no="INVOICE_NO-" + str(order.id),
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                price=item['price'],
                total=float(item['qty']) * float(item['price'])
            )

        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': cart_total_amount,
            'item_name': "Order-Item-No-" + str(order.id),
            'invoice': "INVOICE_NO-" + str(order.id),
            'currency_code': "EUR",
            'notify_url': 'http://{}{}'.format(host, reverse("core:paypal-ipn")),
            'return_url': 'http://{}{}'.format(host, reverse("core:payment-completed", kwargs={ 'order_id': order.id })),
            'cancel_url': 'http://{}{}'.format(host, reverse("core:payment-failed")),
        }

        paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)

        try:
            active_address = Address.objects.get(user=request.user, status=True)

        except:
            messages.warning(request, "There are multiple addresses, only one should be activated.")
            active_address = None

        return render(request, "core/checkout.html", {"cart_data": request.session['cart_data_obj'],
                                                      'totalcartitems': len(request.session['cart_data_obj']),
                                                      'cart_total_amount': cart_total_amount,
                                                      'paypal_payment_button': paypal_payment_button,
                                                      'active_address': active_address})


@login_required
def payment_completed_view(request, order_id):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            product_price_count = int(item['qty']) * float(item['price'])
            product_count = int(item['qty'])
            cart_total_amount += product_price_count

            product = Product.objects.filter(pk=p_id).first()
            if product:
                product.calculate_stock(stock_to_remove=product_count)

    cart_data = request.session['cart_data_obj']
    request.session['cart_data_obj'] = {}

    order = CartOrder.objects.filter(pk=order_id).first()
    if order:
        order.paid_status = True
        order.save()

    return render(request, 'core/payment-completed.html', {'cart_data': cart_data,
                                                           'totalcartitems': len(cart_data),
                                                           'cart_total_amount': cart_total_amount})


@login_required
def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')


@login_required
def customer_dashboard(request):
    orders = CartOrder.objects.filter(
        user=request.user,
        paid_status=True,
    ).order_by("-order_date")
    address = Address.objects.filter(user=request.user)

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
        )
        messages.success(request, "Address added successfully.")
        return redirect("core:dashboard")
    else:
        print("Error while adding new address")

    user_profile = Profile.objects.get(user=request.user)

    context = {
        "user_profile": user_profile,
        "orders": orders,
        "address": address,
    }
    return render(request, 'core/dashboard.html', context)


def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderProducts.objects.filter(order=order).order_by("item")

    context = {
        "order_items": order_items,
    }
    return render(request, 'core/order-detail.html', context)


def make_address_default(request):
    id = request.GET['id']
    Address.objects.filter(user=request.user).update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})
