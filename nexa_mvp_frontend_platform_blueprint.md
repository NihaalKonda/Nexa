# Nexa — MVP Frontend & Platform Blueprint

This document lays out pragmatic framework choices and a reference architecture so you can ship Nexa quickly: company sign‑up, product search, and GenAI RFP generation.

---

## What Nexa Needs (MVP scope)
1) **Company Registration & Auth** — Company name, password, location; invite teammates later.
2) **Product Search UI** — Query box + filters; results fed by your backend/search index.
3) **GenAI RFP Builder** — Guided form → prompt → draft RFP → editable preview → export (PDF/Docx) and share.
4) **Basic Admin** — View companies, manage usage, feature flags.

---

## Recommended Stack Options

### Option A — **JavaScript‑first (ship fastest)**
**Best for:** Speed, smallest team, great DX, SSR/ISR, edge functions.

- **Framework:** Next.js 15 (App Router) + **TypeScript**
- **Hosting:** **Vercel** (preview deployments, edge/runtime flexibility)
- **Auth:** **Auth.js (NextAuth)** with email+password and OAuth (optional)
- **DB:** **Supabase Postgres** (managed Postgres + RLS + storage)
- **ORM:** **Prisma**
- **Search:** **Meilisearch** (managed via Meili Cloud) or **Typesense Cloud**
- **UI:** **Tailwind CSS** + **shadcn/ui** (+ Radix primitives)
- **State/Data:** **TanStack Query**; light local store with **Zustand** if needed
- **GenAI:** Provider SDK (e.g., OpenAI/Anthropic/Azure OpenAI) via **server actions** or **route handlers**
- **Email:** **Resend** (magic links, invites)
- **Files/Export:** **Supabase Storage** + **react-pdf** (or server-side **pdf-lib**) for RFP export
- **Analytics/Error:** **PostHog** + **Sentry**

**Why this option**
- 1 repo, 1 language. SSR + static where possible. Easiest deploys.
- Scales to early product-market fit without major rewrites.

---

### Option B — **Python‑friendly (ML/agents nearby)**
**Best for:** Heavy Python/ML needs, custom scrapers/agents.

- **Frontend:** Next.js (as above)
- **Backend (services):** **FastAPI** on **Railway/Fly.io/Render**
- **DB:** Supabase Postgres (still great) or Neon
- **Search:** Meilisearch/Typesense (managed)
- **GenAI:** Call from FastAPI (Python SDKs); frontend hits Next route → FastAPI

**Why this option**
- Keep UI velocity of Next.js; run Python where it shines.

---

### Option C — **Firebase‑heavy (no custom backend initially)**
**Best for:** Extreme speed, minimal ops, early prototypes.

- **Frontend:** Next.js
- **Auth/DB:** Firebase Auth + Firestore
- **Search:** Algolia (excellent with Firestore)
- **GenAI:** Edge functions or Cloud Functions

**Trade‑off:** Migrating complex SQL and joins later can be painful.

---

## Suggested Pick for Nexa
**Option A (Next.js + Supabase + Meilisearch + Auth.js)** for the MVP, with an optional **FastAPI microservice** later when you productize scraping/agents.

---

## High‑Level Architecture
```
[Browser]
  └─ Next.js (App Router)
      ├─ UI (Tailwind + shadcn)
      ├─ Server Actions/Route Handlers (/app/api/*)
      │    ├─ Prisma → Supabase (Postgres)
      │    ├─ Search Client → Meilisearch/Typesense
      │    └─ GenAI Provider SDK (RFP drafts)
      └─ Edge Middleware (auth checks, A/B flags)

[Supabase]
  ├─ Postgres (companies, users, products, rfps)
  ├─ RLS policies
  └─ Storage (attachments, exports)

[Search]
  └─ Meilisearch/Typesense (indexed product docs)

[Emails]
  └─ Resend (invites, verification, notifications)

[Observability]
  ├─ Sentry (errors)
  └─ PostHog (analytics, feature flags if needed)
```

---

## Data Model (initial)
```sql
Company(id, name, slug, location_city, location_country, created_at)
User(id, company_idFK, email, password_hash, role, created_at)
Product(id, supplier_id, name, sku, mpn, price_text, currency, unit,
        specs_json, certifications_json, source_url, last_seen_at, score)
SearchQuery(id, company_idFK, user_idFK, q, filters_json, created_at)
RFP(id, company_idFK, user_idFK, title, body_md, status, draft_json,
    created_at, updated_at)
RFPShare(id, rfp_idFK, link_token, expires_at)
```
- Keep **raw scraped** fields; also maintain a **canonicalized** subset.
- Use **RLS** so users can read/write only their company’s rows.

---

## Pages & Routes (Next.js App Router)
```
/app
  /(public)
    /page.tsx                # Landing
    /pricing/page.tsx
  /auth
    /signup/page.tsx
    /signin/page.tsx
  /dashboard
    /page.tsx                # Overview
    /search/page.tsx         # Product search UI
    /rfp
      /new/page.tsx          # GenAI RFP builder
      /[id]/page.tsx         # Editor/preview
    /settings/page.tsx
  /api
    /auth/*                  # Auth.js handlers
    /products/search/route.ts
    /rfp/generate/route.ts
    /rfp/[id]/export/route.ts
  layout.tsx
```

---

## UI/UX Components (shadcn/ui + Tailwind)
- **Auth:** Email/password form, password strength meter
- **Search:** Search bar, facets panel (supplier, price range, certifications), result cards, infinite scroll
- **RFP Builder:** Stepper (scope → requirements → delivery → terms), AI prompt sidebar, editable preview (Markdown + toolbar), export buttons
- **Global:** Top nav, user menu, company switcher (future), toast system

---

## Search Layer
- Pick **Meilisearch** (managed) for zero‑config speed.
- Index fields: `name`, `sku`, `mpn`, `specs_text`, `certifications`, `supplier`, `score`.
- Set searchable attributes + filterable facets. Support typo‑tolerance and synonyms.
- Ingest via a small server action/cron from your product DB.

---

## GenAI RFP Generation
- Server‑side function (keeps keys safe). Inputs: company profile, product shortlist, constraints (budget, delivery window, standards/certs), location.
- Output: structured `draft_json` + human‑readable Markdown.
- Provide temperature slider + style presets (formal/concise/comprehensive).
- Persist each generation to `RFP` for auditability and edits.

**Prompt skeleton (server):**
```
System: You are a procurement specialist drafting RFPs.
User: Create an RFP for {category} to be delivered to {location} by {date}.
Consider {standards/certs}, preferred suppliers {list}, and budget {amount}.
Return a structured JSON with sections: Overview, Scope, Technical Requirements, Compliance, Delivery, Evaluation Criteria, Submission Instructions.
```

---

## Security & Auth
- **Auth.js** credentials provider with email+password; add OAuth later (Google/Microsoft) for enterprises.
- **RLS** on Supabase with `company_id` scoping.
- Enforce **password hashing** (bcrypt/argon2) server‑side; never send raw passwords to the client.
- Add **rate limits** on `/api/*` (middleware) and basic WAF via Vercel.

---

## Dev → Prod Flow
- Branch‑based previews on Vercel.
- `.env` per environment; never commit secrets.
- Seed script for local dev (dummy companies/products).
- Migrations via Prisma.

---

## Quickstart Commands (Option A)
```bash
npx create-next-app@latest nexa --ts --eslint --app --tailwind
cd nexa
pnpm add @tanstack/react-query zod @hookform/resolvers react-hook-form zustand \
  @supabase/supabase-js next-auth @auth/prisma-adapter prisma @prisma/client \
  class-variance-authority clsx next-themes

pnpm dlx prisma init
# set DATABASE_URL to Supabase in .env
pnpm dlx prisma migrate dev

# UI kit
pnpm dlx shadcn-ui@latest init
pnpm dlx shadcn-ui@latest add button card input textarea table dialog toast skeleton

# Deploy
pnpm dlx vercel
```

---

## Minimal Prisma Schema Snippet
```prisma
model Company {
  id       String  @id @default(cuid())
  name     String
  slug     String  @unique
  city     String?
  country  String?
  users    User[]
  rfps     RFP[]
  createdAt DateTime @default(now())
}

model User {
  id         String   @id @default(cuid())
  email      String   @unique
  password   String   // hashed
  role       String   @default("member")
  company    Company  @relation(fields: [companyId], references: [id])
  companyId  String
  createdAt  DateTime @default(now())
}

model RFP {
  id         String   @id @default(cuid())
  company    Company  @relation(fields: [companyId], references: [id])
  companyId  String
  title      String
  bodyMd     String
  draftJson  Json
  status     String   @default("draft")
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt
}
```

---

## Example Route Handlers (Next.js)
```ts
// app/api/products/search/route.ts
import { NextRequest } from "next/server";
import { meili } from "@/lib/meili";

export async function POST(req: NextRequest) {
  const { q, filters, page = 1 } = await req.json();
  const res = await meili.index("products").search(q ?? "", {
    filter: filters || undefined,
    page,
    hitsPerPage: 20,
  });
  return Response.json(res);
}
```

```ts
// app/api/rfp/generate/route.ts
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { generateRfp } from "@/lib/ai";

export async function POST(req: Request) {
  const session = await auth(); // server-side check
  if (!session) return new Response("Unauthorized", { status: 401 });

  const payload = await req.json(); // {title, companyId, params}
  const draft = await generateRfp(payload);
  const rfp = await prisma.rFP.create({
    data: {
      companyId: payload.companyId,
      title: payload.title,
      bodyMd: draft.markdown,
      draftJson: draft.json,
    },
  });
  return Response.json(rfp);
}
```

---

## Styling & Branding
- Name: **Nexa**
- Design: clean, industrial‑grade feel (blues/neutral grays), rounded‑xl cards, soft shadows.
- Typography: Inter; monospaced accents for specs.

---

## Roadmap After MVP
- Team invites & roles (admin, buyer, approver)
- Saved searches & alerts
- Supplier portal (submit bids securely)
- RFP templates library; comparison matrix
- SSO (Google/Microsoft), SCIM for enterprise
- Audit log & SOC2 readiness basics

---

### TL;DR
Use **Next.js + Supabase + Meilisearch + Auth.js + Tailwind/shadcn + Vercel**. Add a Python **FastAPI** service later for heavier AI/agent workloads. This setup gets Nexa live fast and won’t block you as requirements grow.

