from django.core.management.base import BaseCommand
from menu.models import Category, MenuItem, Restaurant

DATA = {
    "Starters": [
        ("Paneer Tikka", "Char-grilled cottage cheese with spices", 220, True),
        ("Chicken 65", "Spicy South Indian fried chicken", 260, False),
        ("Veg Spring Rolls", "Crispy rolls with seasoned vegetables", 160, True),
    ],
    "Main Course": [
        ("Butter Chicken", "Creamy tomato gravy with tandoori chicken", 320, False),
        ("Dal Makhani", "Slow-cooked black lentils", 240, True),
        ("Masala Dosa", "Crispy dosa with potato filling", 140, True),
    ],
    "Desserts": [
        ("Gulab Jamun", "Two warm milk dumplings in syrup", 90, True),
        ("Brownie with Ice Cream", "Warm chocolate brownie", 150, True),
    ],
    "Drinks": [
        ("Filter Coffee", "South Indian style", 60, True),
        ("Mango Lassi", "Chilled yogurt mango drink", 90, True),
    ],
}


class Command(BaseCommand):
    help = "Create a demo restaurant with sample menu"

    def handle(self, *args, **options):
        r, _ = Restaurant.objects.get_or_create(
            slug="demo-cafe",
            defaults={"name": "Demo Cafe", "tagline": "Fresh. Fast. Delicious."},
        )
        for i, (cat, items) in enumerate(DATA.items()):
            c, _ = Category.objects.get_or_create(restaurant=r, name=cat, defaults={"order": i})
            for name, desc, price, veg in items:
                MenuItem.objects.get_or_create(
                    category=c, name=name,
                    defaults={"description": desc, "price": price, "is_veg": veg},
                )
        self.stdout.write(self.style.SUCCESS("Seeded 'demo-cafe' -> /m/demo-cafe/"))
