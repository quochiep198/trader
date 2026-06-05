---
name: TradeMind AI
colors:
  surface: '#131315'
  surface-dim: '#131315'
  surface-bright: '#39393b'
  surface-container-lowest: '#0e0e10'
  surface-container-low: '#1b1b1d'
  surface-container: '#1f1f21'
  surface-container-high: '#2a2a2b'
  surface-container-highest: '#353436'
  on-surface: '#e4e2e4'
  on-surface-variant: '#c6c6cd'
  inverse-surface: '#e4e2e4'
  inverse-on-surface: '#303032'
  outline: '#909097'
  outline-variant: '#45464d'
  surface-tint: '#bec6e0'
  primary: '#bec6e0'
  on-primary: '#283044'
  primary-container: '#0f172a'
  on-primary-container: '#798098'
  inverse-primary: '#565e74'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#dec29a'
  on-tertiary: '#3e2d11'
  tertiary-container: '#231500'
  on-tertiary-container: '#957d5a'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#fcdeb5'
  tertiary-fixed-dim: '#dec29a'
  on-tertiary-fixed: '#271901'
  on-tertiary-fixed-variant: '#574425'
  background: '#131315'
  on-background: '#e4e2e4'
  surface-variant: '#353436'
  status-good: '#10B981'
  status-caution: '#F59E0B'
  status-high-risk: '#F43F5E'
  status-critical: '#991B1B'
  action-buy: '#3B82F6'
  action-sell: '#F43F5E'
  surface-card: '#1E293B'
  surface-border: '#334155'
typography:
  display-score:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  subheading:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-std:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  legal-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '400'
    lineHeight: 14px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
  container-max: 1440px
---

## Brand & Style

The brand persona is that of a **Professional Trading Discipline Coach**: objective, authoritative, and stoic. It acts as a behavioral mirror for traders, replacing emotional volatility with systematic rigor. The target audience consists of professional and aspiring retail traders who require high-density data visualization and psychological guardrails.

The design system follows a **Corporate / Modern** style with **Tactile** accents. It prioritizes clarity and functional density, utilizing a structured layout that feels like a high-end financial terminal. Visual interest is achieved through subtle gradients and "glassy" surfaces that suggest high-tech intelligence without distracting from critical financial metrics.

## Colors

The palette is rooted in a deep navy dark mode to reduce eye strain during long trading sessions. 

- **Primary**: Deep Navy is used for the canvas and structural backgrounds, establishing a serious, institutional feel.
- **Secondary**: Emerald serves as the primary success indicator, reinforcing disciplined behavior and profitable trade states.
- **Functional Semantics**: The system uses a traffic-light logic for discipline scores. **Emerald** (80-100), **Amber** (60-79), **Rose** (40-59), and **Deep Red** (0-39) represent decreasing levels of psychological control.
- **Action Colors**: While Rose is used for risk, a distinct Blue is reserved for BUY actions to separate trade direction from emotional status.

## Typography

This design system utilizes **Inter** for its neutral, systematic clarity. A secondary monospaced font, **JetBrains Mono**, is introduced specifically for financial figures (prices, quantities, p/l) to ensure tabular alignment and technical precision.

- **Display Score**: Used exclusively for the Discipline Score to make the primary KPI unmistakable.
- **Hierarchy**: Clear distinction between section headers and data labels. Labels use a semi-bold weight and slight letter spacing to remain legible even at small sizes within dense tables.
- **Legal**: Disclaimers are rendered in a smaller, italicized style to ensure compliance while staying out of the primary cognitive path.

## Layout & Spacing

The system employs a **Fixed Grid** for desktop and a **Fluid Grid** for mobile. 
- **Desktop**: A 12-column grid with 16px gutters. The layout is dashboard-centric, prioritizing sidebars for navigation and a main content area for data visualization.
- **Mobile**: A 4-column fluid grid. Data-heavy tables collapse into card-based lists to maintain readability.
- **Rhythm**: A 4px baseline grid ensures consistent vertical rhythm. Components use generous padding (16px-24px) for AI-led feedback sections to provide focus, while utilizing dense padding (8px) for trade journals and input forms to maximize information density.

## Elevation & Depth

Hierarchy is established through **Tonal Layers** and **Ambient Shadows**. 
- **Base Layer**: The darkest navy (#0F172A) forms the background.
- **Surface Layer**: Component containers (cards, sidebars) use a lighter navy (#1E293B) with a subtle 1px border (#334155).
- **Elevated States**: Overlays for "Soft Cooldown" warnings use a backdrop blur (12px) and a semi-transparent dark fill to create a focused, high-priority state that interrupts the user's flow without feeling jarring.
- **Shadows**: Low-opacity, diffused shadows (0px 4px 20px rgba(0,0,0, 0.4)) are used sparingly to lift active cards or modal windows from the background.

## Shapes

The design system uses a **Soft** shape language to balance professional precision with modern accessibility.
- **Components**: Standard input fields and buttons use a 4px (0.25rem) radius to maintain a crisp, financial-tool aesthetic.
- **Status Tags**: Status pills (e.g., "Planned", "Closed") utilize a fully rounded (pill) shape to distinguish them from interactive buttons.
- **Data Containers**: Larger dashboard cards use an 8px (0.5rem) radius to soften the high-density information layout.

## Components

### Buttons & Inputs
- **Primary Action**: Solid Emerald or Blue backgrounds with bold white text. High-contrast and clearly defined.
- **Secondary/Ghost**: Outlined with 1px borders, using the structural border color. 
- **Inputs**: Darker backgrounds than the cards they sit on to create "inset" depth. Focus states use a 2px primary-colored ring.

### Data Visualization
- **Gauges**: Use a semi-circular stroke. The stroke color dynamically updates based on the Discipline Score (Emerald to Red).
- **Charts**: Clean line charts with area fills using subtle gradients of the status colors.

### Feedback & Coaching
- **Emotion Tags**: Small, high-contrast chips (e.g., "FOMO", "Revenge Trade") that use the Rose palette for negative traits and Emerald for "Calm/Rational."
- **Soft Cooldown Overlay**: A full-screen or prominent modal that uses a blur effect. It must include a mandatory "Reflective Question" field before allowing the user to proceed.

### Lists & Tables
- **Trade Journal**: Hairline dividers only. Alternating row colors are avoided; instead, use hover states to highlight rows. Monospaced font for all numerical data columns.