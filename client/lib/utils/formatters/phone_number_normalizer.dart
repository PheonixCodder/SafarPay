class SPhoneNumberNormalizer {
  SPhoneNumberNormalizer._();

  static final RegExp _allowedInput = RegExp(r'^[+\d\s-]+$');
  static final RegExp _backendPattern = RegExp(r'^\+?[1-9]\d{7,14}$');

  static String? normalizeForPakistan(String? value) {
    final input = value?.trim();
    if (input == null || input.isEmpty) return null;
    if (!_allowedInput.hasMatch(input)) return null;

    final hasPlus = input.startsWith('+');
    final digits = input.replaceAll(RegExp(r'\D'), '');

    final normalized = switch (digits) {
      final phone when phone.length == 11 && phone.startsWith('03') =>
        '+92${phone.substring(1)}',
      final phone when phone.length == 10 && phone.startsWith('3') =>
        '+92$phone',
      final phone when phone.length == 12 && phone.startsWith('92') =>
        '+$phone',
      _ => hasPlus ? '+$digits' : digits,
    };

    if (!normalized.startsWith('+92')) return null;
    if (!_backendPattern.hasMatch(normalized)) return null;

    return normalized;
  }
}
