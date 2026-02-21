#!/bin/bash
# Upload local media files to Google Cloud Storage for production
# Usage: ./scripts/upload-media-to-gcs.sh BUCKET_NAME [--public]

set -e
BUCKET="${1:?Usage: $0 BUCKET_NAME [--public]}"
PUBLIC="${2:-}"

MEDIA_DIR="$(cd "$(dirname "$0")/.." && pwd)/media"
if [ ! -d "$MEDIA_DIR" ]; then
    echo "media/ folder not found at $MEDIA_DIR"
    exit 1
fi

echo "Uploading media from $MEDIA_DIR to gs://$BUCKET/ ..."
if [ "$PUBLIC" = "--public" ]; then
    gsutil -m cp -r -a public-read "$MEDIA_DIR"/* gs://"$BUCKET"/
else
    gsutil -m cp -r "$MEDIA_DIR"/* gs://"$BUCKET"/
fi

echo "Done. To make bucket publicly readable: gsutil iam ch allUsers:objectViewer gs://$BUCKET"
