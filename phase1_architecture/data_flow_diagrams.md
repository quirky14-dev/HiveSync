
# Data Flow Diagrams

This document contains the full set of expanded, unified, and consistently formatted data‑flow diagrams for HiveSync. All diagrams have been updated to reflect the restored concepts (Project Manifest, comment threading, multi‑file AI refactor pipeline, future messaging backbone, and multi‑stage preview cleanup). All Mermaid diagrams are included in fully expanded form.

---

# 1. AI Documentation Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client (Desktop/Plugin)
    participant B as Backend API
    participant W as AI Worker
    participant M as Repo Mirror
    participant S as Storage

    C->>B: Submit AI Documentation Request
    B->>B: Validate Project + Permissions
    B->>W: Queue AI Job

    W->>M: Read Repo Mirror
    W->>W: Build Context from Manifest
    W->>S: (Optional) Load Additional Assets
    W->>AI: Request Documentation Output
    AI-->>W: Structured Suggestions

    W->>B: Store AI Results in DB
    C->>B: Poll or Receive Notification
    B-->>C: AI Suggestions (Linked to Manifest)
```

---

# 2. Multi‑File Variable Rename / Refactor Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client (Desktop/Plugin)
    participant B as Backend API
    participant W as Refactor Worker
    participant M as Repo Mirror

    C->>B: Submit Variable Rename Request
    B->>B: Validate & Persist Request
    B->>W: Queue Refactor Job

    W->>M: Analyze Repo Mirror (Symbol Graph)
    W->>W: Generate Cross‑File Proposal Set
    W->>B: Store Proposed Changes

    C->>B: Request Proposal Set
    B-->>C: Return Refactor Suggestions (Diffs)

    C->>B: Approve Changes
    B->>W: Queue Apply‑Changes Job

    W->>M: Apply Updates to Repo Mirror
    W->>B: Update Manifest + Metadata
```

---

# 3. Comment Threading & AI Documentation Thread Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client UI
    participant B as Backend API
    participant D as DB (Comment Store)
    participant W as AI Worker

    C->>B: Create/Update Comment Thread
    B->>D: Persist Thread + Anchors
    C->>B: Request AI Help on Thread
    B->>W: Queue Thread‑Context AI Job

    W->>D: Load Thread History
    W->>AI: Generate AI Response
    AI-->>W: AI Comment Suggestion
    W->>D: Persist AI Suggestion in Thread
    C->>B: Poll or Receive Notification
    B-->>C: Updated Thread with AI Response
```

---

# 4. Preview Flow (Desktop → Backend → Mobile)

```mermaid
sequenceDiagram
    autonumber
    participant D as Desktop App
    participant B as Backend API
    participant S as Storage
    participant M as Mobile App

    D->>B: Request Preview Session
    B->>B: Generate Preview Token
    B-->>D: Return Token

    D->>D: Build Preview Bundle
    D->>S: Upload Bundle
    D->>B: Notify Bundle Ready

    M->>B: Enter Preview Token
    B->>S: Lookup Bundle Metadata
    B-->>M: Return Bundle URL

    M->>S: Download Bundle
    M->>M: Render Preview
```

---

# 5. Repo Sync Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant B as Backend API
    participant W as Repo Sync Worker
    participant G as Git Remote
    participant M as Repo Mirror

    C->>B: Request Repo Sync
    B->>W: Queue Sync Job

    W->>G: Fetch / Clone Repo
    W->>M: Update Repo Mirror
    W->>B: Store Sync Metadata

    C->>B: Poll for Completion
    B-->>C: Sync Completed Event
```

---

# 6. Multi‑Stage Preview Cleanup Flow

```mermaid
sequenceDiagram
    autonumber
    participant B as Backend API
    participant W as Cleanup Worker
    participant S as Storage
    participant DB as Database

    B->>DB: Mark Expired Tokens
    DB->>W: Emit Expired‑Bundle List

    W->>S: Soft Delete Bundles
    W->>DB: Mark Soft‑Deleted

    W->>S: Purge Bundles Permanently
    W->>DB: Update Cleanup Metadata
```

---

# 7. Project Manifest Generation Flow

```mermaid
sequenceDiagram
    autonumber
    participant B as Backend
    participant W as Worker
    participant M as Repo Mirror
    participant D as DB

    B->>W: Request Manifest Update
    W->>M: Read Repo Mirror
    W->>W: Compute Metadata + Hash Map
    W->>D: Write Manifest Snapshot
    B-->>Client: Updated Manifest Available
```

---

# 8. Future Messaging Backbone (Placeholder Diagram)

```mermaid
sequenceDiagram
    autonumber
    participant W as Worker
    participant E as Event Bus
    participant B as Backend API
    participant C as Clients

    W->>E: Publish Event
    E->>B: Deliver Event to Backend
    B->>C: Notify Clients via Push/Poll
```

---

*(End of file)*
