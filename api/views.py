from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Case, When, Value, IntegerField, Avg
from .models import User, Place, Review
from .serializers import UserSerializer, PlaceSerializer, SearchResultSerializer

# 1. Registration View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny] # Only endpoint that is public

# 2. Add Review View (Logic: Find or Create Place)
class AddReviewView(APIView):
    def post(self, request):
        name = request.data.get('name')
        address = request.data.get('address')
        rating = request.data.get('rating')
        text = request.data.get('review_text', '')

        if not all([name, address, rating]):
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        # Logic: find or create place based on unique name+address
        place, created = Place.objects.get_or_create(
            name=name, 
            address=address
        )

        Review.objects.create(
            place=place,
            user=request.user,
            rating=rating,
            review_text=text
        )

        return Response({"message": "Review added successfully"}, status=status.HTTP_201_CREATED)

# 3. Search View (Custom Ordering Logic)
class PlaceSearchView(generics.ListAPIView):
    serializer_class = SearchResultSerializer

    def get_queryset(self):
        queryset = Place.objects.all()
        name_query = self.request.query_params.get('name', None)
        min_rating = self.request.query_params.get('min_rating', None)

        if name_query:
            # Filter matches
            queryset = queryset.filter(name__icontains=name_query)
            
            # Custom Ordering: Exact matches get priority 1, partial matches priority 2
            queryset = queryset.annotate(
                match_priority=Case(
                    When(name__iexact=name_query, then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('match_priority', 'name')

        if min_rating:
            # Aggregate and filter by average rating
            queryset = queryset.annotate(avg_r=Avg('reviews__rating')).filter(avg_r__gte=min_rating)

        return queryset

# 4. Detail View
class PlaceDetailView(generics.RetrieveAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer