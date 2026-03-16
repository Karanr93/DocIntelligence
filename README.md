# DocClause - Document Clause Extraction System

A system that processes PDF documents, extracts Medical/Finance/Sports clauses using OCR + AI, and presents them in a dashboard with highlighted PDFs.

---

## What This Application Does

1. **Upload PDF documents** (drag & drop or click to upload)
2. **Automatically OCR** each page and extract text
3. **Detect clauses** (Medical, Finance, Sports) using a hybrid Rule + AI engine
4. **Highlight relevant text** in the PDF with color coding:
   - Blue = Medical
   - Green = Finance
   - Amber = Sports
5. **Dashboard** shows stats, charts, and lets you drill down into documents
6. **Role-based filtering** - switch between Medical Clinician / Finance Analyst / Sports Analyst views
7. **Human Review Queue** - low-confidence extractions are flagged for manual approval
8. **S3 Storage** - all data (PDFs, OCR text, extractions) is automatically synced to AWS S3

---

## Two Ways to Run

| Mode | LLM Provider | Data Privacy | Cost | Best For |
|------|-------------|-------------|------|----------|
| **Local** | Groq (free) or Ollama (offline) | Data goes to Groq servers (or stays local with Ollama) | Free | Development, testing |
| **AWS (Production)** | Bedrock (Claude Sonnet) | Data stays in your AWS account | ~$10/month | Demos, sharing with others |

---

## Part 1: Running Locally

### Prerequisites

#### 1. Python 3.9 or higher
- Download from: https://www.python.org/downloads/
- During installation, **check the box "Add Python to PATH"**
- Verify:
  ```
  python --version
  ```

#### 2. Node.js 18 or higher
- Download from: https://nodejs.org/ (choose LTS version)
- Verify:
  ```
  node --version
  npm --version
  ```

#### 3. Tesseract OCR (Optional - for scanned image PDFs)
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR\`
- Only needed for scanned image PDFs. Regular text PDFs work without it.

### Step 1: Clone the Repository

```
git clone https://github.com/Karanr93/DocIntelligence.git
cd DocIntelligence
```

### Step 2: Create Your .env File

```
copy .env.example backend\.env
```

Open `backend\.env` in a text editor and configure your LLM provider:

**Option A: Groq (free, recommended for local)**
```
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-70b-versatile
GROQ_API_KEY=your-groq-key-here
```
Get a free API key at: https://console.groq.com

**Option B: Ollama (free, fully offline)**
```
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1
```
Install Ollama from https://ollama.com, then run: `ollama pull llama3.1`

**Option C: OpenAI (paid)**
```
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-openai-key-here
```

**AWS credentials (optional for local - needed only for S3 storage):**
```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=document-clause-system
```
If you skip AWS credentials, the app still works - files are stored locally instead of S3.

### Step 3: Install Backend Dependencies

```
cd backend
pip install -r requirements.txt
cd ..
```

> **Note:** If you see a `greenlet` build error, run:
> ```
> pip install "sqlalchemy==1.4.50" --no-deps
> ```
> Then run `pip install -r requirements.txt` again.

### Step 4: Install Frontend Dependencies

```
cd frontend
npm install
cd ..
```

### Step 5: Generate Sample PDFs (Optional)

Creates 10 sample PDFs with Medical/Finance/Sports content for testing:
```
cd backend
python sample_generator/generate_pdfs.py
cd ..
```

### Step 6: Start the Application

You need **two terminal windows**:

**Terminal 1 - Backend:**
```
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
You should see: `Uvicorn running on http://127.0.0.1:8000`

**Terminal 2 - Frontend:**
```
cd frontend
npm run dev
```
You should see: `Local: http://localhost:3000/`

### Step 7: Open the Application

Open your browser and go to: **http://localhost:3000**

### Step 8: Upload Sample Documents (Optional)

With the backend running, open a third terminal:
```
cd backend
python upload_samples.py
```

---

## Part 2: Deploying to AWS (Production)

This deploys the app to an EC2 instance so others can access it via a public URL.

### Prerequisites

- AWS account with credits
- AWS credentials (Access Key ID and Secret Access Key) in your `backend/.env`
- Python with `boto3` installed locally

### Step 1: Create EC2 Infrastructure

```
cd deploy
python setup_ec2.py
```

This automatically creates:
- EC2 instance (t3.micro, ~$7.60/month)
- Security group (ports 22 and 80)
- SSH key pair (saved as `deploy/docclause-key.pem`)
- Elastic IP (static public IP)

The script outputs your server details:
```
Instance ID:  i-0xxxxxxxxxx
Public IP:    xx.xx.xx.xx
SSH Command:  ssh -i deploy/docclause-key.pem ec2-user@xx.xx.xx.xx
Web URL:      http://xx.xx.xx.xx
```

### Step 2: SSH into the Server

```
ssh -i deploy/docclause-key.pem ec2-user@<your-public-ip>
```

### Step 3: Install Dependencies on EC2

```bash
# Install Python 3.8+
sudo amazon-linux-extras install python3.8 -y

# Install pip packages
sudo python3.8 -m pip install fastapi==0.104.1 uvicorn==0.24.0 "sqlalchemy==1.4.50" \
  pydantic==1.10.13 python-multipart==0.0.6 python-dotenv==1.0.0 \
  PyMuPDF==1.23.7 pytesseract==0.3.10 reportlab==4.0.8 \
  boto3==1.34.0 aiofiles==23.2.1 openai groq

# Install Node.js (for building frontend)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 16
```

### Step 4: Upload Code to EC2

From your **local machine**:
```bash
# Upload backend
scp -i deploy/docclause-key.pem -r backend/ ec2-user@<your-ip>:/opt/docclause/backend/

# Build frontend locally and upload
cd frontend
npm run build
scp -i ../deploy/docclause-key.pem -r dist/* ec2-user@<your-ip>:/opt/docclause/frontend/
```

### Step 5: Configure .env for Production

SSH into the server and edit the backend `.env`:
```bash
nano /opt/docclause/backend/.env
```

Set the LLM provider to Bedrock (data stays in AWS):
```
LLM_PROVIDER=bedrock
LLM_MODEL=us.anthropic.claude-sonnet-4-20250514-v1:0
BEDROCK_REGION=us-east-1

AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=document-clause-system
```

### Step 6: Configure Nginx

```bash
sudo tee /etc/nginx/conf.d/docclause.conf > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    root /opt/docclause/frontend;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
        client_max_body_size 50M;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
EOF

sudo nginx -t && sudo systemctl restart nginx
```

### Step 7: Create Backend Service

```bash
sudo tee /etc/systemd/system/docclause.service > /dev/null <<'EOF'
[Unit]
Description=DocClause FastAPI Backend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/docclause/backend
ExecStart=/usr/bin/python3.8 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5
Environment=PATH=/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable docclause
sudo systemctl start docclause
```

### Step 8: Access Your Application

Open in browser: **http://your-public-ip**

### Managing the EC2 Instance

| Action | How |
|--------|-----|
| **Stop** (save money) | AWS Console -> EC2 -> Instances -> Stop instance |
| **Start** (before demo) | AWS Console -> EC2 -> Instances -> Start instance |
| **View logs** | `sudo journalctl -u docclause -f` |
| **Restart backend** | `sudo systemctl restart docclause` |

**Important:** Use **Stop**, not **Terminate**. Terminate deletes everything permanently.

When stopped, cost drops from ~$7.60/month to ~$0.50/month (storage only). The Elastic IP keeps your URL the same after restart.

---

## How to Use the Application

### Upload Documents
1. Click **"Upload"** in the navigation bar
2. Drag and drop PDF files, or click to browse
3. The system automatically processes each page:
   - OCR text extraction
   - Rule-based keyword matching
   - LLM verification (for ambiguous cases)
   - S3 sync (if AWS is configured)
4. Go to **Dashboard** to see results

### Dashboard
- Summary cards: total documents, processed, pending, failed
- Bar chart: clause counts by category
- Click any clause card to drill down into matching documents

### Filter by Role
- Use the **Role** dropdown (top-right)
- Medical Clinician / Finance Analyst / Sports Analyst / All Roles

### View Document Details
1. Click any document to see its details
2. **"Highlighted PDF"** tab: shows the PDF with colored highlights in-browser
3. **"Extractions"** tab: shows extracted text, confidence scores, metadata

### Download Highlighted PDF
- Click **"Download PDF"** on any document detail page
- Get a color-coded PDF with Medical (blue), Finance (green), Sports (amber) highlights

### Review Queue
- Click **"Review Queue"** in navigation
- Low-confidence extractions appear here for manual verification
- **Approve**: confirms the extraction (sets confidence to 100%)
- **Reject**: removes the extraction

---

## How the Extraction Pipeline Works

```
PDF Upload -> OCR (text extraction) -> For each page x category:

  Rule Engine (keyword matching)
    |
    +-- 0 matches ---------> SKIP (not relevant)
    |
    +-- 3+ matches --------> ACCEPT (high confidence, no LLM needed)
    |
    +-- 1-2 matches -------> CALL LLM for verification
                               |
                               +-- LLM says not relevant -> SKIP
                               +-- LLM confirms (high confidence) -> ACCEPT
                               +-- LLM confirms (low confidence) -> ACCEPT + HUMAN REVIEW
```

### LLM Provider Comparison

| Provider | Model | Cost | Data Privacy | Speed |
|----------|-------|------|-------------|-------|
| Groq | Llama 3.1 70B | Free | Data goes to Groq | Fast |
| Ollama | Llama 3.1 (local) | Free | Fully offline | Depends on hardware |
| OpenAI | GPT-4o-mini | ~$0.001/page | Data goes to OpenAI | Fast |
| Bedrock | Claude Sonnet | ~$0.003/page | Data stays in AWS | Medium |

---

## Where is the Data Stored?

| Data | Local Location | S3 Location |
|------|---------------|-------------|
| Uploaded PDFs | `backend/uploaded_pdfs/` | `documents/{id}/original.pdf` |
| OCR Text | SQLite database | `documents/{id}/ocr/page_N.txt` |
| Extractions | SQLite database | `documents/{id}/extractions/{category}/page_N.json` |
| Highlighted PDFs | `backend/annotated_pdfs/` | Generated on-demand |
| Database | `backend/clause_system.db` | - |

---

## Project Structure

```
DocIntelligence/
├── README.md
├── .env.example                 <- Template for API keys
├── .gitignore
├── DocClause_System_Documentation.md  <- Technical documentation
│
├── backend/
│   ├── app/
│   │   ├── main.py              <- FastAPI application entry point
│   │   ├── models.py            <- Database tables (Document, Page, Extraction, ReviewItem)
│   │   ├── schemas.py           <- API request/response formats
│   │   ├── config.py            <- Settings and environment variables
│   │   ├── routers/
│   │   │   ├── documents.py     <- Upload, list, download APIs
│   │   │   ├── dashboard.py     <- Dashboard stats and charts API
│   │   │   └── review.py        <- Human review queue API
│   │   └── services/
│   │       ├── ocr_service.py   <- PDF text extraction (PyMuPDF + Tesseract)
│   │       ├── rule_engine.py   <- Keyword-based clause detection
│   │       ├── llm_service.py   <- AI extraction (Bedrock/Groq/OpenAI/Ollama)
│   │       ├── extraction.py    <- Hybrid pipeline orchestrator
│   │       ├── pdf_annotator.py <- Color-coded PDF highlighting
│   │       └── s3_service.py    <- AWS S3 storage
│   ├── sample_generator/        <- Scripts to create test PDFs
│   ├── requirements.txt
│   └── upload_samples.py        <- Bulk upload script
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              <- Main application with role selector
│   │   ├── api.js               <- Backend API client
│   │   └── components/
│   │       ├── Dashboard.jsx    <- Stats cards + bar chart
│   │       ├── DocumentList.jsx <- Document table with search
│   │       ├── DocumentDetail.jsx <- PDF viewer + extractions
│   │       ├── UploadPanel.jsx  <- File upload interface
│   │       └── ReviewQueue.jsx  <- Human review interface
│   ├── package.json
│   └── vite.config.js
│
└── deploy/
    └── setup_ec2.py             <- Creates EC2 infrastructure
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Failed to load dashboard" | Make sure backend is running (`python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`) |
| `greenlet` build error | Run `pip install "sqlalchemy==1.4.50" --no-deps` first |
| `python` command not found | Use full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe` |
| `npm` command not found | Install Node.js from https://nodejs.org/ |
| Port 8000 already in use | Use `--port 8001` and update `frontend/vite.config.js` to match |
| Backend crashes with "Segmentation fault" | Use standard Python instead of Anaconda |
| Ollama connection refused | Make sure Ollama is running: `ollama serve` |
| Bedrock "access denied" | Enable Claude model access in AWS Console -> Bedrock -> Model access |

---

## API Documentation

Once the backend is running, visit **http://localhost:8000/docs** for interactive Swagger UI.

Key endpoints:
- `POST /api/documents/upload` - Upload a PDF
- `GET /api/documents/` - List all documents
- `GET /api/documents/{id}` - Get document details with extractions
- `GET /api/documents/{id}/annotated?role=Medical` - Download highlighted PDF
- `POST /api/documents/{id}/reprocess` - Reprocess a document
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/documents-by-clause?category=Medical` - Filter by clause
- `GET /api/review/` - Review queue items
- `PUT /api/review/{id}` - Approve or reject a review item

---

## AWS Cost Estimate

| Service | Monthly Cost |
|---------|-------------|
| EC2 t3.micro (running 24/7) | ~$7.60 |
| EC2 t3.micro (stopped, storage only) | ~$0.50 |
| Elastic IP (attached to running instance) | Free |
| S3 storage | < $0.50 |
| Bedrock Claude Sonnet | ~$0.50-$2.00 (depends on usage) |
| **Total (running)** | **~$10/month** |
| **Total (stopped between demos)** | **~$1/month** |
