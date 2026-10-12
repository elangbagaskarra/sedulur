from django.urls import path
from . import views


app_name = "products"


urlpatterns = [

    path(
        "",
        views.product_list,
        name="list",
    ),

    path(
        "tambah/",
        views.product_create,
        name="create",
    ),

    path(
        "<int:pk>/",
        views.product_detail,
        name="detail",
    ),

    path(
        "<int:pk>/edit/",
        views.product_update,
        name="update",
    ),

    path(
        "<int:pk>/stok/",
        views.stock_adjustment,
        name="stock_adjustment",
    ),

    path(
        "stok/riwayat/",
        views.stock_history,
        name="stock_history",
    ),

    path(
        "kategori/",
        views.category_list,
        name="category_list",
    ),

    path(
        "kategori/tambah/",
        views.category_create,
        name="category_create",
    ),
]