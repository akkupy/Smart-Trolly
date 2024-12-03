from django.urls import path,re_path
from . import views
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
     path('ws/cart/<int:user_id>/', consumers.CartConsumer.as_asgi(), name='cart_ws'),  # WebSocket URL pattern
]

urlpatterns = [
    path("", views.redir, name="redir"),
    path("login/", views.login_view, name="login"),
    path("add-name/<int:user_id>/", views.add_name_view, name="add_name"),
    path("delete/<int:cart_id>/", views.delete, name="delete"),
    path("pay-confirm/<int:user_id>/", views.pay, name="pay"),
    path("checkout/<int:user_id>/", views.checkout, name="checkout"),
    path("dashboard/<int:user_id>/", views.dashboard_view, name="dashboard"),
    path("start-cart/<int:user_id>/", views.start_cart_view, name="start_cart"),
    path("update-cart/", views.update_cart_view, name="update_cart"),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path("previous-purchases/<int:user_id>/", views.purchase_history_view, name="previous_purchases"),
]
