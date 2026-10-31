from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, help_text="Used in the menu URL, e.g. my-cafe")
    tagline = models.CharField(max_length=200, blank=True)
    currency = models.CharField(max_length=5, default="₹")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.restaurant.name} – {self.name}"


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="items/", blank=True, null=True)
    is_veg = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


import uuid


class Order(models.Model):
    NEW, PREPARING, READY, SERVED, CANCELLED = "new", "preparing", "ready", "served", "cancelled"
    STATUS_CHOICES = [
        (NEW, "New"), (PREPARING, "Preparing"), (READY, "Ready"),
        (SERVED, "Served"), (CANCELLED, "Cancelled"),
    ]
    ACTIVE = (NEW, PREPARING, READY)

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    table_number = models.CharField(max_length=20, blank=True)
    customer_name = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    note = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=NEW)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} ({self.restaurant.name})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    is_veg = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.quantity} x {self.name}"
