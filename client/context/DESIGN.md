---
name: Midnight Elite
colors:
  surface: '#121414'
  surface-dim: '#121414'
  surface-bright: '#38393a'
  surface-container-lowest: '#0d0e0f'
  surface-container-low: '#1a1c1c'
  surface-container: '#1e2020'
  surface-container-high: '#292a2a'
  surface-container-highest: '#343535'
  on-surface: '#e3e2e2'
  on-surface-variant: '#d2c5ac'
  inverse-surface: '#e3e2e2'
  inverse-on-surface: '#2f3131'
  outline: '#9b9079'
  outline-variant: '#4e4633'
  surface-tint: '#f3c016'
  primary: '#ffe29e'
  on-primary: '#3e2e00'
  primary-container: '#f6c21a'
  on-primary-container: '#695100'
  inverse-primary: '#765b00'
  secondary: '#c6c6cd'
  on-secondary: '#2e3036'
  secondary-container: '#47494f'
  on-secondary-container: '#b7b8bf'
  tertiary: '#e7e4e3'
  on-tertiary: '#313030'
  tertiary-container: '#cbc8c8'
  on-tertiary-container: '#555453'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffdf93'
  primary-fixed-dim: '#f3c016'
  on-primary-fixed: '#241a00'
  on-primary-fixed-variant: '#594400'
  secondary-fixed: '#e2e2e9'
  secondary-fixed-dim: '#c6c6cd'
  on-secondary-fixed: '#1a1c20'
  on-secondary-fixed-variant: '#45474c'
  tertiary-fixed: '#e5e2e1'
  tertiary-fixed-dim: '#c9c6c5'
  on-tertiary-fixed: '#1c1b1b'
  on-tertiary-fixed-variant: '#474646'
  background: '#121414'
  on-background: '#e3e2e2'
  surface-variant: '#343535'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 22px
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
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  container-padding: 1.5rem
  stack-gap-lg: 2rem
  stack-gap-md: 1rem
  stack-gap-sm: 0.5rem
  gutter: 1rem
---

## Brand & Style
The design system is engineered for a premium urban mobility experience, prioritizing confidence, exclusivity, and precision. It targets a high-end demographic that values efficiency paired with a sophisticated aesthetic.

The visual style blends **Corporate Modern** with **Glassmorphism** accents. It utilizes a "Deep Tech" atmosphere characterized by high-contrast typography, expansive black surfaces, and precise golden accents. The emotional response should be one of "effortless luxury"—where the UI feels as quiet and powerful as a high-end electric vehicle. All interactions should feel lubricated and expensive, utilizing subtle blurs and light-based affordances to guide the user.

## Colors
This design system operates on a "True Black" foundation to maximize OLED contrast and evoke a sense of nighttime urban luxury.

- **Primary Accent:** A rich golden yellow (#F6C21A) reserved for high-intent actions, active route paths, and critical status indicators.
- **Surfaces:** Use tiered charcoal shades to create hierarchy. `#16181C` is for primary card surfaces, while `#1B1D22` is used for elevated modal or floating elements.
- **Typography:** High-contrast pure white (#FFFFFF) for readability, with soft grays for metadata and supporting information to maintain a clean visual density.
- **Status Markers:** Use a vibrant green specifically for "Pickup" or "Current Location" and a bold red for "Destination" or "Emergency" actions.

## Typography
The typography system uses a dual-font approach. **Plus Jakarta Sans** provides a modern, geometric character for headings and titles, adding a touch of approachable luxury. **Inter** is utilized for body text and labels to ensure maximum legibility and a technical, precise feel.

- **Headlines:** Use tight letter-spacing on larger sizes to create a "compact" and authoritative look.
- **Labels:** Small labels should use uppercase styling with increased letter spacing for a "navigation-grade" utility feel.
- **Contrast:** Always use primary white for headlines. Secondary gray should be restricted to body-copy that is not vital for the user's immediate action.

## Layout & Spacing
The layout follows a **Fixed Grid** model on desktop and a **Fluid** model on mobile, anchored by a generous 24px (1.5rem) outer margin.

- **Vertical Rhythm:** A base 8px grid system regulates all spacing. Use 24px increments for major section breaks and 16px for internal card padding.
- **Bottom Sheets:** In mobile views, the bottom sheet is the primary interaction container. It should have a default 32px top-corner radius and always occupy a consistent "safe-area" height.
- **Safe Zones:** Ensure content never butts against the edge of the screen; the "luxurious" feel is derived from the "air" around the elements.

## Elevation & Depth
Depth is communicated through **Tonal Layering** and **Subtle Illumination**.

- **Surface Levels:** The background is the lowest level. Primary cards "float" 1-step above with a subtle `#16181C` fill. High-priority modals or selection states use `#1B1D22`.
- **Shadows:** Use ultra-diffused shadows (`blur: 40px, opacity: 30%`) with a dark neutral tint. Avoid hard, high-opacity shadows.
- **Glow Effects:** The primary action button (e.g., "Request Ride") and active map paths should utilize a subtle outer glow (0px 0px 15px) using the Primary Gold color at 20% opacity to simulate a neon-like light source.
- **Glassmorphism:** Navigation bars and top-status overlays should use a 20px backdrop blur with a 10% white overlay to maintain legibility over the moving map.

## Shapes
The shape language is extremely soft and organic, contrasting with the technical dark theme.

- **Standard Buttons:** Always pill-shaped (fully rounded) to imply safety and comfort.
- **Cards:** Use a 20px (`rounded-lg`) corner radius for all main UI containers.
- **Bottom Sheets:** Use a 32px (`rounded-xl`) radius on the top-left and top-right corners only.
- **Active Indicators:** Selection states (e.g., car type selection) should use a continuous, thick stroke that follows the roundedness of the container.

## Components
- **Buttons:** Primary buttons use the Gold accent with black text. Secondary buttons are outlined with a 1px stroke of the Primary White at 20% opacity.
- **Input Fields:** Search bars should be integrated into a pill-shaped container with a `#16181C` fill. Use the Gold color for the cursor and active borders.
- **Chips:** Car category selection (e.g., "Elite," "SUV," "Electric") uses 40px tall pill-shaped chips. When selected, the chip fill changes to Gold; when inactive, it remains a dark charcoal.
- **Cards:** Vehicle option cards should feature a large image of the car, with the price right-aligned in `title-md` styling.
- **Central Navigation:** The primary navigation hub at the bottom should feature a "floating" effect with a more intense golden glow than other elements, making it the clear focal point of the app.
- **Map Markers:** Pickup markers are green circles with a white inner dot; destination markers are red with a subtle white outer ring.