from django.http import HttpResponse
from django.shortcuts import render, redirect
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