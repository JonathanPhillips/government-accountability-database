# GADB Quick Start Guide for Claude Code

## How to Use These Documents

### Document 1: Main Implementation Prompt

**File: `GADB_Claude_Code_Prompt.md`**

This is the primary prompt to give Claude Code. It contains:

- Complete project specification
- All 7 phases with milestones
- Detailed tasks for each milestone
- Test requirements (pytest + Playwright)
- Success criteria

**Usage:** Copy this into Claude Code as your initial prompt. Claude Code should work through it phase by phase, milestone by milestone.

### Document 2: Seed Data Specification

**File: `GADB_Seed_Data.md`**

Reference data for Claude Code to use when implementing:

- Category definitions
- Agency hierarchy
- Target categories
- Legal frameworks
- Pattern definitions
- Sample incidents
- RSS feed sources
- Keyword lists

**Usage:** Provide this as a second document when Claude Code reaches Phase 1, Milestone 1.3 (Seed Data).

---

## Recommended Workflow

### Initial Setup

```bash
# Create project directory
mkdir gadb && cd gadb

# Start Claude Code session
claude

# Paste the main implementation prompt
```

### Working Through Phases

**After each milestone, verify:**

1. Tests pass: `pytest tests/ -v` or `npx playwright test`
2. Manual spot-check with Playwright MCP or Claude Chrome
3. Commit with descriptive message

**Checkpoint prompts to use:**

```
"Run all tests for the current milestone and report results."

"Use Playwright MCP to visually verify [specific UI feature]."

"Before moving to next milestone, confirm: 1) All tests pass, 2) Code is committed, 3) Any blockers noted."
```

### Phase Transitions

When completing a phase, ask Claude Code:

```
"Summarize what was built in Phase X. List any deferred items or known issues. Confirm ready for Phase Y."
```

---

## Testing Commands Reference

### Backend (pytest)

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api_incidents.py -v

# Run specific test
pytest tests/test_api_incidents.py::test_create_incident_minimal -v
```

### Frontend (React Testing Library)

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

### E2E (Playwright)

```bash
# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e/incidents.spec.ts

# Run with UI (see browser)
npx playwright test --headed

# Run with debug
npx playwright test --debug

# Generate report
npx playwright show-report
```

### Using Playwright MCP for Verification

When you want Claude Code to visually verify UI:

```
"Use Playwright MCP to:
1. Navigate to the incidents page
2. Take a screenshot
3. Verify the incident list is visible
4. Click on the first incident
5. Verify the detail view loads correctly"
```

### Using Claude Chrome MCP for Verification

For more interactive testing:

```
"Use Claude Chrome to:
1. Open the application at localhost:3000
2. Walk through creating a new incident
3. Verify form validation works
4. Submit and confirm incident appears in list"
```

---

## Common Issues & Solutions

### Database Issues

```
Problem: SQLite locked
Solution: Ensure only one connection, or switch to PostgreSQL for development

Problem: Migration conflicts
Solution: `alembic downgrade base && alembic upgrade head`
```

### Test Issues

```
Problem: Playwright tests flaky
Solution: Add explicit waits, increase timeouts for CI

Problem: React tests failing on state updates
Solution: Wrap in act(), use waitFor()
```

### API Issues

```
Problem: CORS errors
Solution: Check FastAPI CORS middleware configuration

Problem: 422 Validation Error
Solution: Check Pydantic schema matches request body
```

---

## Milestone Checklist Template

Use this for each milestone:

```markdown
## Milestone X.Y: [Name]

### Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

### Tests Written
- [ ] test_function_1
- [ ] test_function_2

### Tests Passing
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass (if applicable)

### Visual Verification
- [ ] Playwright MCP verification complete
- [ ] Screenshots captured (if UI milestone)

### Code Quality
- [ ] Code committed with descriptive message
- [ ] No linting errors
- [ ] Documentation updated

### Notes/Blockers
- 

### Ready for Next Milestone: [ ] Yes / [ ] No
```

---

## Key Architecture Decisions

These decisions are already made—don't re-debate them:

1. **SQLite for development** → PostgreSQL for production
2. **FastAPI** for backend (async, modern, auto-docs)
3. **React + TypeScript** for frontend
4. **Tailwind** for styling (dark mode default)
5. **React Query** for API state
6. **Celery + Redis** for background tasks
7. **NetworkX** for graph (in-memory, migrate to Neo4j if needed)
8. **Playwright** for E2E tests

---

## Definition of Done

A milestone is complete when:

1. ✅ All specified functionality works
2. ✅ All tests written and passing
3. ✅ Visual verification done (for UI milestones)
4. ✅ Code committed
5. ✅ No critical bugs or blockers
6. ✅ Documentation reflects current state

---

## Emergency Fallbacks

If stuck on a milestone for too long:

1. **Simplify scope** - Note what's deferred, implement minimum viable version
2. **Skip non-critical features** - Core CRUD more important than polish
3. **Document blocker** - Clear description of issue for later resolution
4. **Move forward** - Don't let perfect be enemy of good

The goal is a working system you can start using and iterating on, not a perfect system that never ships.


# Government Accountability Database (GADB) - Claude Code Implementation Prompt

## Project Overview

Build a hybrid database system for tracking and documenting government activity, with focus on accountability, legal violations, authoritarian patterns, and civil liberties concerns. The system should support manual entry, automated ingestion from multiple sources, human verification workflows, and generate statistics, timelines, reports, and visualizations.

**Tech Stack:**

- Backend: Python (FastAPI)
- Database: SQLite (development) → PostgreSQL (production-ready migration path)
- Graph Layer: NetworkX (in-memory) with option to migrate to Neo4j
- Frontend: React + TypeScript + Tailwind CSS
- Testing: pytest (backend), Playwright (E2E), React Testing Library (frontend)
- Task Queue: Celery with Redis (for automated ingestion)

**Key Principles:**

- Every claim must link to verifiable sources
- Clear confidence/verification levels on all data
- Designed for one user now, but architected for multi-user future
- All automated ingestion requires human verification before "confirmed" status

---

## PHASE 1: Core Database Schema & Models

### Milestone 1.1: Project Setup & Schema Design

**Tasks:**

1. Initialize project structure:

```
gadb/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   └── ingestion/
│   ├── tests/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── tests/
│   └── package.json
├── docker-compose.yml
└── README.md
```

2. Create SQLAlchemy models for core entities:

```python
# Core Entities Needed:

class Incident:
    """Primary unit of documentation"""
    id: UUID
    title: str
    date_occurred: date
    date_range_end: Optional[date]  # For ongoing incidents
    summary: text
    detailed_description: text
    category: ForeignKey(Category)
    subcategory: Optional[ForeignKey(Subcategory)]
    severity: Enum('low', 'medium', 'high', 'critical')
    verification_status: Enum('unverified', 'pending_review', 'disputed', 'documented', 'adjudicated')
    geographic_scope: Enum('local', 'state', 'federal', 'international')
    location_state: Optional[str]
    location_city: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str  # For future multi-user
    
class Actor:
    """Government agencies, officials, entities involved"""
    id: UUID
    name: str
    actor_type: Enum('agency', 'official', 'contractor', 'entity', 'foreign_government')
    parent_actor: Optional[ForeignKey(Actor)]  # e.g., ICE -> DHS
    description: text
    wikipedia_url: Optional[str]
    active: bool
    
class Person:
    """Specific individuals (officials, not victims)"""
    id: UUID
    name: str
    current_title: Optional[str]
    agency: Optional[ForeignKey(Actor)]
    biography_summary: text
    
class Target:
    """Categories of people/entities targeted"""
    id: UUID
    name: str  # e.g., "Asylum seekers", "Journalists", "Protesters"
    description: text

class LegalFramework:
    """Laws, constitutional provisions, treaties potentially violated"""
    id: UUID
    name: str
    framework_type: Enum('constitutional', 'statutory', 'treaty', 'court_order', 'regulation')
    citation: str  # e.g., "5th Amendment", "18 U.S.C. § 1001"
    description: text
    url: Optional[str]

class Source:
    """Documentation/evidence for incidents"""
    id: UUID
    incident: ForeignKey(Incident)
    source_type: Enum('court_filing', 'government_report', 'foia', 'news_primary', 'news_secondary', 'academic', 'ngo_report', 'firsthand_account', 'video', 'social_media', 'leaked_document')
    title: str
    url: Optional[str]
    publication_date: Optional[date]
    publisher: Optional[str]
    author: Optional[str]
    reliability: Enum('primary', 'secondary', 'tertiary')
    archived_url: Optional[str]  # Wayback machine link
    archived_locally: bool
    local_file_path: Optional[str]
    excerpt: Optional[text]  # Relevant quote
    
class Pattern:
    """Named patterns that incidents can be part of"""
    id: UUID
    name: str  # e.g., "Executive court defiance", "Press intimidation"
    description: text
    historical_precedent: Optional[text]  # e.g., link to historical examples
    
class Category:
    """Primary categorization"""
    id: UUID
    name: str
    description: text
    # Categories include:
    # - court_order_defiance
    # - unauthorized_surveillance
    # - excessive_force
    # - unlawful_detention
    # - press_suppression
    # - protest_suppression
    # - electoral_interference
    # - corruption_self_dealing
    # - federalism_violation
    # - due_process_violation
    # - targeting_political_opposition
    # - whistleblower_retaliation
    # - unauthorized_data_access
    # - deportation_violation

# Junction Tables
class IncidentActor:
    incident_id: ForeignKey
    actor_id: ForeignKey
    role: Enum('perpetrator', 'complicit', 'resistor', 'whistleblower')
    
class IncidentPerson:
    incident_id: ForeignKey
    person_id: ForeignKey
    role: Enum('ordered', 'executed', 'resisted', 'exposed')

class IncidentTarget:
    incident_id: ForeignKey
    target_id: ForeignKey

class IncidentLegalFramework:
    incident_id: ForeignKey
    legal_framework_id: ForeignKey
    violation_type: Enum('alleged', 'documented', 'adjudicated')

class IncidentPattern:
    incident_id: ForeignKey
    pattern_id: ForeignKey

class RelatedIncidents:
    incident_id: ForeignKey
    related_incident_id: ForeignKey
    relationship_type: Enum('preceded_by', 'followed_by', 'related', 'escalation_of', 'response_to')

class IngestionQueue:
    """Track automated ingestion items awaiting review"""
    id: UUID
    source_url: str
    source_type: str
    raw_content: text
    extracted_data: JSON  # AI-extracted structured data
    status: Enum('pending', 'approved', 'rejected', 'needs_edit')
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    created_incident_id: Optional[ForeignKey(Incident)]
```

3. Set up Alembic for migrations

**Tests for 1.1:**

```python
# tests/test_models.py
def test_incident_creation()
def test_actor_hierarchy()  # Parent-child relationships
def test_source_incident_relationship()
def test_all_enums_valid()
def test_junction_table_constraints()
```

**Verification:** Run `pytest tests/test_models.py -v` - all pass

---

### Milestone 1.2: Core API Endpoints (CRUD)

**Tasks:**

1. Create Pydantic schemas for all models (request/response)
2. Implement CRUD endpoints:

```python
# Incidents
POST   /api/incidents                    # Create incident
GET    /api/incidents                    # List with filters
GET    /api/incidents/{id}               # Get single
PUT    /api/incidents/{id}               # Update
DELETE /api/incidents/{id}               # Soft delete

# With query parameters:
# ?category=court_order_defiance
# ?actor=ICE
# ?date_from=2025-01-01&date_to=2025-12-31
# ?verification_status=documented
# ?severity=high
# ?pattern=executive_court_defiance
# ?search=deportation  (full-text search)

# Actors
POST   /api/actors
GET    /api/actors
GET    /api/actors/{id}
GET    /api/actors/{id}/incidents        # All incidents involving actor
PUT    /api/actors/{id}

# Sources
POST   /api/incidents/{id}/sources       # Add source to incident
GET    /api/incidents/{id}/sources
DELETE /api/sources/{id}

# Similar for: persons, targets, legal_frameworks, patterns, categories

# Relationships
POST   /api/incidents/{id}/related       # Link incidents
POST   /api/incidents/{id}/actors        # Add actor to incident
POST   /api/incidents/{id}/patterns      # Add pattern to incident

# Search & Discovery
GET    /api/search?q=                    # Full-text search
GET    /api/timeline                     # Incidents as timeline
GET    /api/network/{incident_id}        # Related incident graph
```

3. Implement filtering, pagination, sorting on list endpoints
4. Add full-text search using SQLite FTS5

**Tests for 1.2:**

```python
# tests/test_api_incidents.py
def test_create_incident_minimal()
def test_create_incident_full()
def test_create_incident_validation_errors()
def test_list_incidents_pagination()
def test_filter_by_category()
def test_filter_by_date_range()
def test_filter_by_actor()
def test_filter_by_verification_status()
def test_filter_combined()
def test_full_text_search()
def test_update_incident()
def test_soft_delete()

# tests/test_api_actors.py
def test_create_actor()
def test_actor_hierarchy()
def test_get_actor_incidents()

# tests/test_api_sources.py
def test_add_source_to_incident()
def test_source_types_validated()

# tests/test_api_relationships.py
def test_link_incidents()
def test_add_actor_to_incident()
def test_add_pattern_to_incident()
```

**Verification:** Run `pytest tests/test_api_*.py -v` - all pass

---

### Milestone 1.3: Seed Data & Data Integrity

**Tasks:**

1. Create seed data script with:
    
    - All categories and subcategories
    - Common actors (federal agencies hierarchy): DOJ, DHS (ICE, CBP, USCIS), DOD, FBI, CIA, NSA, Treasury, State Dept, etc.
    - Common targets: Immigrants, Asylum seekers, Journalists, Protesters, Whistleblowers, Political opposition, etc.
    - Key legal frameworks: Constitutional amendments, major statutes (Posse Comitatus, Privacy Act, FOIA, etc.)
    - Initial patterns based on historical precedent
2. Create 10-15 sample incidents with full data (real, documented events from 2025) to test the schema comprehensively
    
3. Add database constraints:
    
    - Incidents must have at least one source
    - Sources must have URL or local file
    - Verification status rules (can't be "adjudicated" without court filing source)

**Tests for 1.3:**

```python
# tests/test_seed_data.py
def test_all_categories_exist()
def test_federal_agency_hierarchy()
def test_sample_incidents_valid()

# tests/test_data_integrity.py
def test_incident_requires_source()
def test_adjudicated_requires_court_filing()
def test_no_orphaned_sources()
```

**Verification:** Run seed script, verify via API calls, run integrity tests

---

## PHASE 2: Frontend Core Interface

### Milestone 2.1: React Project Setup & Component Architecture

**Tasks:**

1. Initialize React + TypeScript + Vite project
2. Set up Tailwind CSS with custom theme (dark mode default, professional/serious aesthetic)
3. Configure React Router
4. Set up React Query for API state management
5. Create component structure:

```
src/
├── components/
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   ├── Badge.tsx (for status, severity)
│   │   ├── Card.tsx
│   │   └── DataTable.tsx
│   ├── incidents/
│   │   ├── IncidentList.tsx
│   │   ├── IncidentCard.tsx
│   │   ├── IncidentDetail.tsx
│   │   ├── IncidentForm.tsx
│   │   ├── IncidentFilters.tsx
│   │   └── SourceList.tsx
│   ├── actors/
│   │   ├── ActorList.tsx
│   │   ├── ActorDetail.tsx
│   │   └── ActorForm.tsx
│   ├── visualization/
│   │   ├── Timeline.tsx
│   │   ├── NetworkGraph.tsx
│   │   ├── StatsDashboard.tsx
│   │   └── CategoryBreakdown.tsx
│   └── ingestion/
│       ├── IngestionQueue.tsx
│       ├── ReviewForm.tsx
│       └── ManualEntry.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── Incidents.tsx
│   ├── IncidentPage.tsx
│   ├── Actors.tsx
│   ├── ActorPage.tsx
│   ├── Timeline.tsx
│   ├── Reports.tsx
│   ├── Ingestion.tsx
│   └── Search.tsx
├── hooks/
│   ├── useIncidents.ts
│   ├── useActors.ts
│   └── useSearch.ts
├── api/
│   └── client.ts
└── types/
    └── index.ts
```

6. Create TypeScript types matching backend schemas

**Tests for 2.1:**

```typescript
// Component unit tests with React Testing Library
// tests/components/Badge.test.tsx
// tests/components/DataTable.test.tsx
```

**Verification:** `npm test`, visual inspection of component storybook/examples

---

### Milestone 2.2: Incident Management UI

**Tasks:**

1. Build IncidentList with:
    
    - Sortable columns (date, severity, category, verification status)
    - Filter sidebar
    - Search box
    - Pagination
    - Quick view preview on hover/click
2. Build IncidentDetail view showing:
    
    - Full incident information
    - All sources with links
    - Related actors with links
    - Applicable legal frameworks
    - Patterns this incident fits
    - Related incidents (graph preview)
    - Edit/Update capability
3. Build IncidentForm for:
    
    - Creating new incidents
    - Full validation
    - Actor lookup/creation
    - Source addition (multiple)
    - Pattern tagging
    - Legal framework selection

**Playwright E2E Tests for 2.2:**

```typescript
// tests/e2e/incidents.spec.ts
test('can view incident list')
test('can filter incidents by category')
test('can filter incidents by date range')
test('can search incidents')
test('can view incident detail')
test('can create new incident with minimal fields')
test('can create new incident with full fields')
test('can add source to existing incident')
test('can edit incident')
test('validation prevents invalid submission')
test('can link related incidents')
```

**Verification:** `npx playwright test tests/e2e/incidents.spec.ts`

---

### Milestone 2.3: Dashboard & Statistics

**Tasks:**

1. Build StatsDashboard showing:
    
    - Total incidents by verification status
    - Incidents by category (bar chart)
    - Incidents over time (line chart)
    - Severity distribution
    - Most frequent actors
    - Most common patterns
2. Use Recharts or D3 for visualizations
    
3. Add date range selector for all stats
    
4. Build "Key Findings" summary generator:
    
    - Auto-generate text summaries like "ICE has been involved in X documented incidents of Y type since Z date"

**Tests for 2.3:**

```typescript
// tests/e2e/dashboard.spec.ts
test('dashboard loads with statistics')
test('can change date range and stats update')
test('charts render correctly')
test('can click chart element to see related incidents')
```

**Verification:** Playwright visual comparison tests, manual review of chart accuracy

---

### Milestone 2.4: Timeline & Network Visualization

**Tasks:**

1. Build Timeline component:
    
    - Vertical scrolling timeline
    - Filter by category/actor/pattern
    - Zoom levels (day/week/month/year)
    - Click to expand incident details
    - Color coding by category or severity
2. Build NetworkGraph component:
    
    - Show incident relationships
    - Show actor involvement
    - Interactive zoom/pan
    - Click node for details
    - Use D3-force or similar
3. Export timeline as image/PDF
    

**Tests for 2.4:**

```typescript
// tests/e2e/timeline.spec.ts
test('timeline renders incidents in order')
test('can filter timeline by category')
test('can zoom timeline')
test('clicking incident shows detail')

// tests/e2e/network.spec.ts
test('network graph renders')
test('can click node to see details')
test('graph updates when filters change')
```

**Verification:** Playwright tests + manual visual QA

---

## PHASE 3: Ingestion Pipeline

### Milestone 3.1: Manual Entry Enhancement

**Tasks:**

1. Build streamlined manual entry form with:
    
    - Smart actor lookup (search as you type)
    - Source URL auto-fetch (grab title, publication date)
    - Wayback Machine integration (auto-archive URLs)
    - Duplicate detection (warn if similar incident exists)
    - Template system (pre-fill common patterns)
2. Bulk import from CSV/JSON
    

**Tests for 3.1:**

```typescript
// tests/e2e/manual-entry.spec.ts
test('actor autocomplete works')
test('url fetch retrieves metadata')
test('duplicate warning appears for similar incident')
test('can use template to pre-fill form')
test('csv import creates multiple incidents')
```

---

### Milestone 3.2: RSS/News Feed Ingestion

**Tasks:**

1. Create ingestion service for RSS feeds:
    
    - Configure feed sources (AP, Reuters, NPR, ProPublica, etc.)
    - Keyword/topic filtering
    - Deduplication
    - Rate limiting
2. Create AI extraction pipeline:
    
    - Use Claude API (or local model) to:
        - Determine if article is relevant
        - Extract structured data (date, actors, category, summary)
        - Suggest sources/citations
        - Assign confidence score
3. Queue extracted items for human review
    

```python
# backend/app/ingestion/rss_ingestor.py
class RSSIngestor:
    def fetch_feeds()
    def filter_relevant()
    def extract_structured_data()
    def queue_for_review()

# backend/app/ingestion/ai_extractor.py
class AIExtractor:
    def is_relevant(article_text) -> bool
    def extract_incident_data(article_text) -> ExtractedIncident
    def suggest_category(text) -> Category
    def suggest_actors(text) -> List[Actor]
    def confidence_score(extraction) -> float
```

**Tests for 3.2:**

```python
# tests/test_rss_ingestion.py
def test_feed_fetch()
def test_keyword_filtering()
def test_deduplication()

# tests/test_ai_extraction.py
def test_relevance_detection_positive()
def test_relevance_detection_negative()
def test_structured_extraction()
def test_category_suggestion()
def test_actor_extraction()
```

---

### Milestone 3.3: YouTube Transcript Ingestion

**Tasks:**

1. Build YouTube ingestion service:
    
    - Accept YouTube URL
    - Fetch transcript via youtube-transcript-api
    - Timestamp preservation
    - Speaker identification (if available)
2. AI extraction for:
    
    - Relevant segments identification
    - Timestamp linking for citations
    - Multiple incident extraction from single video
3. Support for:
    
    - Congressional hearings
    - Press conferences
    - Documentaries
    - News clips

```python
# backend/app/ingestion/youtube_ingestor.py
class YouTubeIngestor:
    def fetch_transcript(url)
    def identify_relevant_segments(transcript)
    def extract_incidents(segments)
    def create_timestamped_citations()
```

**Tests for 3.3:**

```python
# tests/test_youtube_ingestion.py
def test_transcript_fetch()
def test_segment_extraction()
def test_timestamp_citation_format()
```

---

### Milestone 3.4: Document Ingestion (PDFs, FOIA)

**Tasks:**

1. PDF text extraction (PyPDF2, pdfplumber)
    
2. OCR for scanned documents (Tesseract)
    
3. FOIA document handling:
    
    - Redaction detection
    - Page reference preservation
    - Multi-document package handling
4. Court filing parser:
    
    - Case number extraction
    - Party identification
    - Date extraction
    - Ruling/order extraction

```python
# backend/app/ingestion/document_ingestor.py
class DocumentIngestor:
    def extract_text(file_path)
    def ocr_if_needed(file_path)
    def parse_court_filing(text)
    def parse_foia_document(text)
```

**Tests for 3.4:**

```python
# tests/test_document_ingestion.py
def test_pdf_text_extraction()
def test_ocr_extraction()
def test_court_filing_parsing()
```

---

### Milestone 3.5: Verification Queue UI

**Tasks:**

1. Build IngestionQueue interface showing:
    
    - Pending items from all sources
    - AI-extracted data preview
    - Confidence scores
    - Original source link/content
2. Review workflow:
    
    - Approve (creates incident)
    - Reject (marks as not relevant)
    - Edit and approve (modify extracted data)
    - Merge (combine with existing incident)
    - Flag for later
3. Bulk actions for efficient review
    

**Playwright Tests for 3.5:**

```typescript
// tests/e2e/ingestion-queue.spec.ts
test('queue shows pending items')
test('can approve item and incident is created')
test('can reject item')
test('can edit extracted data before approval')
test('can merge with existing incident')
test('bulk approve works')
```

---

## PHASE 4: Graph Layer & Advanced Queries

### Milestone 4.1: NetworkX Integration

**Tasks:**

1. Build graph service:
    
    - Nodes: Incidents, Actors, Persons, Patterns
    - Edges: Relationships, involvement, pattern membership
2. Graph queries:
    
    - Shortest path between incidents
    - Actor centrality (who's involved in most incidents)
    - Cluster detection
    - Pattern strength (how many incidents fit pattern)

```python
# backend/app/services/graph_service.py
class GraphService:
    def build_graph()
    def get_incident_network(incident_id, depth=2)
    def actor_centrality()
    def detect_clusters()
    def find_path(incident_a, incident_b)
    def pattern_strength(pattern_id)
```

**Tests for 4.1:**

```python
# tests/test_graph_service.py
def test_graph_builds()
def test_incident_network()
def test_actor_centrality_calculation()
def test_path_finding()
```

---

### Milestone 4.2: Advanced Query Interface

**Tasks:**

1. Build query builder UI:
    
    - Multi-condition filters
    - Save/load queries
    - Export results
2. Natural language query (Claude-powered):
    
    - "Show me all ICE incidents where court orders were defied"
    - "What patterns has DHS been involved in since January?"
    - "Find incidents related to press freedom"

```python
# backend/app/services/query_service.py
class QueryService:
    def natural_language_to_query(text) -> SQLQuery
    def execute_query(query) -> Results
    def save_query(query, name)
    def load_query(name)
```

**Tests for 4.2:**

```typescript
// tests/e2e/query-builder.spec.ts
test('can build multi-condition query')
test('natural language query returns results')
test('can save and load queries')
test('can export query results')
```

---

## PHASE 5: Reports & Export

### Milestone 5.1: Report Generation

**Tasks:**

1. Build report templates:
    
    - Incident summary report
    - Actor dossier
    - Pattern analysis
    - Timeline report
    - Statistical overview
2. Export formats:
    
    - PDF (via WeasyPrint or similar)
    - Markdown
    - HTML
    - CSV (data export)
3. Customization:
    
    - Date range
    - Included sections
    - Detail level
    - Source citation format

```python
# backend/app/services/report_service.py
class ReportService:
    def generate_incident_report(incident_id, format)
    def generate_actor_dossier(actor_id, format)
    def generate_pattern_analysis(pattern_id, format)
    def generate_timeline_report(filters, format)
    def generate_statistics_report(date_range, format)
```

**Tests for 5.1:**

```python
# tests/test_report_generation.py
def test_incident_report_pdf()
def test_actor_dossier_contains_all_incidents()
def test_timeline_report_ordering()
def test_csv_export_complete()
```

**Playwright Tests:**

```typescript
// tests/e2e/reports.spec.ts
test('can generate and download incident report')
test('can generate actor dossier')
test('can export data as CSV')
```

---

### Milestone 5.2: Shareable Visualizations

**Tasks:**

1. Generate embeddable/shareable:
    
    - Timeline images
    - Network graph images
    - Statistics charts
    - Incident cards (social sharing format)
2. Public link generation (for future public mode):
    
    - Shareable incident links
    - Shareable report links
    - Embed codes

**Tests for 5.2:**

```typescript
// tests/e2e/sharing.spec.ts
test('can generate timeline image')
test('can generate chart image')
test('generated images are correct dimensions')
```

---

## PHASE 6: Automation & Scheduling

### Milestone 6.1: Celery Task Queue

**Tasks:**

1. Set up Celery with Redis
    
2. Create scheduled tasks:
    
    - RSS feed polling (configurable interval)
    - URL archiving (Wayback Machine)
    - Graph rebuilding (nightly)
    - Statistics caching
3. Task monitoring dashboard
    

```python
# backend/app/tasks/scheduled.py
@celery.task
def poll_rss_feeds()

@celery.task
def archive_urls()

@celery.task
def rebuild_graph()

@celery.task
def cache_statistics()
```

**Tests for 6.1:**

```python
# tests/test_celery_tasks.py
def test_rss_poll_task()
def test_archive_task()
def test_graph_rebuild()
```

---

### Milestone 6.2: Notification & Alerts

**Tasks:**

1. Alert system for:
    
    - New high-severity incidents (from ingestion)
    - Pattern threshold reached
    - Related incident detected
2. Daily/weekly digest email (optional)
    

---

## PHASE 7: Hardening & Deployment

### Milestone 7.1: Security & Data Integrity

**Tasks:**

1. Input sanitization on all endpoints
2. Rate limiting
3. Backup automation
4. Audit logging (who changed what, when)
5. Data validation rules enforcement

**Tests:**

```python
# tests/test_security.py
def test_sql_injection_prevention()
def test_xss_prevention()
def test_rate_limiting()
```

---

### Milestone 7.2: Docker & Deployment

**Tasks:**

1. Dockerfile for backend
2. Dockerfile for frontend
3. docker-compose.yml for full stack
4. Environment configuration
5. PostgreSQL migration path
6. Backup/restore scripts

```yaml
# docker-compose.yml structure
services:
  backend:
  frontend:
  db:
  redis:
  celery-worker:
  celery-beat:
```

**Tests:**

```bash
# Deployment verification
docker-compose up -d
curl http://localhost:8000/health
npx playwright test --project=docker
```

---

## Testing Strategy Summary

### Unit Tests (pytest)

- All model operations
- All service functions
- Data validation
- Graph algorithms

### Integration Tests (pytest)

- API endpoints
- Database operations
- Ingestion pipeline

### E2E Tests (Playwright)

- All user workflows
- Form submissions
- Navigation
- Visualizations render
- Export functionality

### Test Commands

```bash
# Backend
cd backend
pytest tests/ -v --cov=app --cov-report=html

# Frontend unit
cd frontend
npm test

# E2E
npx playwright test

# Full suite
./scripts/run-all-tests.sh
```

---

## Success Criteria Per Phase

**Phase 1 Complete When:**

- [ ] All models created and migrated
- [ ] All CRUD endpoints working
- [ ] Seed data loaded
- [ ] All backend tests pass

**Phase 2 Complete When:**

- [ ] Can create, view, edit, delete incidents via UI
- [ ] Dashboard shows accurate statistics
- [ ] Timeline displays correctly
- [ ] All Playwright tests pass

**Phase 3 Complete When:**

- [ ] Can manually enter incidents efficiently
- [ ] RSS feeds populate queue
- [ ] YouTube transcripts can be ingested
- [ ] PDFs can be processed
- [ ] Review queue allows approve/reject/edit

**Phase 4 Complete When:**

- [ ] Graph visualizations work
- [ ] Actor centrality calculated
- [ ] Natural language queries work

**Phase 5 Complete When:**

- [ ] Can generate PDF reports
- [ ] Can export data as CSV
- [ ] Can generate shareable visualizations

**Phase 6 Complete When:**

- [ ] Automated feed polling works
- [ ] URL archiving automated
- [ ] Tasks run on schedule

**Phase 7 Complete When:**

- [ ] Full docker deployment works
- [ ] Security tests pass
- [ ] Backup/restore verified

---

## Notes for Claude Code

1. **Commit after each sub-milestone** with descriptive messages
2. **Run tests before moving to next milestone** - don't proceed with failing tests
3. **Use Playwright MCP or Claude Chrome MCP** for E2E test verification - visually confirm UI elements work as expected
4. **Ask for clarification** if any requirement is ambiguous
5. **Document as you go** - README, API docs, code comments
6. **Prioritize working software** - it's okay to simplify scope if hitting blockers, but note what was deferred

Start with Phase 1, Milestone 1.1. Create the project structure and database models. Run the model tests before proceeding.


# GADB Seed Data Specification

This document provides the initial taxonomy and sample data for the Government Accountability Database.

## Categories

```python
CATEGORIES = [
    {
        "id": "court_order_defiance",
        "name": "Court Order Defiance",
        "description": "Executive branch ignoring, defying, or circumventing judicial orders"
    },
    {
        "id": "unlawful_detention",
        "name": "Unlawful Detention",
        "description": "Detention without legal authority, beyond legal limits, or in violation of due process"
    },
    {
        "id": "deportation_violation",
        "name": "Deportation Violation",
        "description": "Deportations conducted illegally, to wrong countries, or in violation of protections"
    },
    {
        "id": "excessive_force",
        "name": "Excessive Force",
        "description": "Use of force beyond what is legally justified"
    },
    {
        "id": "press_suppression",
        "name": "Press Suppression",
        "description": "Actions targeting journalists, restricting press access, or chilling press freedom"
    },
    {
        "id": "protest_suppression",
        "name": "Protest Suppression",
        "description": "Unlawful restrictions on assembly, excessive response to protests"
    },
    {
        "id": "unauthorized_surveillance",
        "name": "Unauthorized Surveillance",
        "description": "Surveillance without legal authority or beyond authorized scope"
    },
    {
        "id": "unauthorized_data_access",
        "name": "Unauthorized Data Access",
        "description": "Access to personal or government data without proper authorization"
    },
    {
        "id": "corruption_self_dealing",
        "name": "Corruption & Self-Dealing",
        "description": "Using government position for personal financial benefit"
    },
    {
        "id": "federalism_violation",
        "name": "Federalism Violation",
        "description": "Federal overreach into state authority, or violation of state sovereignty"
    },
    {
        "id": "due_process_violation",
        "name": "Due Process Violation",
        "description": "Denial of legal procedures required by constitution"
    },
    {
        "id": "targeting_political_opposition",
        "name": "Targeting Political Opposition",
        "description": "Using government power against political opponents"
    },
    {
        "id": "whistleblower_retaliation",
        "name": "Whistleblower Retaliation",
        "description": "Punishing those who expose wrongdoing"
    },
    {
        "id": "electoral_interference",
        "name": "Electoral Interference",
        "description": "Actions to manipulate elections or restrict voting"
    },
    {
        "id": "records_destruction",
        "name": "Records Destruction/Obstruction",
        "description": "Destroying records, obstructing FOIA, hiding documentation"
    },
    {
        "id": "parallel_governance",
        "name": "Parallel Governance",
        "description": "Creation of unofficial power structures outside legal authority"
    }
]
```

## Federal Agency Hierarchy

```python
ACTORS_AGENCIES = [
    # Executive Office
    {"id": "executive_office", "name": "Executive Office of the President", "type": "agency", "parent": None},
    {"id": "white_house", "name": "White House", "type": "agency", "parent": "executive_office"},
    {"id": "omb", "name": "Office of Management and Budget", "type": "agency", "parent": "executive_office"},
    
    # DHS and sub-agencies
    {"id": "dhs", "name": "Department of Homeland Security", "type": "agency", "parent": None},
    {"id": "ice", "name": "Immigration and Customs Enforcement (ICE)", "type": "agency", "parent": "dhs"},
    {"id": "cbp", "name": "Customs and Border Protection (CBP)", "type": "agency", "parent": "dhs"},
    {"id": "uscis", "name": "U.S. Citizenship and Immigration Services", "type": "agency", "parent": "dhs"},
    {"id": "secret_service", "name": "U.S. Secret Service", "type": "agency", "parent": "dhs"},
    {"id": "tsa", "name": "Transportation Security Administration", "type": "agency", "parent": "dhs"},
    
    # DOJ and sub-agencies
    {"id": "doj", "name": "Department of Justice", "type": "agency", "parent": None},
    {"id": "fbi", "name": "Federal Bureau of Investigation", "type": "agency", "parent": "doj"},
    {"id": "dea", "name": "Drug Enforcement Administration", "type": "agency", "parent": "doj"},
    {"id": "atf", "name": "Bureau of Alcohol, Tobacco, Firearms", "type": "agency", "parent": "doj"},
    {"id": "usms", "name": "U.S. Marshals Service", "type": "agency", "parent": "doj"},
    {"id": "bop", "name": "Federal Bureau of Prisons", "type": "agency", "parent": "doj"},
    
    # DOD
    {"id": "dod", "name": "Department of Defense", "type": "agency", "parent": None},
    {"id": "army", "name": "U.S. Army", "type": "agency", "parent": "dod"},
    {"id": "navy", "name": "U.S. Navy", "type": "agency", "parent": "dod"},
    {"id": "air_force", "name": "U.S. Air Force", "type": "agency", "parent": "dod"},
    {"id": "national_guard", "name": "National Guard Bureau", "type": "agency", "parent": "dod"},
    
    # Intelligence
    {"id": "cia", "name": "Central Intelligence Agency", "type": "agency", "parent": None},
    {"id": "nsa", "name": "National Security Agency", "type": "agency", "parent": "dod"},
    {"id": "dni", "name": "Office of the Director of National Intelligence", "type": "agency", "parent": None},
    
    # Other Departments
    {"id": "treasury", "name": "Department of the Treasury", "type": "agency", "parent": None},
    {"id": "irs", "name": "Internal Revenue Service", "type": "agency", "parent": "treasury"},
    {"id": "state", "name": "Department of State", "type": "agency", "parent": None},
    {"id": "hhs", "name": "Department of Health and Human Services", "type": "agency", "parent": None},
    {"id": "ed", "name": "Department of Education", "type": "agency", "parent": None},
    {"id": "doi", "name": "Department of the Interior", "type": "agency", "parent": None},
    {"id": "usda", "name": "Department of Agriculture", "type": "agency", "parent": None},
    {"id": "doc", "name": "Department of Commerce", "type": "agency", "parent": None},
    {"id": "dol", "name": "Department of Labor", "type": "agency", "parent": None},
    {"id": "dot", "name": "Department of Transportation", "type": "agency", "parent": None},
    {"id": "doe", "name": "Department of Energy", "type": "agency", "parent": None},
    {"id": "va", "name": "Department of Veterans Affairs", "type": "agency", "parent": None},
    {"id": "hud", "name": "Department of Housing and Urban Development", "type": "agency", "parent": None},
    
    # Non-standard entities
    {"id": "doge", "name": "Department of Government Efficiency (DOGE)", "type": "entity", "parent": None,
     "description": "Non-statutory advisory entity with unclear legal authority"},
]
```

## Target Categories

```python
TARGETS = [
    {"id": "immigrants", "name": "Immigrants (general)", "description": "Non-citizens including legal residents"},
    {"id": "asylum_seekers", "name": "Asylum Seekers", "description": "Those seeking asylum protection"},
    {"id": "refugees", "name": "Refugees", "description": "Those with refugee status"},
    {"id": "undocumented", "name": "Undocumented Immigrants", "description": "Those without legal status"},
    {"id": "legal_residents", "name": "Legal Permanent Residents", "description": "Green card holders"},
    {"id": "naturalized_citizens", "name": "Naturalized Citizens", "description": "Foreign-born citizens"},
    {"id": "journalists", "name": "Journalists", "description": "Press and media workers"},
    {"id": "protesters", "name": "Protesters", "description": "Those exercising assembly rights"},
    {"id": "whistleblowers", "name": "Whistleblowers", "description": "Those exposing wrongdoing"},
    {"id": "federal_employees", "name": "Federal Employees", "description": "Government workers"},
    {"id": "political_opposition", "name": "Political Opposition", "description": "Opposition party members/supporters"},
    {"id": "defense_attorneys", "name": "Defense Attorneys", "description": "Lawyers representing defendants"},
    {"id": "judges", "name": "Judges", "description": "Judicial officials"},
    {"id": "ngos", "name": "NGOs/Nonprofits", "description": "Civil society organizations"},
    {"id": "state_governments", "name": "State Governments", "description": "State-level government entities"},
    {"id": "local_governments", "name": "Local Governments", "description": "Municipal/county government entities"},
    {"id": "muslims", "name": "Muslims", "description": "Muslim individuals and communities"},
    {"id": "lgbtq", "name": "LGBTQ+ Individuals", "description": "LGBTQ+ community members"},
    {"id": "academics", "name": "Academics/Researchers", "description": "University faculty and researchers"},
    {"id": "students", "name": "Students", "description": "Particularly international and activist students"},
]
```

## Legal Frameworks

```python
LEGAL_FRAMEWORKS = [
    # Constitutional
    {"id": "1a_speech", "name": "1st Amendment - Free Speech", "type": "constitutional", 
     "citation": "U.S. Const. amend. I"},
    {"id": "1a_press", "name": "1st Amendment - Free Press", "type": "constitutional",
     "citation": "U.S. Const. amend. I"},
    {"id": "1a_assembly", "name": "1st Amendment - Assembly", "type": "constitutional",
     "citation": "U.S. Const. amend. I"},
    {"id": "1a_petition", "name": "1st Amendment - Petition", "type": "constitutional",
     "citation": "U.S. Const. amend. I"},
    {"id": "4a", "name": "4th Amendment - Search and Seizure", "type": "constitutional",
     "citation": "U.S. Const. amend. IV"},
    {"id": "5a_due_process", "name": "5th Amendment - Due Process", "type": "constitutional",
     "citation": "U.S. Const. amend. V"},
    {"id": "5a_self_incrimination", "name": "5th Amendment - Self-Incrimination", "type": "constitutional",
     "citation": "U.S. Const. amend. V"},
    {"id": "6a", "name": "6th Amendment - Right to Counsel", "type": "constitutional",
     "citation": "U.S. Const. amend. VI"},
    {"id": "8a", "name": "8th Amendment - Cruel and Unusual Punishment", "type": "constitutional",
     "citation": "U.S. Const. amend. VIII"},
    {"id": "10a", "name": "10th Amendment - State Powers", "type": "constitutional",
     "citation": "U.S. Const. amend. X"},
    {"id": "14a_due_process", "name": "14th Amendment - Due Process", "type": "constitutional",
     "citation": "U.S. Const. amend. XIV"},
    {"id": "14a_equal_protection", "name": "14th Amendment - Equal Protection", "type": "constitutional",
     "citation": "U.S. Const. amend. XIV"},
    
    # Statutory
    {"id": "apa", "name": "Administrative Procedure Act", "type": "statutory",
     "citation": "5 U.S.C. § 551 et seq."},
    {"id": "posse_comitatus", "name": "Posse Comitatus Act", "type": "statutory",
     "citation": "18 U.S.C. § 1385"},
    {"id": "privacy_act", "name": "Privacy Act", "type": "statutory",
     "citation": "5 U.S.C. § 552a"},
    {"id": "foia", "name": "Freedom of Information Act", "type": "statutory",
     "citation": "5 U.S.C. § 552"},
    {"id": "whistleblower_protection", "name": "Whistleblower Protection Act", "type": "statutory",
     "citation": "5 U.S.C. § 2302(b)(8)"},
    {"id": "cfaa", "name": "Computer Fraud and Abuse Act", "type": "statutory",
     "citation": "18 U.S.C. § 1030"},
    {"id": "tvpa", "name": "Torture Victim Protection Act", "type": "statutory",
     "citation": "28 U.S.C. § 1350"},
    {"id": "immigration_nationality", "name": "Immigration and Nationality Act", "type": "statutory",
     "citation": "8 U.S.C. § 1101 et seq."},
    {"id": "habeas_corpus", "name": "Habeas Corpus Statute", "type": "statutory",
     "citation": "28 U.S.C. § 2241"},
    {"id": "antideficiency", "name": "Antideficiency Act", "type": "statutory",
     "citation": "31 U.S.C. § 1341"},
    {"id": "impoundment_control", "name": "Impoundment Control Act", "type": "statutory",
     "citation": "2 U.S.C. § 681-688"},
    {"id": "hatch_act", "name": "Hatch Act", "type": "statutory",
     "citation": "5 U.S.C. § 7321-7326"},
    {"id": "emoluments", "name": "Emoluments Clause", "type": "constitutional",
     "citation": "U.S. Const. art. I, § 9, cl. 8"},
    
    # Treaty/International
    {"id": "cat", "name": "Convention Against Torture", "type": "treaty",
     "citation": "CAT, ratified by U.S. 1994"},
    {"id": "refugee_convention", "name": "1951 Refugee Convention/1967 Protocol", "type": "treaty",
     "citation": "U.S. acceded to Protocol 1968"},
    {"id": "iccpr", "name": "International Covenant on Civil and Political Rights", "type": "treaty",
     "citation": "ICCPR, ratified by U.S. 1992"},
    {"id": "non_refoulement", "name": "Non-Refoulement Principle", "type": "treaty",
     "citation": "CAT Art. 3; Refugee Convention Art. 33"},
]
```

## Patterns

```python
PATTERNS = [
    {
        "id": "executive_court_defiance",
        "name": "Executive Court Defiance",
        "description": "Pattern of executive branch treating judicial orders as advisory rather than binding",
        "historical_precedent": "Andrew Jackson allegedly defying Worcester v. Georgia; Nixon and the tapes"
    },
    {
        "id": "deportation_acceleration",
        "name": "Deportation Acceleration",
        "description": "Rapid deportation with reduced due process protections",
        "historical_precedent": "Operation Wetback 1954; post-9/11 special registration"
    },
    {
        "id": "press_intimidation",
        "name": "Press Intimidation",
        "description": "Actions designed to chill press coverage through access denial, legal threats, or targeting",
        "historical_precedent": "Nixon enemies list; Espionage Act prosecutions of sources"
    },
    {
        "id": "parallel_governance",
        "name": "Parallel Governance Structures",
        "description": "Creation of power centers outside normal legal/oversight frameworks",
        "historical_precedent": "Iran-Contra operations; warrantless surveillance programs"
    },
    {
        "id": "norm_erosion",
        "name": "Norm Erosion",
        "description": "Systematic violation of previously respected norms that lack legal enforcement",
        "historical_precedent": "Varied throughout history"
    },
    {
        "id": "inspector_general_neutralization",
        "name": "Inspector General Neutralization",
        "description": "Firing, sidelining, or undermining internal watchdogs",
        "historical_precedent": "2020 IG firings"
    },
    {
        "id": "sanctuary_confrontation",
        "name": "Sanctuary City Confrontation",
        "description": "Federal-state conflict over immigration enforcement cooperation",
        "historical_precedent": "Arizona SB 1070 era conflicts (reversed direction)"
    },
    {
        "id": "denaturalization_threat",
        "name": "Denaturalization Threat",
        "description": "Using citizenship revocation or threats against naturalized citizens",
        "historical_precedent": "1920s-30s denaturalization campaigns"
    },
    {
        "id": "protest_criminalization",
        "name": "Protest Criminalization",
        "description": "Using law enforcement and prosecution to suppress protest movements",
        "historical_precedent": "COINTELPRO; 1968 Democratic Convention; Standing Rock"
    },
    {
        "id": "data_weaponization",
        "name": "Data Weaponization",
        "description": "Using government databases for purposes beyond their authorized scope",
        "historical_precedent": "WWII Japanese internment used census data"
    },
]
```

## Sample Incidents

```python
SAMPLE_INCIDENTS = [
    {
        "title": "Deportation flights to El Salvador continue after federal court restraining order",
        "date": "2025-03-15",
        "category": "court_order_defiance",
        "actors": ["dhs", "ice"],
        "targets": ["asylum_seekers"],
        "legal_frameworks": ["5a_due_process", "habeas_corpus"],
        "patterns": ["executive_court_defiance", "deportation_acceleration"],
        "severity": "critical",
        "verification_status": "documented",
        "summary": "Federal judge in DC issued restraining order halting deportations to El Salvador under Alien Enemies Act. Within hours, DHS conducted deportation flight claiming the order was not properly served or didn't apply to those already in transit.",
        "sources": [
            {
                "type": "court_filing",
                "title": "J.G.G. v. Trump - Temporary Restraining Order",
                "reliability": "primary"
            },
            {
                "type": "news_primary",
                "title": "AP: Administration defies court order on deportations",
                "reliability": "secondary"
            }
        ]
    },
    {
        "title": "DOGE personnel access Treasury payment systems without security clearances",
        "date": "2025-02-03",
        "category": "unauthorized_data_access",
        "actors": ["doge", "treasury"],
        "targets": ["federal_employees"],
        "legal_frameworks": ["privacy_act", "cfaa"],
        "patterns": ["parallel_governance", "data_weaponization"],
        "severity": "high",
        "verification_status": "documented",
        "summary": "Individuals associated with DOGE given access to Treasury Department payment systems containing sensitive personal and financial data. Access granted without standard security clearance procedures.",
        "sources": [
            {
                "type": "court_filing",
                "title": "AFL-CIO v. U.S. Treasury - Complaint",
                "reliability": "primary"
            },
            {
                "type": "news_primary", 
                "title": "NYT: Musk associates gain access to federal payment systems",
                "reliability": "secondary"
            }
        ]
    },
    {
        "title": "ICE arrests at courthouse despite state policy",
        "date": "2025-02-15",
        "category": "federalism_violation",
        "actors": ["ice"],
        "targets": ["undocumented", "state_governments"],
        "legal_frameworks": ["10a", "immigration_nationality"],
        "patterns": ["sanctuary_confrontation"],
        "severity": "medium",
        "verification_status": "documented",
        "summary": "ICE conducted arrests inside state courthouse in jurisdiction with explicit policy prohibiting immigration enforcement in courts. Action chilled court attendance by witnesses in ongoing cases.",
        "sources": [
            {
                "type": "news_primary",
                "title": "Local news coverage with courthouse video",
                "reliability": "secondary"
            },
            {
                "type": "government_report",
                "title": "State Attorney General statement",
                "reliability": "primary"
            }
        ]
    },
    {
        "title": "Probationary federal employees terminated en masse without cause documentation",
        "date": "2025-02-10",
        "category": "due_process_violation",
        "actors": ["omb", "doge"],
        "targets": ["federal_employees"],
        "legal_frameworks": ["5a_due_process", "apa"],
        "patterns": ["parallel_governance"],
        "severity": "high",
        "verification_status": "documented",
        "summary": "Thousands of probationary federal employees across multiple agencies terminated simultaneously. Terminations reportedly coordinated through DOGE rather than normal OPM processes. Many employees received no specific cause.",
        "sources": [
            {
                "type": "news_primary",
                "title": "WaPo: Mass firings across federal agencies",
                "reliability": "secondary"
            },
            {
                "type": "firsthand_account",
                "title": "Compiled employee testimonies",
                "reliability": "secondary"
            }
        ]
    },
    {
        "title": "Associated Press excluded from White House briefing following coverage",
        "date": "2025-02-20",
        "category": "press_suppression",
        "actors": ["white_house"],
        "targets": ["journalists"],
        "legal_frameworks": ["1a_press"],
        "patterns": ["press_intimidation"],
        "severity": "medium",
        "verification_status": "documented",
        "summary": "AP correspondents excluded from White House press briefing. Exclusion followed critical coverage. White House Correspondents Association issued formal protest.",
        "sources": [
            {
                "type": "news_primary",
                "title": "WHCA Statement",
                "reliability": "primary"
            }
        ]
    }
]
```

## Source Types & Reliability

```python
SOURCE_TYPES = {
    "court_filing": {
        "description": "Official court documents, filings, orders",
        "default_reliability": "primary",
        "examples": ["Complaint", "Order", "Ruling", "Motion", "Brief"]
    },
    "government_report": {
        "description": "Official government reports, IG reports, GAO reports",
        "default_reliability": "primary",
        "examples": ["Inspector General Report", "GAO Audit", "Congressional Report"]
    },
    "foia": {
        "description": "Documents obtained through FOIA requests",
        "default_reliability": "primary",
        "examples": ["FOIA release", "Disclosed documents"]
    },
    "congressional_testimony": {
        "description": "Testimony before Congress",
        "default_reliability": "primary",
        "examples": ["Hearing testimony", "Deposition"]
    },
    "news_primary": {
        "description": "Original reporting from major news organizations",
        "default_reliability": "secondary",
        "examples": ["AP", "Reuters", "NYT", "WaPo", "WSJ investigation"]
    },
    "news_secondary": {
        "description": "News coverage citing other sources",
        "default_reliability": "secondary",
        "examples": ["Analysis pieces", "Aggregated reporting"]
    },
    "academic": {
        "description": "Peer-reviewed research or academic institution reports",
        "default_reliability": "secondary",
        "examples": ["Journal article", "University study"]
    },
    "ngo_report": {
        "description": "Reports from established civil liberties/human rights organizations",
        "default_reliability": "secondary",
        "examples": ["ACLU report", "Human Rights Watch", "Brennan Center"]
    },
    "firsthand_account": {
        "description": "Direct testimony from witnesses or participants",
        "default_reliability": "secondary",
        "examples": ["Affidavit", "Recorded interview", "Written statement"]
    },
    "video": {
        "description": "Video documentation",
        "default_reliability": "varies",
        "examples": ["Body camera", "Surveillance footage", "Journalist footage", "Bystander video"]
    },
    "leaked_document": {
        "description": "Unofficial release of internal documents",
        "default_reliability": "secondary",
        "requires_verification": True,
        "examples": ["Internal memo", "Email", "Draft policy"]
    },
    "social_media": {
        "description": "Social media posts, often from officials",
        "default_reliability": "tertiary",
        "examples": ["Official Twitter/X", "Press release on social media"]
    }
}

RELIABILITY_LEVELS = {
    "primary": "Direct evidence - court documents, official government records, FOIA releases, direct video",
    "secondary": "Credible reporting on primary sources - major news organizations, established NGOs, academic research",
    "tertiary": "Sources that should be corroborated - social media, opinion pieces, unverified accounts"
}
```

## Verification Status Definitions

```python
VERIFICATION_STATUS = {
    "unverified": "Newly entered, sources not yet reviewed",
    "pending_review": "In review queue, sources being validated",
    "disputed": "Conflicting evidence or credible counter-claims exist",
    "documented": "Multiple reliable sources confirm; factual basis established",
    "adjudicated": "Court ruling or official finding confirms (requires court_filing source)"
}

# Rules
VERIFICATION_RULES = [
    "Status 'adjudicated' requires at least one source of type 'court_filing'",
    "Status 'documented' requires at least two sources with 'primary' or 'secondary' reliability",
    "Status 'disputed' must include note explaining the dispute",
    "New ingestion items start as 'unverified' until human review"
]
```

## Severity Definitions

```python
SEVERITY_LEVELS = {
    "low": "Norm violations, minor procedural issues, isolated incidents with limited impact",
    "medium": "Clear legal violations, pattern formation, measurable harm to individuals or institutions",
    "high": "Significant constitutional violations, widespread harm, defiance of judicial authority",
    "critical": "Fundamental breakdown of rule of law, physical harm/death, mass scale violations"
}
```

---

## RSS Feed Sources (Initial List)

```python
RSS_FEEDS = [
    # Wire Services
    {"name": "AP News - Government", "url": "https://rsshub.app/apnews/topics/government", "priority": "high"},
    {"name": "Reuters - Politics", "url": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best&best-type=reuters-best-politics", "priority": "high"},
    
    # Major Papers
    {"name": "NYT - Politics", "url": "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml", "priority": "high"},
    {"name": "Washington Post - Politics", "url": "https://feeds.washingtonpost.com/rss/politics", "priority": "high"},
    
    # Investigative
    {"name": "ProPublica", "url": "https://www.propublica.org/feeds/propublica/main", "priority": "high"},
    {"name": "The Intercept", "url": "https://theintercept.com/feed/?rss", "priority": "medium"},
    {"name": "Reveal News", "url": "https://revealnews.org/feed/", "priority": "medium"},
    
    # Legal/Court
    {"name": "SCOTUSblog", "url": "https://www.scotusblog.com/feed/", "priority": "high"},
    {"name": "Lawfare", "url": "https://www.lawfareblog.com/rss.xml", "priority": "high"},
    {"name": "Just Security", "url": "https://www.justsecurity.org/feed/", "priority": "high"},
    
    # Civil Liberties
    {"name": "ACLU News", "url": "https://www.aclu.org/news/feed/", "priority": "medium"},
    {"name": "Brennan Center", "url": "https://www.brennancenter.org/rss/all", "priority": "medium"},
    
    # Immigration Specific  
    {"name": "Immigration Impact", "url": "https://immigrationimpact.com/feed/", "priority": "high"},
]

# Keywords for filtering
RELEVANCE_KEYWORDS = [
    # Actions
    "detained", "deported", "arrested", "raided", "targeted", "fired", "terminated",
    "defied", "ignored", "violated", "blocked", "restricted", "banned", "surveilled",
    
    # Actors
    "ICE", "CBP", "DHS", "DOGE", "DOJ", "FBI", "administration", "executive order",
    
    # Legal
    "court order", "injunction", "restraining order", "lawsuit", "constitutional",
    "due process", "habeas corpus", "civil rights", "civil liberties",
    
    # Subjects
    "immigrant", "deportation", "asylum", "refugee", "journalist", "press freedom",
    "protester", "whistleblower", "sanctuary",
    
    # Patterns
    "authoritarian", "overreach", "abuse of power", "corruption", "unprecedented"
]
```

This seed data should be loaded during Phase 1, Milestone 1.3.

# GADB Quick Start Guide for Claude Code

## How to Use These Documents

### Document 1: Main Implementation Prompt

**File: `GADB_Claude_Code_Prompt.md`**

This is the primary prompt to give Claude Code. It contains:

- Complete project specification
- All 7 phases with milestones
- Detailed tasks for each milestone
- Test requirements (pytest + Playwright)
- Success criteria

**Usage:** Copy this into Claude Code as your initial prompt. Claude Code should work through it phase by phase, milestone by milestone.

### Document 2: Seed Data Specification

**File: `GADB_Seed_Data.md`**

Reference data for Claude Code to use when implementing:

- Category definitions
- Agency hierarchy
- Target categories
- Legal frameworks
- Pattern definitions
- Sample incidents
- RSS feed sources
- Keyword lists

**Usage:** Provide this as a second document or reference it