# DocClause — Document Clause Extraction System

A system that processes PDF documents, extracts Medical/Finance/Sports clauses using OCR + AI, and presents them in a dashboard with highlighted PDFs.

---

## What This Application Does

1. **Upload PDF documents** (drag & drop or click to upload)
2. **Automatically OCR** each page and extract text
3. **Detect clauses** (Medical, Finance, Sports) using a hybrid Rule + AI engine
4. **Highlight relevant text** in the PDF with color coding:
   - 🔵 Blue = Medical
   - 🟢 Green = Finance
   - 🟡 Amber = Sports
5. **Dashboard** shows stats, charts, and lets you drill down into documents
6. **Role-based filtering** — switch between Medical Clinician / Finance Analyst / Sports Analyst views
7. **Human Review Queue** — low-confidence extractions are flagged for manual approval
8. **S3 Storage** — all data (PDFs, OCR text, extractions) is automatically synced to AWS S3

---

## Prerequisites (Install These First)

### 1. Python 3.9 or higher

- Download from: https://www.python.org/downloads/
- During installation, **check the box "Add Python to PATH"**
- To verify, open Command Prompt and type:
  ```
  python --version
  ```
  You should see something like `Python 3.9.13`

### 2. Node.js 18 or higher

- Download from: https://nodejs.org/ (choose the LTS version)
- During installation, keep all defaults
- To verify, open Command Prompt and type:
  ```
  node --version
  npm --version
  ```
  You should see something like `v18.16.0` and `9.5.1`

### 3. Tesseract OCR (Optional — for scanned image PDFs)

- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to the default location: `C:\Program Files\Tesseract-OCR\`
- This is only needed if your PDFs are scanned images. Regular text PDFs work without it.

---

## Setup Instructions (One-Time)

### Step 1: Open Command Prompt

- Press `Windows + R`, type `cmd`, press Enter
- Navigate to the project folder:
  ```
  cd "C:\Document match project"
  ```

### Step 2: Set Up Your API Keys

1. Open the file `.env.example` in the `backend` folder (use Notepad or any text editor):
   ```
   notepad backend\.env.example
   ```

2. Fill in your credentials:
   ```
   # LLM API Keys (get from https://console.groq.com — it's free)
   GROQ_API_KEY=your-groq-api-key-here

   # AWS Credentials (from AWS IAM Console)
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=document-clause-system
   ```

3. Save the file, then **rename it** from `.env.example` to `.env`:
   ```
   copy backend\.env.example backend\.env
   ```

### Step 3: Install Backend Dependencies

Run this command (it will download all required Python packages):
```
cd backend
pip install fastapi==0.104.1 uvicorn==0.24.0 "sqlalchemy==1.4.50" --no-deps
pip install "pydantic>=1.10,<2" python-multipart==0.0.6 PyMuPDF==1.23.7 python-dotenv==1.0.0 reportlab==4.0.8 aiofiles==23.2.1 httpx==0.25.2 openai==1.6.1 groq==0.4.2 boto3 Pillow
cd ..
```

> **Note:** If you see an error about `greenlet`, run this first:
> ```
> pip install "sqlalchemy==1.4.50" --no-deps
> ```
> Then run the rest of the install command again.

### Step 4: Install Frontend Dependencies

```
cd frontend
npm install
cd ..
```

### Step 5: Generate Sample PDFs (Optional)

This creates 10 sample PDFs with Medical/Finance/Sports content for testing:
```
cd backend
python sample_generator/generate_pdfs.py
cd ..
```

You should see:
```
Generating 10 sample PDFs...
  Created: healthcare_policy_2024.pdf
  Created: sports_league_contract.pdf
  ... (10 files)
Done!
```

---

## How to Run the Application

You need **two Command Prompt windows** — one for the backend, one for the frontend.

### Window 1: Start the Backend Server

1. Open Command Prompt
2. Run:
   ```
   cd "C:\Document match project\backend"
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
3. You should see:
   ```
   INFO:     Started server process
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:8000
   ```
4. **Keep this window open** — the backend is now running

### Window 2: Start the Frontend

1. Open a **new** Command Prompt window
2. Run:
   ```
   cd "C:\Document match project\frontend"
   npm run dev
   ```
3. You should see:
   ```
   VITE ready in 500 ms
   ➜  Local:   http://localhost:3000/
   ```
4. **Keep this window open** — the frontend is now running

### Step 3: Open the Application

Open your web browser (Chrome, Edge, Firefox) and go to:

```
http://localhost:3000
```

You should see the **DocClause Dashboard**.

---

## How to Use the Application

### Upload Documents

1. Click **"Upload"** in the top navigation bar
2. Drag and drop PDF files onto the upload area, or click to browse
3. The system will automatically:
   - Extract text from each page (OCR)
   - Detect Medical, Finance, and Sports clauses
   - Calculate confidence scores
   - Store everything in the database and S3
4. Processing takes a few seconds per document
5. Go back to the **Dashboard** to see the results

### Upload Sample Documents (Bulk)

If you generated sample PDFs in Step 5 of setup, you can upload them all at once:

1. Make sure the backend is running (Window 1)
2. Open a **third** Command Prompt window
3. Run:
   ```
   cd "C:\Document match project\backend"
   python upload_samples.py
   ```
4. You should see:
   ```
   Found 10 sample PDFs to upload
     Uploading: healthcare_policy_2024.pdf... OK (id=1)
     ...
   Total Documents: 10, Processed: 10, Failed: 0
   ```

### View the Dashboard

- The dashboard shows **summary cards** (total documents, processed, pending, failed)
- **Bar chart** shows how many documents contain each clause type
- **Clause cards** show document counts — click any card to drill down

### Filter by Role

- Use the **"Role"** dropdown in the top-right corner
- Select "Medical Clinician" to see only Medical clauses
- Select "Finance Analyst" to see only Finance clauses
- Select "Sports Analyst" to see only Sports clauses
- Select "All Roles" to see everything

### View Document Details

1. From the Dashboard, click a clause card (e.g., "Medical")
2. You'll see a list of documents containing that clause
3. Click any document to see its details
4. Two view modes are available:
   - **"Highlighted PDF"** — shows the actual PDF with colored highlights in the browser
   - **"Extractions"** — shows the extracted text with confidence scores and metadata

### Download Highlighted PDF

1. Open any document detail page
2. Click **"Download PDF"** button (top-right)
3. A PDF file with color-coded highlights will download
4. The highlights match the clause type colors (Blue/Green/Amber)

### Review Low-Confidence Extractions

1. Click **"Review Queue"** in the top navigation
2. You'll see extractions where the system is not confident
3. For each item, you can:
   - Click **"Approve"** if the extraction is correct
   - Click **"Reject"** if the extraction is wrong
4. Approved items get a 100% confidence score
5. Rejected items are removed from the results

### Search Within Documents

- On the document list page, use the **search box** to find specific terms
- Example: search "diabetes" within Medical documents

---

## How to Stop the Application

1. Go to **Window 1** (backend) → press `Ctrl + C`
2. Go to **Window 2** (frontend) → press `Ctrl + C`

---

## How to Restart the Application

Just follow the "How to Run" section again:
1. Start backend in Window 1
2. Start frontend in Window 2
3. Open http://localhost:3000

Your data is saved in the database — you won't lose any uploaded documents.

---

## Where is the Data Stored?

| Data | Local Location | S3 Location |
|------|---------------|-------------|
| Uploaded PDFs | `backend/uploaded_pdfs/` | `s3://document-clause-system/documents/{id}/original.pdf` |
| OCR Text | SQLite database | `s3://document-clause-system/documents/{id}/ocr/page_N.txt` |
| Extractions | SQLite database | `s3://document-clause-system/documents/{id}/extractions/{category}/page_N.json` |
| Highlighted PDFs | `backend/annotated_pdfs/` | Generated on-demand |
| Database | `backend/clause_system.db` | — |

---

## Troubleshooting

### "Failed to load dashboard"
- Make sure the backend is running (Window 1)
- Check that it says `Uvicorn running on http://127.0.0.1:8000`
- Try opening http://localhost:8000/api/health in your browser — it should show `{"status":"healthy"}`

### "pip install fails with greenlet error"
- Run: `pip install "sqlalchemy==1.4.50" --no-deps`
- Then run the rest of the install command

### "python command not found"
- Python may not be in your PATH
- Try using the full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe`
- Or reinstall Python and check "Add Python to PATH"

### "npm command not found"
- Node.js may not be installed or not in PATH
- Download and install from https://nodejs.org/

### "Port 8000 already in use"
- Another program is using port 8000
- Either close that program, or start the backend on a different port:
  ```
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
  ```
- If you change the backend port, also update `frontend/vite.config.js` to match

### Backend crashes with "Segmentation fault"
- This happens with Anaconda Python. Use the standard Python installation instead:
  ```
  "C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```

---

## Project Structure

```
Document match project/
├── README.md                    ← You are here
├── .env.example                 ← Template for API keys
├── .gitignore
│
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI application entry point
│   │   ├── models.py            ← Database tables
│   │   ├── schemas.py           ← API request/response formats
│   │   ├── config.py            ← Settings and environment variables
│   │   ├── routers/
│   │   │   ├── documents.py     ← Upload, list, download APIs
│   │   │   ├── dashboard.py     ← Dashboard stats and charts API
│   │   │   └── review.py        ← Human review queue API
│   │   └── services/
│   │       ├── ocr_service.py   ← PDF text extraction (PyMuPDF + Tesseract)
│   │       ├── rule_engine.py   ← Keyword-based clause detection
│   │       ├── llm_service.py   ← AI-powered extraction (Groq/OpenAI)
│   │       ├── extraction.py    ← Hybrid pipeline orchestrator
│   │       ├── pdf_annotator.py ← Color-coded PDF highlighting
│   │       └── s3_service.py    ← AWS S3 storage
│   ├── sample_generator/
│   │   └── generate_pdfs.py     ← Creates 10 test PDFs
│   ├── sample_pdfs/             ← Generated test PDFs
│   ├── uploaded_pdfs/           ← Your uploaded PDFs
│   ├── annotated_pdfs/          ← Highlighted PDFs (generated on demand)
│   ├── upload_samples.py        ← Script to bulk-upload sample PDFs
│   ├── sync_to_s3.py            ← Manual S3 sync script
│   ├── requirements.txt
│   ├── start.bat                ← Double-click to start backend
│   └── clause_system.db         ← SQLite database (created on first run)
│
└── frontend/
    ├── src/
    │   ├── App.jsx              ← Main application
    │   ├── App.css              ← Styling
    │   ├── api.js               ← Backend API client
    │   └── components/
    │       ├── Dashboard.jsx    ← Stats cards + bar chart
    │       ├── DocumentList.jsx ← Document table with search
    │       ├── DocumentDetail.jsx ← PDF viewer + extractions
    │       ├── UploadPanel.jsx  ← File upload interface
    │       └── ReviewQueue.jsx  ← Human review interface
    ├── package.json
    └── vite.config.js
```

---

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

Key endpoints:
- `POST /api/documents/upload` — Upload a PDF
- `GET /api/documents/` — List all documents
- `GET /api/documents/{id}` — Get document details
- `GET /api/documents/{id}/annotated?role=Medical` — Download highlighted PDF
- `GET /api/dashboard/stats` — Dashboard statistics
- `GET /api/dashboard/documents-by-clause?category=Medical` — Filter by clause
- `GET /api/review/` — Review queue
- `PUT /api/review/{id}` — Approve/reject a review item

---

## Cost Estimate (AWS)

| Service | 10 Documents (POC) | 1000 Documents (Production) |
|---------|-------------------|----------------------------|
| S3 Storage | < $0.01 | ~$0.50 |
| Groq LLM (free tier) | $0.00 | $0.00 |
| **Total** | **< $0.01** | **~$0.50** |

Well within the $100 budget. The main cost driver would be if you switch to OpenAI or AWS Bedrock for the LLM.
