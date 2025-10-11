# Nexa Frontend

Modern procurement platform built with Next.js 15, Supabase, and AI.

## Stack

- **Framework**: Next.js 15 (App Router) + TypeScript
- **Database**: Supabase Postgres + Prisma ORM
- **Auth**: NextAuth.js (Auth.js)
- **UI**: Tailwind CSS + shadcn/ui
- **Hosting**: Vercel
- **State**: TanStack Query + Zustand

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Set Up Environment

```bash
cp .env.example .env
```

Fill in your Supabase credentials and other environment variables. See [SETUP.md](./SETUP.md) for detailed instructions.

### 3. Set Up Database

```bash
# Generate Prisma client
npx prisma generate

# Push schema to database
npx prisma db push

# (Optional) Seed with test data
npx prisma db seed
```

### 4. Run Development Server

```bash
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (public)/          # Public pages (landing, pricing)
│   │   ├── auth/              # Authentication pages
│   │   ├── dashboard/         # Protected dashboard pages
│   │   └── api/               # API routes
│   ├── components/            # React components
│   │   └── ui/                # shadcn/ui components
│   ├── lib/                   # Utilities and configs
│   │   ├── auth.ts           # NextAuth configuration
│   │   ├── db.ts             # Prisma client
│   │   ├── supabase.ts       # Supabase client
│   │   └── utils.ts          # Helper functions
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript types
│   └── generated/             # Generated files (Prisma)
├── prisma/
│   └── schema.prisma          # Database schema
├── public/                    # Static assets
└── .env                       # Environment variables (not committed)
```

## Key Features

- **Smart Product Search**: Search thousands of industrial products
- **AI RFP Generation**: Generate professional RFPs with AI
- **Multi-tenant**: Company-scoped data with RLS
- **Authentication**: Email/password + OAuth support
- **Type-safe**: End-to-end TypeScript with Prisma

## Development

### Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npx prisma studio` - Open Prisma Studio (database GUI)
- `npx prisma migrate dev` - Create and apply migrations

### Using v0 for UI Components

Use [v0.dev](https://v0.dev) to quickly generate React components:

1. Visit v0.dev and sign in
2. Describe your component
3. Copy the generated code
4. Paste into `src/components/`

See [SETUP.md](./SETUP.md#using-v0-by-vercel) for examples.

### Adding shadcn/ui Components

```bash
npx shadcn@latest add [component-name]
```

Available components: button, card, input, form, dialog, etc.

## Deployment

### Deploy to Vercel

```bash
vercel
```

Or connect your GitHub repo to Vercel for automatic deployments.

**Important**: Add all environment variables in Vercel dashboard before deploying.

## Documentation

- [SETUP.md](./SETUP.md) - Detailed setup guide with Supabase, Vercel, and v0
- [Architecture Blueprint](../nexa_mvp_frontend_platform_blueprint.md) - Full architecture docs

## Environment Variables

See [.env.example](./.env.example) for all required and optional environment variables.

**Required:**
- `DATABASE_URL` - Supabase Postgres connection string
- `NEXTAUTH_URL` - Your app URL
- `NEXTAUTH_SECRET` - Random secret for NextAuth
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key

**Optional:**
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` - For AI RFP generation
- `MEILISEARCH_HOST` / `MEILISEARCH_API_KEY` - For advanced search
- `RESEND_API_KEY` - For sending emails
- `NEXT_PUBLIC_POSTHOG_KEY` - For analytics

## Troubleshooting

See the [Troubleshooting section in SETUP.md](./SETUP.md#troubleshooting)

## Contributing

1. Create a feature branch
2. Make your changes
3. Run `npm run build` to test
4. Submit a PR

## License

Proprietary - All rights reserved

---

Built with ❤️ using Next.js, Supabase, and AI
