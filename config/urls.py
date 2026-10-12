from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "login/",
        LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    path(
        "",
        include("apps.dashboard.urls"),
    ),
    path(
    "pelanggan/",
    include("apps.customers.urls"),
),
path(
    "produk/",
    include("apps.products.urls"),
),
path(
    "pajak/",
    include("apps.taxes.urls"),
),
path(
    "invoice/",
    include("apps.invoices.urls"),
),
path(
    "pembayaran/",
    include("apps.payments.urls"),
),
path(
    "pengaturan/",
    include("apps.company.urls"),
),
path(
    "laporan/",
    include("apps.reports.urls"),
),

]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )