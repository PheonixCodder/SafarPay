import 'package:client/features/location/data/bidding_repository.dart';
import 'package:client/features/location/data/demo/location_demo_data.dart';
import 'package:client/features/location/data/geospatial_repository.dart';
import 'package:client/features/location/data/location_repository.dart';
import 'package:client/features/location/data/ride_repository.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('demo geocode and reverse geocode return Lahore UI data', () async {
    final repository = SLocationRepository();

    final geocode = await repository.geocode('hospital');
    final reverse = await repository.reverseGeocode(
      const SCoordinate(latitude: 31.4821, longitude: 74.4096),
    );

    expect(geocode.formatted, contains('Ayesha Hospital'));
    expect(reverse.formatted, contains('Demo pin'));
    expect(reverse.city, 'Lahore');
  });

  test('demo route preview is available without backend', () async {
    const repository = SGeospatialRepository();
    final route = await repository.calculateRoute(
      origin: SLocationDemoData.pickup.coordinate,
      destination: SLocationDemoData.dropoff.coordinate,
    );
    final validation = await repository.validatePickup(
      SLocationDemoData.pickup.coordinate,
    );
    final surge = await repository.getSurge(SLocationDemoData.pickup.coordinate);

    expect(route.distanceKm, greaterThan(0));
    expect(route.durationMinutes, greaterThan(0));
    expect(route.steps, isNotEmpty);
    expect(validation['valid'], isTrue);
    expect(surge['surge_multiplier'], 1.0);
  });

  test('demo ride creation and session lookup stay hybrid', () async {
    final offer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.cityRides,
    ).firstWhere((item) => item.id == 'city-mini');
    final body = SRideRepository.buildHybridRideRequest(
      pickup: SLocationDemoData.pickup,
      dropoff: SLocationDemoData.dropoff,
      offer: offer,
      passengerOffer: 250,
      autoAcceptDriver: true,
    );

    final ride = await const SRideRepository().createRide(body);
    final rideDetails = await const SRideRepository().fetchRide(
      ride['id'].toString(),
    );
    final session = await const SBiddingRepository().getSessionForRide(
      ride['id'].toString(),
    );
    final bids = await const SBiddingRepository().getBidsForSession(
      session['session_id'].toString(),
    );
    final counter = await const SBiddingRepository().sendPassengerCounter(
      sessionId: session['session_id'].toString(),
      counterPrice: 250,
      counterEtaMinutes: 4,
    );
    final locations = await SLocationRepository().getRideLocations(
      ride['id'].toString(),
    );

    expect(ride['id'], 'demo-ride-001');
    expect(ride['pricing_mode'], 'HYBRID');
    expect(rideDetails['status'], 'MATCHING');
    expect(session['session_id'], 'demo-hybrid-session-001');
    expect(session['pricing_mode'], 'HYBRID');
    expect(bids['status'], 'OPEN');
    expect(counter['status'], 'PENDING');
    expect(locations.driver?.driverId, 'demo-driver-001');
  });
}
