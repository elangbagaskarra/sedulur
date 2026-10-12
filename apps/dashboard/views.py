from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from apps.invoices.models import Invoice
from apps.payments.models import Payment


MONTH_NAMES = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Agu",
    "Sep",
    "Okt",
    "Nov",
    "Des",
]


def get_month(year, month, offset):
    month_index = (
        year * 12
        + month
        - 1
        + offset
    )

    new_year = month_index // 12
    new_month = month_index % 12 + 1

    return date(
        new_year,
        new_month,
        1,
    )


@login_required
def dashboard(request):

    today = timezone.localdate()

    current_month = today.replace(
        day=1
    )

    issued_statuses = [
        "UNPAID",
        "PARTIAL",
        "PAID",
        "OVERDUE",
    ]

    # ==========================================
    # OMZET BULAN INI
    # ==========================================

    omzet_bulan_ini = (
        Invoice.objects
        .filter(
            invoice_date__year=today.year,
            invoice_date__month=today.month,
            status__in=issued_statuses,
        )
        .aggregate(
            total=Sum("grand_total")
        )["total"]
        or Decimal("0")
    )

    invoice_bulan_ini = (
        Invoice.objects
        .filter(
            invoice_date__year=today.year,
            invoice_date__month=today.month,
            status__in=issued_statuses,
        )
        .count()
    )

    # ==========================================
    # PIUTANG AKTIF
    # ==========================================

    active_receivables = (
        Invoice.objects
        .filter(
            status__in=[
                "UNPAID",
                "PARTIAL",
                "OVERDUE",
            ],
            balance_due__gt=0,
        )
    )

    piutang_aktif = (
        active_receivables
        .aggregate(
            total=Sum("balance_due")
        )["total"]
        or Decimal("0")
    )

    piutang_count = (
        active_receivables.count()
    )

    # ==========================================
    # JATUH TEMPO
    # berdasarkan tanggal aktual,
    # bukan hanya field status
    # ==========================================

    overdue_queryset = (
        Invoice.objects
        .filter(
            due_date__lt=today,
            balance_due__gt=0,
        )
        .exclude(
            status__in=[
                "DRAFT",
                "PAID",
                "CANCELLED",
            ]
        )
        .select_related(
            "customer"
        )
        .order_by(
            "due_date"
        )
    )

    overdue_count = (
        overdue_queryset.count()
    )

    overdue_amount = (
        overdue_queryset
        .aggregate(
            total=Sum("balance_due")
        )["total"]
        or Decimal("0")
    )

    # ==========================================
    # PAJAK BULAN INI
    # ==========================================

    ppn_keluaran = (
        Invoice.objects
        .filter(
            invoice_date__year=today.year,
            invoice_date__month=today.month,
            status__in=issued_statuses,
        )
        .aggregate(
            total=Sum("tax_total")
        )["total"]
        or Decimal("0")
    )

    pph_potongan = (
        Invoice.objects
        .filter(
            invoice_date__year=today.year,
            invoice_date__month=today.month,
            status__in=issued_statuses,
        )
        .aggregate(
            total=Sum("withholding_total")
        )["total"]
        or Decimal("0")
    )

    # ==========================================
    # GRAFIK 12 BULAN
    # ==========================================

    first_chart_month = get_month(
        today.year,
        today.month,
        -11,
    )

    monthly_sales = (
        Invoice.objects
        .filter(
            invoice_date__gte=first_chart_month,
            status__in=issued_statuses,
        )
        .annotate(
            month=TruncMonth(
                "invoice_date"
            )
        )
        .values(
            "month"
        )
        .annotate(
            total=Sum(
                "grand_total"
            )
        )
        .order_by(
            "month"
        )
    )

    sales_map = {}

    for row in monthly_sales:

        month = row["month"]

        sales_map[
            (
                month.year,
                month.month,
            )
        ] = row["total"] or Decimal("0")

    chart_labels = []
    chart_data = []

    for offset in range(-11, 1):

        month_date = get_month(
            today.year,
            today.month,
            offset,
        )

        chart_labels.append(
            (
                f"{MONTH_NAMES[month_date.month - 1]} "
                f"{month_date.year}"
            )
        )

        value = sales_map.get(
            (
                month_date.year,
                month_date.month,
            ),
            Decimal("0"),
        )

        chart_data.append(
            float(value)
        )

    # ==========================================
    # INVOICE PERLU PERHATIAN
    # ==========================================

    attention_invoices = []

    for invoice in overdue_queryset[:5]:

        days_overdue = (
            today
            - invoice.due_date
        ).days

        attention_invoices.append(
            {
                "invoice": invoice,
                "days_overdue": days_overdue,
            }
        )

    # ==========================================
    # INVOICE TERBARU
    # ==========================================

    recent_invoices = (
        Invoice.objects
        .exclude(
            status="DRAFT"
        )
        .select_related(
            "customer"
        )
        .order_by(
            "-created_at"
        )[:6]
    )

    # ==========================================
    # PEMBAYARAN TERBARU
    # ==========================================

    recent_payments = (
        Payment.objects
        .select_related(
            "invoice",
            "invoice__customer",
        )
        .order_by(
            "-created_at"
        )[:5]
    )

    context = {

        "today": today,

        "omzet_bulan_ini":
            omzet_bulan_ini,

        "invoice_bulan_ini":
            invoice_bulan_ini,

        "piutang_aktif":
            piutang_aktif,

        "piutang_count":
            piutang_count,

        "overdue_count":
            overdue_count,

        "overdue_amount":
            overdue_amount,

        "ppn_keluaran":
            ppn_keluaran,

        "pph_potongan":
            pph_potongan,

        "chart_labels":
            chart_labels,

        "chart_data":
            chart_data,

        "attention_invoices":
            attention_invoices,

        "recent_invoices":
            recent_invoices,

        "recent_payments":
            recent_payments,
    }

    return render(
        request,
        "dashboard/index.html",
        context,
    )