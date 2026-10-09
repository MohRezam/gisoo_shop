# Gisoo Center

Backend API for **گیسو سنتر** ([gisoocenter.ir](https://gisoocenter.ir/)) — an Iranian hair-care store with catalog, cart, orders, hair consultation, magazine, and account management.

This repository is the **Django REST API**. The storefront / mobile client lives in a separate frontend.

---

## Overview

Customers browse products by brand, category, hair type, and hair problem. They can mix **product variants** and **bundles** in one cart, apply discounts, choose a shipping address, and place an order. Payment today is **card-to-card (C2C)**: the API issues a payment intent with destination card details; the customer uploads a receipt for admin review.

Auth is **OTP on Iranian mobile numbers** (JWT). Logged-in users manage profile, extra phone numbers, and addresses. Guests can still fill a cart (UUID) and request a hair consultation; after login, cart and consultations are merged onto the account.

---

## Tech stack

| Layer | Choice |
| --- | --- |
| Language | Python 3.12+ |
| API | Django 6, Django REST Framework, SimpleJWT |
| Docs | OpenAPI via drf-spectacular (`/api/docs/` in DEBUG) |
| Database | PostgreSQL 17 (SQLite fallback via `LOCAL_DB_ENABLED`) |
| Cache / broker | Redis 7, Celery + django-celery-beat |
| Storage | S3-compatible (django-storages / boto3) |
| SMS | Melipayamak pattern SMS |
| Push | Firebase / fcm-django |
| Observability | Sentry, Silk, Django Debug Toolbar (DEBUG) |
| Deploy | Docker Compose, Gunicorn, Nginx |

Dependency manager: **Poetry** (`pyproject.toml` / `poetry.lock`).

---

## Domain modules (`apps/`)

| App | Responsibility |
| --- | --- |
| `users` | OTP login/logout, JWT refresh, profile, extra phone numbers |
| `products` | Catalog, variants, bundles, brands, hair types/problems, wishlist, campaigns |
| `cart` | Guest/user cart, mix of variants + bundles, discount codes, totals |
| `orders` | Checkout, order list/detail, cancel, confirm delivery |
| `payments` | C2C payment intent, receipt upload, admin approve/reject |
| `addresses` | CRUD shipping addresses (default flag) |
| `shipping` | Shipping methods |
| `discounts` | Coupon / discount rules |
| `consultations` | Hair consultation form, staff recommendations, add-to-cart |
| `magazine` | Editorial content |
| `home` | Banners, sliders, about, FAQs, social links |
| `reviews` | Product and homepage reviews |
| `marketing` | SMS subscribe + OTP verify |
| `notifications` | In-app inbox + OTP helpers |
| `sms` | Pattern SMS sending |
| `shared` | Base models, cache helpers |

Project package: `core_gisoo_backend` (settings split under `settings/components/`).

---

## API surface

All business APIs are under **`/api/`**. Admin is at `/admin/`.

| Area | Prefix (examples) |
| --- | --- |
| Auth | `POST /api/users/v1/otp/request/`, `…/otp/verify/`, `…/token/refresh/`, `…/logout/` |
| Profile | `GET\|PATCH /api/users/v1/profile/`, phone numbers under `/api/users/profile/phone-numbers/` |
| Products | `/api/products/v1/`, wishlist, filters, campaigns |
| Cart | `POST /api/cart/add/v1/`, `GET /api/cart/v1/<uuid>/`, item update/delete, discount |
| Orders | `POST /api/orders/v1/`, `GET /api/orders/v1/my/` |
| Payments | `/api/payments/v1/orders/<id>/payment-intent/`, receipt submit |
| Addresses | `/api/addresses/` |
| Consultations | `/api/consultations/` |
| Home / magazine / reviews | `/api/home/…`, `/api/magazine/…`, `/api/reviews/…` |

Interactive docs (when `DEBUG=True` and docs are not disabled):

- Schema: `/api/schema/`
- Swagger UI: `/api/docs/`

Auth header after OTP verify:

```http
Authorization: Bearer <access_token>
```

---

## Requirements

- Python **3.12+** (Poetry)
- PostgreSQL **17** (or SQLite for local-only)
- Redis **7** (cache + Celery)
- Docker & Docker Compose (optional, recommended for full stack)

---

## Local setup

```bash
git clone <repo-url>
cd gisoo_center

cp .env.sample .env
# edit .env: DB_*, SECRET, REDIS, SMS, storage keys, etc.

poetry install
poetry shell

python manage.py migrate
python manage.py createcachetable
python manage.py createsuperuser
python manage.py runserver
```

Celery (separate terminals):

```bash
celery -A core_gisoo_backend worker -l info
celery -A core_gisoo_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Useful commands:

```bash
python manage.py sync_celery_beat
python manage.py collectstatic --noinput
python manage.py check
```

Admin: `http://127.0.0.1:8000/admin/`

---

## Docker

**Development** (`docker-compose.dev.yml`): Postgres, Redis, web (Gunicorn `:8000`), Celery worker, beat, Nginx `:80`.

```bash
cp .env.sample .env
docker compose -f docker-compose.dev.yml up --build
```

**Production** (`docker-compose.prod.yml`): same services on an internal network; Nginx bound to `127.0.0.1:81` (put a TLS terminator in front).

The image entrypoint waits for Postgres, then runs `migrate`, `createcachetable`, `sync_celery_beat`, `collectstatic`. Celery services skip that via `SKIP_ENTRYPOINT_SETUP=1`.

---

## Configuration

Copy `.env.sample` and set at least:

| Variable | Purpose |
| --- | --- |
| `DEBUG`, `ALLOWED_HOSTS`, `SECRET_API_KEY_TOKEN` | Django |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Postgres |
| `LOCAL_DB_ENABLED` | `True` → SQLite for quick local runs |
| `REDIS_URL` / `REDIS_HOST` | Cache and Celery |
| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | Celery |
| `AWS_*` / `AWS_BOTO_*` | Object storage |
| `SMS_*`, `SMS_OTP_BODY_ID`, pattern body IDs | Melipayamak |
| `PAYMENT_DESTINATION_*`, `PAYMENT_INTENT_EXPIRATION_MINUTES` | C2C destination card |
| `SENTRY_URL` | Error tracking |
| `CLIENT_URL` | Frontend origin (CORS / links) |

Do **not** commit `.env`.

---

## Checkout flow (current)

1. Add variants and/or bundles to cart (guest UUID or authenticated user).
2. Optional discount code on the cart.
3. Create order with a saved address (`POST /api/orders/v1/`). If the user has no address, the client should collect one first via `/api/addresses/`.
4. Create a **payment intent** for that order; show destination card + amount.
5. Customer uploads a receipt; staff approve or reject in admin.
6. Order status moves through preparing → shipped → delivered (SMS patterns exist for these events).

Cart pricing must include mixed line items (variant + bundle) without double-counting stock or discounts.

---

## Project layout

```text
apps/                      # domain applications
core_gisoo_backend/        # settings, URLs, WSGI/ASGI, Celery, storage
utils/                     # exceptions, pagination, helpers
templates/  static_src/
docker-compose.dev.yml
docker-compose.prod.yml
Dockerfile  nginx/
manage.py  pyproject.toml
```

---

## Development notes

- Settings are composed from `core_gisoo_backend/settings/components/`.
- Pre-commit: merge-conflict checks, large-file guard, Black (`.pre-commit-config.yaml`).
- Tests: pytest with `DJANGO_SETTINGS_MODULE=core_gisoo_backend.settings` (see `pyproject.toml`).
- Locale: Persian (`LANGUAGE_CODE=fa` in sample env). Jalali dates in admin where enabled.

---

## License

Private / proprietary unless a license file is added. Contact the maintainers before reuse.

**Author:** Mohammad Reza (`mkalhor81126@gmail.com`)
