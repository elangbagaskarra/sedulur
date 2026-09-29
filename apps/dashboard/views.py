from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard(request):
    context = {
        "page_title": "Dashboard",
    }

    return render(
        request,
        "dashboard/index.html",
        context
    )