import 'package:intl/intl.dart';

String sFormatMoney(double value, {String currency = 'PKR'}) {
  final formatter = NumberFormat.decimalPattern();
  final prefix = currency == 'PKR' ? 'Rs.' : currency;
  return '$prefix ${formatter.format(value.round())}';
}

String sFormatMinutes(int minutes) {
  final hours = minutes ~/ 60;
  final remaining = minutes % 60;
  if (hours <= 0) return '${remaining}m';
  if (remaining <= 0) return '${hours}h';
  return '${hours}h ${remaining}m';
}

String sFormatServiceType(String value) {
  return value
      .split('_')
      .where((part) => part.isNotEmpty)
      .map((part) => '${part[0]}${part.substring(1).toLowerCase()}')
      .join(' ');
}
