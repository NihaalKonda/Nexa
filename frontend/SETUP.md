# Nexa Frontend Setup Guide

This guide will walk you through setting up the Nexa frontend application using **Option A** from the architecture blueprint: Next.js + Supabase + Auth.js + Vercel.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Supabase Setup](#supabase-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup with Prisma](#database-setup-with-prisma)
5. [Running Locally](#running-locally)
6. [Deploying to Vercel](#deploying-to-vercel)
7. [Using v0 by Vercel](#using-v0-by-vercel)
8. [Optional Services](#optional-services)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Node.js** 18+ and npm/pnpm/yarn
- A **Supabase** account (free tier is fine)
- A **Vercel** account (optional, for deployment)
- **Git** for version control

---

## Supabase Setup

### Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click **"New Project"**
3. Fill in the details:
   - **Project Name**: `nexa` (or your choice)
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Select closest to your users
   - **Pricing Plan**: Start with Free
4. Click **"Create new project"** and wait 2-3 minutes

### Step 2: Get Your Supabase Credentials

Once your project is ready:

1. Go to **Project Settings** (gear icon in sidebar)
2. Navigate to **API** section
3. Copy the following values:
   - **Project URL**: `https://[YOUR-PROJECT-REF].supabase.co`
   - **anon/public key**: This is your `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role key**: This is your `SUPABASE_SERVICE_ROLE_KEY` (keep secret!)

4. Navigate to **Database** section
5. Scroll down to **Connection String** → **URI**
6. Copy the connection string (it will look like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```
   Replace `[YOUR-PASSWORD]` with the database password you created in Step 1.

### Step 3: Configure Row Level Security (RLS)

Supabase uses RLS to secure your data. We'll set this up after creating tables.

---

## Environment Configuration

### Step 1: Create `.env` File

In the `frontend/` directory, copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Fill in Environment Variables

Open `.env` and update with your Supabase credentials:

```env
# Database - Supabase Postgres URL
DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# NextAuth Configuration
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-here"  # Generate with: openssl rand -base64 32

# Supabase
NEXT_PUBLIC_SUPABASE_URL="https://[YOUR-PROJECT-REF].supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="your-supabase-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"
```

### Step 3: Generate NextAuth Secret

Run this command to generate a secure secret:

```bash
openssl rand -base64 32
```

Copy the output and paste it as your `NEXTAUTH_SECRET`.

---

## Database Setup with Prisma

### Step 1: Install Dependencies

If you haven't already, install all dependencies:

```bash
npm install
```

### Step 2: Generate Prisma Client

```bash
npx prisma generate
```

This creates the Prisma client in `src/generated/prisma`.

### Step 3: Push Schema to Supabase

```bash
npx prisma db push
```

This will:
- Create all tables in your Supabase database
- Set up relationships and indexes
- Show you a preview of changes

**Note**: For production, use `npx prisma migrate dev` to create migration files.

### Step 4: Verify Tables in Supabase

1. Go to your Supabase dashboard
2. Click **"Table Editor"** in the sidebar
3. You should see tables: `Company`, `User`, `Product`, `RFP`, `SearchQuery`, `RFPShare`, `Account`, `Session`, `VerificationToken`

### Step 5: Set Up Row Level Security (Optional but Recommended)

In Supabase dashboard:

1. Go to **Authentication** → **Policies**
2. For each table (`Company`, `User`, `RFP`, etc.), create policies like:

**Example Policy for `RFP` table:**
```sql
-- Enable RLS
ALTER TABLE "RFP" ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their company's RFPs
CREATE POLICY "Users can view own company RFPs"
ON "RFP"
FOR SELECT
USING (
  "companyId" IN (
    SELECT "companyId" FROM "User" WHERE id = auth.uid()
  )
);
```

**Note**: Since we're using NextAuth (not Supabase Auth), you may handle authorization in your API routes instead of RLS. RLS is optional for this setup.

---

## Running Locally

### Step 1: Start Development Server

```bash
npm run dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

### Step 2: Test the Application

1. **Landing Page**: Visit `http://localhost:3000`
2. **Sign Up**: Go to `/auth/signup` (you'll need to create this page)
3. **Dashboard**: After auth, visit `/dashboard`
4. **Search**: Try `/dashboard/search`
5. **Create RFP**: Visit `/dashboard/rfp/new`

### Step 3: Seed Database (Optional)

Create a seed script to populate your database with sample data:

```bash
npx prisma db seed
```

(You'll need to create `prisma/seed.ts` - see example below)

---

## Deploying to Vercel

### Step 1: Install Vercel CLI

```bash
npm i -g vercel
```

### Step 2: Deploy

From the `frontend/` directory:

```bash
vercel
```

Follow the prompts:
- Link to existing project or create new
- Set up project settings
- Add environment variables

### Step 3: Add Environment Variables in Vercel Dashboard

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add all variables from your `.env` file:
   - `DATABASE_URL`
   - `NEXTAUTH_URL` (update to your production URL)
   - `NEXTAUTH_SECRET`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

4. Redeploy to apply changes

### Step 4: Update NEXTAUTH_URL

After deployment, update `NEXTAUTH_URL` in Vercel environment variables to your production URL:

```
NEXTAUTH_URL=https://your-app.vercel.app
```

---

## Using v0 by Vercel

[v0](https://v0.dev) is Vercel's AI-powered UI generator. Use it to quickly create components for Nexa.

### How to Use v0:

1. Go to [v0.dev](https://v0.dev)
2. Sign in with your Vercel account
3. Describe the component you want:
   - "Create a product search card with image, title, price, and specs"
   - "Build an RFP form with title, category, budget, and delivery date"
   - "Design a modern pricing table with 3 tiers"

4. Copy the generated code
5. Paste into your project:
   ```
   frontend/src/components/ProductCard.tsx
   frontend/src/components/RfpForm.tsx
   frontend/src/components/PricingTable.tsx
   ```

### Example v0 Prompts for Nexa:

- **Product Search Card**:
  > "Create a product card component showing product name, SKU, supplier, price, certifications badges, and a 'View Details' button. Use Tailwind CSS and shadcn/ui styling."

- **RFP Builder Form**:
  > "Build a multi-step form for creating an RFP with steps: 1) Basic Info (title, category), 2) Requirements (specs, budget), 3) Delivery (location, date), 4) Review. Use shadcn/ui form components."

- **Dashboard Layout**:
  > "Create a dashboard layout with sidebar navigation (Search, RFPs, Settings, Profile) and a main content area. Include a top header with company name and user menu."

### Integrating v0 Components:

1. Install any missing shadcn/ui components:
   ```bash
   npx shadcn@latest add [component-name]
   ```

2. Update imports to match your project structure

3. Connect to your API routes and state management

---

## Optional Services

### 1. Meilisearch (Product Search)

**Setup:**
1. Go to [Meilisearch Cloud](https://www.meilisearch.com/cloud)
2. Create a free project
3. Get your host URL and API key
4. Add to `.env`:
   ```env
   MEILISEARCH_HOST="https://your-instance.meilisearch.io"
   MEILISEARCH_API_KEY="your-api-key"
   ```

**Create Index:**
```bash
# Install Meilisearch SDK
npm install meilisearch

# Then in your code or a script:
import { MeiliSearch } from 'meilisearch'

const client = new MeiliSearch({
  host: process.env.MEILISEARCH_HOST,
  apiKey: process.env.MEILISEARCH_API_KEY,
})

await client.createIndex('products', { primaryKey: 'id' })
```

**Index Products:**
Create a script to sync your Prisma products to Meilisearch.

### 2. Resend (Email)

**Setup:**
1. Go to [Resend](https://resend.com)
2. Sign up and verify your domain (or use their test domain)
3. Get API key
4. Add to `.env`:
   ```env
   RESEND_API_KEY="re_..."
   ```

**Install:**
```bash
npm install resend
```

**Usage:**
```typescript
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

await resend.emails.send({
  from: 'Nexa <onboarding@yourdomain.com>',
  to: user.email,
  subject: 'Welcome to Nexa',
  html: '<p>Welcome!</p>',
})
```

### 3. OpenAI or Anthropic (RFP Generation)

**OpenAI:**
```bash
npm install openai
```

```env
OPENAI_API_KEY="sk-..."
```

**Anthropic (Claude):**
```bash
npm install @anthropic-ai/sdk
```

```env
ANTHROPIC_API_KEY="sk-ant-..."
```

Update `src/app/api/rfp/generate/route.ts` to use your chosen AI provider.

### 4. PostHog (Analytics)

**Setup:**
1. Go to [PostHog](https://posthog.com)
2. Create a project
3. Get your API key and host
4. Add to `.env`:
   ```env
   NEXT_PUBLIC_POSTHOG_KEY="phc_..."
   NEXT_PUBLIC_POSTHOG_HOST="https://app.posthog.com"
   ```

**Install:**
```bash
npm install posthog-js
```

---

## Troubleshooting

### Issue: Prisma Client Not Found

**Solution:**
```bash
npx prisma generate
```

### Issue: Database Connection Error

**Check:**
- Is `DATABASE_URL` correct in `.env`?
- Is your Supabase project running?
- Did you replace `[YOUR-PASSWORD]` with your actual password?

**Test connection:**
```bash
npx prisma db pull
```

### Issue: NextAuth Session Not Working

**Check:**
- Is `NEXTAUTH_SECRET` set?
- Is `NEXTAUTH_URL` correct?
- Are you using the correct session strategy in `src/lib/auth.ts`?

### Issue: API Routes Return 401

**Check:**
- Are you calling `getServerSession(authOptions)` in your API routes?
- Is the user logged in?
- Check browser console for auth errors

### Issue: Build Errors on Vercel

**Common fixes:**
- Run `npm run build` locally first
- Check that all environment variables are set in Vercel dashboard
- Ensure `DATABASE_URL` is accessible from Vercel (check Supabase IP allowlist if needed)

---

## Next Steps

1. **Create Auth Pages**: Build signup/signin forms in `src/app/auth/`
2. **Add UI Components**: Use v0 or shadcn/ui to build out your UI
3. **Implement Search**: Connect to Meilisearch or implement Prisma full-text search
4. **Add AI RFP Generation**: Integrate OpenAI or Anthropic in the RFP generate route
5. **Set Up Email**: Configure Resend for user invitations and notifications
6. **Add Analytics**: Integrate PostHog or your preferred analytics tool
7. **Implement RLS**: Set up Row Level Security policies in Supabase for production

---

## Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Docs](https://supabase.com/docs)
- [Prisma Docs](https://www.prisma.io/docs)
- [NextAuth.js Docs](https://next-auth.js.org)
- [shadcn/ui Components](https://ui.shadcn.com)
- [v0 by Vercel](https://v0.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

## Example Seed Script

Create `prisma/seed.ts`:

```typescript
import { PrismaClient } from '../src/generated/prisma'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  // Create a test company
  const company = await prisma.company.create({
    data: {
      name: 'Acme Manufacturing',
      slug: 'acme-manufacturing',
      city: 'San Francisco',
      country: 'USA',
    },
  })

  // Create a test user
  const hashedPassword = await bcrypt.hash('password123', 10)
  const user = await prisma.user.create({
    data: {
      email: 'admin@acme.com',
      password: hashedPassword,
      name: 'Admin User',
      role: 'admin',
      companyId: company.id,
    },
  })

  // Create sample products
  await prisma.product.createMany({
    data: [
      {
        name: 'Industrial Valve Type A',
        sku: 'IV-A-001',
        mpn: 'MPN12345',
        priceText: '$150.00',
        currency: 'USD',
        unit: 'each',
        supplierId: 'supplier-1',
        score: 0.95,
      },
      {
        name: 'Steel Pipe 6in',
        sku: 'SP-6-001',
        priceText: '$45.00',
        currency: 'USD',
        unit: 'ft',
        supplierId: 'supplier-2',
        score: 0.88,
      },
    ],
  })

  console.log('Seed data created successfully!')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
```

Add to `package.json`:

```json
{
  "prisma": {
    "seed": "ts-node --compiler-options {\"module\":\"CommonJS\"} prisma/seed.ts"
  }
}
```

Install ts-node:

```bash
npm install -D ts-node
```

Run seed:

```bash
npx prisma db seed
```

---

Happy building with Nexa! 🚀
