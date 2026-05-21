enum SAppMode {
  passenger('passenger'),
  driver('driver');

  const SAppMode(this.value);

  final String value;
}

extension SAppModeX on SAppMode {
  static SAppMode fromValue(String? value) {
    return switch (value) {
      'driver' => SAppMode.driver,
      _ => SAppMode.passenger,
    };
  }
}
