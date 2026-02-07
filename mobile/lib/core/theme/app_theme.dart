import 'package:flutter/material.dart';
import 'colors.dart';
import 'text_styles.dart';

/// Dark cosmic theme with glassmorphic elements
class AppTheme {
  AppTheme._();

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: Colors.black,
      primaryColor: CosmicColors.cosmicPurple,
      secondaryHeaderColor: CosmicColors.solarGold,

      // App bar theme
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: CosmicTextStyles.heading2.copyWith(
          color: CosmicColors.textPrimary,
        ),
        iconTheme: const IconThemeData(color: CosmicColors.textPrimary),
      ),

      // Text theme
      textTheme: TextTheme(
        displayLarge: CosmicTextStyles.heading1,
        displayMedium: CosmicTextStyles.heading2,
        displaySmall: CosmicTextStyles.heading3,
        headlineSmall: CosmicTextStyles.heading3,
        titleLarge: CosmicTextStyles.heading2,
        titleMedium: CosmicTextStyles.heading3,
        titleSmall: CosmicTextStyles.body1,
        bodyLarge: CosmicTextStyles.body1,
        bodyMedium: CosmicTextStyles.body2,
        labelLarge: CosmicTextStyles.button,
        labelMedium: CosmicTextStyles.caption,
      ),

      // Card theme
      cardTheme: CardThemeData(
        color: CosmicColors.midnight,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(
            color: CosmicColors.glassBorder,
            width: 1,
          ),
        ),
      ),

      // Input decoration
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: CosmicColors.midnight,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(
            color: CosmicColors.glassBorder,
            width: 1,
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(
            color: CosmicColors.glassBorder,
            width: 1,
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(
            color: CosmicColors.cosmicPurple,
            width: 2,
          ),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 14,
        ),
        hintStyle: CosmicTextStyles.body2.copyWith(
          color: CosmicColors.textTertiary,
        ),
        labelStyle: CosmicTextStyles.body2.copyWith(
          color: CosmicColors.textSecondary,
        ),
      ),

      // Button themes
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          backgroundColor: CosmicColors.cosmicPurple,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: CosmicTextStyles.button,
          elevation: 0,
        ),
      ),

      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          foregroundColor: CosmicColors.cosmicPurple,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(
              color: CosmicColors.cosmicPurple,
              width: 1.5,
            ),
          ),
          textStyle: CosmicTextStyles.button,
        ),
      ),

      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: CosmicColors.cosmicPurple,
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          textStyle: CosmicTextStyles.button,
        ),
      ),

      // Bottom navigation
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: CosmicColors.midnight,
        selectedItemColor: CosmicColors.cosmicPurple,
        unselectedItemColor: CosmicColors.textSecondary,
        elevation: 8,
        type: BottomNavigationBarType.fixed,
        selectedLabelStyle: CosmicTextStyles.caption.copyWith(
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: CosmicTextStyles.caption,
      ),

      // Divider
      dividerTheme: const DividerThemeData(
        color: CosmicColors.divider,
        thickness: 1,
        space: 16,
      ),

      // Snackbar
      snackBarTheme: SnackBarThemeData(
        backgroundColor: CosmicColors.nebula,
        contentTextStyle: CosmicTextStyles.body2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),

      // Dialog
      dialogTheme: DialogThemeData(
        backgroundColor: CosmicColors.midnight,
        elevation: 8,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(
            color: CosmicColors.glassBorder,
            width: 1,
          ),
        ),
      ),

      // Slider
      sliderTheme: SliderThemeData(
        activeTrackColor: CosmicColors.cosmicPurple,
        inactiveTrackColor: CosmicColors.nebula,
        thumbColor: CosmicColors.cosmicPurple,
        overlayColor: CosmicColors.cosmicPurple.withOpacity(0.2),
      ),
    );
  }
}
