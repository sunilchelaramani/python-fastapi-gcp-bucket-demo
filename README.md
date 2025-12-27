# FastAPI GCP Bucket Demo

A FastAPI application that provides REST API endpoints to interact with Google Cloud Storage buckets. The application is containerized for Cloud Run deployment and uses service account authentication.

## Features

- **Health Check**: Verify API status
- **Upload Files**: Upload files to GCP Cloud Storage bucket
- **Download Files**: Download files from GCP Cloud Storage bucket
- **Delete Files**: Delete files from GCP Cloud Storage bucket
- **File Validation**: Configurable file size limits and type restrictions
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes

## Prerequisites

- Python 3.11+
- Google Cloud Platform account
- GCP Cloud Storage bucket
- Docker (for containerization)
- Google Cloud SDK (for deployment)

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd python-fastapi-gcp-bucket-demo
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example environment file and update with your values:

```bash
cp .env.example .env
```

Edit `.env` and set your GCP bucket name:

```env
GCP_BUCKET_NAME=your-bucket-name
MAX_FILE_SIZE=10485760  # 10MB in bytes
ALLOWED_FILE_TYPES=jpg,png,pdf  # Optional: comma-separated list
```

### 4. Local Development

For local development, you'll need to authenticate with GCP. You can either:

**Option A: Use Application Default Credentials**
```bash
gcloud auth application-default login
```

**Option B: Use Service Account Key File**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

Then run the application:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### POST /upload
Upload a file to the GCP bucket.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File in form field named `file`

**Response:**
```json
{
  "message": "File uploaded successfully",
  "data": {
    "filename": "example.pdf",
    "bucket": "your-bucket-name",
    "size": 1024,
    "content_type": "application/pdf"
  }
}
```

### GET /download/{filename}
Download a file from the GCP bucket.

**Parameters:**
- `filename`: Name of the file to download

**Response:**
- Returns the file as a streaming response with appropriate content type

### DELETE /delete/{filename}
Delete a file from the GCP bucket.

**Parameters:**
- `filename`: Name of the file to delete

**Response:**
```json
{
  "message": "File deleted successfully",
  "data": {
    "message": "File 'example.pdf' deleted successfully",
    "filename": "example.pdf"
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "File size (15728640 bytes) exceeds maximum allowed size (10485760 bytes)"
}
```

### 404 Not Found
```json
{
  "detail": "File 'example.pdf' not found in bucket"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to upload file: <error message>"
}
```

## Docker Build

Build the Docker image:

```bash
docker build -t gcp-bucket-api .
```

Run the container:

```bash
docker run -p 8080:8080 --env-file .env gcp-bucket-api
```

## Cloud Run Deployment

### 1. Build and push to Google Container Registry

```bash
# Set your project ID
export PROJECT_ID=your-project-id
export SERVICE_NAME=gcp-bucket-api

# Build the image
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Push to GCR
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account your-service-account@your-project.iam.gserviceaccount.com \
  --set-env-vars GCP_BUCKET_NAME=your-bucket-name,MAX_FILE_SIZE=10485760
```

### 3. Service Account Permissions

The Cloud Run service account needs the following IAM roles or permissions:

- `roles/storage.objectCreator` (for upload) OR `storage.objects.create`
- `roles/storage.objectViewer` (for download) OR `storage.objects.get`
- `roles/storage.objectAdmin` (for delete) OR `storage.objects.delete`

You can assign these roles using:

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
  --role="roles/storage.objectAdmin"
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GCP_BUCKET_NAME` | Yes | - | Name of the GCP Cloud Storage bucket |
| `MAX_FILE_SIZE` | No | 10485760 | Maximum file size in bytes (10MB) |
| `ALLOWED_FILE_TYPES` | No | None | Comma-separated list of allowed file extensions (e.g., "jpg,png,pdf") |
| `PORT` | No | 8080 | Port number for the application |

## Testing

### Using curl

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Upload File:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@example.pdf"
```

**Download File:**
```bash
curl -O "http://localhost:8000/download/example.pdf"
```

**Delete File:**
```bash
curl -X DELETE "http://localhost:8000/delete/example.pdf"
```

### Using Python requests

```python
import requests

# Upload
with open('example.pdf', 'rb') as f:
    response = requests.post('http://localhost:8000/upload', files={'file': f})
    print(response.json())

# Download
response = requests.get('http://localhost:8000/download/example.pdf')
with open('downloaded.pdf', 'wb') as f:
    f.write(response.content)

# Delete
response = requests.delete('http://localhost:8000/delete/example.pdf')
print(response.json())
```

## Project Structure

```
python-fastapi-gcp-bucket-demo/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app and routes
│   ├── config.py            # Configuration from environment
│   └── storage.py           # GCP Storage operations
├── .env.example             # Example environment variables
├── .env                     # Actual environment file (gitignored)
├── .gitignore
├── requirements.txt         # Python dependencies
├── Dockerfile              # Cloud Run container
└── README.md               # This file
```

## License

This project is provided as-is for demonstration purposes.

