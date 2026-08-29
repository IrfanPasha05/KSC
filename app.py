"""
KSC Wholesale Chicken — Flask web application.

Run locally:
    python -m venv venv
    source venv/bin/activate      (Windows: venv\\Scripts\\activate)
    pip install -r requirements.txt
    python app.py

Then open http://127.0.0.1:5000
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, g

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "orders.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "ksc-dev-secret-change-me"  # replace before real deployment


# ---------------------------------------------------------------------------
# Site content — kept as plain Python data so it's easy to edit without
# touching template markup.
# ---------------------------------------------------------------------------

BUSINESS = {
    "name": "KSC Wholesale Chicken",
    "proprietor": "Mohammed Zaki DZ",
    "phone_display": "99024 41027",
    "phone_tel": "+919902441027",
    "whatsapp": "https://wa.me/919902441027",
    "address_lines": [
        '#6, "B" Cooks Road',
        "Thimmiah Road Cross",
        "Bangalore 560051",
    ],
    "address_full": '#6, "B" Cooks Road, Thimmiah Road Cross, Bangalore 560051',
}

# Order matters — drives both the tab buttons and the default view.
CUT_ORDER = ["whole", "breast", "drumstick", "wing", "organs", "special"]

CUTS = {
    "whole": {
        "tag": "01 / Whole Bird",
        "name": "Whole Chicken",
        "label": "Whole Bird",
        "img": "whole-chicken.jpg",
        "desc": "Skin-on and dressed to order — plain, skinless, curry cut or "
                "biryani cut. The standard for home-style gravies and "
                "large-format cooking.",
    },
    "breast": {
        "tag": "02 / Breast",
        "name": "Breast",
        "label": "Breast",
        "img": "breast.jpg",
        "desc": "Lean, boneless-ready cut. Sliced or whole, it's the go-to "
                "for grills, tandoori and stir-fry lines.",
    },
    "drumstick": {
        "tag": "03 / Leg",
        "name": "Drumstick & Leg",
        "label": "Drumstick",
        "img": "drumstick.jpg",
        "desc": "The classic leg piece. Bone-in for flavour, portioned for "
                "fry, roast or curry service.",
    },
    "wing": {
        "tag": "04 / Wing",
        "name": "Wings",
        "label": "Wings",
        "img": "wings.jpg",
        "desc": "Whole wings, built for high-heat cooking: fry, grill or "
                "tandoor.",
    },
    "organs": {
        "tag": "05 / Organs",
        "name": "Heart & Organs",
        "label": "Organs",
        "img": "heart.jpg",
        "desc": "Liver, gizzard and heart — cleaned and ready. Full-flavour "
                "cuts for stocks, stir-fries and regional specialities.",
    },
    "special": {
        "tag": "06 / Special Order",
        "name": "Marinated & Special Cuts",
        "label": "Special Order",
        "img": "custom-cut.jpg",
        "desc": "Tandoori and grill-cut marinades, made to your recipe or "
                "ours — ready to hit the coals or the tandoor.",
    },
}

# Per-item thumbnail photos shown next to each line in the order-sheet
# categories. Items not listed here simply show a plain bullet — send more
# photos and add them here as they come in.
ITEM_PHOTOS = {
    "Whole Chicken": "whole-chicken.jpg",
    "Skinless Chicken": "skinless-chicken.jpg",
    "Curry Cut": "curry-cut.jpg",
    "Biryani Cut": "biryani-cut.jpg",
    "Breast": "breast.jpg",
    "Boneless Breast": "boneless-breast.jpg",
    "Boneless Thigh": "boneless-thigh.jpg",
    "Thigh": "thigh.jpg",
    "Leg": "leg.jpg",
    "Drumstick": "drumstick.jpg",
    "Wings": "wings.jpg",
    "Neck": "neck.jpg",
    "Back": "back.jpg",
    "Soup Bones": "soup-bones.jpg",
    "Boneless Chicken": "boneless-chicken.jpg",
    "Chicken Mince (Keema)": "chicken-mince.jpg",
    "Chicken Strips": "chicken-strips.jpg",
    "Chicken Cubes": "chicken-cubes.jpg",
    "Heart": "heart.jpg",
    "Custom Cut": "custom-cut.jpg",
    "Tandoori Cut": "tandoori-cut.jpg",
    "Grill Cut": "grill-cut.jpg",
    "Biryani Special Cut": "biryani-special-cut.jpg",
    # Still needed (no clean photo yet — watermarked stock excluded):
    # "Lollipop", "Liver", "Gizzard", "BBQ Cut"
}

CATEGORIES = [
    {
        "num": "01",
        "title": "Whole Chicken",
        "img": "whole-chicken.jpg",
        "wide": False,
        "products": ["Whole Chicken", "Skinless Chicken", "Curry Cut", "Biryani Cut"],
    },
    {
        "num": "02",
        "title": "Chicken Cuts",
        "img": "custom-cut.jpg",
        "wide": True,
        "products": [
            "Breast", "Boneless Breast", "Thigh", "Boneless Thigh", "Leg",
            "Drumstick", "Wings", "Lollipop", "Neck", "Back", "Soup Bones",
        ],
    },
    {
        "num": "03",
        "title": "Boneless & Processed",
        "img": "boneless-chicken.jpg",
        "wide": False,
        "products": ["Boneless Chicken", "Chicken Mince (Keema)", "Chicken Strips", "Chicken Cubes"],
    },
    {
        "num": "04",
        "title": "Chicken Organs",
        "img": "heart.jpg",
        "wide": False,
        "products": ["Liver", "Gizzard", "Heart"],
    },
    {
        "num": "05",
        "title": "Special Orders",
        "img": "grill-cut.jpg",
        "wide": False,
        "products": ["Custom Cut", "BBQ Cut", "Tandoori Cut", "Grill Cut", "Biryani Special Cut"],
    },
]

CUT_CHOICES = [CUTS[k]["name"] for k in CUT_ORDER]


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                cut TEXT NOT NULL,
                quantity TEXT,
                notes TEXT
            )
            """
        )
        db.commit()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template(
        "index.html",
        business=BUSINESS,
        categories=CATEGORIES,
        cuts=CUTS,
        cut_order=CUT_ORDER,
        item_photos=ITEM_PHOTOS,
        year=datetime.now().year,
    )


@app.route("/order", methods=["POST"])
def place_order():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    cut = request.form.get("cut", "").strip()
    quantity = request.form.get("quantity", "").strip()
    notes = request.form.get("notes", "").strip()

    if not name or not phone or not cut:
        flash("Please fill in your name, phone number and the cut you need.", "error")
        return redirect(url_for("home") + "#order")

    db = get_db()
    db.execute(
        "INSERT INTO orders (created_at, name, phone, cut, quantity, notes) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), name, phone, cut, quantity, notes),
    )
    db.commit()

    flash(f"Thanks {name} — we've got your enquiry and will call you on {phone} shortly.", "success")
    return redirect(url_for("home") + "#order")


@app.route("/orders")
def view_orders():
    """
    Very basic internal view of submitted enquiries.
    NOTE: this has no authentication — add login protection before putting
    this route on a public server.
    """
    db = get_db()
    rows = db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    return render_template("orders.html", orders=rows, business=BUSINESS)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
else:
    # Also make sure the table exists when run via `flask run` / a WSGI server.
    init_db()
