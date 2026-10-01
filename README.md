# Simple Point of Sale

A point-of-sale web app for small shops and field sales teams. Cashiers log in
from any browser, tap a product to sell it, and get an instant confirmation over
a WebSocket. Every sale is tied to the cashier who made it, and a sale can only
be undone with a written reason that is kept for later review.

Built with Django and Django Channels.

## Features

- **Instant sales** – the till page records sales over a WebSocket, so there is
  no page reload between customers.
- **Prices come from the catalogue** – the browser only says *which* product was
  sold; the server applies the price, so a tampered page cannot record a sale at
  a made-up amount.
- **Accountable cancellations** – cancelling a sale requires a reason. The sale
  moves to a cancelled-sales history with the reason, price and product picture.
- **Per-cashier records** – each cashier sees their own sales and cancellations;
  managers see everything in the Django admin.
- **Sale snapshots** – a sale keeps the product name, price and picture it was
  sold with, even if the product is edited later.

## How it works

```
Browser (till.js) ──WebSocket /ws/sales/──▶ SalesConsumer ──▶ Sale.record()
       │                                        │
       └── HTTP pages (Django views) ◀──────────┴── Product, Sale, CancelledSale
```

- `sales/consumers.py` accepts WebSocket connections only from logged-in users
  on an allowed host, and records each sale through `Sale.record()`.
- `sales/models.py` holds the business rules: recording a sale at catalogue
  price, and cancelling it atomically into `CancelledSale`.
- `pointofsaleproject/asgi.py` routes HTTP to Django and WebSockets to Channels.

## Getting started

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://localhost:8000/admin/ to add products and cashier accounts, then
log in at http://localhost:8000/ to use the till.

`runserver` serves WebSockets too, because Daphne is installed as the
development server.

## Configuration

Settings are read from environment variables. With none set, the app runs in
local development mode. See [`.env.example`](.env.example) for the full list;
the important ones for a deployment are `DJANGO_DEBUG=false`,
`DJANGO_SECRET_KEY` and `DJANGO_ALLOWED_HOSTS`. The app refuses to start with
debug off and no secret key.

## Development

```bash
ruff check .               # lint
ruff format .              # format
python manage.py test      # run the test suite
```

The same checks run on every push through GitHub Actions.
