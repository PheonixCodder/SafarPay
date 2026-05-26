import 'package:flutter/material.dart';

import '../../../../../utils/constants/sizes.dart';
import '../../../controllers/driver_requests_controller.dart';
import 'driver_request_card.dart';

class SDriverRequestList extends StatelessWidget {
  const SDriverRequestList({super.key, required this.controller});

  final SDriverRequestsController controller;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: controller.requests
          .map(
            (request) => Padding(
              padding: const EdgeInsets.only(bottom: SSizes.md),
              child: SDriverRequestCard(
                request: request,
                onTap: () => controller.openRequest(request),
              ),
            ),
          )
          .toList(),
    );
  }
}
