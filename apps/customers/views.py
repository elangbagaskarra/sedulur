from django.contrib import messages

from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

from django.db.models import Q

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import CustomerForm

from .models import Customer


@login_required
def customer_list(request):

    customers = Customer.objects.all()

    query = request.GET.get(
        "q",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        "active"
    )

    if query:

        customers = customers.filter(

            Q(code__icontains=query)
            |
            Q(name__icontains=query)
            |
            Q(company_name__icontains=query)
            |
            Q(npwp__icontains=query)
            |
            Q(email__icontains=query)
            |
            Q(phone__icontains=query)

        )

    if status == "active":

        customers = customers.filter(
            is_active=True
        )

    elif status == "inactive":

        customers = customers.filter(
            is_active=False
        )

    paginator = Paginator(
        customers,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        "page_obj": page_obj,

        "query": query,

        "status": status,

        "total_customers":
            Customer.objects.count(),

        "active_customers":
            Customer.objects.filter(
                is_active=True
            ).count(),

        "inactive_customers":
            Customer.objects.filter(
                is_active=False
            ).count(),

    }

    return render(
        request,
        "customers/list.html",
        context
    )


@login_required
def customer_create(request):

    if request.method == "POST":

        form = CustomerForm(
            request.POST
        )

        if form.is_valid():

            customer = form.save()

            messages.success(
                request,
                f"Pelanggan {customer.name} berhasil ditambahkan."
            )

            return redirect(
                "customers:detail",
                pk=customer.pk,
            )

    else:

        form = CustomerForm()

    return render(
        request,
        "customers/form.html",
        {
            "form": form,
            "title": "Tambah Pelanggan",
            "subtitle":
                "Tambahkan pelanggan baru ke sistem.",
        }
    )


@login_required
def customer_detail(
    request,
    pk
):

    customer = get_object_or_404(
        Customer,
        pk=pk
    )

    return render(
        request,
        "customers/detail.html",
        {
            "customer": customer,
        }
    )


@login_required
def customer_update(
    request,
    pk
):

    customer = get_object_or_404(
        Customer,
        pk=pk
    )

    if request.method == "POST":

        form = CustomerForm(
            request.POST,
            instance=customer
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Data pelanggan berhasil diperbarui."
            )

            return redirect(
                "customers:detail",
                pk=customer.pk,
            )

    else:

        form = CustomerForm(
            instance=customer
        )

    return render(
        request,
        "customers/form.html",
        {
            "form": form,
            "customer": customer,
            "title": "Edit Pelanggan",
            "subtitle":
                f"Perbarui data {customer.name}.",
        }
    )


@login_required
def customer_toggle_status(
    request,
    pk
):

    customer = get_object_or_404(
        Customer,
        pk=pk
    )

    if request.method == "POST":

        customer.is_active = (
            not customer.is_active
        )

        customer.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        if customer.is_active:

            messages.success(
                request,
                "Pelanggan berhasil diaktifkan."
            )

        else:

            messages.warning(
                request,
                "Pelanggan berhasil dinonaktifkan."
            )

    return redirect(
        "customers:detail",
        pk=customer.pk,
    )