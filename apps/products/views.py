from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    CategoryForm,
    ProductForm,
    StockAdjustmentForm,
)

from .models import (
    Category,
    Product,
    StockMovement,
)


@login_required
def product_list(request):

    products = Product.objects.select_related(
        "category",
        "default_tax",
    )

    query = request.GET.get(
        "q",
        ""
    ).strip()

    product_type = request.GET.get(
        "type",
        "all"
    )

    status = request.GET.get(
        "status",
        "active"
    )

    if query:

        products = products.filter(
            Q(sku__icontains=query)
            |
            Q(name__icontains=query)
            |
            Q(category__name__icontains=query)
        )

    if product_type in ["GOODS", "SERVICE"]:
        products = products.filter(
            product_type=product_type
        )

    if status == "active":
        products = products.filter(
            is_active=True
        )

    elif status == "inactive":
        products = products.filter(
            is_active=False
        )

    paginator = Paginator(
        products,
        10
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "page_obj": page_obj,
        "query": query,
        "product_type": product_type,
        "status": status,

        "total_products":
            Product.objects.count(),

        "active_products":
            Product.objects.filter(
                is_active=True
            ).count(),

        "low_stock_products":
            Product.objects.filter(
                manage_stock=True,
                is_active=True,
            ).count(),
    }

    return render(
        request,
        "products/list.html",
        context
    )


@login_required
def product_create(request):

    if request.method == "POST":

        form = ProductForm(
            request.POST
        )

        if form.is_valid():

            product = form.save()

            messages.success(
                request,
                f"{product.name} berhasil ditambahkan."
            )

            return redirect(
                "products:detail",
                pk=product.pk
            )

    else:
        form = ProductForm()

    return render(
        request,
        "products/form.html",
        {
            "form": form,
            "title": "Tambah Produk / Jasa",
            "subtitle":
                "Tambahkan produk atau jasa ke sistem.",
        }
    )


@login_required
def product_update(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if request.method == "POST":

        form = ProductForm(
            request.POST,
            instance=product
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Produk berhasil diperbarui."
            )

            return redirect(
                "products:detail",
                pk=product.pk
            )

    else:

        form = ProductForm(
            instance=product
        )

    return render(
        request,
        "products/form.html",
        {
            "form": form,
            "product": product,
            "title": "Edit Produk / Jasa",
            "subtitle":
                f"Perbarui data {product.name}.",
        }
    )


@login_required
def product_detail(request, pk):

    product = get_object_or_404(
        Product.objects.select_related(
            "category",
            "default_tax",
        ),
        pk=pk
    )

    movements = product.stock_movements.all()[:10]

    return render(
        request,
        "products/detail.html",
        {
            "product": product,
            "movements": movements,
        }
    )


@login_required
@transaction.atomic
def stock_adjustment(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if not product.manage_stock:

        messages.warning(
            request,
            "Produk ini tidak menggunakan manajemen stok."
        )

        return redirect(
            "products:detail",
            pk=product.pk
        )

    if request.method == "POST":

        form = StockAdjustmentForm(
            request.POST
        )

        if form.is_valid():

            movement_type = (
                form.cleaned_data["movement_type"]
            )

            quantity = Decimal(
                form.cleaned_data["quantity"]
            )

            stock_before = product.stock_quantity

            if movement_type == "IN":

                stock_after = (
                    stock_before + quantity
                )

            elif movement_type == "OUT":

                if quantity > stock_before:

                    form.add_error(
                        "quantity",
                        "Stok tidak mencukupi."
                    )

                    return render(
                        request,
                        "products/stock_form.html",
                        {
                            "product": product,
                            "form": form,
                        }
                    )

                stock_after = (
                    stock_before - quantity
                )

            else:

                stock_after = quantity

            StockMovement.objects.create(
                product=product,
                movement_type=movement_type,
                quantity=quantity,
                stock_before=stock_before,
                stock_after=stock_after,
                reference=form.cleaned_data[
                    "reference"
                ],
                notes=form.cleaned_data[
                    "notes"
                ],
            )

            product.stock_quantity = (
                stock_after
            )

            product.save(
                update_fields=[
                    "stock_quantity",
                    "updated_at",
                ]
            )

            messages.success(
                request,
                "Stok berhasil diperbarui."
            )

            return redirect(
                "products:detail",
                pk=product.pk
            )

    else:

        form = StockAdjustmentForm()

    return render(
        request,
        "products/stock_form.html",
        {
            "product": product,
            "form": form,
        }
    )


@login_required
def stock_history(request):

    movements = (
        StockMovement.objects
        .select_related("product")
        .all()
    )

    query = request.GET.get(
        "q",
        ""
    ).strip()

    if query:

        movements = movements.filter(
            Q(product__name__icontains=query)
            |
            Q(product__sku__icontains=query)
            |
            Q(reference__icontains=query)
        )

    paginator = Paginator(
        movements,
        20
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "products/stock_history.html",
        {
            "page_obj": page_obj,
            "query": query,
        }
    )


@login_required
def category_list(request):

    categories = Category.objects.all()

    return render(
        request,
        "products/category_list.html",
        {
            "categories": categories,
        }
    )


@login_required
def category_create(request):

    if request.method == "POST":

        form = CategoryForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Kategori berhasil ditambahkan."
            )

            return redirect(
                "products:category_list"
            )

    else:

        form = CategoryForm()

    return render(
        request,
        "products/category_form.html",
        {
            "form": form,
        }
    )