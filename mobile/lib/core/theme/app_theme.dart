import 'package:flutter/material.dart';

// ============================================================
// COLORS
// ============================================================

class C {
  C._();

  // Backgrounds
  static const bg = Color(0xFF050508);
  static const surface = Color(0xFF0D0D14);
  static const surfaceLight = Color(0xFF16161F);

  // Glass
  static const glassBg = Color(0x0FFFFFFF); // white 6%
  static const glassBorder = Color(0x1AFFFFFF); // white 10%
  static const glassHighlight = Color(0x33FFFFFF); // white 20%

  // Primary (white-based)
  static const accent = Color(0xFFE8E8E8); // soft white
  static const accentDim = Color(0x33E8E8E8); // white 20%
  static const accentSurface = Color(0x1AE8E8E8); // white 10%

  // Planet / semantic colors (used contextually, not as primary)
  static const mercury = Color(0xFF00E676);
  static const venus = Color(0xFFE91E90);
  static const mars = Color(0xFFFF5252);
  static const jupiter = Color(0xFFFFB300);
  static const saturn = Color(0xFF7C3AED);
  static const sun = Color(0xFFFF8F00);
  static const moon = Color(0xFFC0C0C0);
  static const rahu = Color(0xFF607D8B);
  static const ketu = Color(0xFF795548);

  // Status
  static const positive = Color(0xFF00E676);
  static const warning = Color(0xFFFFB300);
  static const negative = Color(0xFFFF5252);

  // Text
  static const textPrimary = Color(0xFFE8E8E8);
  static const textSecondary = Color(0xFF999999);
  static const textMuted = Color(0xFF666666);
  static const textOnAccent = Color(0xFF050508);

  // Divider
  static const divider = Color(0xFF1A1A24);
}

// ============================================================
// TEXT STYLES
// ============================================================

class T {
  T._();

  static const h1 = TextStyle(
    fontSize: 28,
    fontWeight: FontWeight.w700,
    color: C.textPrimary,
    height: 1.2,
    letterSpacing: -0.5,
  );

  static const h2 = TextStyle(
    fontSize: 22,
    fontWeight: FontWeight.w600,
    color: C.textPrimary,
    height: 1.3,
    letterSpacing: -0.3,
  );

  static const h3 = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: C.textPrimary,
    height: 1.3,
  );

  static const body = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w400,
    color: C.textPrimary,
    height: 1.5,
  );

  static const bodySm = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: C.textSecondary,
    height: 1.5,
  );

  static const caption = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w400,
    color: C.textMuted,
    height: 1.4,
  );

  static const label = TextStyle(
    fontSize: 11,
    fontWeight: FontWeight.w600,
    color: C.textMuted,
    letterSpacing: 1.2,
  );

  static const button = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    height: 1.0,
  );
}

// ============================================================
// SPACING & RADIUS
// ============================================================

class S {
  S._();

  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
  static const double xxl = 32;
  static const double xxxl = 48;

  static const pagePadding = EdgeInsets.symmetric(horizontal: 24);
}

class R {
  R._();

  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 20;
  static const double xxl = 24;

  static final smBr = BorderRadius.circular(sm);
  static final mdBr = BorderRadius.circular(md);
  static final lgBr = BorderRadius.circular(lg);
  static final xlBr = BorderRadius.circular(xl);
  static final xxlBr = BorderRadius.circular(xxl);
}

// ============================================================
// MATERIAL THEME
// ============================================================

class AppTheme {
  AppTheme._();

  static ThemeData get dark => ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: C.bg,
        colorScheme: const ColorScheme.dark(
          primary: C.accent,
          secondary: C.textSecondary,
          surface: C.surface,
          error: C.negative,
          onPrimary: C.textOnAccent,
          onSurface: C.textPrimary,
          onError: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          elevation: 0,
          centerTitle: true,
          titleTextStyle: T.h3,
          iconTheme: IconThemeData(color: C.textPrimary),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: C.accent,
            foregroundColor: C.textOnAccent,
            elevation: 0,
            minimumSize: const Size(double.infinity, 52),
            shape: RoundedRectangleBorder(borderRadius: R.lgBr),
            textStyle: T.button,
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: C.textPrimary,
            side: const BorderSide(color: C.glassBorder),
            minimumSize: const Size(double.infinity, 52),
            shape: RoundedRectangleBorder(borderRadius: R.lgBr),
            textStyle: T.button,
          ),
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: C.accent,
            textStyle: T.bodySm.copyWith(fontWeight: FontWeight.w500),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: false,
          hintStyle: T.body.copyWith(color: C.textMuted),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.lg),
          border: InputBorder.none,
        ),
        snackBarTheme: SnackBarThemeData(
          backgroundColor: C.surfaceLight,
          contentTextStyle: T.bodySm.copyWith(color: C.textPrimary),
          shape: RoundedRectangleBorder(borderRadius: R.mdBr),
          behavior: SnackBarBehavior.floating,
        ),
        dividerTheme: const DividerThemeData(
          color: C.divider,
          thickness: 1,
          space: 0,
        ),
      );
}
