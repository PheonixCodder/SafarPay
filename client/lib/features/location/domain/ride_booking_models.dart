import '../../../data/rides/ride_models.dart';
import '../../../utils/constants/images.dart';

enum SBookingLocationTarget {
  pickup,
  dropoff,
}

enum SBookingSheetMode {
  compose,
  search,
  route,
  vehicles,
  matching,
}

enum SPassengerServiceCategory {
  groceries,
  cityRides,
  cityToCity,
  courier,
  freight,
}

class SRideServiceOption {
  const SRideServiceOption({
    required this.category,
    required this.title,
    required this.subtitle,
    required this.image,
    required this.isBookable,
  });

  final SPassengerServiceCategory category;
  final String title;
  final String subtitle;
  final String image;
  final bool isBookable;
}

class SRideVehicleOffer {
  const SRideVehicleOffer({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.image,
    required this.serviceType,
    required this.category,
    required this.vehicleType,
    required this.baseFare,
    required this.passengerCapacity,
    this.requiresAc = false,
    this.isShared = false,
    this.isBookable = true,
  });

  final String id;
  final String title;
  final String subtitle;
  final String image;
  final ServiceType serviceType;
  final ServiceCategory category;
  final String vehicleType;
  final double baseFare;
  final int passengerCapacity;
  final bool requiresAc;
  final bool isShared;
  final bool isBookable;
}

class SRideBookingCatalog {
  const SRideBookingCatalog._();

  static const services = <SRideServiceOption>[
    SRideServiceOption(
      category: SPassengerServiceCategory.groceries,
      title: 'Groceries',
      subtitle: 'Store delivery',
      image: SImages.groceries,
      isBookable: false,
    ),
    SRideServiceOption(
      category: SPassengerServiceCategory.cityRides,
      title: 'City rides',
      subtitle: 'Daily passenger rides',
      image: SImages.cityRides,
      isBookable: true,
    ),
    SRideServiceOption(
      category: SPassengerServiceCategory.cityToCity,
      title: 'City to City',
      subtitle: 'Longer trips',
      image: SImages.cityToCity,
      isBookable: true,
    ),
    SRideServiceOption(
      category: SPassengerServiceCategory.courier,
      title: 'Couriers',
      subtitle: 'Parcel delivery',
      image: SImages.courier,
      isBookable: true,
    ),
    SRideServiceOption(
      category: SPassengerServiceCategory.freight,
      title: 'Freight',
      subtitle: 'Cargo delivery',
      image: SImages.freight,
      isBookable: true,
    ),
  ];

  static const vehiclesByService =
      <SPassengerServiceCategory, List<SRideVehicleOffer>>{
    SPassengerServiceCategory.groceries: [
      SRideVehicleOffer(
        id: 'grocery-bike',
        title: 'Bike delivery',
        subtitle: 'Store selection required',
        image: SImages.courier,
        serviceType: ServiceType.grocery,
        category: ServiceCategory.bike,
        vehicleType: 'BIKE',
        baseFare: 140,
        passengerCapacity: 1,
        isBookable: false,
      ),
      SRideVehicleOffer(
        id: 'grocery-car',
        title: 'Car delivery',
        subtitle: 'Store selection required',
        image: SImages.cityRides,
        serviceType: ServiceType.grocery,
        category: ServiceCategory.mini,
        vehicleType: 'HATCHBACK',
        baseFare: 240,
        passengerCapacity: 1,
        isBookable: false,
      ),
    ],
    SPassengerServiceCategory.cityRides: [
      SRideVehicleOffer(
        id: 'city-moto',
        title: 'Moto',
        subtitle: '1 passenger, fast pickup',
        image: SImages.courier,
        serviceType: ServiceType.cityRide,
        category: ServiceCategory.bike,
        vehicleType: 'BIKE',
        baseFare: 110,
        passengerCapacity: 1,
      ),
      SRideVehicleOffer(
        id: 'city-mini',
        title: 'Mini',
        subtitle: '4 seats, lower fares',
        image: SImages.driverVehicleCar,
        serviceType: ServiceType.cityRide,
        category: ServiceCategory.mini,
        vehicleType: 'HATCHBACK',
        baseFare: 210,
        passengerCapacity: 4,
      ),
      SRideVehicleOffer(
        id: 'city-rickshaw',
        title: 'Rickshaw',
        subtitle: '3 seats, short trips',
        image: SImages.cityRides,
        serviceType: ServiceType.cityRide,
        category: ServiceCategory.rickshaw,
        vehicleType: 'RICKSHAW',
        baseFare: 180,
        passengerCapacity: 3,
      ),
      SRideVehicleOffer(
        id: 'city-ac',
        title: 'Ride A/C',
        subtitle: '4 seats, air conditioned',
        image: SImages.driverVehicleCar,
        serviceType: ServiceType.cityRide,
        category: ServiceCategory.rideAc,
        vehicleType: 'SEDAN',
        baseFare: 260,
        passengerCapacity: 4,
        requiresAc: true,
      ),
      SRideVehicleOffer(
        id: 'city-premium',
        title: 'Premium',
        subtitle: 'Sedans with higher comfort',
        image: SImages.driverVehicleCar,
        serviceType: ServiceType.cityRide,
        category: ServiceCategory.premium,
        vehicleType: 'SUV',
        baseFare: 390,
        passengerCapacity: 4,
        requiresAc: true,
      ),
    ],
    SPassengerServiceCategory.cityToCity: [
      SRideVehicleOffer(
        id: 'intercity-car',
        title: 'Car',
        subtitle: 'Private intercity trip',
        image: SImages.cityToCity,
        serviceType: ServiceType.intercity,
        category: ServiceCategory.private,
        vehicleType: 'SEDAN',
        baseFare: 1200,
        passengerCapacity: 4,
        requiresAc: true,
      ),
      SRideVehicleOffer(
        id: 'intercity-van',
        title: 'Van',
        subtitle: 'More seats and luggage',
        image: SImages.cityToCity,
        serviceType: ServiceType.intercity,
        category: ServiceCategory.comfort,
        vehicleType: 'VAN',
        baseFare: 1800,
        passengerCapacity: 8,
        requiresAc: true,
      ),
    ],
    SPassengerServiceCategory.courier: [
      SRideVehicleOffer(
        id: 'courier-bike',
        title: 'Bike courier',
        subtitle: 'Small parcel delivery',
        image: SImages.courier,
        serviceType: ServiceType.courier,
        category: ServiceCategory.bike,
        vehicleType: 'BIKE',
        baseFare: 150,
        passengerCapacity: 1,
      ),
      SRideVehicleOffer(
        id: 'courier-car',
        title: 'Car courier',
        subtitle: 'Medium parcels',
        image: SImages.driverVehicleCar,
        serviceType: ServiceType.courier,
        category: ServiceCategory.mini,
        vehicleType: 'HATCHBACK',
        baseFare: 260,
        passengerCapacity: 1,
      ),
      SRideVehicleOffer(
        id: 'courier-rickshaw',
        title: 'Rickshaw courier',
        subtitle: 'Local package runs',
        image: SImages.courier,
        serviceType: ServiceType.courier,
        category: ServiceCategory.rickshaw,
        vehicleType: 'RICKSHAW',
        baseFare: 230,
        passengerCapacity: 1,
      ),
    ],
    SPassengerServiceCategory.freight: [
      SRideVehicleOffer(
        id: 'freight-pickup',
        title: 'Pickup',
        subtitle: 'Light cargo',
        image: SImages.freight,
        serviceType: ServiceType.freight,
        category: ServiceCategory.private,
        vehicleType: 'PICKUP',
        baseFare: 900,
        passengerCapacity: 1,
      ),
      SRideVehicleOffer(
        id: 'freight-mini-truck',
        title: 'Mini truck',
        subtitle: 'Medium cargo',
        image: SImages.freight,
        serviceType: ServiceType.freight,
        category: ServiceCategory.comfort,
        vehicleType: 'MINI_TRUCK',
        baseFare: 1400,
        passengerCapacity: 1,
      ),
      SRideVehicleOffer(
        id: 'freight-truck',
        title: 'Truck',
        subtitle: 'Large cargo',
        image: SImages.freight,
        serviceType: ServiceType.freight,
        category: ServiceCategory.private,
        vehicleType: 'TRUCK',
        baseFare: 2400,
        passengerCapacity: 1,
      ),
    ],
  };

  static List<SRideVehicleOffer> vehiclesFor(
    SPassengerServiceCategory category,
  ) {
    return vehiclesByService[category] ?? const [];
  }
}
