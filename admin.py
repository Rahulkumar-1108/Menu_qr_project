from django.contrib import admin
from .models import Category, MenuItem, Restaurant


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "order")
    list_filter = ("restaurant",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_veg", "is_available")
    list_filter = ("category__restaurant", "category", "is_veg", "is_available")
    list_editable = ("price", "is_available")
    search_fields = ("name", "description")


from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "price", "quantity", "is_veg")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "restaurant", "table_number", "status", "total", "created_at")
    list_filter = ("restaurant", "status")
    inlines = [OrderItemInline]
