from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def rupiah(value):
    try:
        number = Decimal(value or 0)

        number = int(round(number))

        formatted = f"{number:,}".replace(",", ".")

        return f"Rp {formatted}"

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return "Rp 0"