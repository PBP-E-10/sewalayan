from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

from order.models import Order


@login_required(login_url="user:login")
def show_order(request):
    user = get_object_or_404(User, id=request.user.id)
    rents = user.rents.all()
    context = {
        "rents": rents,
    }
    return render(request, "order/index.html", context)


@login_required(login_url="user:login")
def show_rental(request):
    user = get_object_or_404(User, id=request.user.id)
    items = user.items.all()
    context = {
        "items": items,
    }

    return render(request, "order/rental.html", context)


@login_required(login_url="user:login")
def show_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    return render(request, "order/details.html", {"order": order})
