# Prompt: Reusable Ride Search Result Widget

Create a reusable widget for ride location search results that matches the provided reference image.

## Prompt

Create `client/lib/common/widgets/ride/search_result.dart`. The widget should show a rounded icon tile, a location title, the actual address beneath it, and the travel time aligned to the far right. The icon, location title, address, and time should be passed as arguments. Use existing SafarPay utilities, colors, theme text styles, and spacing constants.

## Target Files

- `lib/common/widgets/ride/search_result.dart`
- `client/context/**`
- `client/plans/**`

## Acceptance Criteria

- Widget class is reusable and named `SSearchResult`.
- Constructor accepts `icon`, `title`, `address`, and `duration`.
- Optional `onTap` makes the row tappable without changing the visual layout.
- Optional `showDivider` controls the bottom divider.
- Visual structure matches the reference: leading rounded light icon tile, title/address text column, duration on the far right, and divider aligned under the text area.
- Long titles, addresses, and durations use ellipsis instead of overflowing.
- Uses `SColors`, `SSizes`, and `Theme.of(context).textTheme`.
- Does not introduce raw `Colors.*`.
