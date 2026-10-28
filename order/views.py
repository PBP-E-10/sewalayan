from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from order.models import Order, User


@login_required(login_url="user:login")
def show_order(request):
    user = get_object_or_404(User, id=request.user.id)
    rents = user.rents.all()
    items = user.items.all()
    context = {
        "rents": rents,
        "items": items,
    }
    return render(request, "order/index.html", context)


def show_order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "order/details.html", {"order": order})
