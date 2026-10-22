from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from review.models import Review
from django.contrib.auth.decorators import login_required
from review.forms import ReviewForm

def show_review(request):
    reviews = Review.objects.select_related('reviewer')
    context = {
        'reviews': reviews,
    }
    return render(request, 'review/review_list.html', context)

@login_required(login_url='/admin/login')
def create_review(request):
    form = ReviewForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.reviewer = request.user
        review.save()
        return redirect('review:show')
    
    context = {
        'form': form,
    }
    return render(request, 'review/review_form.html', context)

@login_required(login_url='/admin/login')
def edit_review(request, id):
    review = get_object_or_404(Review, pk=id, reviewer=request.user)
    form = ReviewForm(request.POST or None, instance=review)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('review:show')

    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'review/review_form.html', context)

@login_required(login_url='/admin/login')
@require_POST
def delete_review(request, id):
    review = get_object_or_404(Review, pk=id, reviewer=request.user)
    review.delete()
    return redirect('review:show')