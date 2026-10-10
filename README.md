# WhatsApp Attendance & Daily Task Tracker (HR Management Portal)

An enterprise-grade WhatsApp-driven daily task tracking and payroll attendance system with a modern Next.js HR management web portal and a FastAPI backend powered by PostgreSQL (Prisma) and LLM structured outputs (Google Gemini / OpenAI).

---

## 🏛️ System Architecture & Constraints

```
       [ WhatsApp Client ] 
               │
               ▼ (Inbound E.164 message: e.g. +94771234567)
  [ Meta WhatsApp Cloud API ]
               │
               ▼ (POST /api/v1/webhook)
     ┌────────────────────────────────────────────────────────┐
     │                   FastAPI Backend                      │
     │                                                        │
     │ 1. Idempotency Check:                                  │
     │    `processed_webhook_messages` table via `message_id` │
     │    (Deduplicates retries without reprocessing)         │
     │                                                        │
     │ 2. Structured AI Parsing:                              │
     │    Google Gemini / OpenAI JSON Schema Structured Mode  │
     │    - Intent: CHECK_IN | CHECK_OUT | TASK_LOG | LEAVE   │
     │    - Tasks: [description, duration, category]          │
     │                                                        │
     │ 3. Unified Relational Data Persistence:                │
     │    PostgreSQL via Prisma ORM                           │
     │    - NO per-employee tables                            │
     │    - `@@unique([employee_id, date])`                   │
     │                                                        │
     │ 4. Outbound WhatsApp Reply:                            │
     │    Polite acknowledgment via Meta Cloud API            │
     └────────────────────────────────────────────────────────┘
               │
               ▼
      [ PostgreSQL Database ] ◄─────────┐
                                        │
                         [ Next.js HR Portal ]
                         (App Router, Tailwind CSS, Dark Theme)
```

### Architectural Guarantees:
1. **Single Relational Schema (No Per-Employee Tables)**:
   - All daily logs and tasks reside in unified relational tables with foreign keys and composite unique constraints (`@@unique([employeeId, date])`).
2. **Strict E.164 Standard**:
   - All WhatsApp phone numbers must strictly match the E.164 regex format (`^\+[1-9]\d{1,14}$`), e.g., `+94771234567`.
3. **Idempotent Webhook Processing**:
   - Meta WhatsApp webhook retries are deduplicated via unique `message_id` (`wamid.HBg...`) stored in `processed_webhook_messages`.

---

## 📁 Monorepo Structure

```
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── webhook.py        # Meta GET verification challenge & idempotent POST handler
│   │   │   │   ├── employees.py      # Employee directory CRUD
│   │   │   │   ├── attendance.py     # Attendance queries & date filters
│   │   │   │   ├── tasks.py          # Daily tasks timeline
│   │   │   │   └── payroll.py        # Payroll calculations
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── config.py             # Pydantic v2 application settings
│   │   │   └── database.py           # Prisma lifecycle connection management
│   │   ├── schemas/
│   │   │   ├── whatsapp.py           # E.164 regex validator & Meta webhook payload schemas
│   │   │   ├── ai_parser.py          # JSON Schema structured output contract
│   │   │   ├── employee.py           # Employee models
│   │   │   ├── attendance.py         # Attendance log models
│   │   │   ├── task.py               # Daily task models
│   │   │   └── payroll.py            # Payroll period & record models
│   │   ├── services/
│   │   │   ├── whatsapp_service.py   # Idempotency engine & outbound Meta API dispatch
│   │   │   ├── llm_parser_service.py # Gemini & OpenAI structured JSON parser
│   │   │   └── attendance_service.py # Unified DB operations & composite key updates
│   │   └── main.py                   # FastAPI application entrypoint
│   ├── prisma/
│   │   └── schema.prisma             # Unified PostgreSQL Prisma schema
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx              # Executive HR Overview Dashboard
│   │   │   ├── attendance/page.tsx   # Daily Attendance Matrix
│   │   │   ├── tasks/page.tsx        # Daily Tasks Feed & AI Confidence Score
│   │   │   ├── employees/page.tsx    # Unified Employees Directory
│   │   │   ├── payroll/page.tsx      # Payroll Processing Portal
│   │   │   ├── globals.css           # Modern Dark Mode & WhatsApp Emerald accents
│   │   │   └── layout.tsx            # Root App Layout with Sidebar & Navbar
│   │   ├── components/
│   │   │   ├── sidebar.tsx
│   │   │   └── navbar.tsx
│   │   └── lib/
│   │       ├── api.ts                # Client API methods with mock fallbacks
│   │       └── utils.ts
│   ├── package.json
│   ├── tailwind.config.ts
│   └── .env.example
├── scripts/
│   ├── migrations/
│   │   └── 001_initial_schema.sql    # Pure PostgreSQL DDL migration script
│   ├── migrate.py                    # Prisma migration runner
│   ├── seed_data.py                  # Seed initial employees & attendance
│   └── test_webhook_payload.py       # Simulates Meta webhook & verifies idempotency
├── docker-compose.yml                # PostgreSQL service container
├── .env.example                      # Master configuration placeholders
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Environment Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Ensure placeholders are updated:
- `DATABASE_URL`: PostgreSQL connection string
- `META_ACCESS_TOKEN`: Meta Graph API System User Token
- `META_VERIFY_TOKEN`: Verification token matching Meta Webhook configuration
- `META_PHONE_NUMBER_ID`: WhatsApp Phone Number ID from Meta Developer Portal
- `LLM_API_KEY`: Google Gemini or OpenAI API Key

### 2. Launch PostgreSQL Database

```bash
docker compose up -d
```

### 3. Database Migration & Prisma Generation

Run the migration script:
```bash
python scripts/migrate.py
```
Or with Prisma CLI directly:
```bash
npx prisma db push --schema=backend/prisma/schema.prisma
```

### 4. Start the FastAPI Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API docs are available at: `http://localhost:8000/api/v1/docs`.

### 5. Start the Next.js Frontend

```bash
cd frontend
npm install
npm run dev
```
Access the HR Portal at: `http://localhost:3000`.

---

## 🧪 Testing the WhatsApp Webhook & Idempotency

Run the automated simulation script:
```bash
python scripts/test_webhook_payload.py
```

This verifies:
1. **GET Verification Challenge**: Tests `hub.mode=subscribe` and `hub.verify_token`.
2. **Inbound Message Extraction**: Processes an incoming message, parses tasks with AI, and clocks the employee.
3. **Idempotency Deduplication**: Sends the identical `message_id` a second time and verifies that duplicate execution is blocked.