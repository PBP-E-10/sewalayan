from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from review.models import Review
from django.contrib.auth.decorators import login_required
from review.forms import ReviewForm

def show_review(request):
    context = {
        'form': ReviewForm(user=request.user),
    }
    return render(request, 'review/review_list.html', context)

@login_required(login_url='user:login')
def create_review(request):
    form = ReviewForm(request.POST or None, user=request.user)

    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.reviewer = request.user
        review.save()
        return redirect('review:show')
    
    context = {
        'form': form,
    }
    return render(request, 'review/review_form.html', context)

@login_required(login_url='user:login')
def edit_review(request, id):
    review = get_object_or_404(Review, pk=id, reviewer=request.user)
    form = ReviewForm(request.POST or None, instance=review, user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('review:show')

    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'review/review_form.html', context)

@login_required(login_url='user:login')
@require_POST
def delete_review(request, id):
    review = get_object_or_404(Review, pk=id, reviewer=request.user)
    review.delete()
    return redirect('review:show')

def show_review_json(request):
    reviews = Review.objects.select_related('reviewer', 'item')

    item_id = request.GET.get('item')
    if item_id:
        reviews = reviews.filter(item_id=item_id)

    data = [
        {
            'id': review.id,
            'reviewer': review.reviewer.username if review.reviewer else 'Anonim',
            'item_id': review.item_id,
            'item': review.item.name if review.item else '-',
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_at.isoformat(),
            'is_owner': review.reviewer_id == request.user.id,
        }
        for review in reviews
    ]
    return JsonResponse(data, safe=False)

@require_POST
def create_review_ajax(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Kamu harus login dulu.'}, status=401)

    form = ReviewForm(request.POST, user=request.user)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)

    review = form.save(commit=False)
    review.reviewer = request.user
    review.save()
    return JsonResponse({'id': review.id}, status=201)

@require_POST
def delete_review_ajax(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Kamu harus login dulu.'}, status=401)

    review = get_object_or_404(Review, pk=id, reviewer=request.user)
    review.delete()
    return JsonResponse({'status': 'deleted'})