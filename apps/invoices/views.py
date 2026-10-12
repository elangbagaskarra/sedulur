from decimal import Decimal

from django.contrib import messages
from io import BytesIO

from django.http import HttpResponse

from django.template.loader import (
    get_template,
)

from xhtml2pdf import pisa

from apps.company.models import (
    CompanySetting,
)
from django.contrib.auth.decorators import (
    login_required,
)

from django.core.paginator import Paginator

from django.db import transaction

from django.db.models import Q

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from django.utils import timezone


from .forms import (
    InvoiceForm,
    InvoiceItemFormSet,
)

from .models import Invoice

from .services import (
    calculate_item,
    generate_invoice_number,
    reduce_invoice_stock,
)

from apps.products.models import Product


@login_required
def invoice_list(request):

    invoices = (
        Invoice.objects
        .select_related("customer")
        .all()
    )

    query = request.GET.get(
        "q",
        ""
    ).strip()

    status = request.GET.get(
        "status",
        "all"
    )

    if query:

        invoices = invoices.filter(
            Q(
                invoice_number__icontains=query
            )
            |
            Q(
                customer_name__icontains=query
            )
        )

    if status != "all":

        invoices = invoices.filter(
            status=status
        )

    paginator = Paginator(
        invoices,
        15
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "page_obj": page_obj,

        "query": query,

        "status": status,

        "total_invoices":
            Invoice.objects.count(),

        "unpaid_invoices":
            Invoice.objects.filter(
                status="UNPAID"
            ).count(),

        "paid_invoices":
            Invoice.objects.filter(
                status="PAID"
            ).count(),

        "draft_invoices":
            Invoice.objects.filter(
                status="DRAFT"
            ).count(),
    }

    return render(
        request,
        "invoices/list.html",
        context,
    )


@login_required
@transaction.atomic
def invoice_create(request):

    invoice = Invoice()

    if request.method == "POST":

        form = InvoiceForm(
            request.POST,
            instance=invoice,
        )

        formset = InvoiceItemFormSet(
            request.POST,
            instance=invoice,
            prefix="items",
        )

        if (
            form.is_valid()
            and formset.is_valid()
        ):

            invoice = form.save(
                commit=False
            )

            customer = (
                invoice.customer
            )

            invoice.customer_name = (
                customer.company_name
                or customer.name
            )

            invoice.customer_npwp = (
                customer.npwp
            )

            invoice.customer_address = (
                customer.address
            )

            invoice.invoice_number = (
                generate_invoice_number(
                    invoice.invoice_date
                )
            )

            invoice.subtotal = (
                Decimal("0")
            )

            invoice.discount_total = (
                Decimal("0")
            )

            invoice.tax_total = (
                Decimal("0")
            )

            invoice.withholding_total = (
                Decimal("0")
            )

            invoice.grand_total = (
                Decimal("0")
            )

            invoice.paid_amount = (
                Decimal("0")
            )

            invoice.balance_due = (
                Decimal("0")
            )

            action = request.POST.get(
                "action",
                "draft"
            )

            if action == "issue":

                invoice.status = (
                    "UNPAID"
                )

            else:

                invoice.status = (
                    "DRAFT"
                )

            invoice.save()


            items = formset.save(
                commit=False
            )

            subtotal = Decimal("0")
            discount_total = Decimal("0")
            add_tax_total = Decimal("0")
            withholding_total = (
                Decimal("0")
            )

            saved_items = 0

            for item in items:

                if not item.product:
                    continue

                product = (
                    item.product
                )

                result = calculate_item(
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    discount_percent=(
                        item.discount_percent
                    ),
                    tax=item.tax,
                    tax_mode=(
                        invoice.tax_mode
                    ),
                )

                item.invoice = invoice

                item.product_name = (
                    product.name
                )

                item.description = (
                    product.description
                )

                item.unit = product.unit

                item.discount_amount = (
                    result[
                        "discount_amount"
                    ]
                )

                item.line_subtotal = (
                    result[
                        "line_subtotal"
                    ]
                )

                item.tax_name = (
                    result[
                        "tax_name"
                    ]
                )

                item.tax_rate = (
                    result[
                        "tax_rate"
                    ]
                )

                item.tax_effect = (
                    result[
                        "tax_effect"
                    ]
                )

                item.tax_amount = (
                    result[
                        "tax_amount"
                    ]
                )

                item.line_total = (
                    result[
                        "line_total"
                    ]
                )

                item.save()

                saved_items += 1

                subtotal += (
                    result["gross"]
                )

                discount_total += (
                    result[
                        "discount_amount"
                    ]
                )

                if (
                    result["tax_effect"]
                    == "ADD"
                ):

                    add_tax_total += (
                        result[
                            "tax_amount"
                        ]
                    )

                elif (
                    result["tax_effect"]
                    == "DEDUCT"
                ):

                    withholding_total += (
                        result[
                            "tax_amount"
                        ]
                    )


            if saved_items == 0:

                transaction.set_rollback(
                    True
                )

                messages.error(
                    request,
                    "Invoice harus mempunyai "
                    "minimal satu item."
                )

            else:

                base_after_discount = (
                    subtotal
                    - discount_total
                )

                if (
                    invoice.tax_mode
                    == "INCLUSIVE"
                ):

                    grand_total = (
                        base_after_discount
                        - withholding_total
                    )

                else:

                    grand_total = (
                        base_after_discount
                        + add_tax_total
                        - withholding_total
                    )

                invoice.subtotal = (
                    subtotal
                )

                invoice.discount_total = (
                    discount_total
                )

                invoice.tax_total = (
                    add_tax_total
                )

                invoice.withholding_total = (
                    withholding_total
                )

                invoice.grand_total = (
                    grand_total
                )

                invoice.balance_due = (
                    grand_total
                )

                invoice.save()


                if action == "issue":

                    try:

                        reduce_invoice_stock(
                            invoice
                        )

                    except ValueError as exc:

                        transaction.set_rollback(
                            True
                        )

                        messages.error(
                            request,
                            str(exc)
                        )

                        return render(
                            request,
                            "invoices/form.html",
                            {
                                "form":
                                    form,

                                "formset":
                                    formset,

                                "products":
                                    Product.objects
                                    .filter(
                                        is_active=True
                                    ),
                            }
                        )


                messages.success(
                    request,
                    (
                        f"Invoice "
                        f"{invoice.invoice_number} "
                        f"berhasil disimpan."
                    )
                )

                return redirect(
                    "invoices:detail",
                    pk=invoice.pk
                )

    else:

        form = InvoiceForm(
            initial={
                "invoice_date":
                    timezone.localdate(),

                "currency":
                    "IDR",

                "tax_mode":
                    "EXCLUSIVE",
            }
        )

        formset = InvoiceItemFormSet(
            instance=invoice,
            prefix="items",
        )


    product_data = {}

    for product in (
        Product.objects
        .filter(is_active=True)
        .select_related(
            "default_tax"
        )
    ):

        product_data[
            str(product.pk)
        ] = {
            "price":
                float(
                    product.sale_price
                ),

            "tax":
                (
                    product.default_tax_id
                    or ""
                ),

            "unit":
                product.unit,

            "stock":
                float(
                    product.stock_quantity
                ),

            "manage_stock":
                product.manage_stock,
        }


    return render(
        request,
        "invoices/form.html",
        {
            "form": form,

            "formset": formset,

            "product_data":
                product_data,
        }
    )


@login_required
def invoice_detail(request, pk):

    invoice = get_object_or_404(
        Invoice.objects
        .select_related("customer")
        .prefetch_related(
            "items__product",
            "payments",
        ),
        pk=pk,
    )

    return render(
        request,
        "invoices/detail.html",
        {
            "invoice": invoice,
        },
    )

@login_required
def invoice_print(request, pk):

    invoice = get_object_or_404(
        Invoice.objects
        .select_related(
            "customer"
        )
        .prefetch_related(
            "items",
            "payments",
        ),
        pk=pk,
    )

    company = (
        CompanySetting.objects
        .first()
    )

    context = {
        "invoice": invoice,
        "company": company,
    }

    return render(
        request,
        "invoices/print.html",
        context,
    )


@login_required
def invoice_pdf(request, pk):

    invoice = get_object_or_404(
        Invoice.objects
        .select_related(
            "customer"
        )
        .prefetch_related(
            "items",
            "payments",
        ),
        pk=pk,
    )

    company = (
        CompanySetting.objects
        .first()
    )

    template = get_template(
        "invoices/pdf.html"
    )

    html = template.render(
        {
            "invoice": invoice,
            "company": company,
        }
    )

    result = BytesIO()

    pdf = pisa.CreatePDF(
        src=html,
        dest=result,
        encoding="UTF-8",
    )

    if pdf.err:

        return HttpResponse(
            "Terjadi kesalahan saat membuat PDF.",
            status=500,
        )

    response = HttpResponse(
        result.getvalue(),
        content_type="application/pdf",
    )

    filename = (
        invoice.invoice_number
        .replace("/", "-")
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="{filename}.pdf"'
    )

    return response