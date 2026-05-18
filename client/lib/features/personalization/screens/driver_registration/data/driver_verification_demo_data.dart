enum SDriverVerificationDemoScenario {
  notStarted,
  partiallySubmitted,
  readyToSubmit,
  underReview,
  verified,
  identityRejected,
  licenseRejected,
  selfieRejected,
  vehicleRejected,
  multipleRejected,
}

const SDriverVerificationDemoScenario activeDriverVerificationDemoScenario =
    SDriverVerificationDemoScenario.readyToSubmit;

class SDriverVerificationDemoData {
  SDriverVerificationDemoData._();

  static Map<String, dynamic> get activeResponse {
    return responseFor(activeDriverVerificationDemoScenario);
  }

  static Iterable<Map<String, dynamic>> get allResponses {
    return SDriverVerificationDemoScenario.values.map(responseFor);
  }

  static Map<String, dynamic> responseFor(
    SDriverVerificationDemoScenario scenario,
  ) {
    return switch (scenario) {
      SDriverVerificationDemoScenario.notStarted => _notStarted,
      SDriverVerificationDemoScenario.partiallySubmitted =>
        _partiallySubmitted,
      SDriverVerificationDemoScenario.readyToSubmit => _readyToSubmit,
      SDriverVerificationDemoScenario.underReview => _underReview,
      SDriverVerificationDemoScenario.verified => _verified,
      SDriverVerificationDemoScenario.identityRejected => _identityRejected,
      SDriverVerificationDemoScenario.licenseRejected => _licenseRejected,
      SDriverVerificationDemoScenario.selfieRejected => _selfieRejected,
      SDriverVerificationDemoScenario.vehicleRejected => _vehicleRejected,
      SDriverVerificationDemoScenario.multipleRejected => _multipleRejected,
    };
  }

  static final Map<String, dynamic> _notStarted = {
    'driver_id': null,
    'overall_status': 'not_started',
    'identity': _group('not_submitted'),
    'license': _group('not_submitted'),
    'selfie': _group('not_submitted'),
    'vehicle': _group('not_submitted'),
  };

  static final Map<String, dynamic> _partiallySubmitted = {
    'driver_id': '11111111-1111-4111-8111-111111111111',
    'overall_status': 'pending',
    'identity': _group(
      'pending',
      documents: [
        _document('id-front-1', 'id_front', 'pending'),
        _document('id-back-1', 'id_back', 'pending'),
      ],
    ),
    'license': _group(
      'pending',
      documents: [
        _document('license-front-1', 'license_front', 'pending'),
        _document('license-back-1', 'license_back', 'pending'),
      ],
    ),
    'selfie': _group('not_submitted'),
    'vehicle': _group('not_submitted'),
  };

  static final Map<String, dynamic> _readyToSubmit = {
    'driver_id': '22222222-2222-4222-8222-222222222222',
    'overall_status': 'pending',
    'identity': _group(
      'pending',
      documents: [
        _document('id-front-2', 'id_front', 'pending'),
        _document('id-back-2', 'id_back', 'pending'),
      ],
    ),
    'license': _group(
      'pending',
      documents: [
        _document('license-front-2', 'license_front', 'pending'),
        _document('license-back-2', 'license_back', 'pending'),
      ],
    ),
    'selfie': _group(
      'pending',
      documents: [_document('selfie-2', 'selfie_id', 'pending')],
    ),
    'vehicle': _group(
      'pending',
      documents: [
        _document('registration-front-2', 'registration_doc_front', 'pending'),
        _document('registration-back-2', 'registration_doc_back', 'pending'),
        _document('vehicle-front-2', 'vehicle_photo_front', 'pending'),
        _document('vehicle-back-2', 'vehicle_photo_back', 'pending'),
      ],
    ),
  };

  static final Map<String, dynamic> _underReview = {
    'driver_id': '33333333-3333-4333-8333-333333333333',
    'overall_status': 'under_review',
    'identity': _group(
      'pending',
      documents: [
        _document('id-front-3', 'id_front', 'pending'),
        _document('id-back-3', 'id_back', 'pending'),
      ],
    ),
    'license': _group(
      'pending',
      documents: [
        _document('license-front-3', 'license_front', 'pending'),
        _document('license-back-3', 'license_back', 'pending'),
      ],
    ),
    'selfie': _group(
      'pending',
      documents: [_document('selfie-3', 'selfie_id', 'pending')],
    ),
    'vehicle': _group(
      'pending',
      documents: [
        _document('registration-front-3', 'registration_doc_front', 'pending'),
        _document('registration-back-3', 'registration_doc_back', 'pending'),
        _document('vehicle-front-3', 'vehicle_photo_front', 'pending'),
        _document('vehicle-back-3', 'vehicle_photo_back', 'pending'),
      ],
    ),
  };

  static final Map<String, dynamic> _verified = {
    'driver_id': '44444444-4444-4444-8444-444444444444',
    'overall_status': 'verified',
    'identity': _group(
      'verified',
      documents: [
        _document('id-front-4', 'id_front', 'verified'),
        _document('id-back-4', 'id_back', 'verified'),
      ],
    ),
    'license': _group(
      'verified',
      documents: [
        _document('license-front-4', 'license_front', 'verified'),
        _document('license-back-4', 'license_back', 'verified'),
      ],
    ),
    'selfie': _group(
      'verified',
      documents: [_document('selfie-4', 'selfie_id', 'verified')],
    ),
    'vehicle': _group(
      'verified',
      documents: [
        _document('registration-front-4', 'registration_doc_front', 'verified'),
        _document('registration-back-4', 'registration_doc_back', 'verified'),
        _document('vehicle-front-4', 'vehicle_photo_front', 'verified'),
        _document('vehicle-back-4', 'vehicle_photo_back', 'verified'),
      ],
    ),
  };

  static final Map<String, dynamic> _identityRejected = _rejectedResponse(
    rejectedGroup: 'identity',
    reason: 'DOC_BLURRY',
    documentType: 'id_front',
  );

  static final Map<String, dynamic> _licenseRejected = _rejectedResponse(
    rejectedGroup: 'license',
    reason: 'LICENSE_EXPIRED',
    documentType: 'license_front',
  );

  static final Map<String, dynamic> _selfieRejected = _rejectedResponse(
    rejectedGroup: 'selfie',
    reason: 'FACE_NOT_MATCHED',
    documentType: 'selfie_id',
  );

  static final Map<String, dynamic> _vehicleRejected = _rejectedResponse(
    rejectedGroup: 'vehicle',
    reason: 'PLATE_NOT_READABLE',
    documentType: 'vehicle_photo_front',
  );

  static final Map<String, dynamic> _multipleRejected = {
    'driver_id': '99999999-9999-4999-8999-999999999999',
    'overall_status': 'rejected',
    'identity': _group(
      'rejected',
      rejectionReason: 'DOC_BLURRY',
      documents: [
        _document(
          'id-front-9',
          'id_front',
          'rejected',
          rejectionReason: 'DOC_BLURRY',
        ),
        _document('id-back-9', 'id_back', 'pending'),
      ],
    ),
    'license': _verifiedLicense,
    'selfie': _verifiedSelfie,
    'vehicle': _group(
      'rejected',
      rejectionReason: 'PLATE_NOT_READABLE',
      documents: [
        _document('registration-front-9', 'registration_doc_front', 'pending'),
        _document('registration-back-9', 'registration_doc_back', 'pending'),
        _document(
          'vehicle-front-9',
          'vehicle_photo_front',
          'rejected',
          rejectionReason: 'PLATE_NOT_READABLE',
        ),
        _document('vehicle-back-9', 'vehicle_photo_back', 'pending'),
      ],
    ),
  };

  static Map<String, dynamic> _rejectedResponse({
    required String rejectedGroup,
    required String reason,
    required String documentType,
  }) {
    return {
      'driver_id': '88888888-8888-4888-8888-888888888888',
      'overall_status': 'rejected',
      'identity': rejectedGroup == 'identity'
          ? _rejectedIdentity(reason, documentType)
          : _verifiedIdentity,
      'license': rejectedGroup == 'license'
          ? _rejectedLicense(reason, documentType)
          : _verifiedLicense,
      'selfie': rejectedGroup == 'selfie'
          ? _rejectedSelfie(reason, documentType)
          : _verifiedSelfie,
      'vehicle': rejectedGroup == 'vehicle'
          ? _rejectedVehicle(reason, documentType)
          : _verifiedVehicle,
    };
  }

  static Map<String, dynamic> _rejectedIdentity(
    String reason,
    String rejectedDocumentType,
  ) {
    return _group(
      'rejected',
      rejectionReason: reason,
      documents: [
        _document(
          'id-front-8',
          'id_front',
          rejectedDocumentType == 'id_front' ? 'rejected' : 'pending',
          rejectionReason:
              rejectedDocumentType == 'id_front' ? reason : null,
        ),
        _document(
          'id-back-8',
          'id_back',
          rejectedDocumentType == 'id_back' ? 'rejected' : 'pending',
          rejectionReason: rejectedDocumentType == 'id_back' ? reason : null,
        ),
      ],
    );
  }

  static Map<String, dynamic> _rejectedLicense(
    String reason,
    String rejectedDocumentType,
  ) {
    return _group(
      'rejected',
      rejectionReason: reason,
      documents: [
        _document(
          'license-front-8',
          'license_front',
          rejectedDocumentType == 'license_front' ? 'rejected' : 'pending',
          rejectionReason:
              rejectedDocumentType == 'license_front' ? reason : null,
        ),
        _document(
          'license-back-8',
          'license_back',
          rejectedDocumentType == 'license_back' ? 'rejected' : 'pending',
          rejectionReason:
              rejectedDocumentType == 'license_back' ? reason : null,
        ),
      ],
    );
  }

  static Map<String, dynamic> _rejectedSelfie(
    String reason,
    String rejectedDocumentType,
  ) {
    return _group(
      'rejected',
      rejectionReason: reason,
      documents: [
        _document(
          'selfie-8',
          'selfie_id',
          rejectedDocumentType == 'selfie_id' ? 'rejected' : 'pending',
          rejectionReason:
              rejectedDocumentType == 'selfie_id' ? reason : null,
        ),
      ],
    );
  }

  static Map<String, dynamic> _rejectedVehicle(
    String reason,
    String rejectedDocumentType,
  ) {
    return _group(
      'rejected',
      rejectionReason: reason,
      documents: [
        _document(
          'registration-front-8',
          'registration_doc_front',
          rejectedDocumentType == 'registration_doc_front'
              ? 'rejected'
              : 'pending',
          rejectionReason: rejectedDocumentType == 'registration_doc_front'
              ? reason
              : null,
        ),
        _document(
          'registration-back-8',
          'registration_doc_back',
          rejectedDocumentType == 'registration_doc_back'
              ? 'rejected'
              : 'pending',
          rejectionReason: rejectedDocumentType == 'registration_doc_back'
              ? reason
              : null,
        ),
        _document(
          'vehicle-front-8',
          'vehicle_photo_front',
          rejectedDocumentType == 'vehicle_photo_front'
              ? 'rejected'
              : 'pending',
          rejectionReason: rejectedDocumentType == 'vehicle_photo_front'
              ? reason
              : null,
        ),
        _document(
          'vehicle-back-8',
          'vehicle_photo_back',
          rejectedDocumentType == 'vehicle_photo_back'
              ? 'rejected'
              : 'pending',
          rejectionReason: rejectedDocumentType == 'vehicle_photo_back'
              ? reason
              : null,
        ),
      ],
    );
  }

  static Map<String, dynamic> get _verifiedIdentity {
    return _group(
      'verified',
      documents: [
        _document('id-front-verified', 'id_front', 'verified'),
        _document('id-back-verified', 'id_back', 'verified'),
      ],
    );
  }

  static Map<String, dynamic> get _verifiedLicense {
    return _group(
      'verified',
      documents: [
        _document('license-front-verified', 'license_front', 'verified'),
        _document('license-back-verified', 'license_back', 'verified'),
      ],
    );
  }

  static Map<String, dynamic> get _verifiedSelfie {
    return _group(
      'verified',
      documents: [_document('selfie-verified', 'selfie_id', 'verified')],
    );
  }

  static Map<String, dynamic> get _verifiedVehicle {
    return _group(
      'verified',
      documents: [
        _document(
          'registration-front-verified',
          'registration_doc_front',
          'verified',
        ),
        _document(
          'registration-back-verified',
          'registration_doc_back',
          'verified',
        ),
        _document('vehicle-front-verified', 'vehicle_photo_front', 'verified'),
        _document('vehicle-back-verified', 'vehicle_photo_back', 'verified'),
      ],
    );
  }

  static Map<String, dynamic> _group(
    String status, {
    List<Map<String, dynamic>> documents = const [],
    String? rejectionReason,
  }) {
    return {
      'status': status,
      'documents': documents,
      'rejection_reason': rejectionReason,
    };
  }

  static Map<String, dynamic> _document(
    String id,
    String documentType,
    String status, {
    String? rejectionReason,
  }) {
    return {
      'id': id,
      'document_type': documentType,
      'status': status,
      'rejection_reason': rejectionReason,
      'submitted_at': '2026-05-17T12:00:00Z',
    };
  }
}
