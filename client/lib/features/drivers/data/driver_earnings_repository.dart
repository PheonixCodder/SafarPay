import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import '../domain/earnings_models.dart';

class SDriverEarningsRepository {
  const SDriverEarningsRepository();

  Future<SDriverEarnings> fetchEarnings(SDriverEarningsPeriod period) async {
    final data = await SHttpClient.get(
      '/earnings/me?period=${period.value}',
      service: SApiService.payment,
      requiresAuth: true,
    );
    return SDriverEarnings.fromJson(data);
  }
}
