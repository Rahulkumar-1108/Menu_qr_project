from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("m/<slug:slug>/", views.menu_view, name="menu"),
    path("m/<slug:slug>/qr/", views.qr_page, name="qr_page"),
    path("m/<slug:slug>/qr.png", views.qr_png, name="qr_png"),
    path("m/<slug:slug>/order/", views.place_order, name="place_order"),
    path("order/<uuid:token>/", views.order_status, name="order_status"),
    path("order/<uuid:token>/status.json", views.order_status_json, name="order_status_json"),
    path("m/<slug:slug>/dashboard/", views.dashboard, name="dashboard"),
    path("m/<slug:slug>/dashboard/orders.json", views.dashboard_orders, name="dashboard_orders"),
    path("m/<slug:slug>/dashboard/order/<int:pk>/status/", views.update_order_status,
         name="update_order_status"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]
