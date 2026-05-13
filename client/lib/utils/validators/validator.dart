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

    // Regular expression for phone number validation (10-15 digits, optional + prefix)
    final phoneRegExp = RegExp(r'^\+?[\d\s-]{10,15}$');

    if (!phoneRegExp.hasMatch(value)) {
      return 'Invalid phone number.';
    }

    return null;
  }

  static String? validateNotEmpty(String? value, {String fieldName = 'Field'}) {
    if (value == null || value.trim().isEmpty) {
      return '$fieldName is required.';
    }

    return null;
  }

  static String? validateMinLength(String? value, int minLength, {String fieldName = 'Field'}) {
    if (value == null || value.isEmpty) {
      return '$fieldName is required.';
    }

    if (value.length < minLength) {
      return '$fieldName must be at least $minLength characters.';
    }

    return null;
  }

  static String? validateMaxLength(String? value, int maxLength, {String fieldName = 'Field'}) {
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

  static String? validateUrl(String? value) {
    if (value == null || value.isEmpty) {
      return null; // URL is optional
    }

    final urlRegExp = RegExp(r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$');
    if (!urlRegExp.hasMatch(value)) {
      return 'Invalid URL format.';
    }

    return null;
  }
}