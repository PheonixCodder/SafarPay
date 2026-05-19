import '../../../../../../../utils/constants/api_constants.dart';
import '../../../../../../../utils/http/client.dart';
import '../models/support_ticket_models.dart';

class SSupportTicketRepository {
  const SSupportTicketRepository();

  static const bool _useDemoMode = true;

  Future<SSupportTicketCreateResponse> createTicket(
    SSupportTicketCreateRequest request,
  ) async {
    // Restore this call when the support-ticket backend exists:
    // final data = await SHttpClient.post(
    //   '/support/tickets',
    //   service: SApiService.gateway,
    //   requiresAuth: true,
    //   body: request.toJson(),
    // );
    final data = _useDemoMode
        ? await _demoCreateTicket()
        : await SHttpClient.post(
            '/support/tickets',
            service: SApiService.gateway,
            requiresAuth: true,
            body: request.toJson(),
          );

    return SSupportTicketCreateResponse.fromJson(data);
  }

  Future<Map<String, dynamic>> _demoCreateTicket() async {
    await Future<void>.delayed(const Duration(milliseconds: 350));
    return {
      'ticket_id': 'SUP-82571',
      'status': 'OPEN',
      'expected_response_minutes': 15,
      'message':
          'Your ticket has been received. Our support team will get back to you shortly.',
    };
  }
}
