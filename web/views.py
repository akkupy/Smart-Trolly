from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from db.models import User, Cart, Purchase
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render
from db.models import Cart, CartItem
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
import json
from django.views.decorators.csrf import csrf_exempt

current_user = 0

def login_view(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        user, created = User.objects.get_or_create(phone_number=phone_number)
        global current_user
        current_user = user.id
        if created or not user.name:
            return redirect("add_name", user_id=user.id)
        return redirect("dashboard", user_id=user.id)
    return render(request, "login.html")


def add_name_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        user.name = request.POST.get("name")
        user.save()
        return redirect("dashboard", user_id=user.id)
    return render(request, "update_username.html", {"user_id": user.id})


def dashboard_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "dashboard.html", {"user": user,"user_id":user_id})


def start_cart_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    cart, created = Cart.objects.get_or_create(user=user)
    return render(request, "cart.html", {"user": user})


def update_cart_view(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        item_name = request.POST.get("item_name")
        user = get_object_or_404(User, phone_number=phone_number)
        cart, created = Cart.objects.get_or_create(user=user)

async def get_cart_items(cart):
    # Fetch the items asynchronously
    items = await sync_to_async(list)(cart.items.all())
    # Process the items
    return [
        {
            'product_name': item.product_name,
            'quantity': item.quantity,
            'price': str(item.price),
            'total_item_price': str(item.total_item_price())
        }
        for item in items
    ]

@csrf_exempt
async def add_to_cart(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        global current_user
        user_id = current_user  # Assuming the user is logged in
        
        # Get or create the cart
        cart, created = await sync_to_async(Cart.objects.get_or_create)(user_id=user_id, purchased_at__isnull=True)
        # Create the cart item
        cart_item = await sync_to_async(CartItem.objects.create)(
        cart=cart,
        product_name=product_name,
        price=price,
        quantity=quantity,
        )

        # Prepare data to be sent to WebSocket

        cart_items = await get_cart_items(cart)
        
        # Send message to WebSocket group
        channel_layer = get_channel_layer()
        group_name = f'cart_{user_id}'  # Use the user_id to create a unique group
        await channel_layer.group_send(
            group_name,
            {
                'type': 'cart_update',
                'cart_items': cart_items
            }
        )
        
        return JsonResponse({"message": "Item added to cart"})


def purchase_history_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    purchases = user.purchases.all()
    return render(request, "purchase_history.html", {"purchases": purchases,"user_id":user_id})
