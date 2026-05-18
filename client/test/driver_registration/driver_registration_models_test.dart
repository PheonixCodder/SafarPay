import 'package:flutter_test/flutter_test.dart';

import 'package:client/features/personalization/screens/driver_registration/controllers/driver_verification_controller.dart';
import 'package:client/features/personalization/screens/driver_registration/data/driver_verification_demo_data.dart';
import 'package:client/features/personalization/screens/driver_registration/models/driver_registration_models.dart';

void main() {
  group('SVerificationStatusResponse', () {
    test('parses aggregated verification status response', () {
      final status = SVerificationStatusResponse.fromJson({
        'driver_id': 'driver-1',
        'overall_status': 'rejected',
        'identity': {
          'status': 'verified',
          'documents': [
            {
              'id': 'doc-1',
              'document_type': 'id_front',
              'status': 'verified',
              'rejection_reason': null,
              'submitted_at': '2026-05-17T12:00:00Z',
            },
          ],
          'rejection_reason': null,
        },
        'license': {
          'status': 'rejected',
          'documents': [],
          'rejection_reason': 'DOC_BLURRY',
        },
        'selfie': {
          'status': 'pending',
          'documents': [],
          'rejection_reason': null,
        },
        'vehicle': {
          'status': 'not_submitted',
          'documents': [],
          'rejection_reason': null,
        },
      });

      expect(status.driverId, 'driver-1');
      expect(status.overallStatus, SVerificationOverallStatus.rejected);
      expect(status.identity.status, SVerificationGroupStatus.verified);
      expect(status.license.status, SVerificationGroupStatus.rejected);
      expect(status.license.rejectionReason, 'DOC_BLURRY');
      expect(status.selfie.status, SVerificationGroupStatus.pending);
      expect(status.vehicle.status, SVerificationGroupStatus.notSubmitted);
      expect(status.identity.documents.single.documentType, 'id_front');
      expect(status.identity.documents.single.submittedAt, isNotNull);
    });

    test('defaults unknown and missing fields to not started states', () {
      final status = SVerificationStatusResponse.fromJson({
        'overall_status': 'unknown',
      });

      expect(status.overallStatus, SVerificationOverallStatus.notStarted);
      expect(status.identity.status, SVerificationGroupStatus.notSubmitted);
      expect(status.license.documents, isEmpty);
      expect(status.selfie.documents, isEmpty);
      expect(status.vehicle.documents, isEmpty);
    });
  });

  group('SDriverRegistrationCatalog', () {
    test('returns category-specific vehicle options', () {
      expect(
        SDriverRegistrationCatalog.vehiclesFor(SDriverWorkCategoryType.city)
            .map((vehicle) => vehicle.title),
        ['Car', 'Motorcycle', 'Rickshaw'],
      );
      expect(
        SDriverRegistrationCatalog.vehiclesFor(SDriverWorkCategoryType.freight)
            .map((vehicle) => vehicle.title),
        ['Pickup', 'Mini truck', 'Truck'],
      );
      expect(
        SDriverRegistrationCatalog.vehiclesFor(SDriverWorkCategoryType.grocery)
            .map((vehicle) => vehicle.title),
        ['Motorcycle', 'Car'],
      );
    });
  });

  group('driver verification submission models', () {
    test('parses document upload urls response', () {
      final response = SDocumentUploadUrlsResponse.fromJson({
        'message': 'Success',
        'urls': {
          'id_front': {
            'key': 'user/identity/id_front_uuid',
            'url': 'https://example.com/id-front',
          },
          'id_back': {
            'key': 'user/identity/id_back_uuid',
            'url': 'https://example.com/id-back',
          },
        },
      });

      expect(response.message, 'Success');
      expect(response.urls.keys, containsAll(['id_front', 'id_back']));
      expect(response.urls['id_front']?.key, 'user/identity/id_front_uuid');
      expect(response.urls['id_back']?.url, 'https://example.com/id-back');
    });

    test('serializes CNIC and license requests with backend keys', () {
      final expiry = DateTime(2030, 4, 12);

      expect(
        SCnicSubmissionRequest(
          idNumber: '3520212345671',
          expiryDate: expiry,
        ).toJson(),
        {
          'id_number': '3520212345671',
          'expiry_date': '2030-04-12',
        },
      );

      expect(
        SDriverLicenseSubmissionRequest(
          licenseNumber: 'LIC-12345',
          expiryDate: expiry,
        ).toJson(),
        {
          'license_number': 'LIC-12345',
          'expiry_date': '2030-04-12',
        },
      );
    });

    test('serializes vehicle request with backend keys', () {
      final request = SVehicleSubmissionRequest(
        brand: 'Toyota',
        model: 'Corolla',
        color: 'White',
        vehicleType: SVerificationVehicleType.economy,
        maxPassengers: 4,
        plateNumber: 'ABC-123',
        productionYear: 2022,
      );

      expect(request.toJson(), {
        'vehicle_id': null,
        'brand': 'Toyota',
        'model': 'Corolla',
        'color': 'White',
        'vehicle_type': 'economy',
        'max_passengers': 4,
        'plate_number': 'ABC-123',
        'production_year': 2022,
      });
    });

    test('maps display vehicle options to verification vehicle enum', () {
      expect(
        SVerificationVehicleType.fromDisplayVehicle(SDriverVehicleType.car),
        SVerificationVehicleType.economy,
      );
      expect(
        SVerificationVehicleType.fromDisplayVehicle(
          SDriverVehicleType.motorcycle,
        ),
        SVerificationVehicleType.moto,
      );
      expect(
        SVerificationVehicleType.fromDisplayVehicle(SDriverVehicleType.truck),
        SVerificationVehicleType.freight,
      );
    });
  });

  group('SDriverVerificationDemoData', () {
    test('all demo scenarios parse into verification status responses', () {
      for (final scenario in SDriverVerificationDemoScenario.values) {
        final response = SVerificationStatusResponse.fromJson(
          SDriverVerificationDemoData.responseFor(scenario),
        );

        expect(response.identity.documents, isNotNull, reason: scenario.name);
        expect(response.license.documents, isNotNull, reason: scenario.name);
        expect(response.selfie.documents, isNotNull, reason: scenario.name);
        expect(response.vehicle.documents, isNotNull, reason: scenario.name);
      }
    });

    test('under review demo maps all cards to blocked state', () {
      final controller = SDriverVerificationController();
      controller.status.value = SVerificationStatusResponse.fromJson(
        SDriverVerificationDemoData.responseFor(
          SDriverVerificationDemoScenario.underReview,
        ),
      );

      final cards = controller.stepCards();

      expect(cards, hasLength(4));
      expect(cards.every((card) => !card.isEnabled), isTrue);
      expect(cards.every((card) => card.supportingText == 'Under review'),
          isTrue);
    });

    test('verified demo maps all cards to approved blocked state', () {
      final controller = SDriverVerificationController();
      controller.status.value = SVerificationStatusResponse.fromJson(
        SDriverVerificationDemoData.responseFor(
          SDriverVerificationDemoScenario.verified,
        ),
      );

      final cards = controller.stepCards();

      expect(cards, hasLength(4));
      expect(cards.every((card) => !card.isEnabled), isTrue);
      expect(cards.every((card) => card.supportingText == 'Approved'), isTrue);
    });

    test('rejected demos expose rejection reasons', () {
      final scenarios = {
        SDriverVerificationDemoScenario.identityRejected: 'DOC_BLURRY',
        SDriverVerificationDemoScenario.licenseRejected: 'LICENSE_EXPIRED',
        SDriverVerificationDemoScenario.selfieRejected: 'FACE_NOT_MATCHED',
        SDriverVerificationDemoScenario.vehicleRejected: 'PLATE_NOT_READABLE',
      };

      for (final entry in scenarios.entries) {
        final response = SVerificationStatusResponse.fromJson(
          SDriverVerificationDemoData.responseFor(entry.key),
        );

        final rejectedGroups = [
          response.identity,
          response.license,
          response.selfie,
          response.vehicle,
        ].where(
          (group) => group.status == SVerificationGroupStatus.rejected,
        );

        expect(rejectedGroups.single.rejectionReason, entry.value);
      }
    });

    test('ready to submit demo enables submit for review', () {
      final controller = SDriverVerificationController();
      controller.status.value = SVerificationStatusResponse.fromJson(
        SDriverVerificationDemoData.responseFor(
          SDriverVerificationDemoScenario.readyToSubmit,
        ),
      );

      expect(controller.canSubmitForReview, isTrue);
    });

    test('non-ready demos do not enable submit for review', () {
      final blockedScenarios = [
        SDriverVerificationDemoScenario.notStarted,
        SDriverVerificationDemoScenario.partiallySubmitted,
        SDriverVerificationDemoScenario.underReview,
        SDriverVerificationDemoScenario.verified,
        SDriverVerificationDemoScenario.identityRejected,
        SDriverVerificationDemoScenario.licenseRejected,
        SDriverVerificationDemoScenario.selfieRejected,
        SDriverVerificationDemoScenario.vehicleRejected,
        SDriverVerificationDemoScenario.multipleRejected,
      ];

      for (final scenario in blockedScenarios) {
        final controller = SDriverVerificationController();
        controller.status.value = SVerificationStatusResponse.fromJson(
          SDriverVerificationDemoData.responseFor(scenario),
        );

        expect(
          controller.canSubmitForReview,
          isFalse,
          reason: scenario.name,
        );
      }
    });

    test('demo submit for review moves status to under review', () async {
      final controller = SDriverVerificationController();
      controller.status.value = SVerificationStatusResponse.fromJson(
        SDriverVerificationDemoData.responseFor(
          SDriverVerificationDemoScenario.readyToSubmit,
        ),
      );

      await controller.submitForReview();

      expect(
        controller.status.value?.overallStatus,
        SVerificationOverallStatus.underReview,
      );
      expect(controller.canSubmitForReview, isFalse);
      expect(controller.isSubmittingReview.value, isFalse);
    });
  });
}
