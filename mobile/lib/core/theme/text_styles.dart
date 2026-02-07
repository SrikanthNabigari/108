import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'colors.dart';

/// Cosmic typography scale using SpaceGrotesk font family via GoogleFonts
class CosmicTextStyles {
  CosmicTextStyles._();

  // Headings
  static TextStyle heading1 = GoogleFonts.spaceGrotesk(
    fontSize: 32,
    fontWeight: FontWeight.bold,
    color: CosmicColors.textPrimary,
    letterSpacing: -0.5,
    height: 1.2,
  );

  static TextStyle heading2 = GoogleFonts.spaceGrotesk(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: CosmicColors.textPrimary,
    letterSpacing: -0.3,
    height: 1.3,
  );

  static TextStyle heading3 = GoogleFonts.spaceGrotesk(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: CosmicColors.textPrimary,
    letterSpacing: 0,
    height: 1.4,
  );

  // Body text
  static TextStyle body1 = GoogleFonts.spaceGrotesk(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: CosmicColors.textPrimary,
    letterSpacing: 0.2,
    height: 1.5,
  );

  static TextStyle body2 = GoogleFonts.spaceGrotesk(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: CosmicColors.textSecondary,
    letterSpacing: 0.1,
    height: 1.5,
  );

  // Small text
  static TextStyle caption = GoogleFonts.spaceGrotesk(
    fontSize: 12,
    fontWeight: FontWeight.normal,
    color: CosmicColors.textTertiary,
    letterSpacing: 0.3,
    height: 1.4,
  );

  // Button text
  static TextStyle button = GoogleFonts.spaceGrotesk(
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: CosmicColors.textPrimary,
    letterSpacing: 0.5,
    height: 1.4,
  );

  // Overline (all caps)
  static TextStyle overline = GoogleFonts.spaceGrotesk(
    fontSize: 10,
    fontWeight: FontWeight.w600,
    color: CosmicColors.textSecondary,
    letterSpacing: 1.0,
    height: 1.6,
  );

  // Accent text (for highlighted data)
  static TextStyle accent = GoogleFonts.spaceGrotesk(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: CosmicColors.cosmicPurple,
    letterSpacing: 0.2,
    height: 1.5,
  );

  // Score/metric display
  static TextStyle metric = GoogleFonts.spaceGrotesk(
    fontSize: 28,
    fontWeight: FontWeight.bold,
    color: CosmicColors.textPrimary,
    letterSpacing: -0.3,
    height: 1.2,
  );
}
