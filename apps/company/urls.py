from django.urls import path

from . import views


app_name = "company"


urlpatterns = [

    path(
        "",
        views.company_settings,
        name="settings",
    ),

    path(
        "backup/",
        views.database_backup_page,
        name="backup",
    ),

    path(
        "backup/download/",
        views.database_backup_download,
        name="backup_download",
    ),

    path(
        "backup/restore/",
        views.database_restore,
        name="restore",
    ),

]