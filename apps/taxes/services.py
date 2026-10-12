from decimal import Decimal, ROUND_HALF_UP


MONEY_PLACES = Decimal("0.01")


def money(value):
    return Decimal(value).quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP
    )


def calculate_tax(
    amount,
    rate,
    effect="ADD",
    tax_mode="EXCLUSIVE",
):
    amount = Decimal(amount)
    rate = Decimal(rate)

    rate_decimal = rate / Decimal("100")

    result = {
        "input_amount": money(amount),
        "base_amount": money(amount),
        "tax_amount": Decimal("0.00"),
        "total": money(amount),
        "effect": effect,
        "tax_mode": tax_mode,
    }

    # Pajak menambah harga, contoh PPN
    if effect == "ADD":

        if tax_mode == "INCLUSIVE":

            divisor = (
                Decimal("1") + rate_decimal
            )

            if divisor == 0:
                return result

            base_amount = (
                amount / divisor
            )

            tax_amount = (
                amount - base_amount
            )

            result["base_amount"] = money(
                base_amount
            )

            result["tax_amount"] = money(
                tax_amount
            )

            result["total"] = money(
                amount
            )

        else:

            tax_amount = (
                amount * rate_decimal
            )

            result["tax_amount"] = money(
                tax_amount
            )

            result["total"] = money(
                amount + tax_amount
            )

    # Pajak pemotongan, contoh PPh
    elif effect == "DEDUCT":

        tax_amount = (
            amount * rate_decimal
        )

        result["tax_amount"] = money(
            tax_amount
        )

        result["total"] = money(
            amount - tax_amount
        )

    return result