from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variation = []
    if request.method == 'POST':
        for key in request.POST:
            value = request.POST[key]

            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass    
    

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))# get the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id =_cart_id(request)
        )
    cart.save()

     # Check if the item already exists in cart with same variations
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    if is_cart_item_exists:
        cart_items = CartItem.objects.filter(product=product, cart=cart)
        for item in cart_items:
            existing_variation = item.variations.all()
            if set(existing_variation) == set(product_variation):
                # Found the same item with same variations
                item.quantity += 1
                item.save()
                break
        else:
            # No matching variation set, so create a new item
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                cart_item.variations.set(product_variation)
            cart_item.save()
    else:
        # New cart item altogether
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if len(product_variation) > 0:
            cart_item.variations.set(product_variation)
        cart_item.save()

    return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the cart_id present in the session
    product = get_object_or_404(Product, id=product_id)  # Get the product
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)  # Get the cart item
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  # Decrement the quantity if more than one
            cart_item.save()
        else:
            cart_item.delete()  # Remove the item from the cart if quantity is 1
    except:
        pass        
    return redirect('cart')  # Redirect to the cart view

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the cart_id present in the session
    product = get_object_or_404(Product, id=product_id)  # Get the product
    cart_item = CartItem.objects.get(product=product, cart=cart)  # Get the cart item
    cart_item.delete()  # Remove the item from the cart
    return redirect('cart')  # Redirect to the cart view


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the cart_id present in the session
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)  # Get all items in the cart
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)  # Calculate total price
            quantity += cart_item.quantity  # Calculate total quantity
        tax = (2 * total) / 100  # Calculate tax (2% of total)    
        grand_total = total + tax  # Calculate grand total
    except Cart.DoesNotExist:
        pass  # If no cart exists, do nothing

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/carts.html', context)  # Render the cart template with the context
 