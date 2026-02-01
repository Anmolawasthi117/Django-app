from rest_framework import serializers
from .models import User, Place, Review
from django.db.models import Avg

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'phone_number', 'password')

    def create(self, validated_data):
        
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        return user

class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.name')

    class Meta:
        model = Review
        fields = ('id', 'rating', 'review_text', 'user_name', 'created_at')

class PlaceSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ('id', 'name', 'address', 'average_rating', 'reviews')

    def get_average_rating(self, obj):
        # Calculate avg rating on the fly
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    def get_reviews(self, obj):
        # Special logic: Current user's review first, then newest
        user = self.context.get('request').user
        all_reviews = obj.reviews.all().order_items = obj.reviews.all().order_by('-created_at')
        
        if user.is_authenticated:
            user_review = all_reviews.filter(user=user)
            other_reviews = all_reviews.exclude(user=user)
            # Combine: user review (if exists) + others
            final_list = list(user_review) + list(other_reviews)
            return ReviewSerializer(final_list, many=True).data
        
        return ReviewSerializer(all_reviews, many=True).data

class SearchResultSerializer(serializers.ModelSerializer):
    """Simplified serializer for search results to match the task requirement"""
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = ('id', 'name', 'average_rating')

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0