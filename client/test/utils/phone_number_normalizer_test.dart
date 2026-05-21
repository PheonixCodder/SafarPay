import 'package:client/utils/formatters/phone_number_normalizer.dart';
import 'package:client/utils/validators/validator.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SPhoneNumberNormalizer', () {
    test('normalizes Pakistani local phone numbers to backend format', () {
      expect(
        SPhoneNumberNormalizer.normalizeForPakistan('0300 1234567'),
        '+923001234567',
      );
      expect(
        SPhoneNumberNormalizer.normalizeForPakistan('0300-1234567'),
        '+923001234567',
      );
    });

    test('normalizes Pakistani numbers with country code to backend format', () {
      expect(
        SPhoneNumberNormalizer.normalizeForPakistan('+92 300 1234567'),
        '+923001234567',
      );
      expect(
        SPhoneNumberNormalizer.normalizeForPakistan('923001234567'),
        '+923001234567',
      );
    });

    test('normalizes Pakistani numbers without local zero to backend format', () {
      expect(
        SPhoneNumberNormalizer.normalizeForPakistan('3001234567'),
        '+923001234567',
      );
    });

    test('returns null for invalid phone numbers', () {
      expect(SPhoneNumberNormalizer.normalizeForPakistan('12345'), isNull);
      expect(SPhoneNumberNormalizer.normalizeForPakistan('+1 300 1234567'), isNull);
      expect(SPhoneNumberNormalizer.normalizeForPakistan('0300 abc 4567'), isNull);
    });
  });

  group('SValidator.validatePhoneNumber', () {
    test('accepts phone numbers that can be normalized for OTP backend', () {
      expect(SValidator.validatePhoneNumber('0300 1234567'), isNull);
      expect(SValidator.validatePhoneNumber('+92 300 1234567'), isNull);
      expect(SValidator.validatePhoneNumber('3001234567'), isNull);
    });

    test('rejects values that cannot be sent to OTP backend', () {
      expect(SValidator.validatePhoneNumber('12345'), isNotNull);
      expect(SValidator.validatePhoneNumber('+1 300 1234567'), isNotNull);
    });
  });
}
