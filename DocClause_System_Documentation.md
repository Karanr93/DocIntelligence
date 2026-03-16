# DocClause - Document Clause Extraction System
## Technical Documentation

---

## 1. Extraction Logic: Rule-Based, LLM, and Human Review

The system uses a **three-tier hybrid pipeline** to classify each page of a PDF against each clause category (Medical, Finance, Sports). The flow is:

```
PDF Upload --> OCR (text extraction) --> For each page x category:
    |
    +--> Rule Engine (keyword matching)
            |
            +-- 0 keyword matches --> SKIP (not relevant)
            |
            +-- 3+ keyword matches (confidence >= 0.80) --> ACCEPT (rule-only, no LLM call)
            |
            +-- 1-2 keyword matches (confidence 0.40-0.79) --> CALL LLM
                    |
                    +--> LLM says not relevant --> SKIP
                    +--> LLM confirms relevant:
                            |
                            +-- Combined confidence >= 0.50 --> ACCEPT
                            +-- Combined confidence < 0.50 --> ACCEPT + FLAG FOR HUMAN REVIEW
```

### Step 1: Rule-Based Classification (Always runs first)

**File:** `backend/app/services/rule_engine.py` (Lines 15-54)

The rule engine scans the page text for category-specific keywords using regex word-boundary matching. Each category has a predefined keyword list (e.g., Medical has "patient", "diagnosis", "treatment", etc.).

**Confidence scoring:**
| Keyword Matches | Confidence Score | What Happens |
|---|---|---|
| 0 matches | 0.0 | Page skipped entirely for this category |
| 1 match | 0.50 | Medium confidence - LLM is called |
| 2 matches | 0.60 | Medium confidence - LLM is called |
| 3+ matches | 0.80 - 0.95 | High confidence - **accepted without LLM** |

**Formula (Lines 40-45):**
- 3+ matches: `confidence = min(0.95, 0.70 + (match_count * 0.05))`
- 1-2 matches: `confidence = 0.40 + (match_count * 0.10)`

### Step 2: LLM Call (Only for ambiguous cases)

**File:** `backend/app/services/llm_service.py` (Lines 105-172)

The LLM is called ONLY when the rule engine produces a medium-confidence result (1-2 keyword matches, confidence 0.40-0.79). This saves cost — most pages are resolved by rule alone.

**When LLM is triggered:**
- Rule engine found some keywords but not enough for high confidence
- The LLM receives the page text and category definition
- It returns a structured JSON with: is_relevant, confidence, extracted_sections, reasoning

**Combined confidence formula** (`backend/app/services/extraction.py`, Line 135):
```
combined_confidence = (rule_confidence * 0.3) + (llm_confidence * 0.7)
```

The LLM's judgment is weighted more heavily (70%) since it understands context, while the rule engine (30%) provides a sanity check.

### Step 3: Human Review Queue (Only for low-confidence LLM results)

**File:** `backend/app/services/extraction.py` (Lines 148, 73-79)

An extraction is flagged for human review when:
- The LLM confirmed relevance, but the **combined confidence < 0.50**
- This means the rule engine had weak evidence AND the LLM was uncertain

**What happens in review:**
- The item appears in the Review Queue in the UI
- A reviewer (Medical Clinician, Finance Analyst, or Sports Analyst) can:
  - **Approve**: Sets confidence to 1.0 and source to "human"
  - **Reject**: Deletes the extraction entirely
- File: `backend/app/routers/review.py` (Lines 63-91)

### When does each tier handle the work?

| Scenario | Rule Engine | LLM | Human Review |
|---|---|---|---|
| Page about heart surgery with words "patient", "treatment", "diagnosis", "clinical" | 4 matches = 0.90 confidence. **ACCEPTED by rule only.** | NOT called | NOT needed |
| Page mentioning "insurance claim" once | 1 match = 0.50 confidence | Called. If LLM says relevant with 0.80 confidence → combined = 0.71. **ACCEPTED.** | NOT needed |
| Page with word "score" (could be sports or finance) | 1 match = 0.50 confidence | Called. LLM uncertain, gives 0.40 → combined = 0.43. **ACCEPTED but FLAGGED.** | Reviewer decides |
| Page about cooking recipes | 0 matches | NOT called | NOT needed. **SKIPPED.** |

---

## 2. Where Does Deployment Take Place?

### AWS Infrastructure

The application is deployed on **AWS EC2** with supporting services:

| Component | AWS Service | Details |
|---|---|---|
| **Application Server** | EC2 (t3.micro) | Amazon Linux 2, 2 vCPU, 1GB RAM |
| **Web Server** | Nginx (on EC2) | Reverse proxy on port 80 |
| **Backend API** | FastAPI + Uvicorn (on EC2) | Python 3.8, runs on port 8000 |
| **Frontend** | Static files (on EC2) | React build served by Nginx |
| **File Storage** | S3 | Bucket: `document-clause-system` |
| **LLM AI** | Bedrock | Claude Sonnet - pay per API call |
| **Database** | SQLite (on EC2) | File-based, no separate DB server needed |
| **Public IP** | Elastic IP | Static IP: `52.1.93.111` |

### Deployment Architecture

```
User's Browser (http://52.1.93.111)
        |
        v
    [Nginx - Port 80]
        |
        +-- /api/*  -->  [FastAPI Backend - Port 8000]
        |                       |
        |                       +-- SQLite DB (local file)
        |                       +-- S3 (file storage)
        |                       +-- Bedrock (LLM calls)
        |
        +-- /*  -->  [React Static Files]
```

### Deployment Files

| File | Purpose |
|---|---|
| `deploy/setup_ec2.py` | Creates EC2 instance, security group, key pair, Elastic IP |
| `deploy/deployment_info.json` | Stores instance ID, IP, SSH command |
| `deploy/docclause-key.pem` | SSH private key to access the server |

### How to SSH into the server:
```bash
ssh -i deploy/docclause-key.pem ec2-user@52.1.93.111
```

### Services on EC2:
- **Backend**: `sudo systemctl status docclause` (systemd service)
- **Nginx**: `sudo systemctl status nginx`
- **App directory**: `/opt/docclause/`

---

## 3. What to See in S3, EC2, and Bedrock

### S3 (AWS Console -> S3 -> document-clause-system)

Browse the bucket to see:

```
document-clause-system/
|
+-- metadata/
|     +-- document_index.json          <-- Global index of all processed documents
|
+-- documents/
      +-- 1_athletic_training_program/
      |     +-- original.pdf           <-- The uploaded PDF
      |     +-- extraction_summary.json <-- Summary of all extractions
      |     +-- ocr/
      |     |     +-- page_1.txt       <-- Raw OCR text for page 1
      |     |     +-- page_2.txt       <-- Raw OCR text for page 2
      |     |     +-- page_3.txt
      |     |     +-- full_document_ocr.json  <-- All pages combined
      |     +-- extractions/
      |           +-- medical/
      |           |     +-- page_1.json  <-- Medical extraction for page 1
      |           +-- finance/
      |           |     +-- page_2.json  <-- Finance extraction for page 2
      |           +-- sports/
      |                 +-- page_1.json  <-- Sports extraction for page 1
      |                 +-- page_2.json
      |                 +-- page_3.json
      +-- 2_corporate_annual_report/
      |     +-- (same structure)
      +-- ...
```

**What each file contains:**

- **`page_N.txt`** (OCR folder): Raw text extracted from that page via PyMuPDF/Tesseract
- **`page_N.json`** (extractions folder): Structured data including:
  - `extracted_text`: The verbatim text that matched the category
  - `confidence_score`: 0.0 to 1.0
  - `source`: "rule" or "llm" or "human"
  - `structured_data`: Matched keywords, LLM reasoning, entities
  - `bbox_coordinates`: Bounding boxes for highlighting in the PDF
- **`extraction_summary.json`**: Aggregated view of all extractions for a document
- **`document_index.json`**: Master list of all documents with their clause counts

**Code:** `backend/app/services/s3_service.py` (Lines 73-149) handles all S3 uploads.

### EC2 (AWS Console -> EC2 -> Instances)

You will see:

| Item | Where to Find | What You See |
|---|---|---|
| **Running Instance** | EC2 -> Instances | `DocClause-Server`, t3.micro, running |
| **Elastic IP** | EC2 -> Elastic IPs | `52.1.93.111`, attached to the instance |
| **Security Group** | EC2 -> Security Groups | `docclause-sg` with ports 22 (SSH) and 80 (HTTP) open |
| **Key Pair** | EC2 -> Key Pairs | `docclause-key` |

**Instance details to check:**
- Instance state: Running
- Public IPv4: 52.1.93.111
- Instance type: t3.micro
- AMI: Amazon Linux 2
- Monitoring tab: CPU usage, network traffic

### Bedrock (AWS Console -> Amazon Bedrock)

Bedrock is a serverless API — there are no persistent resources to see. However:

| Where to Look | What You See |
|---|---|
| **Bedrock -> Model access** | Verify "Claude Sonnet" by Anthropic is enabled (green checkmark) |
| **Bedrock -> Providers -> Anthropic** | List of available Claude models |
| **CloudWatch -> Log groups** | Invocation logs if logging is enabled |

**Important:** Bedrock keeps your data private. Unlike OpenAI or Groq, your document text is NOT sent to third-party servers. It stays within your AWS account.

**Model used:** `us.anthropic.claude-sonnet-4-20250514-v1:0`
**Code:** `backend/app/services/llm_service.py` (Lines 54-83)

---

## 4. How We Prevent LLM Hallucination

The system implements **four layers** of hallucination prevention:

### Layer 1: Low Temperature (Line 68 in llm_service.py)
```python
"temperature": 0.1  # Near-deterministic output, minimal creativity
```
A temperature of 0.1 makes the LLM extremely focused and factual. It will not "imagine" content that doesn't exist.

### Layer 2: Strict Prompt Instructions (Lines 7-42 in llm_service.py)
The prompt explicitly tells the LLM:
```
"Only extract information that ACTUALLY exists in the text. Do NOT hallucinate or infer."
```
And the system prompt:
```
"You are a precise document analysis assistant. Never fabricate information. Only extract what exists in the text."
```
The LLM must return structured JSON with verbatim quotes from the source text.

### Layer 3: Word-Level Verification (Lines 136-155 in llm_service.py)
After the LLM returns extracted text, the system verifies it against the original:

```python
# Check if at least 60% of words from extraction exist in original
words = extracted.lower().split()
match_count = sum(1 for w in words if w in text.lower())
match_ratio = match_count / len(words)
if match_ratio >= 0.6:
    verified_sections.append(section)    # KEEP - verified
else:
    result["confidence"] -= 0.3          # PENALIZE - likely hallucinated
```

**What this does:**
- Takes each section the LLM claims to have extracted
- Checks what percentage of words actually exist in the source page text
- If less than 60% of words match, the section is DISCARDED as hallucination
- If ALL sections fail verification, the entire extraction is marked as not relevant

### Layer 4: Human Review Queue (Lines 73-79 in extraction.py)
When combined confidence is low (< 0.50), the extraction is flagged for human review. A domain expert can verify whether the extraction is accurate.

### Summary of Anti-Hallucination Measures

```
LLM Output
    |
    +--> Temperature 0.1 (minimal randomness)
    +--> Explicit "do not hallucinate" instructions
    +--> 60% word-match verification against source text
    +--> Low-confidence results go to human review
    |
    = Target: 98% F1 accuracy
```

---

## 5. Important Code Logic with File References

### 5.1 OCR Text Extraction

**File:** `backend/app/services/ocr_service.py`

| Lines | Logic |
|---|---|
| 30-44 | **PyMuPDF extraction**: Opens PDF, extracts text and word-level bounding boxes per page |
| 39-44 | **Word bounding boxes**: Captures x0, y0, x1, y1 coordinates for each word (used for PDF highlighting) |
| 49-69 | **Tesseract fallback**: If PyMuPDF extracts < 50 characters (scanned/image PDF), falls back to Tesseract OCR at 300 DPI |

### 5.2 Rule Engine - Keyword Matching

**File:** `backend/app/services/rule_engine.py`

| Lines | Logic |
|---|---|
| 26-35 | **Regex matching**: Uses word-boundary regex `\b{keyword}\b` to find exact keyword matches in page text, records start/end positions |
| 37-38 | **Deduplication**: Tracks unique keywords and total match count separately |
| 40-45 | **Confidence formula**: 3+ matches = HIGH (0.80-0.95), 1-2 matches = MEDIUM (0.40-0.60), 0 = skip |
| 56-74 | **Bounding box lookup**: Maps matched keywords to their word-level coordinates for PDF highlighting |

### 5.3 LLM Service - Bedrock/Groq/OpenAI

**File:** `backend/app/services/llm_service.py`

| Lines | Logic |
|---|---|
| 7-42 | **Extraction prompt template**: Defines the full prompt with category definitions, rules, and expected JSON output format |
| 44 | **System prompt**: "Never fabricate information" instruction |
| 54-83 | **Bedrock API call**: Creates `bedrock-runtime` client, sends request with `anthropic_version: "bedrock-2023-05-31"`, max_tokens=2000, temperature=0.1 |
| 85-103 | **Groq/OpenAI API call**: Alternative providers using the standard chat completions API |
| 113-115 | **Text truncation**: Limits input to 6000 characters to stay within token limits |
| 127-131 | **Markdown cleanup**: Strips markdown code blocks from LLM response before JSON parsing |
| 136-155 | **Hallucination guard**: 60% word-match verification (see Section 4 above) |
| 159-165 | **Error handling**: Returns safe default (not relevant) if JSON parsing or API call fails |

### 5.4 Hybrid Extraction Pipeline

**File:** `backend/app/services/extraction.py`

| Lines | Logic |
|---|---|
| 11-13 | **Threshold constants**: HIGH_CONFIDENCE=0.85, LOW_CONFIDENCE=0.50, RULE_ONLY_THRESHOLD=0.80 |
| 19-102 | **Main pipeline**: OCR -> iterate pages x categories -> classify -> store -> S3 sync |
| 30 | **OCR call**: `ocr_service.extract_text_from_pdf(pdf_path)` |
| 52-55 | **Classification loop**: Each page is checked against each category |
| 104-158 | **Hybrid classification logic**: Rule first -> LLM if needed -> Review if uncertain |
| 108-111 | **Skip path**: 0 keyword matches = not relevant, return immediately |
| 114-127 | **Rule-only path**: Confidence >= 0.80 = accept without LLM call |
| 130-158 | **LLM path**: Medium confidence = call LLM, combine scores with 30/70 weighting |
| 135 | **Combined confidence**: `(rule * 0.3) + (llm * 0.7)` |
| 148 | **Review flag**: `needs_review = combined_confidence < 0.50` |
| 160-191 | **S3 sync**: Uploads PDF, OCR text, extractions to S3 after processing |
| 193-204 | **Sentence extraction**: Pulls sentences containing matched keywords for the extracted_text field |

### 5.5 PDF Annotation (Highlighting)

**File:** `backend/app/services/pdf_annotator.py`

| Lines | Logic |
|---|---|
| 13-17 | **Color map**: Medical = Blue (#3B82F6), Finance = Green (#10B981), Sports = Amber (#F59E0B) |
| 24-101 | **Annotation logic**: Opens original PDF, overlays color-coded highlights per extraction |
| 63-74 | **Method 1 - Bbox highlighting**: Uses stored bounding box coordinates to place precise highlights |
| 77-91 | **Method 2 - Text search highlighting**: Falls back to searching for extracted text phrases in the PDF |
| 93-99 | **Save**: Outputs annotated PDF to `annotated_pdfs/` directory |

### 5.6 Data Models

**File:** `backend/app/models.py`

| Lines | Logic |
|---|---|
| 14-26 | **Document model**: filename, s3_key, local_path, total_pages, status (uploaded/processing/completed/failed) |
| 28-38 | **Page model**: document_id, page_number, ocr_text, processed flag |
| 41-49 | **ClauseCategory model**: name, color_hex, keywords (JSON list) |
| 52-67 | **Extraction model**: page_id, category_id, extracted_text, structured_data (JSON), confidence_score, source (rule/llm/human), needs_review, bbox_coordinates |
| 70-79 | **ReviewItem model**: extraction_id, status (pending/approved/rejected), reviewer_role, reviewed_at |
| 87-115 | **Database initialization**: Creates tables, seeds 3 default categories with ~22 keywords each |

### 5.7 S3 Data Sync

**File:** `backend/app/services/s3_service.py`

| Lines | Logic |
|---|---|
| 11-23 | **Auto-detection**: Checks if AWS credentials are configured, falls back to local storage if not |
| 25-33 | **File upload**: Uploads PDFs to S3, returns S3 URI or local path |
| 73-149 | **Full document sync**: Uploads original PDF, OCR text per page, extraction JSON per category per page, and extraction summary |
| 151-180 | **Global index**: Maintains `metadata/document_index.json` with all documents and their clause counts |

### 5.8 API Routes

**File:** `backend/app/routers/documents.py`

| Lines | Logic |
|---|---|
| 17-51 | **POST /api/documents/upload**: Saves PDF locally, creates DB record, uploads to S3, triggers background processing |
| 64-103 | **GET /api/documents/**: Lists all documents with optional status/category/search filters |
| 106-154 | **GET /api/documents/{id}**: Returns full document detail with pages and extractions, supports role filtering |
| 157-176 | **GET /api/documents/{id}/annotated**: Generates and returns color-highlighted annotated PDF |

**File:** `backend/app/routers/dashboard.py`

| Lines | Logic |
|---|---|
| 11-47 | **GET /api/dashboard/stats**: Returns total/processed/pending/failed counts, clause counts per category |
| 50-110 | **GET /api/dashboard/documents-by-clause**: Lists documents containing a specific clause category with confidence averages |

**File:** `backend/app/routers/review.py`

| Lines | Logic |
|---|---|
| 11-60 | **GET /api/review/**: Returns pending review items, supports role filtering |
| 63-91 | **PUT /api/review/{id}**: Approve (confidence=1.0, source="human") or reject (delete extraction) |

---

## Cost Summary

| Service | Monthly Cost |
|---|---|
| EC2 t3.micro | ~$7.60 |
| Elastic IP | Free (attached to running instance) |
| S3 storage | < $0.50 |
| Bedrock Claude Sonnet | ~$0.50-$2.00 (depends on LLM call volume) |
| **Total** | **~$10/month** |

---

## Quick Reference

| What | Where |
|---|---|
| Live URL | http://52.1.93.111 |
| SSH access | `ssh -i deploy/docclause-key.pem ec2-user@52.1.93.111` |
| Backend logs | `sudo journalctl -u docclause -f` (on EC2) |
| Restart backend | `sudo systemctl restart docclause` (on EC2) |
| S3 bucket | `document-clause-system` in us-east-1 |
| Bedrock model | `us.anthropic.claude-sonnet-4-20250514-v1:0` |
| Local dev backend | `cd backend && python -m uvicorn app.main:app --reload` |
| Local dev frontend | `cd frontend && npm run dev` |
