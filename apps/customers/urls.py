from django.urls import path

from . import views


app_name = "customers"


urlpatterns = [

    path(
        "",
        views.customer_list,
        name="list",
    ),

    path(
        "tambah/",
        views.customer_create,
        name="create",
    ),

    path(
        "<int:pk>/",
        views.customer_detail,
        name="detail",
    ),

    path(
        "<int:pk>/edit/",
        views.customer_update,
        name="update",
    ),

    path(
        "<int:pk>/toggle-status/",
        views.customer_toggle_status,
        name="toggle_status",
    ),

]