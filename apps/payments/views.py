from django.contrib import messages

from django.contrib.auth.decorators import (
    login_required,
)

from django.core.paginator import Paginator

from django.db import transaction

from django.db.models import Q, Sum

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from django.utils import timezone


from .forms import PaymentForm

from .models import Payment

from .services import (
    update_invoice_payment_status,
)

from apps.invoices.models import Invoice


@login_required
def payment_list(request):

    payments = (
        Payment.objects
        .select_related(
            "invoice",
            "invoice__customer",
        )
        .all()
    )

    query = request.GET.get(
        "q",
        ""
    ).strip()

    if query:

        payments = payments.filter(
            Q(
                invoice__invoice_number__icontains=query
            )
            |
            Q(
                invoice__customer_name__icontains=query
            )
            |
            Q(
                reference_number__icontains=query
            )
        )

    paginator = Paginator(
        payments,
        15
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    total_amount = (
        Payment.objects
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    today_amount = (
        Payment.objects
        .filter(
            payment_date=timezone.localdate()
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )

    context = {
        "page_obj": page_obj,
        "query": query,
        "total_amount": total_amount,
        "today_amount": today_amount,
        "total_payments":
            Payment.objects.count(),
    }

    return render(
        request,
        "payments/list.html",
        context,
    )


@login_required
@transaction.atomic
def payment_create(
    request,
    invoice_id
):

    invoice = get_object_or_404(
        Invoice,
        pk=invoice_id
    )

    if invoice.status == "DRAFT":

        messages.warning(
            request,
            "Invoice draft belum dapat menerima pembayaran."
        )

        return redirect(
            "invoices:detail",
            pk=invoice.pk
        )

    if invoice.status == "CANCELLED":

        messages.warning(
            request,
            "Invoice yang dibatalkan tidak dapat menerima pembayaran."
        )

        return redirect(
            "invoices:detail",
            pk=invoice.pk
        )

    if invoice.balance_due <= 0:

        messages.info(
            request,
            "Invoice ini sudah lunas."
        )

        return redirect(
            "invoices:detail",
            pk=invoice.pk
        )

    if request.method == "POST":

        form = PaymentForm(
            request.POST
        )

        if form.is_valid():

            payment = form.save(
                commit=False
            )

            payment.invoice = invoice

            if (
                payment.amount
                > invoice.balance_due
            ):

                form.add_error(
                    "amount",
                    (
                        "Nominal pembayaran "
                        "melebihi sisa tagihan."
                    )
                )

            else:

                payment.save()

                update_invoice_payment_status(
                    invoice
                )

                messages.success(
                    request,
                    "Pembayaran berhasil dicatat."
                )

                return redirect(
                    "invoices:detail",
                    pk=invoice.pk
                )

    else:

        form = PaymentForm(
            initial={
                "payment_date":
                    timezone.localdate(),

                "amount":
                    invoice.balance_due,
            }
        )

    return render(
        request,
        "payments/form.html",
        {
            "form": form,
            "invoice": invoice,
        }
    )


@login_required
def payment_detail(
    request,
    pk
):

    payment = get_object_or_404(
        Payment.objects.select_related(
            "invoice"
        ),
        pk=pk
    )

    return render(
        request,
        "payments/detail.html",
        {
            "payment": payment,
        }
    )