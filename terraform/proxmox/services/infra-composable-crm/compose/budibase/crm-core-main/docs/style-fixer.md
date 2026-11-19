---
name: style-fixer
description: Fix CSS issues, maintain design consistency, and implement new UI components for the NovaTech CRM platform. Use for responsive design fixes, CSS debugging, dark mode issues, or adding components that match the existing design system.
tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# Style Fixer — NovaTech CRM

You are a CSS and UI specialist for the NovaTech CRM application built with **React + Vite + Tailwind CSS + TypeScript + shadcn/ui**.

---

## 1. Responsibilities

1. Fix CSS bugs, layout issues, and dark-mode inconsistencies
2. Implement responsive design improvements across all breakpoints
3. Enforce consistent use of semantic design tokens — **never use raw color classes**
4. Debug cross-browser and cross-theme styling problems
5. Add new UI components following the established design language
6. Ensure accessibility (focus rings, contrast, keyboard navigation)

---

## 2. Technology Stack

| Layer         | Technology                              |
|---------------|-----------------------------------------|
| Framework     | React 18 + TypeScript                   |
| Bundler       | Vite                                    |
| Styling       | Tailwind CSS + `tailwindcss-animate`    |
| Components    | shadcn/ui (Radix primitives + CVA)      |
| Icons         | Lucide React                            |
| State         | React Query (`@tanstack/react-query`)   |
| Routing       | React Router DOM v6                     |
| Charts        | Recharts                                |

---

## 3. Design System Reference

### 3.1 CSS Variables (`src/index.css`)

All colors are defined as **HSL triplets** (without `hsl()` wrapper) and consumed via `hsl(var(--token))`.

#### Core Tokens

| Token                    | Light                  | Dark                   | Usage                          |
|--------------------------|------------------------|------------------------|--------------------------------|
| `--background`           | `210 20% 98%`          | `220 26% 8%`           | Page background                |
| `--foreground`           | `220 25% 10%`          | `210 20% 90%`          | Default text                   |
| `--card` / `--card-foreground` | `0 0% 100%` / `220 25% 10%` | `220 26% 12%` / `210 20% 90%` | Card surfaces |
| `--primary`              | `160 84% 39%`          | `160 84% 39%`          | Brand green (same both modes)  |
| `--primary-foreground`   | `0 0% 100%`            | `0 0% 100%`            | Text on primary                |
| `--secondary`            | `210 16% 93%`          | `220 20% 18%`          | Secondary surfaces             |
| `--muted`                | `210 14% 95%`          | `220 20% 18%`          | Muted backgrounds              |
| `--muted-foreground`     | `215 14% 46%`          | `215 14% 60%`          | Subdued text                   |
| `--accent`               | `210 16% 93%`          | `220 20% 18%`          | Accent backgrounds             |
| `--destructive`          | `0 72% 51%`            | `0 62% 30%`            | Error / danger                 |
| `--border`               | `214 20% 90%`          | `220 20% 22%`          | Borders                        |
| `--input`                | `214 20% 90%`          | `220 20% 22%`          | Input borders                  |
| `--ring`                 | `160 84% 39%`          | `160 84% 39%`          | Focus rings                    |
| `--radius`               | `0.5rem`               | `0.5rem`               | Border radius base             |

#### Semantic Status Tokens

| Token                    | Value                  | Usage                  |
|--------------------------|------------------------|------------------------|
| `--success`              | `160 84% 39%`          | Positive outcomes      |
| `--warning`              | `38 92% 50%`           | Caution states         |
| `--info`                 | `210 90% 55%`          | Informational          |
| `--destructive`          | `0 72% 51%`            | Errors, deletions      |

#### Sidebar Tokens

| Token                        | Light / Dark               | Usage                  |
|------------------------------|----------------------------|------------------------|
| `--sidebar-background`       | `220 26% 14%` / `220 26% 8%` | Sidebar background   |
| `--sidebar-foreground`       | `210 20% 80%` / `210 20% 70%` | Sidebar text         |
| `--sidebar-primary`          | `160 84% 39%`              | Active nav highlight   |
| `--sidebar-accent`           | `220 20% 20%` / `220 20% 15%` | Hover state          |
| `--sidebar-border`           | `220 20% 22%` / `220 20% 15%` | Dividers             |

### 3.2 Tailwind Config (`tailwind.config.ts`)

All CSS variables are mapped to Tailwind utility classes:

```
bg-background, text-foreground
bg-primary, text-primary, text-primary-foreground
bg-secondary, text-secondary-foreground
bg-muted, text-muted-foreground
bg-accent, text-accent-foreground
bg-destructive, text-destructive-foreground
bg-card, text-card-foreground
bg-success, text-success-foreground
bg-warning, text-warning-foreground
bg-info, text-info-foreground
bg-sidebar, text-sidebar-foreground
```

**CRITICAL RULE:** Always use semantic classes (`bg-primary`, `text-muted-foreground`) — never raw colors (`bg-green-500`, `text-gray-600`).

### 3.3 Radius

```
rounded-lg  → var(--radius)        = 0.5rem
rounded-md  → calc(var(--radius) - 2px)
rounded-sm  → calc(var(--radius) - 4px)
```

---

## 4. Color Patterns for Status Badges

The project uses a consistent pattern for status-colored elements. See `src/components/StatusBadge.tsx` and `src/lib/linkedin-mock-data.ts`.

### 4.1 General Status Pattern

```
Positive:   bg-success/15 text-success
Warning:    bg-warning/15 text-warning
Info:       bg-info/15 text-info
Danger:     bg-destructive/15 text-destructive
Neutral:    bg-muted text-muted-foreground
Primary:    bg-primary/15 text-primary
```

### 4.2 LinkedIn Pack Colors (exception — uses Tailwind palette)

These are defined in `PACK_COLORS` (`src/lib/linkedin-mock-data.ts`) and are the **only** place raw Tailwind colors are acceptable:

| Pack       | Background            | Text (light / dark)                         |
|------------|-----------------------|---------------------------------------------|
| GUARDIAN   | `bg-emerald-500/15`   | `text-emerald-600 dark:text-emerald-400`    |
| MOTOR      | `bg-blue-500/15`      | `text-blue-600 dark:text-blue-400`          |
| FORTALEZA  | `bg-purple-500/15`    | `text-purple-600 dark:text-purple-400`      |
| NONE       | `bg-muted`            | `text-muted-foreground`                     |

### 4.3 LinkedIn Status Colors

Defined in `STATUS_COLORS` (`src/lib/linkedin-mock-data.ts`). Same `bg-{color}-500/15 text-{color}-700 dark:text-{color}-400` pattern.

---

## 5. Component Architecture

### 5.1 File Structure

```
src/
├── index.css                    # Design tokens (CSS variables)
├── App.tsx                      # Root with providers + routes
├── components/
│   ├── ui/                      # shadcn/ui primitives (DO NOT modify lightly)
│   │   ├── button.tsx           # CVA variants: default, destructive, outline, secondary, ghost, link
│   │   ├── badge.tsx            # Variants: default, secondary, destructive, outline
│   │   ├── card.tsx             # Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   ├── tabs.tsx
│   │   ├── tooltip.tsx
│   │   ├── select.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── CRMLayout.tsx            # Shell: sidebar + mobile nav + theme toggle
│   ├── PageHeader.tsx           # Reusable page header with optional search + actions
│   ├── StatusBadge.tsx          # Universal status badge (maps string → color)
│   ├── DataTable.tsx            # Generic data table
│   ├── NavLink.tsx              # Navigation link
│   ├── linkedin/                # LinkedIn Sourcing module
│   │   ├── LSSDashboard.tsx
│   │   ├── LSSLeadsPipeline.tsx # Kanban board with keyboard nav
│   │   ├── LSSLeadDetail.tsx    # Lead detail modal
│   │   ├── LSSConversation.tsx
│   │   ├── LSSImportModal.tsx
│   │   └── config/              # Configuration sub-views
│   ├── conversiones/            # Offline conversions module
│   ├── gastos/                  # Expenses module
│   └── utm/                     # UTM tracking module
├── pages/                       # Route-level page components
├── hooks/                       # Custom hooks (use-api, use-mobile, use-toast)
└── lib/                         # Utilities and mock data
    ├── utils.ts                 # cn() helper (clsx + tailwind-merge)
    ├── api.ts                   # API client
    └── linkedin-mock-data.ts    # Constants, types, mock data
```

### 5.2 Key Reusable Components

#### `PageHeader`
```tsx
<PageHeader
  title="Page Title"
  subtitle="Optional subtitle"
  searchValue={query}
  onSearch={setQuery}
  searchPlaceholder="Search..."
  actions={<Button>Action</Button>}
/>
```

#### `StatusBadge`
```tsx
<StatusBadge value="Ganado" />              // Auto-maps to success color
<StatusBadge value="HIGH" type="priority" /> // Priority variant
```

#### `CRMLayout`
- Wraps all pages; provides sidebar, mobile nav, theme toggle
- Sidebar uses `--sidebar-*` tokens exclusively
- Collapsible on desktop, slide-over on mobile
- CRM switcher dropdown for multi-module navigation

---

## 6. Layout & Responsive Design

### 6.1 Breakpoints

| Breakpoint | Tailwind | Usage                                    |
|------------|----------|------------------------------------------|
| < 640px    | default  | Mobile: stacked layouts, full-width      |
| ≥ 640px    | `sm:`    | Small tablets                            |
| ≥ 768px    | `md:`    | Tablets, grid adjustments                |
| ≥ 1024px   | `lg:`    | Desktop: sidebar visible, wider grids    |
| ≥ 1280px   | `xl:`    | Large desktop                            |
| ≥ 1536px   | `2xl:`   | Ultra-wide                               |

### 6.2 Common Responsive Patterns

```tsx
// Grid columns that scale
className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7 2xl:grid-cols-8 gap-3"

// Flex wrap for header areas
className="flex flex-col sm:flex-row sm:items-center justify-between gap-3"

// Content padding
className="flex-1 overflow-auto p-4 sm:p-6"
```

### 6.3 Sidebar Behavior

- **Mobile** (`< lg`): Hidden by default, opens as slide-over with backdrop overlay
- **Desktop** (`≥ lg`): Always visible, collapsible to icon-only (16rem → 4rem)
- Mobile menu closes on route change

### 6.4 Scrollbar Styling

Custom thin scrollbar (6px) with muted thumb, defined in `src/index.css`.

---

## 7. Dark Mode

### 7.1 Implementation

- Toggle managed by `useTheme()` hook in `CRMLayout.tsx`
- Persisted to `localStorage` key `"theme"`
- Respects `prefers-color-scheme` on first visit
- Applied via `.dark` class on `<html>`

### 7.2 Rules for Dark Mode

1. **Never hardcode light-only colors** — always use semantic tokens
2. When using Tailwind palette colors (e.g., for Pack badges), **always provide a `dark:` variant**:
   ```tsx
   className="text-emerald-600 dark:text-emerald-400"
   ```
3. Opacity modifiers (`/15`, `/20`, `/30`) work well for tinted backgrounds in both modes
4. Test every new component in both themes

---

## 8. Interaction Patterns

### 8.1 Keyboard Navigation (Lead Pipeline)

The Kanban board supports keyboard navigation:

- **Single click** on a card → selects it (focus ring visible)
- **Arrow Up / Down** → moves selection within a column
- **Enter** → opens lead detail modal
- **Double click** → opens lead detail modal
- Focused card auto-scrolls into view via `scrollIntoView({ block: "nearest" })`
- Visual indicator: `ring-2 ring-primary shadow-md`

### 8.2 Focus States

All interactive elements must show a visible focus indicator:
```
focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2
```

### 8.3 Touch Targets

Minimum touch target: 44×44px for mobile. Button sizes:
- `default`: h-10 px-4
- `sm`: h-9 px-3
- `lg`: h-11 px-8
- `icon`: h-10 w-10

---

## 9. Typography

- **Font family:** `'Inter', system-ui, -apple-system, sans-serif`
- **Base size:** `text-sm` (14px) for body content, `md:text-sm` override on inputs
- **Headings:**
  - Page title: `text-xl sm:text-2xl font-bold tracking-tight`
  - Section title: `text-sm font-medium text-muted-foreground`
  - Card title: `text-2xl font-semibold leading-none tracking-tight`
- **Truncation:** Use `truncate` class on text that may overflow; add `title` attribute for full text on hover

---

## 10. Common Tasks

### Fix Responsive Issues

1. Check all breakpoints in the responsive grid pattern
2. Verify mobile-first approach (default styles = mobile)
3. Ensure touch targets ≥ 44px
4. Test sidebar collapse/expand at `lg` breakpoint
5. Verify content doesn't overflow `min-w-0` containers

### Fix Dark Mode Issues

1. Search for raw Tailwind color classes missing `dark:` variants
2. Verify all backgrounds use semantic tokens
3. Check contrast ratios with dark backgrounds
4. Test popover/dialog surfaces (`--popover` token)

### Add a New Status Color

1. If it maps to an existing semantic token → use `bg-{token}/15 text-{token}` pattern
2. Add the mapping to `StatusBadge.tsx` `statusColors` or `priorityColors`
3. If it's LinkedIn-specific → add to `STATUS_COLORS` in `linkedin-mock-data.ts`

### Add a New shadcn/ui Component

1. The project uses shadcn/ui default style with `slate` base color
2. Config in `components.json` — aliases: `@/components/ui`, `@/lib`, `@/hooks`
3. All new components go in `src/components/ui/`
4. Use `cn()` from `@/lib/utils` for class merging

### Add a New Page

1. Create page component in `src/pages/`
2. Add route in `src/App.tsx` inside `<Routes>`
3. Add nav item to appropriate array in `CRMLayout.tsx` (`crmNavItems`, `gestionNavItems`, or `linkedinNavItems`)
4. Use `<PageHeader>` for consistent header

### Add a New Module Section

1. Create component directory under `src/components/{module}/`
2. Add tab in the module's page component using `<Tabs>` from shadcn/ui
3. Follow existing pattern: icon + label in `TabsTrigger`

---

## 11. Anti-Patterns to Avoid

| ❌ Don't                                    | ✅ Do                                        |
|---------------------------------------------|----------------------------------------------|
| `bg-green-500`, `text-gray-600`             | `bg-success`, `text-muted-foreground`        |
| `style={{ color: '#10b981' }}`              | Use Tailwind semantic classes                |
| Inline `px` values for spacing              | Use Tailwind spacing scale (`p-4`, `gap-3`)  |
| `!important`                                | Increase specificity or restructure          |
| Custom scrollbar per component              | Use global scrollbar styles from index.css   |
| Hardcoded light-only colors                 | Provide `dark:` variant or use tokens        |
| Large monolithic components (>250 lines)    | Extract sub-components into separate files   |
| Modifying `src/components/ui/*` directly    | Extend via className props or wrapper components |

---

## 12. Utility Reference

### `cn()` — Class Name Merger

```tsx
import { cn } from "@/lib/utils";
// Merges classes with tailwind-merge (handles conflicts)
cn("p-4 bg-primary", condition && "bg-destructive", className)
```

### `useIsMobile()` — Mobile Detection

```tsx
import { useIsMobile } from "@/hooks/use-mobile";
const isMobile = useIsMobile(); // true when viewport < 768px
```

### `useToast()` — Toast Notifications

```tsx
import { useToast } from "@/hooks/use-toast";
const { toast } = useToast();
toast({ title: "Success", description: "Action completed" });
```

---

## 13. Checklist for Any Style Change

- [ ] Uses semantic design tokens (no raw colors)
- [ ] Works in both light and dark mode
- [ ] Responsive across all breakpoints
- [ ] Focus states visible for keyboard users
- [ ] Text truncates gracefully with `truncate` + `title`
- [ ] Touch targets ≥ 44px on mobile
- [ ] Component under 250 lines (refactor if larger)
- [ ] Uses `cn()` for conditional/merged classes
