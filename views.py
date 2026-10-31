import io
import json
from decimal import Decimal
from urllib.parse import urlencode

import qrcode
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import MenuItem, Order, OrderItem, Restaurant

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff)


def home(request):
    return render(request, "menu/home.html", {"restaurants": Restaurant.objects.all()})


def menu_view(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    categories = restaurant.categories.prefetch_related("items")
    return render(request, "menu/menu.html", {"restaurant": restaurant, "categories": categories})


# ---------------- QR ----------------
def _table(request):
    return request.GET.get("table", "").strip()[:20]


def _menu_url(request, slug):
    url = request.build_absolute_uri(reverse("menu", args=[slug]))
    table = _table(request)
    return url + ("?" + urlencode({"table": table}) if table else "")


def qr_page(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    table = _table(request)
    q = urlencode({"table": table}) if table else ""
    png = reverse("qr_png", args=[slug])
    return render(request, "menu/qr.html", {
        "restaurant": restaurant, "menu_url": _menu_url(request, slug), "table": table,
        "qr_src": png + ("?" + q if q else ""),
        "qr_download": png + "?" + (q + "&" if q else "") + "download=1",
    })


def qr_png(request, slug):
    get_object_or_404(Restaurant, slug=slug)
    img = qrcode.make(_menu_url(request, slug), box_size=12, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    response = HttpResponse(buf.getvalue(), content_type="image/png")
    if request.GET.get("download"):
        name = f"{slug}-table-{_table(request)}" if _table(request) else slug
        response["Content-Disposition"] = f'attachment; filename="{name}-qr.png"'
    return response


# ---------------- Customer ordering ----------------
@require_POST
def place_order(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid request."}, status=400)

    qty_by_id = {}
    for line in data.get("items", []) if isinstance(data, dict) else []:
        try:
            iid, qty = int(line["id"]), int(line["qty"])
        except (KeyError, TypeError, ValueError):
            continue
        if qty >= 1:
            qty_by_id[iid] = min(qty_by_id.get(iid, 0) + qty, 50)
    if not qty_by_id:
        return JsonResponse({"error": "Your cart is empty."}, status=400)

    items = list(MenuItem.objects.filter(
        id__in=qty_by_id, category__restaurant=restaurant, is_available=True))
    if len(items) != len(qty_by_id):
        return JsonResponse({"error": "Some items are no longer available. "
                                      "Please remove them and try again."}, status=400)

    with transaction.atomic():
        order = Order.objects.create(
            restaurant=restaurant,
            table_number=str(data.get("table", "")).strip()[:20],
            customer_name=str(data.get("name", "")).strip()[:80],
            phone=str(data.get("phone", "")).strip()[:20],
            note=str(data.get("note", "")).strip()[:300],
        )
        total = Decimal("0")
        for it in items:
            qty = qty_by_id[it.id]
            OrderItem.objects.create(order=order, item=it, name=it.name,
                                     price=it.price, quantity=qty, is_veg=it.is_veg)
            total += it.price * qty
        order.total = total
        order.save(update_fields=["total"])

    return JsonResponse({"order_id": order.id,
                         "status_url": reverse("order_status", args=[order.token])})


def order_status(request, token):
    order = get_object_or_404(Order.objects.prefetch_related("items"), token=token)
    return render(request, "menu/order_status.html", {"order": order, "restaurant": order.restaurant})


def order_status_json(request, token):
    order = get_object_or_404(Order, token=token)
    return JsonResponse({"status": order.status, "label": order.get_status_display()})


# ---------------- Restaurant dashboard ----------------
def _serialize(o):
    return {
        "id": o.id, "table": o.table_number, "name": o.customer_name, "phone": o.phone,
        "note": o.note, "status": o.status, "label": o.get_status_display(),
        "total": str(o.total),
        "time": timezone.localtime(o.created_at).strftime("%I:%M %p"),
        "items": [{"name": i.name, "qty": i.quantity, "veg": i.is_veg} for i in o.items.all()],
    }


@staff_required
def dashboard(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    return render(request, "menu/dashboard.html", {"restaurant": restaurant})


@staff_required
def dashboard_orders(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    qs = restaurant.orders.prefetch_related("items")
    active = qs.filter(status__in=Order.ACTIVE).order_by("created_at")
    today = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    done = qs.exclude(status__in=Order.ACTIVE).filter(updated_at__gte=today)[:50]
    return JsonResponse({"active": [_serialize(o) for o in active],
                         "done": [_serialize(o) for o in done]})


@staff_required
@require_POST
def update_order_status(request, slug, pk):
    order = get_object_or_404(Order, pk=pk, restaurant__slug=slug)
    try:
        status = json.loads(request.body).get("status")
    except (ValueError, AttributeError):
        status = None
    if status not in dict(Order.STATUS_CHOICES):
        return JsonResponse({"error": "Invalid status."}, status=400)
    order.status = status
    order.save(update_fields=["status", "updated_at"])
    return JsonResponse({"ok": True})
