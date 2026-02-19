# TOXIC LYRICALLY — Official Site

Django web application for **TOXIC LYRICALLY** (MBOKADOBA): music catalog, tour dates, merch, and artist portfolio.

## Features

- **Music** — Albums and tracks with YouTube embeds and streaming links
- **Shows** — Tour dates with venues and ticket links
- **Merch** — Shop items with image galleries, linking to external shop
- **Footer** — Configurable social links, logo, and YouTube embed (admin singleton)
- Responsive layout (Tailwind CSS), HTMX for dynamic updates, parallax and scroll effects

## Tech Stack

- **Backend:** Django 5.x, PostgreSQL (prod) / SQLite (local)
- **Frontend:** Tailwind CSS, HTMX, vanilla JS
- **Admin:** Django Unfold
- **Deploy:** Docker, Gunicorn, Nginx, WhiteNoise

## Local setup

1. **Clone and enter project**
   ```bash
   cd TOXIC
   ```

2. **Create virtualenv and install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. **Build Tailwind CSS**
   ```bash
   npm install
   npm run build
   ```

4. **Database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run server**
   ```bash
   python manage.py runserver
   ```
   Open http://127.0.0.1:8000

## Docker

```bash
docker-compose up
```

- App: http://localhost:8000  
- Admin: http://localhost:8000/admin/  
- Nginx (if used): port 80  

Set `DEBUG=0` and provide `SECRET_KEY` and `ALLOWED_HOSTS` for production.

## Environment variables

| Variable        | Description                          | Default (dev)        |
|----------------|--------------------------------------|----------------------|
| `SECRET_KEY`   | Django secret key                    | (insecure dev key)   |
| `DEBUG`        | Debug mode (0/1)                     | 1                    |
| `ALLOWED_HOSTS`| Comma-separated hosts                | localhost,127.0.0.1  |
| `DATABASE_URL` | DB URL (PostgreSQL or SQLite)        | SQLite path          |
| `REDIS_URL`    | Redis URL (optional, for future cache) | —                  |

## Project layout

```
TOXIC/
├── toxic_project/     # Django settings, urls, wsgi
├── web/               # Main app: models, views, admin, utils, templatetags
├── templates/         # Base + web templates and partials
├── static/            # CSS (Tailwind input/output), images
├── media/             # Uploads (covers, shop, footer) — gitignored
├── nginx/             # Nginx config for production
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── tailwind.config.js
```

## Tests

```bash
python manage.py test web
```

## License

Private — TOXIC LYRICALLY / MBOKADOBA.
