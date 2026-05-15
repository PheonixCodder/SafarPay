# Home Carousel Documentation And Polish Plan

## Summary

Document and polish the home banner carousel in `client/lib/features/home/screens/widgets/carousel.dart`. Keep `SHomeSlider` wired into the current home screen while aligning carousel styling with SafarPay constants.

## Key Changes

- Add feature spec `client/context/feature-specs/014-home-carousel.md`.
- Keep `SHomeSlider` as the public home carousel widget.
- Use `SSizes.imageCarouselHeight` for carousel and image height.
- Use `SSizes.cardRadiusLg` for banner radius.
- Use `SColors.transparent` instead of raw transparent color.
- Remove unused `SCircularContainer` from `carousel.dart`.
- Keep local banner assets declared through `SImages.banner1` and `SImages.banner2`.
- Update context docs and decisions to record local home banner carousel usage.

## Test Plan

- Run `dart format lib/features/home/screens/widgets/carousel.dart lib/features/home/home/home.dart`.
- Run `flutter analyze --no-pub lib/features/home/screens/widgets/carousel.dart lib/features/home/home/home.dart`.
- Confirm no raw `Colors.*` in `carousel.dart`.
- Confirm no `SCircularContainer` remains.
- Confirm `SHomeSlider` renders `SImages.banner1` and `SImages.banner2`.
- Confirm carousel uses `SSizes.imageCarouselHeight` and `SSizes.cardRadiusLg`.

## Assumptions

- The two local banner assets are intentional.
- The `carousel_slider` dependency and `assets/images/banners/` pubspec asset entry are intentional.
- The class name `SHomeSlider` remains unchanged because it is already used by the home screen.
