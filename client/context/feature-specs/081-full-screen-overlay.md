# Full-Screen Native Overlay (081)

## Prompt

Convert the native Android driver requests overlay from a partial top overlay into a premium, full-screen interactive view. 

## Requirements

- Update `WindowManager.LayoutParams` in `DriverRideOverlayService.kt` to use `MATCH_PARENT` for both width and height.
- Position the overlay window to fill the entire screen (remove y offset and top gravity).
- Redesign `buildOverlay` in Kotlin to use a full-screen vertical layout:
  - A clean, spacious white background.
  - Larger, prominent title text (24sp) and readable body text (16sp) with generous padding.
  - Use layout weights to push the action buttons to the bottom of the screen.
  - Modernize action buttons: Make them full-width or side-by-side with high-contrast, rounded corners matching SafarPay's styling.
