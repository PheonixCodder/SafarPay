# Home Category To Ride Search Prompt

When a user taps any service category on the Home screen, open the passenger `RideSearchScreen` with that specific service category already selected in the booking sheet.

Requirements:

- Keep the current visual design of `SHomeCategories` and `SCategoryTile`.
- Add tap behavior to category tiles without duplicating ride-search navigation logic in every tile.
- Use `SRightSlidePageRoute` for the same smooth transition as the Home search bar.
- Pass the selected `SPassengerServiceCategory` into `RideSearchScreen`.
- `RideSearchScreen` must pass the initial category into `SRideSearchController`.
- `SRideSearchController` must initialize selected category and default vehicle from the provided category instead of always forcing city rides.
- Category mappings:
  - Groceries -> `SPassengerServiceCategory.groceries`
  - City rides -> `SPassengerServiceCategory.cityRides`
  - City to City -> `SPassengerServiceCategory.cityToCity`
  - Couriers -> `SPassengerServiceCategory.courier`
  - Freight -> `SPassengerServiceCategory.freight`

Grocery remains visible and can open the ride search screen, but the existing non-bookable gating remains active until store selection exists.
