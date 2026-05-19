# UI Context

## Theme

SafarPay uses a light, clean mobile design language for ride-hailing workflows. Authentication screens should feel secure, direct, and calm: light backgrounds, restrained teal accents, clear form hierarchy, generous touch targets, and simple progress through onboarding, login, OTP, profile, permissions, and home.

## Colors

All app colors should come from `SColors` in `lib/utils/constants/colors.dart`.
Reusable alpha values should come from `SOpacities`, and widgets should apply them through `SHelperFunctions.withOpacity`.

| Role | Token | Value |
| --- | --- | --- |
| Primary accent | `SColors.primary` | `0xFF338B95` |
| Secondary | `SColors.secondary` | `0xFF6B7280` |
| Accent | `SColors.accent` | `0xFFB0C7FF` |
| Page background | `SColors.primaryBackground` | `0xFFF9F9F9` |
| Surface | `SColors.white` | `Colors.white` |
| Light surface | `SColors.lightContainer` | `0xFFF6F6F6` |
| Primary text | `SColors.textPrimary` | `0xFF222222` |
| Secondary text | `SColors.textSecondary` | `0xFF6B7280` |
| Border | `SColors.borderSecondary` | `0xFFE6E6E6` |
| Error | `SColors.error` | `0xFFD32F2F` |
| Success | `SColors.success` | `0xFF388E3C` |

Do not hard-code new hex values in feature UI unless the color is first added to `SColors`.

## Typography

| Role | Font | Source |
| --- | --- | --- |
| App UI text | SF Pro | `pubspec.yaml` font family `SF-Pro` |
| Material text styles | `STextTheme.lightTextTheme` | `lib/utils/theme/custom_themes/text_theme.dart` |

Use theme text styles and override only weight, color, or alignment when needed. SafarPay uses upright typography only; italic font faces are not part of the client visual language and should not be registered in `pubspec.yaml`. If a weight only exists as an italic asset, do not register or use that weight until a matching upright font file is available.

## Spacing And Radius

Use `SSizes` for spacing, icon sizes, card radius, field spacing, and loading indicator dimensions.

| Context | Token examples |
| --- | --- |
| Small gaps | `SSizes.xs`, `SSizes.sm` |
| Form fields | `SSizes.spaceBtwInputFields` |
| Screen sections | `SSizes.spaceBtwSections`, `SSizes.defaultSpace` |
| Cards and panels | `SSizes.cardRadiusSm`, `SSizes.cardRadiusMd`, `SSizes.cardRadiusLg` |
| Buttons and fields | `SSizes.buttonRadius`, `SSizes.inputFieldRadius` |

## Component Conventions

- Authentication screens use `Scaffold`, `SafeArea`, `SingleChildScrollView`, centered `ConstrainedBox(maxWidth: 420)`, and `SColors.primaryBackground`.
- Use `TextFormField` with validators from `SValidator`.
- Use `ElevatedButton` for primary actions and `OutlinedButton` for secondary provider actions.
- Keep `Obx` scoped to the smallest changing widget.
- Use private widgets in the same screen file for one-off composition; move to `widgets/` when reused.

## Icons

Use `iconsax` icons for Flutter UI. Typical sizes come from `SSizes.iconSm`, `SSizes.iconMd`, and `SSizes.iconLg`.

## Layout Patterns And Completed Screens

- Onboarding: full-screen paged layout with bottom navigation controls.
- Login: header, phone form, divider, Google button.
- OTP: header, custom OTP input, verify/resend actions.
- Profile: header, form, terms agreement, primary continue action.
- Permissions: one focused permission request per page.
- Google phone link: identity confirmation card followed by phone number form; no Google button after Google verification.
- Navigation menu: custom bottom bar anchored at the bottom with Home, Trips, Rent, and Profile tabs; active tab uses a primary-colored icon, label, and animated top indicator line with no pill highlight. The indicator position is calculated from the available tab width so it remains centered across screen sizes.
- Ride search result: compact row with a rounded light icon tile, primary title, muted one-line address, muted right-aligned duration, and a divider aligned under the text area.
- Home search: the search field uses common `SSearchBar`; recent ride rows remain Home-owned and render with `SSearchResult`.
- Home carousel: local banner images are displayed with `SHomeSlider`, `SSizes.imageCarouselHeight`, and `SSizes.cardRadiusLg`.
- Home categories: light-mode service tiles are displayed with `SHomeCategories`; the layout uses one dominant Groceries tile, stacked City rides and City to City tiles, then Couriers and Freight tiles below.
- Notification, category, and ride search widgets keep upgraded visual dimensions in `SSizes` rather than local literals.
- Shared visual primitives such as rounded images, circular images, decorative containers, search bars, primary headers, and navigation tabs live in `lib/common/widgets` so reused UI keeps the same sizing and color tokens.
- Settings: personalization settings uses a branded primary header, profile tile, focused settings menu rows, switch rows, and a full-width logout action composed from one-widget files.
- Settings user-info navigation: profile edit and the `User Info` row open the personalization `ProfileScreen` with a reusable right-slide transition from `lib/common/navigation`.
- Common edit drawer: existing-value edits use a right-side shadcn `ShadSheet` with SafarPay colors, compact labels, a single input, and clear cancel/save actions.
- Profile user info: profile rows use boxed edit icons instead of right-arrow affordances and update visible values locally until backend persistence is planned.
- Privacy Policy: the Settings `Privacy & Security` row opens an informational subpage with `SAppBar`, the shared right-slide transition, a white summary panel, compact trust cues, and expandable policy sections rendered from mapped content.
- Notifications: the Settings `Notifications` row opens a timeline-style inbox subpage with a compact summary panel, horizontal filter chips, grouped date labels, and soft notification rows for trips, payments, offers, safety, and system updates.
- Help & Support: the Settings `Help & Support` row opens a reference-matched support hub with a teal `SPrimaryHeaderContainer`, centered scooter support illustration, and a rounded white options sheet with simple icon rows.
- Terms & Conditions: the Help & Support terms row opens a compact legal hub with a rounded white policy list, teal icon tiles, centered last-updated copy, and shared-app-bar detail pages with numbered expandable policy sections backed by typed local data.
- FAQ: the Help & Support FAQ row opens a compact help center with a rounded local search field, interactive category filters, filtered article lists, and shared-app-bar article detail pages with illustration, bullets, highlighted guidance, helpful controls, and related articles.
- Something Else: the Help & Support Something Else row opens a focused support-ticket form with a centered title, issue text area, optional related ride card, image/file/audio attachment action tiles, full-width submit CTA, and a confirmation screen showing ticket id, expected response, My Tickets, and Back to Home actions.
- Contact Us: the Help & Support contact row opens a compact page with `SAppBar`, a centered support-agent illustration, three elevated action cards for call/email/chat, and a simple social media list for Twitter, Instagram, Facebook, Linked In, and Medium.
- Driver registration: the Settings `Register as a Driver` row opens a light-mode earning category list with image tiles, titles, subtitles, and chevrons. Category selection opens a matching vehicle selection list. Vehicle selection opens a teal `SPrimaryHeaderContainer` verification checklist with a stacked vehicle chip, category title, helper copy, right-aligned driver artwork, an overall status notice, and four actionable status cards for CNIC, license, selfie, and vehicle details. Each card opens a focused light-mode form with document upload tiles or a realtime selfie capture surface. When all four status groups are submitted, a full-width primary `Submit for Review` button appears beneath the checklist.
- Trips: the bottom navigation Trips tab opens a clean ride operations page with `SAppBar`, a segmented four-tab control, compact route-first ride cards, and a shared ride details screen.
- Passenger booking: Home search opens a full-screen map-first booking surface. The Mapbox map stays behind a draggable bottom sheet where pickup/dropoff bars, backend search results, service categories, route summary, vehicle choices, fare stepper, auto-accept toggle, and matching state are composed in SafarPay light theme.
- Home: first navigation tab with app bar greeting and a large icon treatment.
- Starter tabs: Trips and Rent use restrained empty states until their full feature units are built; Profile opens the Settings experience.

## Current Visual Assets

- Logo: `assets/logos/logo.png`.
- Google icon: `assets/logos/google-icon.png`.
- Onboarding images: `assets/images/onboarding/ON1.jpg`, `ON2.jpg`, `ON3.jpg`.
- Home banners: `assets/images/banners/banner1.png`, `banner2.png`.
- Home categories: `assets/images/categories/groceries.png`, `city-rides.png`, `city-to-city.png`, `courier.png`, `freight.png`.
- Driver registration: `assets/images/driver/register_image.png`, vehicle placeholders under `assets/images/driver/`, and `assets/images/rides/car.png`.
- Icons: local SVG assets plus Iconsax for Flutter controls.
- Fonts: upright SF Pro Display variants declared in `pubspec.yaml`.
