from django.contrib import admin
from db.models import User,Cart,CartItem,Purchase
# Register your models here.
admin.site.register(User)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Purchase)