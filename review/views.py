from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from review.models import Review, Report
from review.forms import ReviewForm, ReportForm
from item.models import Item
from order.models import Order

def show_review(request):
    return render(request, 'review/review_list.html')

@login_required(login_url='user:login')
def review_order(request, order_id):
    order = get_object_or_404(Order.objects.select_related('item'), id=order_id, buyer=request.user)
    review = Review.objects.filter(order=order).first()

    if review is None and order.status != 'finished':
        return redirect('order:detail', order_id=order.id)

    form = ReviewForm(request.POST or None, instance=review)

    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.reviewer = request.user
        review.order = order
        review.save()
        return redirect('order:detail', order_id=order.id)

    context = {
        'form': form,
        'order': order,
        'is_edit': review is not None,
    }
    return render(request, 'review/review_form.html', context)

def show_review_json(request):
    reviews = Review.objects.select_related('reviewer', 'order__item')

    item_id = request.GET.get('item')
    if item_id:
        reviews = reviews.filter(order__item_id=item_id)

    data = [
        {
            'id': review.id,
            'reviewer': review.reviewer.username if review.reviewer else 'Anonim',
            'order_id': str(review.order_id) if review.order_id else None,
            'item_id': review.order.item_id if review.order else None,
            'item': review.order.item.name if review.order else '-',
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat(),
            'is_owner': review.reviewer_id == request.user.id,
        }
        for review in reviews
    ]
    return JsonResponse(data, safe=False)

@require_POST
def delete_review_ajax(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Kamu harus login dulu.'}, status=401)

    review = get_object_or_404(Review, pk=id, reviewer=request.user)
    review.delete()
    return JsonResponse({'status': 'deleted'})

def show_item_reviews(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    context = {
        'item': item,
    }
    return render(request, 'review/review_list.html', context)

@require_POST
def create_report_ajax(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Kamu harus login dulu.'}, status=401)

    order = get_object_or_404(Order.objects.select_related('item'), id=order_id)

    if request.user not in (order.buyer, order.item.owner):
        return JsonResponse({'error': 'Hanya penyewa atau pemilik barang yang bisa melapor.'}, status=403)
    if Report.objects.filter(order=order, reporter=request.user, status__in=['open', 'in_review']).exists():
        return JsonResponse({'error': 'Kamu sudah punya laporan aktif untuk order ini.'}, status=400)

    form = ReportForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    report = form.save(commit=False)
    report.reporter = request.user
    report.order = order
    report.save()

    order.item.is_available = False
    order.item.save()

    return JsonResponse({'id': report.id}, status=201)


@login_required(login_url='user:login')
def show_my_reports(request):
    reports = Report.objects.filter(reporter=request.user).select_related('order__item')
    context = {
        'reports': reports,
    }
    return render(request, 'review/report_list.html', context)