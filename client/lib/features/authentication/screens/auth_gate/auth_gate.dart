import 'package:flutter/material.dart';

import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/http/client.dart';
import '../../../../utils/local_storage/token_storage.dart';
import '../../../../navigation_menu.dart';
import '../../controllers/permissions.dart';
import '../../repositories/auth_repository.dart';
import '../auth_flow/auth_flow.dart';
import '../permissions/permissions.dart';

class AuthGateScreen extends StatelessWidget {
  const AuthGateScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Widget>(
      future: _resolveInitialScreen(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done &&
            snapshot.hasData) {
          return snapshot.data!;
        }

        return const Scaffold(
          backgroundColor: SColors.primaryBackground,
          body: Center(
            child: SizedBox(
              width: SSizes.loadingIndicatorSize,
              height: SSizes.loadingIndicatorSize,
              child: CircularProgressIndicator(),
            ),
          ),
        );
      },
    );
  }

  Future<Widget> _resolveInitialScreen() async {
    final hasAccessToken = await STokenStorage.hasAccessToken();
    if (!hasAccessToken) return const AuthFlowScreen();

    try {
      await SAuthRepository.instance.getCurrentUser();
    } on SHttpException {
      await STokenStorage.clear();
      return const AuthFlowScreen();
    } catch (_) {
      await STokenStorage.clear();
      return const AuthFlowScreen();
    }

    final permissionsCompleted =
        await SPermissionsController.hasRequiredPermissions();

    if (permissionsCompleted) return const NavigationMenu();

    return const PermissionsScreen();
  }
}
