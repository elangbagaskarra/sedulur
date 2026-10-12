from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    TaxCalculatorForm,
    TaxForm,
)

from .models import Tax
from .services import calculate_tax


@login_required
def tax_list(request):

    taxes = Tax.objects.all()

    query = request.GET.get(
        "q",
        ""
    ).strip()

    effect_filter = request.GET.get(
        "effect",
        "all"
    )

    status = request.GET.get(
        "status",
        "all"
    )

    if query:

        taxes = taxes.filter(
            Q(name__icontains=query)
            |
            Q(code__icontains=query)
            |
            Q(tax_type__icontains=query)
        )

    if effect_filter in [
        "ADD",
        "DEDUCT",
    ]:

        taxes = taxes.filter(
            effect=effect_filter
        )

    if status == "active":

        taxes = taxes.filter(
            is_active=True
        )

    elif status == "inactive":

        taxes = taxes.filter(
            is_active=False
        )

    context = {
        "taxes": taxes,

        "query": query,

        "effect_filter":
            effect_filter,

        "status": status,

        "total_taxes":
            Tax.objects.count(),

        "active_taxes":
            Tax.objects.filter(
                is_active=True
            ).count(),

        "add_taxes":
            Tax.objects.filter(
                is_active=True,
                effect="ADD"
            ).count(),

        "deduct_taxes":
            Tax.objects.filter(
                is_active=True,
                effect="DEDUCT"
            ).count(),
    }

    return render(
        request,
        "taxes/list.html",
        context
    )


@login_required
def tax_create(request):

    if request.method == "POST":

        form = TaxForm(
            request.POST
        )

        if form.is_valid():

            tax = form.save()

            messages.success(
                request,
                f"{tax.name} berhasil ditambahkan."
            )

            return redirect(
                "taxes:list"
            )

    else:

        form = TaxForm()

    return render(
        request,
        "taxes/form.html",
        {
            "form": form,
            "title": "Tambah Pajak",
            "subtitle":
                "Tambahkan tarif pajak baru.",
        }
    )


@login_required
def tax_update(request, pk):

    tax = get_object_or_404(
        Tax,
        pk=pk
    )

    if request.method == "POST":

        form = TaxForm(
            request.POST,
            instance=tax
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Data pajak berhasil diperbarui."
            )

            return redirect(
                "taxes:list"
            )

    else:

        form = TaxForm(
            instance=tax
        )

    return render(
        request,
        "taxes/form.html",
        {
            "form": form,
            "tax": tax,
            "title": "Edit Pajak",
            "subtitle":
                f"Perbarui {tax.name}.",
        }
    )


@login_required
def tax_toggle_status(
    request,
    pk
):

    tax = get_object_or_404(
        Tax,
        pk=pk
    )

    if request.method == "POST":

        tax.is_active = (
            not tax.is_active
        )

        tax.save(
            update_fields=[
                "is_active",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "Status pajak berhasil diperbarui."
        )

    return redirect(
        "taxes:list"
    )


@login_required
def tax_calculator(request):

    result = None

    form = TaxCalculatorForm(
        request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            amount = (
                form.cleaned_data[
                    "amount"
                ]
            )

            tax = (
                form.cleaned_data[
                    "tax"
                ]
            )

            tax_mode = (
                form.cleaned_data[
                    "tax_mode"
                ]
            )

            result = calculate_tax(
                amount=amount,
                rate=tax.rate,
                effect=tax.effect,
                tax_mode=tax_mode,
            )

            result["tax"] = tax

    return render(
        request,
        "taxes/calculator.html",
        {
            "form": form,
            "result": result,
        }
    )