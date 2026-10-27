from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from review.models import Review
from review.forms import ReviewForm
from item.models import Item
from order.models import Order

def show_review(request):
    return render(request, 'review/review_list.html')

@login_required(login_url='user:login')
def edit_review(request, id):
    review = get_object_or_404(Review, pk=id, reviewer=request.user)
    form = ReviewForm(request.POST or None, instance=review)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('review:show')

    context = {
        'form': form,
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
def create_review_ajax(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Kamu harus login dulu.'}, status=401)

    order = get_object_or_404(Order, id=order_id)

    if order.buyer != request.user:
        return JsonResponse({'error': 'Hanya penyewa yang bisa mereview order ini'}, status=403)
    if order.status != 'finished':
        return JsonResponse({'error': 'Review baru bisa ditulis setelah sewa selesai.'}, status=400)
    if Review.objects.filter(order=order).exists():
        return JsonResponse({'error': 'Order ini sudah kamu review.'}, status=400)

    form = ReviewForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    review = form.save(commit=False)
    review.reviewer = request.user
    review.order = order
    review.save()
    return JsonResponse({'id': review.id}, status=201)

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