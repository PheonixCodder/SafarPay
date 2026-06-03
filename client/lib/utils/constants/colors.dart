import 'package:flutter/material.dart';

/// Midnight Elite palette — source: [DESIGN.md].
/// Do not add new hex values in feature widgets; extend here first.
class SColors {
  SColors._();

  // --- Material 3 core (DESIGN.md frontmatter) ---
  static const Color background = Color(0xFF121414);
  static const Color onBackground = Color(0xFFE3E2E2);

  static const Color surface = Color(0xFF121414);
  static const Color surfaceDim = Color(0xFF121414);
  static const Color surfaceBright = Color(0xFF38393A);
  static const Color surfaceContainerLowest = Color(0xFF0D0E0F);
  static const Color surfaceContainerLow = Color(0xFF1A1C1C);
  static const Color surfaceContainer = Color(0xFF1E2020);
  static const Color surfaceContainerHigh = Color(0xFF292A2A);
  static const Color surfaceContainerHighest = Color(0xFF343535);
  static const Color surfaceVariant = Color(0xFF343535);

  static const Color onSurface = Color(0xFFE3E2E2);
  static const Color onSurfaceVariant = Color(0xFFD2C5AC);

  static const Color inverseSurface = Color(0xFFE3E2E2);
  static const Color onInverseSurface = Color(0xFF2F3131);

  static const Color outline = Color(0xFF9B9079);
  static const Color outlineVariant = Color(0xFF4E4633);

  static const Color surfaceTint = Color(0xFFF3C016);

  static const Color primary = Color(0xFFFFE29E);
  static const Color onPrimary = Color(0xFF3E2E00);
  static const Color primaryContainer = Color(0xFFF6C21A);
  static const Color onPrimaryContainer = Color(0xFF695100);
  static const Color inversePrimary = Color(0xFF765B00);

  static const Color secondary = Color(0xFFC6C6CD);
  static const Color onSecondary = Color(0xFF2E3036);
  static const Color secondaryContainer = Color(0xFF47494F);
  static const Color onSecondaryContainer = Color(0xFFB7B8BF);

  static const Color tertiary = Color(0xFFE7E4E3);
  static const Color onTertiary = Color(0xFF313030);
  static const Color tertiaryContainer = Color(0xFFCBC8C8);
  static const Color onTertiaryContainer = Color(0xFF555453);

  static const Color error = Color(0xFFFFB4AB);
  static const Color onError = Color(0xFF690005);
  static const Color errorContainer = Color(0xFF93000A);
  static const Color onErrorContainer = Color(0xFFFFDAD6);

  // --- Prose / component semantics ---
  static const Color gold = primaryContainer;
  static const Color goldSoft = primary;
  static const Color cardElevated = Color(0xFF1B1D22);
  static const Color inputFill = Color(0xFF16181C);

  static const Color pickup = Color(0xFF22C55E);
  static const Color destination = Color(0xFFEF4444);

  static const Color pureBlack = Color(0xFF000000);
  static const Color white = Color(0xFFFFFFFF);
  static const Color transparent = Colors.transparent;

  // --- Legacy aliases (migration) ---
  static const Color accent = goldSoft;
  static const Color textPrimary = onSurface;
  static const Color textSecondary = onSurfaceVariant;
  static const Color textWhite = white;

  static const Color light = surfaceContainerLow;
  static const Color primaryBackground = background;
  static const Color lightContainer = surfaceContainer;

  static const Color buttonPrimary = primaryContainer;
  static const Color buttonSecondary = secondaryContainer;
  static const Color buttonDisabled = surfaceContainerHighest;

  static const Color borderPrimary = outlineVariant;
  static const Color borderSecondary = outline;

  static const Color success = pickup;
  static const Color warning = Color(0xFFF59E0B);
  static const Color info = Color(0xFF38BDF8);
  static const Color pink = Color(0xFFEC4899);
  static const Color purple = Color(0xFFA855F7);

  static const Color black = onBackground;
  static const Color darkerGrey = onSurfaceVariant;
  static const Color darkGrey = outline;
  static const Color grey = surfaceContainerHigh;
}

class SOpacities {
  SOpacities._();

  static const double subtle = 0.03;
  static const double soft = 0.04;
  static const double light = 0.06;
  static const double tinted = 0.08;
  static const double successTint = 0.10;
  static const double placeholder = 0.12;
  static const double glassOverlay = 0.10;
  static const double goldGlow = 0.20;
  static const double shadow = 0.30;
  static const double chipDisabled = 0.40;
  static const double divider = 0.50;
  static const double onboardingGradientMid = 0.54;
  static const double border = 0.60;
  static const double onboardingButtonBorder = 0.65;
  static const double onboardingButtonText = 0.70;
  static const double strong = 0.75;
  static const double stronger = 0.80;
  static const double onboardingGradientDeep = 0.87;
  static const double pageTransitionFadeStart = 0.92;
  static const double nearSolid = 0.95;
  static const double outlineButtonStroke = 0.20;
}
