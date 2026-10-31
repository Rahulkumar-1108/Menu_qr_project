# Menu QR (Django) – with ordering

## Setup (Windows: use `venv\Scripts\activate`)
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py makemigrations menu
    python manage.py migrate
    python manage.py seed
    python manage.py createsuperuser      # this staff user logs in to the Orders dashboard
    python manage.py runserver 0.0.0.0:8000

## URLs
- Menu: /m/<slug>/            (add ?table=5 to prefill a table)
- QR page: /m/<slug>/qr/      (type a table number to make a per-table QR)
- Restaurant orders dashboard: /m/<slug>/dashboard/  (staff login)
- Customer order tracking: /order/<token>/
- Admin: /admin/
