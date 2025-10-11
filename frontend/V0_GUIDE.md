# Using v0 by Vercel for Nexa UI Components

This guide provides specific prompts and instructions for using [v0.dev](https://v0.dev) to generate UI components for the Nexa platform.

## What is v0?

v0 is Vercel's AI-powered UI generator that creates React components using:
- **shadcn/ui** components
- **Tailwind CSS** for styling
- **TypeScript** for type safety
- **Next.js** best practices

## Getting Started with v0

1. Visit [v0.dev](https://v0.dev)
2. Sign in with your Vercel account (or create one)
3. Start generating components!

---

## Essential Component Prompts for Nexa

### 1. Product Search Card

**Prompt:**
```
Create a product card component for an industrial procurement platform.
The card should display:
- Product image (placeholder if none)
- Product name (bold, 18px)
- SKU and MPN in smaller gray text
- Supplier name with a badge
- Price in large text with currency
- Certifications as small badges (e.g., "ISO 9001", "CE")
- A "View Details" button (primary blue)
- Last updated timestamp at the bottom

Use shadcn/ui components, Tailwind CSS with a clean industrial design.
Make it responsive and include hover effects.
```

**Usage:**
- Save as `src/components/ProductCard.tsx`
- Import in search results page

---

### 2. RFP Builder Multi-Step Form

**Prompt:**
```
Create a multi-step form wizard for creating an RFP (Request for Proposal).

Steps:
1. Basic Information: title, category dropdown, description textarea
2. Requirements: budget input, delivery date picker, technical specs textarea
3. Location & Standards: location input, certifications multi-select, preferred suppliers multi-select
4. Review: Show all entered data in a summary view

Include:
- Step indicator at top (1/4, 2/4, etc.)
- "Back" and "Next" buttons (disable Back on first step)
- "Generate RFP" button on final step
- Form validation using react-hook-form and zod
- Use shadcn/ui form, input, textarea, select, button components
- Clean, professional design with blue primary color

Export as a TypeScript React component with proper types.
```

**Usage:**
- Save as `src/components/RfpWizard.tsx`
- Use in `/dashboard/rfp/new`

---

### 3. Dashboard Navigation Sidebar

**Prompt:**
```
Create a dashboard sidebar navigation for a B2B procurement platform.

Navigation items:
- Dashboard (home icon)
- Product Search (search icon)
- My RFPs (document icon)
- Settings (settings icon)
- Sign Out (logout icon)

Include:
- Company logo and name at top
- User avatar and email at bottom
- Active state highlighting (blue background)
- Hover effects
- Responsive: collapsible on mobile
- Use lucide-react for icons
- Use shadcn/ui components
- Clean, modern design with slate gray background

Make it a client component with Next.js Link components.
```

**Usage:**
- Save as `src/components/DashboardSidebar.tsx`
- Add to dashboard layout

---

### 4. Authentication Forms (Sign In & Sign Up)

**Sign In Prompt:**
```
Create a modern sign-in form for a B2B platform.

Fields:
- Email (type email, required)
- Password (type password, required, with show/hide toggle)
- "Remember me" checkbox
- "Forgot password?" link (right-aligned)
- "Sign In" button (full width, blue)
- "Don't have an account? Sign up" link at bottom

Include:
- Form validation with react-hook-form and zod
- Loading state on submit button
- Error message display above form
- shadcn/ui form components
- Clean, centered layout with company logo above
- Professional design

Export as TypeScript component with onSubmit prop.
```

**Sign Up Prompt:**
```
Create a sign-up form for a B2B procurement platform.

Fields:
- Company Name (required)
- Email (type email, required)
- Password (with strength meter)
- Confirm Password (must match)
- Location (city, country)
- "I agree to Terms of Service" checkbox (required)
- "Create Account" button (full width, blue)
- "Already have an account? Sign in" link

Include:
- Form validation (email format, password min 8 chars, passwords match)
- Password strength indicator (weak/medium/strong)
- Loading state
- Error handling
- shadcn/ui components
- Professional, clean design

Export as TypeScript component.
```

**Usage:**
- Save as `src/components/SignInForm.tsx` and `SignUpForm.tsx`
- Use in `/auth/signin` and `/auth/signup`

---

### 5. RFP Editor with Markdown Preview

**Prompt:**
```
Create a split-pane RFP editor component.

Left pane:
- Markdown editor (textarea with monospace font)
- Toolbar with formatting buttons (bold, italic, heading, list)
- Character/word count at bottom

Right pane:
- Live markdown preview
- Styled to look like a professional document
- Table of contents auto-generated from headings

Top bar:
- Title input field
- Status dropdown (Draft, Published, Archived)
- "Export PDF" button
- "Share" button
- "Save" button (primary)

Use shadcn/ui components, react-markdown for preview.
Make it responsive (stack vertically on mobile).
Clean, document-editing interface similar to Notion.
```

**Usage:**
- Save as `src/components/RfpEditor.tsx`
- Use in `/dashboard/rfp/[id]`

---

### 6. Product Search Filters Sidebar

**Prompt:**
```
Create a product search filters sidebar.

Filter sections:
1. Supplier (multi-select checkboxes)
2. Price Range (dual range slider with min/max inputs)
3. Certifications (checkbox list: ISO 9001, CE, UL, etc.)
4. Category (dropdown)
5. Availability (In Stock, Out of Stock, Pre-order)

Include:
- "Apply Filters" button at bottom
- "Clear All" link at top
- Collapsible sections (accordion style)
- Active filter count badges
- shadcn/ui components (checkbox, slider, select, accordion)
- Clean, organized design

Export as TypeScript component with onFilterChange callback.
```

**Usage:**
- Save as `src/components/SearchFilters.tsx`
- Use in `/dashboard/search`

---

### 7. Data Table for Products

**Prompt:**
```
Create a data table component for displaying industrial products.

Columns:
- Product Name (with thumbnail)
- SKU
- Supplier
- Price
- Certifications (badges)
- Actions (View, Add to RFP)

Features:
- Sortable columns
- Search bar above table
- Pagination (showing X-Y of Z results)
- Select rows with checkboxes
- Bulk actions (Add selected to RFP, Export)
- Empty state when no results
- Loading state

Use shadcn/ui table, TanStack Table for functionality.
Professional, data-dense design.
Responsive: convert to cards on mobile.
```

**Usage:**
- Save as `src/components/ProductTable.tsx`
- Use in `/dashboard/search`

---

### 8. Pricing Page

**Prompt:**
```
Create a pricing page with 3 tiers for a B2B SaaS platform.

Tiers:
1. Starter: $99/mo, 5 users, 100 searches/mo, basic RFP generation
2. Professional: $299/mo, 20 users, unlimited searches, advanced AI, priority support
3. Enterprise: Custom pricing, unlimited users, custom integrations, dedicated account manager

Each card should show:
- Tier name and tagline
- Price (large)
- Feature list with checkmarks
- "Choose Plan" button (highlight middle tier)
- "Most Popular" badge on middle tier

Include:
- Toggle for Monthly/Annual billing (show savings for annual)
- FAQ section below
- "Contact Sales" CTA at bottom
- shadcn/ui components
- Clean, modern design with blue accents

Responsive grid layout.
```

**Usage:**
- Save as `src/app/(public)/pricing/page.tsx`

---

## Integration Workflow

### Step 1: Generate with v0
1. Paste one of the prompts above
2. Review the generated code
3. Make adjustments if needed (you can chat with v0)
4. Click "Copy Code"

### Step 2: Add to Project
1. Create the file in your project:
   ```bash
   touch src/components/ComponentName.tsx
   ```
2. Paste the v0-generated code
3. Update imports to match your project structure

### Step 3: Install Missing Dependencies
If v0 uses a component you don't have:
```bash
npx shadcn@latest add [component-name]
```

### Step 4: Connect to Your Data
1. Replace mock data with your API calls
2. Add TypeScript types from your Prisma schema
3. Wire up event handlers (onSubmit, onClick, etc.)

---

## Tips for Better v0 Results

1. **Be Specific**: Include exact field names, validation rules, and design preferences
2. **Mention Tech Stack**: Always specify shadcn/ui, Tailwind, TypeScript, Next.js
3. **Request TypeScript**: Ask for "proper TypeScript types" or "export with types"
4. **Iterate**: You can chat with v0 to refine the output
5. **Copy Styles**: If you like one component's style, mention it in other prompts

---

## Example v0 Conversation

**You:**
> Create a product card component for an industrial procurement platform...

**v0:**
> *Generates component*

**You:**
> Great! Can you add a "Quick Add to RFP" button and make the image larger?

**v0:**
> *Updates component*

**You:**
> Perfect! Now make it work with TypeScript and accept a product prop with type: { id: string, name: string, price: number }

**v0:**
> *Adds TypeScript types*

---

## Common shadcn/ui Components to Request

- `button` - Buttons with variants
- `card` - Card containers
- `input` - Text inputs
- `form` - Form wrapper with validation
- `select` - Dropdowns
- `dialog` - Modals
- `table` - Data tables
- `badge` - Small labels/tags
- `avatar` - User avatars
- `tabs` - Tabbed interfaces
- `accordion` - Collapsible sections
- `toast` - Notifications
- `separator` - Dividers

Install them as needed:
```bash
npx shadcn@latest add button card input form select dialog table badge
```

---

## Next Steps

1. Start with the **Product Search Card** and **Sign In Form**
2. Generate components for your dashboard layout
3. Build out the RFP workflow (wizard → editor → preview)
4. Add search and filtering components
5. Create the pricing page

Each component is self-contained, so you can build incrementally!

---

## Resources

- [v0.dev](https://v0.dev) - Generate components
- [shadcn/ui](https://ui.shadcn.com) - Component library docs
- [Tailwind CSS](https://tailwindcss.com) - Styling reference
- [Lucide Icons](https://lucide.dev) - Icon library used by shadcn

Happy building! 🚀
