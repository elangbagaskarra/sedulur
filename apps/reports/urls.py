from django.urls import path

from . import views


app_name = "reports"


urlpatterns = [
    path(
        "",
        views.report_index,
        name="index",
    ),

    path(
        "export/excel/",
        views.export_excel,
        name="export_excel",
    ),

    path(
        "export/csv/",
        views.export_csv,
        name="export_csv",
    ),
]

