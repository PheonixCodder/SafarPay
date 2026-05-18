import 'package:logger/logger.dart';

class SLoggerHelper {
  SLoggerHelper._();

  static final Logger _logger = Logger(
    printer: PrettyPrinter(),
    // Customize the log levels based on your needs
    level: Level.debug,
  );

  static void debug(String message) {
    _logger.d(message);
  }

  static void info(String message) {
    _logger.i(message);
  }

  static void warning(String message) {
    _logger.w(message);
  }

  static void error(String message, [dynamic error]) {
    _logger.e(message, error: error, stackTrace: StackTrace.current);
  }

  static void verbose(String message) {
    _logger.t(message);
  }

  static void wtf(String message) {
    _logger.f(message);
  }

  // Log with custom level
  static void log(Level level, String message,
      {dynamic error, StackTrace? stackTrace}) {
    _logger.log(level, message,
        error: error, stackTrace: stackTrace ?? StackTrace.current);
  }
}
