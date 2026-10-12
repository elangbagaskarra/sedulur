from decimal import Decimal

from django.utils import timezone


def update_invoice_payment_status(invoice):

    total_paid = sum(
        (
            payment.amount
            for payment in invoice.payments.all()
        ),
        Decimal("0"),
    )

    invoice.paid_amount = total_paid

    balance = (
        invoice.grand_total
        - total_paid
    )

    if balance < 0:
        balance = Decimal("0")

    invoice.balance_due = balance

    if balance <= 0:

        invoice.status = "PAID"

    elif (
        invoice.due_date
        and invoice.due_date < timezone.localdate()
    ):

        invoice.status = "OVERDUE"

    elif total_paid > 0:

        invoice.status = "PARTIAL"

    else:

        invoice.status = "UNPAID"

    invoice.save(
        update_fields=[
            "paid_amount",
            "balance_due",
            "status",
            "updated_at",
        ]
    )

    return invoice