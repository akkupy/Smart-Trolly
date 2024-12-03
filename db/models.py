from django.db import models
from django.utils import timezone

class User(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.phone_number

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user who owns the cart
    created_at = models.DateTimeField(auto_now_add=True)  # Date when the cart was created
    updated_at = models.DateTimeField(auto_now=True)  # Last updated date for the cart
    purchased_at = models.DateTimeField(null=True, blank=True)  # If the cart is purchased, this field will have a timestamp

    def total_price(self):
        # Return the total price of all items in the cart
        return sum(item.total_item_price() for item in self.items.all())

    def checkout(self):
        """
        Move all cart items to Purchase and clear the cart.
        """
        # Prepare purchase items as a dictionary
        purchase_items = [
            {
                "product_name": item.product_name,
                "price": float(item.price),
                "quantity": item.quantity,
                "total_item_price": float(item.total_item_price())
            }
            for item in self.items.all()
        ]

        # Calculate the total price
        total_price = sum(item["total_item_price"] for item in purchase_items)

        # Create a new purchase record
        Purchase.objects.create(
            user=self.user,
            items=purchase_items,
            total_price=total_price
        )

        # Clear all cart items and mark the cart as purchased
        self.items.all().delete()
        self.purchased_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Cart of {self.user.name}-{self.user.id}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)  # Link to the Cart
    product_name = models.CharField(max_length=255)  # Product name
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of one unit of the product
    quantity = models.PositiveIntegerField(default=1)  # Quantity of the product in the cart

    def total_item_price(self):
        # Calculate the total price for this cart item (price * quantity)
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} ({self.quantity} x {self.price})"


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")  # Link to the user
    items = models.JSONField()  # Stores cart items as JSON
    total_price = models.DecimalField(max_digits=15, decimal_places=2)  # Total price of the purchase
    date = models.DateTimeField(auto_now_add=True)  # Purchase date

    def __str__(self):
        return f"Purchase by {self.user.name} on {self.date} (Total: {self.total_price})"
