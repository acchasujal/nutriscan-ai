# Workflow

## Step 1: Frontend

* Upload image
* Convert to base64
* Send to backend

## Step 2: Backend

* Receive image
* Send to Gemini API
* Return structured JSON

## Step 3: Frontend Rendering

* Parse JSON
* Display:

  * Health score
  * Nutrition
  * Advice

## Step 4: Storage

* Save result in localStorage

## Step 5: Deployment

* Push to GitHub
* Deploy via Cloud Run:
  gcloud run deploy --source . --region asia-south1

## Step 6: Evaluation

* AI grader scans:

  * Tests
  * Security
  * Accessibility
