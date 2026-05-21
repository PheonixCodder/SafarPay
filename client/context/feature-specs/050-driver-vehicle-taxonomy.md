# 050 - Driver Vehicle Taxonomy

## Prompt

Normalize driver registration and ride management around clear service, vehicle, category, and pricing boundaries.

The backend currently mixes driver vehicle registration buckets, ride vehicle body styles, passenger categories, and service types. Driver registration must support five service types: City Driver, Courier, City to City Driver, Freight Driver, and Grocery Driver. Vehicle registration must use exactly seven canonical vehicles: Car, Motorcycle, Rickshaw, Van, Pickup, Mini Truck, and Truck.

## Decisions

- `ServiceType` represents the work flow: `CITY_RIDE`, `INTERCITY`, `FREIGHT`, `COURIER`, `GROCERY`.
- `VehicleType` represents physical vehicles only: `CAR`, `MOTORCYCLE`, `RICKSHAW`, `VAN`, `PICKUP`, `MINI_TRUCK`, `TRUCK`.
- `ServiceCategory` remains passenger-facing product/tier selection.
- `PricingMode` remains pricing mechanics and does not affect driver registration.
- Verification owns driver vehicles and driver service capabilities.
- Ride and Bidding must prevent a driver from being active on more than one ride.
