import 'package:client/features/authentication/screens/auth_gate/auth_gate.dart';
import 'package:client/utils/theme/theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:get/get.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return ShadApp.custom(
      themeMode: ThemeMode.system,
      theme: ShadThemeData(
        brightness: Brightness.light,
        colorScheme: const ShadZincColorScheme.light(),
      ),
      appBuilder: (context) => GetMaterialApp(
        themeMode: ThemeMode.system,
        theme: SAppTheme.lightTheme,
        debugShowCheckedModeBanner: false,
        localizationsDelegates: const [
          GlobalShadLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
        ],
        builder: (context, child) => ShadAppBuilder(child: child!),
        home: const AuthGateScreen(),
      ),
    );
  }
}
