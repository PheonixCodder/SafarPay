import '../../../data/rides/ride_models.dart';
import '../../../utils/constants/images.dart';
import 'location_models.dart';

enum SBookingLocationTarget {
  pickup,
  dropoff,
}

enum SBookingSheetMode {
  compose,
  search,
  route,
  vehicles,
  details,
  review,
  matching,
}

enum SDriverGenderPreference {
  noPreference('NO_PREFERENCE'),
  male('MALE'),
  female('FEMALE'),
  any('ANY');

  const SDriverGenderPreference(this.value);

  final String value;
}

enum SFuelType {
  petrol('PETROL'),
  diesel('DIESEL'),
  cng('CNG'),
  hybrid('HYBRID'),
  electric('ELECTRIC');

  const SFuelType(this.value);

  final String value;
}

class SCityRideOptions {
  const SCityRideOptions({
    this.passengerCount = 1,
    this.driverGenderPreference = SDriverGenderPreference.noPreference,
    this.allowedFuelTypes = const [],
    this.isPetAllowed = false,
    this.isSmokingAllowed = false,
    this.requiresWheelchairAccess = false,
    this.maxWaitTimeMinutes,
    this.requiresOtpStart = false,
    this.requiresOtpEnd = false,
  });

  final int passengerCount;
  final SDriverGenderPreference driverGenderPreference;
  final List<SFuelType> allowedFuelTypes;
  final bool isPetAllowed;
  final bool isSmokingAllowed;
  final bool requiresWheelchairAccess;
  final int? maxWaitTimeMinutes;
  final bool requiresOtpStart;
  final bool requiresOtpEnd;
}

class SIntercityRideOptions {
  const SIntercityRideOptions({
    this.passengerCount = 1,
    this.luggageCount = 0,
    this.childCount = 0,
    this.seniorCount = 0,
    this.allowedFuelTypes = const [],
    this.preferredDepartureTime,
    this.departureFlexibilityMinutes,
    this.isRoundTrip = false,
    this.returnTime,
    this.minVehicleCapacity,
    this.requiresLuggageCarrier = false,
    this.isSharedRide = false,
    this.maxCoPassengers,
    this.requiresIdentityVerification = false,
    this.emergencyContactName,
    this.emergencyContactNumber,
  });

  final int passengerCount;
  final int luggageCount;
  final int childCount;
  final int seniorCount;
  final List<SFuelType> allowedFuelTypes;
  final DateTime? preferredDepartureTime;
  final int? departureFlexibilityMinutes;
  final bool isRoundTrip;
  final DateTime? returnTime;
  final int? minVehicleCapacity;
  final bool requiresLuggageCarrier;
  final bool isSharedRide;
  final int? maxCoPassengers;
  final bool requiresIdentityVerification;
  final String? emergencyContactName;
  final String? emergencyContactNumber;
}

class SFreightRideOptions {
  const SFreightRideOptions({
    this.cargoWeight = 20,
    this.cargoType = 'General cargo',
    this.requiresLoader = false,
    this.isFragile = false,
    this.requiresTemperatureControl = false,
    this.declaredValue,
    this.commodityNotes,
    this.estimatedLoadHours,
  });

  final double cargoWeight;
  final String cargoType;
  final bool requiresLoader;
  final bool isFragile;
  final bool requiresTemperatureControl;
  final double? declaredValue;
  final String? commodityNotes;
  final int? estimatedLoadHours;
}

class SCourierRideOptions {
  const SCourierRideOptions({
    this.itemDescription = 'Package',
    this.itemWeight = 1,
    this.totalParcels = 1,
    this.recipientName = 'Recipient',
    this.recipientPhone = '03000000000',
    this.recipientEmail,
    this.isFragile = false,
    this.requiresSignature = false,
    this.declaredValue,
    this.specialHandlingNotes,
  });

  final String itemDescription;
  final double? itemWeight;
  final int totalParcels;
  final String recipientName;
  final String recipientPhone;
  final String? recipientEmail;
  final bool isFragile;
  final bool requiresSignature;
  final double? declaredValue;
  final String? specialHandlingNotes;
}

class SGroceryRideOptions {
  const SGroceryRideOptions({
    this.storeId = '',
    this.totalItems = 0,
    this.specialNotes,
    this.contactlessDelivery = false,
    this.estimatedBagCount,
  });

  final String storeId;
  final int totalItems;
  final String? specialNotes;
  final bool contactlessDelivery;
  final int? estimatedBagCount;
}

class SRideBookingDraft {
  const SRideBookingDraft({
    required this.pickup,
    required this.dropoff,
    required this.offer,
    this.pricingMode = PricingMode.hybrid,
    this.passengerOffer = 0,
    this.autoAcceptDriver = false,
    this.paymentMethod = PassengerPaymentMethod.cash,
    this.paymentMethodId,
    this.scheduledAt,
    this.city = const SCityRideOptions(),
    this.intercity = const SIntercityRideOptions(),
    this.freight = const SFreightRideOptions(),
    this.courier = const SCourierRideOptions(),
    this.grocery = const SGroceryRideOptions(),
  });

  final SAddressResult pickup;
  final SAddressResult dropoff;
  final SRideVehicleOffer offer;
  final PricingMode pricingMode;
  final double passengerOffer;
  final bool autoAcceptDriver;
  final PassengerPaymentMethod paymentMethod;
  final String? paymentMethodId;
  final DateTime? scheduledAt;
  final SCityRideOptions city;
  final SIntercityRideOptions intercity;
  final SFreightRideOptions freight;
  final SCourierRideOptions courier;
  final SGroceryRideOptions grocery;
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
        vehicleType: 'MOTORCYCLE',
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
        vehicleType: 'CAR',
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
        vehicleType: 'MOTORCYCLE',
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
        vehicleType: 'CAR',
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
        vehicleType: 'CAR',
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
        vehicleType: 'CAR',
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
        vehicleType: 'CAR',
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
        vehicleType: 'MOTORCYCLE',
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
        vehicleType: 'CAR',
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
