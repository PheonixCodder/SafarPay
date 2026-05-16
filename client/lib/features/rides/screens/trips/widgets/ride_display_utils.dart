import '../../../../../data/rides/ride_models.dart';

class SRideDisplayUtils {
  SRideDisplayUtils._();

  static String money(double? value) {
    if (value == null) return 'Pending';
    final rounded = value.round();
    return 'Rs. $rounded';
  }

  static String dateTime(DateTime? value) {
    if (value == null) return 'Not set';
    final local = value.toLocal();
    final hour = local.hour > 12 ? local.hour - 12 : local.hour;
    final normalizedHour = hour == 0 ? 12 : hour;
    final minute = local.minute.toString().padLeft(2, '0');
    final meridiem = local.hour >= 12 ? 'PM' : 'AM';
    return '${_month(local.month)} ${local.day}, $normalizedHour:$minute $meridiem';
  }

  static String status(RideStatus status) {
    return switch (status) {
      RideStatus.created => 'Created',
      RideStatus.matching => 'Matching',
      RideStatus.accepted => 'Accepted',
      RideStatus.arriving => 'Arriving',
      RideStatus.inProgress => 'In progress',
      RideStatus.completed => 'Completed',
      RideStatus.cancelled => 'Canceled',
    };
  }

  static String service(ServiceType serviceType) {
    return switch (serviceType) {
      ServiceType.cityRide => 'City ride',
      ServiceType.intercity => 'Intercity',
      ServiceType.freight => 'Freight',
      ServiceType.courier => 'Courier',
      ServiceType.grocery => 'Grocery',
    };
  }

  static String category(ServiceCategory category) {
    return switch (category) {
      ServiceCategory.mini => 'Mini',
      ServiceCategory.rickshaw => 'Rickshaw',
      ServiceCategory.rideAc => 'Ride AC',
      ServiceCategory.premium => 'Premium',
      ServiceCategory.bike => 'Bike',
      ServiceCategory.comfort => 'Comfort',
      ServiceCategory.share => 'Share',
      ServiceCategory.private => 'Private',
    };
  }

  static String pricing(PricingMode pricingMode) {
    return switch (pricingMode) {
      PricingMode.fixed => 'Fixed',
      PricingMode.bidBased => 'Bid based',
      PricingMode.hybrid => 'Hybrid',
    };
  }

  static String payment(PassengerPaymentMethod method) {
    return switch (method) {
      PassengerPaymentMethod.card => 'Card',
      PassengerPaymentMethod.cash => 'Cash',
      PassengerPaymentMethod.easypaisa => 'Easypaisa',
      PassengerPaymentMethod.jazzcash => 'JazzCash',
    };
  }

  static String routeTitle(RideResponse ride) {
    final pickup = ride.pickupStop?.placeName ?? 'Pickup';
    final dropoff = ride.dropoffStop?.placeName ?? 'Dropoff';
    return '$pickup to $dropoff';
  }

  static String _month(int value) {
    return const [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ][value - 1];
  }
}
