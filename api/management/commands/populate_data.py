import random
from django.core.management.base import BaseCommand
from api.models import User, Place, Review

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        Review.objects.all().delete()
        Place.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()

        categories = ['Restaurant', 'Doctor', 'Shop', 'Cafe', 'Gym']
        names = ['The Great', 'Blue', 'Fast', 'Healthy', 'Local', 'Global']
        locations = ['Main St', 'Second Ave', 'Mall Road', 'High Street']

        # 1. Create Users
        users = []
        for i in range(5):
            u = User.objects.create_user(
                phone_number=f"987654321{i}",
                name=f"User {i}",
                password="password123"
            )
            users.append(u)
        
        # 2. Create Places
        places = []
        for i in range(10):
            p = Place.objects.create(
                name=f"{random.choice(names)} {random.choice(categories)}",
                address=f"{random.randint(1, 999)} {random.choice(locations)}",
                category=random.choice(categories)
            )
            places.append(p)

        # 3. Create Reviews
        for p in places:
            # Each place gets 1-4 random reviews
            for _ in range(random.randint(1, 4)):
                Review.objects.create(
                    place=p,
                    user=random.choice(users),
                    rating=random.randint(1, 5),
                    review_text="This is a sample review text for testing purposes."
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))