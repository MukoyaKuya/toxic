# Codebase Improvement Recommendations

## 🔒 Security Improvements

### 1. Security Headers & HTTPS
**Priority: HIGH**

Add security headers in `settings.py`:
```python
# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

**Action:** Add `django-security` or configure manually in settings.py

### 2. Content Security Policy (CSP)
**Priority: HIGH**

Add CSP headers to prevent XSS attacks:
```python
# Install django-csp
MIDDLEWARE = [
    # ... existing middleware ...
    'csp.middleware.CSPMiddleware',
]

CSP_DEFAULT_SRC = ["'self'"]
CSP_SCRIPT_SRC = ["'self'", "https://unpkg.com", "https://www.youtube.com"]
CSP_STYLE_SRC = ["'self'", "https://fonts.googleapis.com"]
CSP_FONT_SRC = ["'self'", "https://fonts.gstatic.com"]
CSP_IMG_SRC = ["'self'", "data:", "https:"]
CSP_FRAME_SRC = ["'self'", "https://www.youtube-nocookie.com"]
```

### 3. URL Validation
**Priority: MEDIUM**

Add URL validation to models to prevent malicious links:
```python
# In web/models.py
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

def validate_youtube_url(value):
    if value and 'youtube.com' not in value and 'youtu.be' not in value:
        raise ValidationError('Please enter a valid YouTube URL')

# Apply to YouTube fields
youtube_link = models.URLField(
    blank=True,
    validators=[validate_youtube_url],
    help_text="YouTube link for the release"
)
```

### 4. Rate Limiting
**Priority: MEDIUM**

Add rate limiting to prevent abuse:
```python
# Install django-ratelimit
# In views.py
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='GET')
def contact(request):
    # ...
```

### 5. Input Sanitization
**Priority: LOW**

Add bleach for HTML sanitization if allowing user-generated content:
```python
# requirements.txt
bleach>=6.0
```

---

## 🚀 Performance Improvements

### 6. Database Indexing
**Priority: HIGH**

Add indexes to frequently queried fields:
```python
# In web/models.py
class TourDate(models.Model):
    date = models.DateTimeField(db_index=True)  # Already ordered by date
    is_sold_out = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['date', 'is_sold_out']),
        ]

class Album(models.Model):
    release_date = models.DateField(db_index=True)
    
class ShopItem(models.Model):
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0, db_index=True)
```

### 7. Redis Caching
**Priority: HIGH**

Redis is configured but not used. Implement caching:
```python
# In settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}

# In views.py
from django.views.decorators.cache import cache_page
from django.core.cache import cache

@cache_page(60 * 15)  # Cache for 15 minutes
def index(request):
    # ...

# Or use low-level caching for expensive queries
def music(request):
    cache_key = 'all_albums'
    albums = cache.get(cache_key)
    if albums is None:
        albums = Album.objects.all().order_by('-release_date')
        cache.set(cache_key, albums, 60 * 30)  # 30 minutes
    return render(request, 'web/music.html', {'albums': albums})
```

### 8. Database Query Optimization
**Priority: MEDIUM**

Improve query efficiency:
```python
# In views.py - already using prefetch_related, but can optimize more
def music(request):
    albums = Album.objects.select_related().prefetch_related(
        'tracks'
    ).order_by('-release_date')
    return render(request, 'web/music.html', {'albums': albums})

def album_detail(request, album_id):
    album = get_object_or_404(
        Album.objects.prefetch_related('tracks'),
        pk=album_id
    )
    # ...
```

### 9. Image Optimization
**Priority: MEDIUM**

Add image optimization for uploaded files:
```python
# Install Pillow (already installed) and add image processing
# Consider adding django-imagekit or django-versatileimagefield
# Or use a service like Cloudinary/ImageKit

# Add to models.py
from django.core.files.storage import default_storage

class Album(models.Model):
    # Add image validation
    def clean(self):
        if self.cover_art:
            # Validate file size (e.g., max 5MB)
            if self.cover_art.size > 5 * 1024 * 1024:
                raise ValidationError('Image file too large (max 5MB)')
```

### 10. Pagination
**Priority: MEDIUM**

Add pagination for large lists:
```python
# In views.py
from django.core.paginator import Paginator

def music(request):
    albums_list = Album.objects.all().order_by('-release_date')
    paginator = Paginator(albums_list, 12)  # 12 per page
    page_number = request.GET.get('page')
    albums = paginator.get_page(page_number)
    return render(request, 'web/music.html', {'albums': albums})
```

---

## 🧪 Testing Improvements

### 11. Fix Broken Tests
**Priority: HIGH**

Tests reference `latest_album` which doesn't exist:
```python
# In web/tests.py - fix test_index_view
def test_index_view(self):
    response = self.client.get(reverse('index'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'web/index.html')
    # Fix: Check for 'latest_releases' instead
    self.assertIn('latest_releases', response.context)
```

### 12. Add Test Coverage
**Priority: MEDIUM**

Add tests for:
- `utils.py` (YouTube URL extraction)
- Error cases (404, invalid URLs)
- Admin functionality
- Model validation
- Context processors

```python
# web/tests/test_utils.py
from django.test import TestCase
from web.utils import extract_youtube_embed_url

class UtilsTests(TestCase):
    def test_extract_youtube_watch_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = extract_youtube_embed_url(url)
        self.assertIn("youtube-nocookie.com/embed/dQw4w9WgXcQ", result)
    
    def test_extract_youtube_shorts_url(self):
        url = "https://www.youtube.com/shorts/abc123"
        result = extract_youtube_embed_url(url)
        self.assertIsNotNone(result)
    
    def test_invalid_url_returns_none(self):
        url = "https://example.com"
        result = extract_youtube_embed_url(url)
        self.assertIsNone(result)
```

### 13. Add Integration Tests
**Priority: LOW**

Test full user flows (browse music → view album → view tour dates)

---

## 📝 Code Quality Improvements

### 14. Code Organization
**Priority: MEDIUM**

Fix import organization in `views.py`:
```python
# Move imports to top
import logging
import re
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Prefetch
from .models import Album, Track, TourDate, ShopItem, ShopItemImage
from .utils import extract_youtube_embed_url

logger = logging.getLogger(__name__)
```

### 15. Add Type Hints
**Priority: LOW**

Improve code maintainability:
```python
from typing import Optional
from django.http import HttpRequest, HttpResponse

def extract_youtube_embed_url(url: Optional[str]) -> Optional[str]:
    # ...
```

### 16. Add Docstrings
**Priority: LOW**

Document functions and classes:
```python
def extract_youtube_embed_url(url: Optional[str]) -> Optional[str]:
    """
    Convert YouTube watch URL, Shorts URL, or other formats to embed URL.
    
    Args:
        url: YouTube URL in various formats (watch, shorts, youtu.be, embed)
    
    Returns:
        Embed URL string or None if URL is invalid or not a video link
    
    Examples:
        >>> extract_youtube_embed_url("https://www.youtube.com/watch?v=abc123")
        "https://www.youtube-nocookie.com/embed/abc123?rel=0"
    """
```

### 17. Error Handling
**Priority: MEDIUM**

Add custom error pages:
```python
# Create templates/404.html and templates/500.html
# In toxic_project/urls.py (for development)
if settings.DEBUG:
    from django.views.static import serve
    # ... existing code ...
else:
    handler404 = 'web.views.handler404'
    handler500 = 'web.views.handler500'

# In web/views.py
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)
```

### 18. Logging Configuration
**Priority: MEDIUM**

Add proper logging:
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'web': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

## 🔍 SEO & Accessibility Improvements

### 19. Meta Tags & Open Graph
**Priority: MEDIUM**

Add SEO meta tags to base template:
```html
<!-- In templates/base.html -->
<head>
    <!-- Existing tags -->
    <meta name="description" content="{% block meta_description %}Official site for TOXIC LYRICALLY (MBOKADOBA) - Music, Tour Dates, Merch{% endblock %}">
    <meta name="keywords" content="{% block meta_keywords %}TOXIC LYRICALLY, MBOKADOBA, music, hip hop{% endblock %}">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{% block og_title %}TOXIC LYRICALLY | Official Site{% endblock %}">
    <meta property="og:description" content="{% block og_description %}Official site for TOXIC LYRICALLY{% endblock %}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{{ request.build_absolute_uri }}">
    {% block og_image %}<meta property="og:image" content="{% static 'images/og-image.jpg' %}">{% endblock %}
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{% block twitter_title %}TOXIC LYRICALLY{% endblock %}">
</head>
```

### 20. Sitemap & Robots.txt
**Priority: LOW**

Add sitemap for search engines:
```python
# Install django.contrib.sitemaps
# In settings.py
INSTALLED_APPS = [
    # ... existing apps ...
    'django.contrib.sitemaps',
]

# Create web/sitemaps.py
from django.contrib.sitemaps import Sitemap
from .models import Album

class AlbumSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8
    
    def items(self):
        return Album.objects.all()
    
    def lastmod(self, obj):
        return obj.release_date

# In toxic_project/urls.py
from django.contrib.sitemaps.views import sitemap
from web.sitemaps import AlbumSitemap

sitemaps = {
    'albums': AlbumSitemap,
}

urlpatterns = [
    # ... existing patterns ...
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
]

# Create static/robots.txt
User-agent: *
Allow: /
Sitemap: https://yourdomain.com/sitemap.xml
```

### 21. Alt Text Validation
**Priority: LOW**

Ensure all images have alt text (add to admin help text and validation)

---

## 🐳 DevOps Improvements

### 22. Health Checks
**Priority: MEDIUM**

Add health check endpoint:
```python
# In web/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # Check database
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'healthy'}, status=200)
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)

# In web/urls.py
path('health/', views.health_check, name='health_check'),

# In docker-compose.yml
services:
  web:
    # ... existing config ...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 23. Production Docker Compose
**Priority: MEDIUM**

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn toxic_project.wsgi:application --bind 0.0.0.0:8000 --workers 4
    environment:
      - DEBUG=0
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - DATABASE_URL=${DATABASE_URL}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 24. Environment Variable Validation
**Priority: MEDIUM**

Add startup validation:
```python
# In settings.py
import sys

# Validate required environment variables in production
if not DEBUG:
    required_vars = ['SECRET_KEY', 'DATABASE_URL', 'ALLOWED_HOSTS']
    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)
```

### 25. Nginx Security Headers
**Priority: MEDIUM**

Update `nginx/nginx.conf`:
```nginx
server {
    # ... existing config ...
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
```

---

## 📚 Documentation Improvements

### 26. README.md
**Priority: HIGH**

Create comprehensive README:
```markdown
# TOXIC LYRICALLY - Official Website

Django web application for artist portfolio, music catalog, tour dates, and merch.

## Features
- Music catalog with albums and tracks
- Tour dates management
- Merch/shop integration
- YouTube video embedding
- Responsive design with Tailwind CSS

## Setup

### Local Development
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Run server: `python manage.py runserver`

### Docker
`docker-compose up`

## Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to 0 in production
- `DATABASE_URL`: PostgreSQL connection string
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
```

### 27. API Documentation
**Priority: LOW**

Document any API endpoints if added in future

---

## 🎨 Frontend Improvements

### 28. Lazy Loading Images
**Priority: MEDIUM**

Add lazy loading for images:
```html
<img src="..." loading="lazy" alt="...">
```

### 29. Service Worker / PWA
**Priority: LOW**

Consider adding PWA capabilities for offline support

### 30. Analytics Integration
**Priority: LOW**

Add Google Analytics or similar (privacy-compliant)

---

## Summary of Priority Actions

**Immediate (This Week):**
1. Fix broken tests (#11)
2. Add security headers (#1)
3. Add database indexes (#6)
4. Create README.md (#26)

**Short Term (This Month):**
5. Implement Redis caching (#7)
6. Add error handling (#17)
7. Add logging (#18)
8. Add health checks (#22)
9. Add SEO meta tags (#19)

**Long Term (Next Quarter):**
10. Add comprehensive test coverage (#12)
11. Add pagination (#10)
12. Image optimization (#9)
13. Add sitemap (#20)

---

## Additional Recommendations

- **Monitoring**: Consider adding Sentry for error tracking
- **Backup**: Set up automated database backups
- **CDN**: Consider CloudFlare or similar for static assets
- **Email**: Configure email backend for contact form (if implemented)
- **CI/CD**: Add GitHub Actions or similar for automated testing/deployment
