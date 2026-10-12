from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from apps.products.models import StockMovement


MONEY = Decimal("0.01")


def money(value):
    return Decimal(value).quantize(
        MONEY,
        rounding=ROUND_HALF_UP,
    )


def generate_invoice_number(invoice_date):
    from .models import Invoice

    prefix = (
        f"INV/"
        f"{invoice_date.year}/"
        f"{invoice_date.month:02d}/"
    )

    last_invoice = (
        Invoice.objects
        .filter(invoice_number__startswith=prefix)
        .order_by("-id")
        .first()
    )

    next_number = 1

    if last_invoice:
        try:
            last_number = int(
                last_invoice.invoice_number
                .split("/")[-1]
            )

            next_number = last_number + 1

        except (ValueError, IndexError):
            pass

    return (
        f"{prefix}"
        f"{next_number:04d}"
    )


def calculate_item(
    quantity,
    unit_price,
    discount_percent,
    tax,
    tax_mode,
):
    quantity = Decimal(quantity)
    unit_price = Decimal(unit_price)

    discount_percent = Decimal(
        discount_percent or 0
    )

    gross = quantity * unit_price

    discount_amount = (
        gross
        * discount_percent
        / Decimal("100")
    )

    amount_after_discount = (
        gross - discount_amount
    )

    tax_amount = Decimal("0")
    line_total = amount_after_discount

    tax_name = ""
    tax_rate = Decimal("0")
    tax_effect = ""

    if tax:
        tax_name = tax.name
        tax_rate = tax.rate
        tax_effect = tax.effect

        rate_decimal = (
            Decimal(tax.rate)
            / Decimal("100")
        )

        if tax.effect == "ADD":

            if tax_mode == "INCLUSIVE":

                base = (
                    amount_after_discount
                    /
                    (
                        Decimal("1")
                        + rate_decimal
                    )
                )

                tax_amount = (
                    amount_after_discount
                    - base
                )

                line_total = (
                    amount_after_discount
                )

            else:

                tax_amount = (
                    amount_after_discount
                    * rate_decimal
                )

                line_total = (
                    amount_after_discount
                    + tax_amount
                )

        elif tax.effect == "DEDUCT":

            tax_amount = (
                amount_after_discount
                * rate_decimal
            )

            line_total = (
                amount_after_discount
                - tax_amount
            )

    return {
        "gross": money(gross),

        "discount_amount":
            money(discount_amount),

        "line_subtotal":
            money(amount_after_discount),

        "tax_amount":
            money(tax_amount),

        "line_total":
            money(line_total),

        "tax_name":
            tax_name,

        "tax_rate":
            tax_rate,

        "tax_effect":
            tax_effect,
    }


@transaction.atomic
def reduce_invoice_stock(invoice):
    for item in invoice.items.select_related(
        "product"
    ):

        product = item.product

        if not product:
            continue

        if product.product_type != "GOODS":
            continue

        if not product.manage_stock:
            continue

        quantity = item.quantity

        if product.stock_quantity < quantity:

            raise ValueError(
                f"Stok {product.name} "
                f"tidak mencukupi."
            )

        stock_before = (
            product.stock_quantity
        )

        stock_after = (
            stock_before - quantity
        )

        StockMovement.objects.create(
            product=product,
            movement_type="OUT",
            quantity=quantity,
            stock_before=stock_before,
            stock_after=stock_after,
            reference=invoice.invoice_number,
            notes=(
                "Pengeluaran stok "
                "dari invoice"
            ),
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