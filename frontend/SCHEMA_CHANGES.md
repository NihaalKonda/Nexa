# Schema Changes - Simplified Architecture

This document describes the major changes made to the database schema to simplify the architecture.

## Summary of Changes

### 1. Removed User Model - Company-Based Authentication

**Before:**
- Separate `User` and `Company` models
- Users belonged to companies
- Multi-user per company

**After:**
- Single `Company` model with auth fields
- Companies register directly with email/password
- One company = one account (can be extended later)

**Benefits:**
- Simpler authentication flow
- Easier to reason about data ownership
- Faster MVP development

---

### 2. Added Supplier Model (Separate Database)

**New Model: `Supplier`**
```prisma
model Supplier {
  id                  String
  name                String
  website             String?
  contactEmail        String?
  contactPhone        String?
  address             String?
  city                String?
  country             String?
  certificationsJson  Json?
  rating              Float?
  verified            Boolean
  description         String?
  products            Product[]  // One-to-many relation
}
```

**Features:**
- Complete supplier information database
- Verified flag for trusted suppliers
- Rating system
- Certifications stored as JSON
- Separate from products (normalized design)

---

### 3. Updated Product Model with Relational Link to Supplier

**Before:**
```prisma
model Product {
  supplierId  String?  // Just a string reference
}
```

**After:**
```prisma
model Product {
  supplier    Supplier  @relation(fields: [supplierId], references: [id])
  supplierId  String    // Foreign key - required
}
```

**Benefits:**
- Proper relational database design
- Can easily fetch product with supplier details
- Referential integrity (cascading deletes)
- Better query performance with joins

**New Fields:**
- `imageUrl` - Product image
- `description` - Detailed product description
- `inStock` - Availability status

---

### 4. Added SessionTableData Model

**New Model:**
```prisma
model SessionTableData {
  id          String
  sessionId   String
  tableKey    String    // e.g., "product_search_results"
  data        Json      // Stores table state
}
```

**Purpose:**
- Persist UI table state per session
- Store search results, filters, sort order, pagination
- Restore user's view when they return
- Session-scoped data management

**Use Cases:**
- Save product search results
- Persist RFP list filters
- Remember supplier list sorting
- Cache filtered data

---

### 5. Simplified Session Model

**Changes:**
- Sessions now link to `Company` instead of `User`
- Added relations: `sessionTableData`, `searchQueries`, `rfps`
- Track which session created which data

---

### 6. Updated Related Models

**SearchQuery:**
- Removed `userId` field
- Kept `companyId` (company-level tracking)
- Added optional `sessionId` (session-level tracking)
- Added `resultsCount` field

**RFP:**
- Removed `userId` field
- Kept `companyId` (company-level ownership)
- Added optional `sessionId` (creation tracking)

---

## Migration Guide

### Step 1: Backup Current Data

If you have existing data, export it before migrating:

```bash
# Export data
npx prisma db pull
pg_dump DATABASE_URL > backup.sql
```

### Step 2: Reset Database (Development Only)

For development, you can reset the database:

```bash
npx prisma migrate reset
```

### Step 3: Push New Schema

```bash
# Generate Prisma client with new schema
npx prisma generate

# Push schema to database
npx prisma db push
```

### Step 4: Seed New Data

Use the updated seed script:

```bash
npx prisma db seed
```

---

## Example Seed Script

```typescript
import { PrismaClient } from '../src/generated/prisma'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  // Create a company (replaces User + Company)
  const hashedPassword = await bcrypt.hash('password123', 10)

  const company = await prisma.company.create({
    data: {
      name: 'Acme Manufacturing',
      slug: 'acme-manufacturing',
      email: 'admin@acme.com',
      password: hashedPassword,
      city: 'San Francisco',
      country: 'USA',
    },
  })

  // Create suppliers
  const supplier1 = await prisma.supplier.create({
    data: {
      name: 'Industrial Parts Co.',
      website: 'https://industrialparts.com',
      contactEmail: 'sales@industrialparts.com',
      city: 'Chicago',
      country: 'USA',
      verified: true,
      rating: 4.5,
      certificationsJson: {
        certifications: ['ISO 9001', 'CE', 'UL'],
      },
    },
  })

  const supplier2 = await prisma.supplier.create({
    data: {
      name: 'Global Manufacturing Ltd',
      website: 'https://globalmfg.com',
      contactEmail: 'contact@globalmfg.com',
      city: 'Shanghai',
      country: 'China',
      verified: true,
      rating: 4.2,
    },
  })

  // Create products linked to suppliers
  await prisma.product.createMany({
    data: [
      {
        supplierId: supplier1.id,
        name: 'Industrial Valve Type A',
        sku: 'IV-A-001',
        mpn: 'MPN12345',
        priceText: '$150.00',
        currency: 'USD',
        unit: 'each',
        score: 0.95,
        inStock: true,
        description: 'High-pressure industrial valve for heavy-duty applications',
      },
      {
        supplierId: supplier1.id,
        name: 'Steel Pipe 6 inch',
        sku: 'SP-6-001',
        priceText: '$45.00',
        currency: 'USD',
        unit: 'ft',
        score: 0.88,
        inStock: true,
      },
      {
        supplierId: supplier2.id,
        name: 'Hydraulic Cylinder HC200',
        sku: 'HC-200',
        mpn: 'HC200-XL',
        priceText: '$850.00',
        currency: 'USD',
        unit: 'each',
        score: 0.92,
        inStock: true,
      },
    ],
  })

  console.log('✅ Seed data created successfully!')
  console.log(`Company: ${company.email} / password123`)
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
```

---

## API Usage Examples

### Fetching Products with Supplier Info

```typescript
const products = await prisma.product.findMany({
  include: {
    supplier: {
      select: {
        name: true,
        verified: true,
        rating: true,
        country: true,
      },
    },
  },
})
```

### Saving Table State

```typescript
await prisma.sessionTableData.upsert({
  where: {
    sessionId_tableKey: {
      sessionId: session.id,
      tableKey: 'product_search_results',
    },
  },
  update: {
    data: {
      filters: { category: 'valves' },
      sort: { field: 'price', order: 'asc' },
      results: [...],
    },
  },
  create: {
    sessionId: session.id,
    tableKey: 'product_search_results',
    data: { ... },
  },
})
```

### Company Authentication

```typescript
const company = await prisma.company.findUnique({
  where: { email: 'admin@acme.com' },
})

const isValid = await bcrypt.compare(password, company.password)
```

---

## Breaking Changes

### Code Updates Required

1. **Authentication:**
   - Update auth flows to use `Company` instead of `User`
   - Update session callbacks
   - ✅ Already updated in `src/lib/auth.ts`

2. **API Routes:**
   - Remove `userId` references
   - Use `companyId` from session
   - ✅ Already updated in API routes

3. **Type Definitions:**
   - Update types to reflect new schema
   - Remove `User` types, use `Company`

---

## Database Diagram

```
┌──────────────┐
│   Company    │
│──────────────│
│ id           │──┐
│ name         │  │
│ email        │  │  One-to-Many
│ password     │  │
└──────────────┘  │
                  │
                  ├──> ┌──────────────┐
                  │    │   Session    │
                  │    │──────────────│
                  │    │ id           │──┐
                  │    │ sessionToken │  │
                  │    │ companyId    │  │  One-to-Many
                  │    └──────────────┘  │
                  │                      │
                  │                      ├──> ┌────────────────────┐
                  │                      │    │ SessionTableData   │
                  │                      │    │────────────────────│
                  │                      │    │ id                 │
                  │                      │    │ sessionId          │
                  │                      │    │ tableKey           │
                  │                      │    │ data (JSON)        │
                  │                      │    └────────────────────┘
                  │                      │
                  │                      └──> ┌──────────────┐
                  │                           │ SearchQuery  │
                  │                           │──────────────│
                  │                           │ id           │
                  │                           │ sessionId    │
                  │                           │ query        │
                  │                           └──────────────┘
                  │
                  └──> ┌──────────────┐
                       │     RFP      │
                       │──────────────│
                       │ id           │
                       │ companyId    │
                       │ sessionId    │
                       └──────────────┘

┌──────────────┐       ┌──────────────┐
│   Supplier   │       │   Product    │
│──────────────│       │──────────────│
│ id           │◄──────│ id           │
│ name         │  1:N  │ supplierId   │ (Foreign Key)
│ verified     │       │ name         │
│ rating       │       │ price        │
└──────────────┘       └──────────────┘
```

---

## Next Steps

1. Run `npx prisma generate` to update Prisma client
2. Run `npx prisma db push` to apply schema changes
3. Update seed script with new models
4. Test authentication with Company model
5. Test product searches with supplier relations
6. Implement session table data persistence in UI

---

## Questions?

See [SETUP.md](./SETUP.md) for full setup instructions or [README.md](./README.md) for project overview.
