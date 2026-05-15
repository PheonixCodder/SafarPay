# Prompt: Home Banner Carousel

Document and polish the home banner carousel created in `client/lib/features/home/screens/widgets/carousel.dart`.

## Prompt

The home screen has a banner carousel using local banner assets. Make sure the widget follows SafarPay UI conventions and document the feature in the client context system.

## Target Files

- `lib/features/home/screens/widgets/carousel.dart`
- `lib/features/home/home/home.dart`
- `client/context/**`
- `client/plans/**`

## Acceptance Criteria

- `SHomeSlider` renders local banner assets from `SImages.banner1` and `SImages.banner2`.
- Carousel uses `SSizes.imageCarouselHeight`.
- Banner image radius uses `SSizes.cardRadiusLg`.
- Carousel UI uses `SColors` and does not introduce raw `Colors.*`.
- Unused helper widgets are removed from `carousel.dart`.
- Carousel remains wired below the home search and recent rides area.
- Context docs, decisions log, and plans are updated.
