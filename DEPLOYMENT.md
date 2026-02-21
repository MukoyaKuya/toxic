# Deployment Guide

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
