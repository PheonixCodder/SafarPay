import '../formatters/phone_number_normalizer.dart';

class SValidator {
  SValidator._();

  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required.';
    }

    // Regular expression for email validation
    final emailRegExp = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');

    if (!emailRegExp.hasMatch(value)) {
      return 'Invalid email address.';
    }

    return null;
  }

  static String? validatePhoneNumber(String? value) {
    if (value == null || value.isEmpty) {
      return 'Phone number is required.';
    }

    if (SPhoneNumberNormalizer.normalizeForPakistan(value) == null) {
      return 'Enter a valid Pakistani phone number.';
    }

    return null;
  }

  static String? validateNotEmpty(String? value, {String fieldName = 'Field'}) {
    if (value == null || value.trim().isEmpty) {
      return '$fieldName is required.';
    }

    return null;
  }

  static String? validateMinLength(String? value, int minLength,
      {String fieldName = 'Field'}) {
    if (value == null || value.isEmpty) {
      return '$fieldName is required.';
    }

    if (value.length < minLength) {
      return '$fieldName must be at least $minLength characters.';
    }

    return null;
  }

  static String? validateMaxLength(String? value, int maxLength,
      {String fieldName = 'Field'}) {
    if (value == null || value.isEmpty) {
      return '$fieldName is required.';
    }

    if (value.length > maxLength) {
      return '$fieldName must not exceed $maxLength characters.';
    }

    return null;
  }

  static String? validateNumeric(String? value, {String fieldName = 'Field'}) {
    if (value == null || value.isEmpty) {
      return '$fieldName is required.';
    }

    final numericRegExp = RegExp(r'^\d+$');
    if (!numericRegExp.hasMatch(value)) {
      return '$fieldName must contain only numbers.';
    }

    return null;
  }

  static String? validateCnicNumber(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'CNIC number is required.';
    }

    final normalized = value.replaceAll(RegExp(r'[\s-]'), '');
    if (!RegExp(r'^\d{13}$').hasMatch(normalized)) {
      return 'Enter a valid 13-digit CNIC number.';
    }

    return null;
  }

  static String? validateLicenseNumber(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'License number is required.';
    }

    if (value.trim().length > 40) {
      return 'License number must not exceed 40 characters.';
    }

    return null;
  }

  static String? validateFutureDate(DateTime? value, {String fieldName = 'Date'}) {
    if (value == null) {
      return '$fieldName is required.';
    }

    final today = DateTime.now();
    final todayOnly = DateTime(today.year, today.month, today.day);
    final selectedOnly = DateTime(value.year, value.month, value.day);

    if (!selectedOnly.isAfter(todayOnly)) {
      return '$fieldName must be in the future.';
    }

    return null;
  }

  static String? validateMinimumAge(
    DateTime? value, {
    int minimumAge = 13,
    String fieldName = 'Date of birth',
  }) {
    if (value == null) {
      return '$fieldName is required.';
    }

    final today = DateTime.now();
    final latestAllowed = DateTime(today.year - minimumAge, today.month, today.day);
    final selectedOnly = DateTime(value.year, value.month, value.day);

    if (selectedOnly.isAfter(latestAllowed)) {
      return 'You must be at least $minimumAge years old.';
    }

    return null;
  }

  static String? validateIntegerRange(
    String? value, {
    required String fieldName,
    required int min,
    required int max,
  }) {
    if (value == null || value.trim().isEmpty) {
      return '$fieldName is required.';
    }

    final parsed = int.tryParse(value.trim());
    if (parsed == null) {
      return '$fieldName must be a number.';
    }

    if (parsed < min || parsed > max) {
      return '$fieldName must be between $min and $max.';
    }

    return null;
  }

  static String? validateUrl(String? value) {
    if (value == null || value.isEmpty) {
      return null; // URL is optional
    }

    final urlRegExp = RegExp(
        r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$');
    if (!urlRegExp.hasMatch(value)) {
      return 'Invalid URL format.';
    }

    return null;
  }
}
