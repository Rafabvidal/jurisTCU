---
name: Jurisprudence Precision
colors:
  surface: '#f6f9ff'
  surface-dim: '#d4dbe2'
  surface-bright: '#f6f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eef4fc'
  surface-container: '#e8eef6'
  surface-container-high: '#e3e9f1'
  surface-container-highest: '#dde3eb'
  on-surface: '#161c22'
  on-surface-variant: '#43474e'
  inverse-surface: '#2b3137'
  inverse-on-surface: '#ebf1f9'
  outline: '#74777f'
  outline-variant: '#c4c6cf'
  surface-tint: '#455f88'
  primary: '#002045'
  on-primary: '#ffffff'
  primary-container: '#1a365d'
  on-primary-container: '#86a0cd'
  inverse-primary: '#adc7f7'
  secondary: '#555f71'
  on-secondary: '#ffffff'
  secondary-container: '#d6e0f6'
  on-secondary-container: '#596376'
  tertiary: '#321b00'
  on-tertiary: '#ffffff'
  tertiary-container: '#4f2e00'
  on-tertiary-container: '#c6955e'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#adc7f7'
  on-primary-fixed: '#001b3c'
  on-primary-fixed-variant: '#2d476f'
  secondary-fixed: '#d9e3f9'
  secondary-fixed-dim: '#bdc7dc'
  on-secondary-fixed: '#121c2c'
  on-secondary-fixed-variant: '#3d4759'
  tertiary-fixed: '#ffddba'
  tertiary-fixed-dim: '#f2bc82'
  on-tertiary-fixed: '#2b1700'
  on-tertiary-fixed-variant: '#633f0f'
  background: '#f6f9ff'
  on-background: '#161c22'
  surface-variant: '#dde3eb'
typography:
  h1:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  h2:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  h3:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 0.25rem
  sm: 0.5rem
  md: 1rem
  lg: 1.5rem
  xl: 2rem
  gutter: 1.5rem
  margin: 2rem
---

## Brand & Style

The brand personality is authoritative, analytical, and uncompromisingly professional. This design system is engineered for legal practitioners who require high-density information without cognitive fatigue. The visual language balances the traditional weight of the legal system with the speed of modern computational analysis.

The chosen style is **Corporate / Modern**, leaning into a structured, systematic aesthetic. It prioritizes clarity over decoration, using purposeful whitespace and a restrained palette to guide the lawyer's eye toward critical case insights and strategic data points. The emotional response should be one of "calm confidence"—the feeling of having the most reliable evidence at one's fingertips.

## Colors

The palette is anchored by a deep Navy Blue, evoking the institutional stability of the TRT6. This is contrasted against a very light cool-gray background to reduce screen glare during long research sessions.

- **Primary:** Used for brand presence, primary actions, and active navigation states.
- **Secondary:** A slate gray used for secondary text and non-critical UI elements to maintain a clear hierarchy.
- **Functional (Success/Warning):** These are reserved strictly for status indicators, such as positive case similarity or alert-level procedural risks.
- **Neutrals:** A range of cool grays provides the necessary scaffolding for data cards and borders without introducing visual noise.

## Typography

This design system utilizes **Inter** for its exceptional legibility in data-heavy environments. The typographic scale is optimized for reading long-form legal text and scanning dense tabular data.

Headlines use tighter letter-spacing and heavier weights to command authority. Body text is set with generous line-height to improve readability. A specialized "Label Caps" style is used for metadata and category headers to provide clear visual separation from narrative content.

## Layout & Spacing

The layout follows a **Fixed Grid** philosophy for the main content area (max-width 1440px) to ensure consistent line lengths for legal documents. A 12-column grid is used for the dashboard, with 24px gutters providing ample breathing room between complex data widgets.

The spacing rhythm is built on a 4px baseline. Components like data cards should use a standard 16px (1rem) padding, while larger section headers utilize 32px (2rem) of vertical space to signify shifts in context.

## Elevation & Depth

To maintain a professional and "flat" institutional feel, depth is communicated primarily through **Tonal Layers** and extremely subtle **Ambient Shadows**.

- **Level 0 (Background):** #F7FAFC.
- **Level 1 (Cards/Widgets):** Pure white (#FFFFFF) with a 1px solid border in #E2E8F0.
- **Level 2 (Hover/Active):** A soft shadow (0px 4px 6px -1px rgba(0, 0, 0, 0.05)) to indicate interactivity.

This approach avoids the "floaty" feel of consumer apps, keeping the interface grounded and focused on the data.

## Shapes

The shape language is disciplined. We use **Soft (Level 1)** rounding to take the edge off the interface while maintaining a serious, legal-oriented structure. 

- Standard components (Buttons, Inputs): 4px (0.25rem) radius.
- Large containers (Data Cards): 8px (0.5rem) radius.
- Similarity Badges: 100px (Pill-shaped) to distinguish them from structural elements.

The use of small radii reinforces a sense of precision and modern engineering.

## Components

### Similarity Badges
Used to indicate how closely a case matches the search query. These are pill-shaped with a subtle background tint derived from the status colors.
- **High Similarity:** Green text on light green background.
- **Moderate:** Orange text on light orange background.
- **Style:** Semi-bold Inter, 12px, 2px horizontal padding.

### Data Cards
The primary container for case summaries. 
- **Header:** Contains the case number in Primary Navy and the Similarity Badge.
- **Content:** Uses Body-MD for snippets.
- **Footer:** Contains metadata in Label-Caps (Date, Judge, Court).

### Interactive Widgets
Strategy tools (like "Timeline of Decisions" or "Outcome Probability") should use interactive charts. 
- **States:** Hovering over data points should use a Primary Navy tooltip with white text.
- **Buttons:** Primary buttons are solid Navy (#1A365D); secondary buttons are outlined in #E2E8F0.

### Input Fields
Strictly rectangular with 4px corners. Labels are always visible above the field in Secondary Gray to ensure the user never loses context during data entry.