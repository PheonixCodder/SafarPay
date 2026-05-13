import 'package:client/features/authentication/screens/auth_gate/auth_gate.dart';
import 'package:client/utils/theme/theme.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      themeMode: ThemeMode.system,
      theme: SAppTheme.lightTheme,
      debugShowCheckedModeBanner: false,
      home: const AuthGateScreen(),
    );
  }
}
