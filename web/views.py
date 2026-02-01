from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Avg, Q
from .forms import UserRegisterForm, ReviewForm
from api.models import Place, Review

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'web/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'web/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    query = request.GET.get('name', '')
    min_rating = request.GET.get('min_rating', '0')
    
    places = Place.objects.all()
    
    if query:
        # Custom search logic as per requirement: exact match first, then substring
        # Django doesn't natively support "order by exact match", so we can sort in python or use CASE WHEN
        # Simpler approach: Filter then sort in python or simple filter
        places = places.filter(name__icontains=query)
    
    # Filter by min rating
    # We need to annotate avg rating first
    places = places.annotate(average_rating=Avg('reviews__rating'))
    
    if min_rating:
        try:
            min_r = float(min_rating)
            places = places.filter(average_rating__gte=min_r)
        except ValueError:
            pass

    # Ordering: Exact name matches first (if query exists)
    places = list(places) # Evaluate to list for Python sorting
    if query:
        places.sort(key=lambda p: p.name.lower() != query.lower()) 

    return render(request, 'web/index.html', {'places': places, 'query': query, 'min_rating': min_rating})

@login_required
def place_detail(request, pk):
    place = get_object_or_404(Place, pk=pk)
    # Context-aware sorting: User's review first, then newest
    reviews = place.reviews.all().order_by('-created_at')
    user_review = reviews.filter(user=request.user).first()
    other_reviews = reviews.exclude(user=request.user)
    
    sorted_reviews = []
    if user_review:
        sorted_reviews.append(user_review)
    sorted_reviews.extend(other_reviews)
    
    avg_rating = place.reviews.aggregate(Avg('rating'))['rating__avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    
    return render(request, 'web/place_detail.html', {
        'place': place, 
        'reviews': sorted_reviews, 
        'avg_rating': avg_rating
    })

@login_required
def add_review(request, pk):
    # This logic seems to need Place existence.
    # The API 'add/' endpoint creates a place if it doesn't exist.
    # But here we are on a specific place page or adding via form.
    # If the user wants to add a review for a NEW place, they probably need a "Add Place & Review" page.
    # However, the requirement "Find or Create" allows creating a place.
    # For now, let's implement adding a review to an EXISTING place from the detail page.
    # If we want to support creating a place, we need a separate form.
    # Based on the prompt "use django only for the frontend", I'll stick to a simple flow:
    # 1. Search -> No result? -> Maybe "Add Place" button?
    # Actually the API logic `AddReviewView` handles creation.
    # I'll implement a simple "Add Review" for existing place here.
    
    place = get_object_or_404(Place, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.place = place
            review.user = request.user
            review.save()
            return redirect('place_detail', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'web/add_review.html', {'form': form, 'place': place})
