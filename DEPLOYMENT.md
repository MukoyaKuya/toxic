To deploy

## Database Content (Albums, Shop, Footer, Tour, etc.)

To push your local content (albums, shop items, footer settings, tour dates, etc.) to production:

### 1. Export from Local Dev

Run from your project root:

```powershell
python manage.py export_production_data
```

This creates `data/production_data.json` with all web app content. **Admin users are not exported** — you create those in production separately.

### 2. Load into Production

Connect to your production database (Cloud SQL or Neon) and run loaddata. Options:

**Option A: Cloud SQL Proxy (recommended)**

```powershell
# Start the proxy (in a separate terminal)
cloud_sql_proxy -instances=PROJECT:REGION:INSTANCE=tcp:5432

# In another terminal, with DATABASE_URL pointing to localhost:5432
$env:DATABASE_URL = "postgres://user:pass@localhost:5432/dbname"
python manage.py loaddata data/production_data.json
```

**Option B: Direct connection**

```powershell
$env:DATABASE_URL = "postgres://user:pass@host:5432/dbname"
python manage.py loaddata data/production_data.json
```

**Option C: Via Cloud Run Job or Cloud Shell**

Upload `data/production_data.json` and run the loaddata command in an environment that can reach the production database.

### 3. Create Admin User in Production

After loading data, create your admin account:

```powershell
python manage.py createsuperuser
```

Enter username, email, and password when prompted.

---

## Media Files (Images, Audio, Thumbnails)

Album covers, shop images, and audio are stored in the `media/` folder locally. Cloud Run does **not** persist files, so media must be stored in **Google Cloud Storage (GCS)**.

### 1. Create a GCS Bucket

In [Google Cloud Console](https://console.cloud.google.com/storage):

1. **Create bucket** → name e.g. `gen-lang-client-0549116861-toxic-media`
2. **Region**: `europe-west1` (same as Cloud Run)
3. **Access control**: Uniform
4. **Public access**: Allow public access (so images can load on the site)

### 2. Upload Media to the Bucket

From your project root (where `media/` exists):

**PowerShell (Windows):**
```powershell
.\scripts\upload-media-to-gcs.ps1 -Bucket "gen-lang-client-0549116861-toxic-media" -Public
```

**Bash/Mac:**
```bash
chmod +x scripts/upload-media-to-gcs.sh
./scripts/upload-media-to-gcs.sh gen-lang-client-0549116861-toxic-media --public
```

Or manually with gsutil:
```bash
gsutil -m cp -r -a public-read media/* gs://YOUR_BUCKET_NAME/
```

### 3. Make Bucket Publicly Readable

If images still don’t load:

```bash
gsutil iam ch allUsers:objectViewer gs://YOUR_BUCKET_NAME
```

### 4. Configure Cloud Build Trigger

1. Go to [Cloud Build → Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Edit your `toxic` trigger
3. Add substitution variable: `_GCS_BUCKET` = `gen-lang-client-0549116861-toxic-media` (your bucket name)
4. Save

### 5. Redeploy

Push a commit or run the trigger manually. Cloud Run will use the GCS bucket for media URLs.
