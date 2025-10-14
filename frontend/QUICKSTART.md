# Nexa Frontend - Quick Start Guide

Get up and running in 10 minutes!

## Prerequisites Checklist

- [ ] Node.js 18+ installed
- [ ] npm or pnpm installed
- [ ] Git installed
- [ ] Supabase account created
- [ ] Text editor (VS Code recommended)

---

## Step-by-Step Setup

### 1. Install Dependencies (2 min)

```bash
cd frontend
npm install
```

### 2. Set Up Supabase (3 min)

#### Create Project:
1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose a name, password, and region
4. Wait for project to initialize (~2 min)

#### Get Credentials:
1. Go to **Settings** → **API**
2. Copy:
   - Project URL
   - anon/public key
   - service_role key

3. Go to **Settings** → **Database**
4. Copy the connection string (URI format)

### 3. Configure Environment (1 min)

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Replace these with your Supabase values
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
NEXT_PUBLIC_SUPABASE_URL="https://[PROJECT-REF].supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="your-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# Generate this
NEXTAUTH_SECRET="run: openssl rand -base64 32"
NEXTAUTH_URL="http://localhost:3000"
```

**Generate NextAuth secret:**
```bash
openssl rand -base64 32
```
Copy the output to `NEXTAUTH_SECRET`.

### 4. Set Up Database (2 min)

```bash
# Generate Prisma client
npx prisma generate

# Create tables in Supabase
npx prisma db push
```

You should see:
```
✔ Generated Prisma Client
✔ Your database is now in sync with your schema.
```

### 5. Run the App (1 min)

```bash
npm run dev
```

Visit: [http://localhost:3000](http://localhost:3000)

---

## Verify Everything Works

### ✅ Checklist:

- [ ] Landing page loads at `http://localhost:3000`
- [ ] No console errors
- [ ] Tailwind CSS styles are applied
- [ ] Can navigate to `/dashboard` (will redirect to signin)

### View Database:

```bash
npx prisma studio
```

This opens a GUI at `http://localhost:5555` to view your database.

---

## Next Steps

### Option A: Build Auth Pages First

Create signin/signup pages so you can test the full flow:

```bash
# Generate forms with v0.dev (see V0_GUIDE.md)
# Or build manually
```

### Option B: Seed Test Data

Create `prisma/seed.ts`:

```typescript
import { PrismaClient } from '../src/generated/prisma'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  const company = await prisma.company.create({
    data: {
      name: 'Test Company',
      slug: 'test-company',
      city: 'San Francisco',
      country: 'USA',
    },
  })

  const password = await bcrypt.hash('password123', 10)

  await prisma.user.create({
    data: {
      email: 'admin@test.com',
      password,
      name: 'Admin User',
      companyId: company.id,
    },
  })

  console.log('✅ Seed data created!')
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
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

Now you can sign in with:
- Email: `admin@test.com`
- Password: `password123`

### Option C: Generate UI with v0

1. Go to [v0.dev](https://v0.dev)
2. Use prompts from [V0_GUIDE.md](./V0_GUIDE.md)
3. Start with:
   - Sign In Form
   - Product Card
   - Dashboard Sidebar

---

## Common Issues

### Issue: "Cannot find module '@/generated/prisma'"

**Fix:**
```bash
npx prisma generate
```

### Issue: "Invalid DATABASE_URL"

**Fix:**
- Check your `.env` file
- Ensure password is correct
- Make sure you replaced `[PASSWORD]` and `[PROJECT-REF]`

### Issue: Port 3000 already in use

**Fix:**
```bash
# Use different port
npm run dev -- -p 3001
```

Or kill the process using 3000:
```bash
lsof -ti:3000 | xargs kill
```

### Issue: Prisma Client errors

**Fix:**
```bash
# Delete generated client and regenerate
rm -rf src/generated
npx prisma generate
```

---

## Development Workflow

### Daily Workflow:

1. **Start dev server:**
   ```bash
   npm run dev
   ```

2. **Open Prisma Studio** (optional):
   ```bash
   npx prisma studio
   ```

3. **Generate components with v0:**
   - Visit v0.dev
   - Generate components
   - Add to `src/components/`

4. **Test changes:**
   - Check browser at localhost:3000
   - Use React DevTools
   - Check Network tab for API calls

### When changing database schema:

```bash
# Update prisma/schema.prisma
# Then:
npx prisma db push        # For development
# OR
npx prisma migrate dev    # For production (creates migration files)

# Regenerate client
npx prisma generate
```

---

## File Structure Reference

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Landing page ✅
│   │   ├── layout.tsx            # Root layout
│   │   ├── dashboard/
│   │   │   └── page.tsx          # Dashboard ✅
│   │   └── api/
│   │       ├── auth/[nextauth]/  # Auth routes ✅
│   │       ├── products/search/  # Product search ✅
│   │       └── rfp/              # RFP routes ✅
│   ├── lib/
│   │   ├── auth.ts               # NextAuth config ✅
│   │   ├── db.ts                 # Prisma client ✅
│   │   └── supabase.ts           # Supabase client ✅
│   └── components/               # Your components (to build)
├── prisma/
│   └── schema.prisma             # Database schema ✅
├── .env                          # Your secrets
├── .env.example                  # Template ✅
├── SETUP.md                      # Detailed setup guide ✅
├── V0_GUIDE.md                   # v0 usage guide ✅
└── QUICKSTART.md                 # This file ✅
```

---

## Deployment (Vercel)

When ready to deploy:

```bash
npm i -g vercel
vercel
```

Follow prompts, then add environment variables in Vercel dashboard.

See [SETUP.md](./SETUP.md#deploying-to-vercel) for detailed deployment instructions.

---

## Getting Help

- **Detailed Setup**: See [SETUP.md](./SETUP.md)
- **v0 Component Generation**: See [V0_GUIDE.md](./V0_GUIDE.md)
- **Architecture**: See [../nexa_mvp_frontend_platform_blueprint.md](../nexa_mvp_frontend_platform_blueprint.md)
- **Prisma Docs**: [prisma.io/docs](https://www.prisma.io/docs)
- **Next.js Docs**: [nextjs.org/docs](https://nextjs.org/docs)
- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)

---

🎉 **You're all set! Start building your components with v0 and watch your app come to life.**
