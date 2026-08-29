# KSC Wholesale Chicken — Flask Web Application

A real Python (Flask) web app for KSC Wholesale Chicken — not a static site.
Content (categories, cuts, business info) is defined as plain Python data in
`app.py`, rendered through Jinja2 templates, with a working order-enquiry
form backed by SQLite.

## Run it locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000**

## What's included

- `app.py` — Flask app: routes, business data (categories/cuts/address), and
  the SQLite-backed order enquiry endpoint.
- `templates/index.html` — main site (Jinja2, loops over the Python data).
- `templates/orders.html` — plain internal listing of submitted enquiries at
  `/orders` (no login — add auth before exposing this publicly).
- `static/css/style.css` — full stylesheet (color system, layout, logo).
- `static/js/main.js` — nav behaviour, scroll reveal, cut-photo tab swapping.
- `static/images/` — product photography, cropped and cleaned from KSC's own
  promotional poster.

## Editing content

Everything text-based — category lists, cut descriptions, phone number,
address — lives in the `BUSINESS`, `CUTS`, and `CATEGORIES` dictionaries at
the top of `app.py`. Change the data there; the templates pick it up
automatically.

## Before deploying publicly

- Change `app.config["SECRET_KEY"]` in `app.py` to a real secret.
- Put a login in front of `/orders`, or remove the route.
- Run behind a real WSGI server (gunicorn/uwsgi) instead of `python app.py`.
- Consider swapping the SQLite file for a managed database if order volume
  grows.

## Photography note

The product photos are cropped from KSC's own existing promotional poster —
they're real, but modest resolution since they came from a phone-screenshot
graphic. For a sharper site, replace the files in `static/images/` with
higher-resolution originals (same filenames, or update the paths in
`app.py`).
