from django.urls import path

from . import views


app_name = "taxes"


urlpatterns = [

    path(
        "",
        views.tax_list,
        name="list",
    ),

    path(
        "tambah/",
        views.tax_create,
        name="create",
    ),

    path(
        "<int:pk>/edit/",
        views.tax_update,
        name="update",
    ),

    path(
        "<int:pk>/toggle/",
        views.tax_toggle_status,
        name="toggle_status",
    ),

    path(
        "kalkulator/",
        views.tax_calculator,
        name="calculator",
    ),

]