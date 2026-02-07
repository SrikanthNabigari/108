import 'package:flutter/material.dart';

/// 108 app color palette — pure black cosmic theme with glass effects
class CosmicColors {
  CosmicColors._();

  // ── Background ──────────────────────────────────────────
  static const Color background = Color(0xFF000000);
  static const Color deepSpace = Color(0xFF000000);
  static const Color midnight = Color(0xFF0A0A0A);
  static const Color nebula = Color(0xFF111111);

  // ── Glass effects ───────────────────────────────────────
  static const Color glass = Color(0x08FFFFFF); // 3% white
  static const Color glassBorder = Color(0x14FFFFFF); // 8% white
  static const Color glassHighlight = Color(0x1FFFFFFF); // 12% white
  static const Color glassHover = Color(0x0DFFFFFF); // 5% white
  static const Color glassWhite = Color(0x08FFFFFF); // alias

  // ── Text hierarchy ──────────────────────────────────────
  static const Color textPrimary = Color(0xFFFFFFFF); // 100% white
  static const Color textDim = Color(0x99FFFFFF); // 60% white
  static const Color textMuted = Color(0x59FFFFFF); // 35% white
  static const Color textSubtle = Color(0x33FFFFFF); // 20% white
  static const Color textSecondary = Color(0x99FFFFFF); // alias for textDim
  static const Color textTertiary = Color(0x59FFFFFF); // alias for textMuted

  // ── Accents ─────────────────────────────────────────────
  static const Color accentPurple = Color(0xFF8B5CF6);
  static const Color accentBlue = Color(0xFF3B82F6);
  static const Color accentGold = Color(0xFFD4AF37);
  static const Color cosmicPurple = Color(0xFF8B5CF6); // alias

  // ── Planet colors ───────────────────────────────────────
  static const Color solarGold = Color(0xFFFFD700);
  static const Color stellarBlue = Color(0xFF4FC3F7);
  static const Color marsRed = Color(0xFFFF5252);
  static const Color venusGreen = Color(0xFF69F0AE);
  static const Color saturnGrey = Color(0xFF78909C);

  // ── Status ──────────────────────────────────────────────
  static const Color success = Color(0xFF34C759);
  static const Color warning = Color(0xFFFFCC00);
  static const Color error = Color(0xFFFF3B30);
  static const Color info = Color(0xFF3B82F6);

  // ── Semantic ────────────────────────────────────────────
  static const Color divider = Color(0x14FFFFFF);
  static const Color shadow = Color(0x26000000);
  static const Color overlay = Color(0x4D000000);
}
