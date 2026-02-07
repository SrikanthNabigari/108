import 'package:flutter/material.dart';
import '../theme/colors.dart';

/// String and number formatting utilities
class FormatUtils {
  FormatUtils._();

  /// Format score (0-10) with a color based on value
  /// Returns ({String} formatted, {Color} color)
  static (String, Color) formatScore(double score) {
    final formatted = score.toStringAsFixed(1);
    final color = _getScoreColor(score);
    return (formatted, color);
  }

  /// Get color for a score value
  static Color _getScoreColor(double score) {
    if (score >= 8) {
      return CosmicColors.venusGreen;
    } else if (score >= 6) {
      return CosmicColors.solarGold;
    } else if (score >= 4) {
      return CosmicColors.stellarBlue;
    } else {
      return CosmicColors.marsRed;
    }
  }

  /// Format credit balance with currency symbol
  static String formatCredits(int credits) {
    return '$credits credits';
  }

  /// Format price in USD
  static String formatPrice(double price) {
    return '\$${price.toStringAsFixed(2)}';
  }

  /// Truncate text with ellipsis
  static String truncateText(String text, {int maxLength = 50}) {
    if (text.length <= maxLength) {
      return text;
    }
    return '${text.substring(0, maxLength)}...';
  }

  /// Capitalize first letter of string
  static String capitalizeFirst(String text) {
    if (text.isEmpty) return text;
    return text[0].toUpperCase() + text.substring(1);
  }

  /// Convert snake_case to Title Case
  static String snakeCaseToTitleCase(String text) {
    return text
        .split('_')
        .map((word) => capitalizeFirst(word))
        .join(' ');
  }

  /// Format percentage (0-100)
  static String formatPercentage(double value) {
    return '${(value * 100).toStringAsFixed(1)}%';
  }

  /// Format number with commas
  static String formatNumber(int number) {
    return number.toString().replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (match) => '${match[1]},',
    );
  }

  /// Format array as comma-separated string
  static String formatArray(List<String> items, {String separator = ', '}) {
    return items.join(separator);
  }

  /// Format planet or rashi name
  static String formatPlanetName(String name) {
    return capitalizeFirst(name.replaceAll('_', ' '));
  }

  /// Get emoji for astrological sign
  static String getSignEmoji(String rashi) {
    const map = {
      'aries': '♈',
      'taurus': '♉',
      'gemini': '♊',
      'cancer': '♋',
      'leo': '♌',
      'virgo': '♍',
      'libra': '♎',
      'scorpio': '♏',
      'sagittarius': '♐',
      'capricorn': '♑',
      'aquarius': '♒',
      'pisces': '♓',
    };
    return map[rashi.toLowerCase()] ?? '◉';
  }

  /// Format house number as ordinal (1st, 2nd, 3rd, etc.)
  static String formatHouse(int house) {
    if (house == 1 || house == 21 || house == 31) return '${house}st';
    if (house == 2 || house == 22) return '${house}nd';
    if (house == 3 || house == 23) return '${house}rd';
    return '${house}th';
  }

  /// Get trend indicator (↑ ↓ →)
  static String getTrendIndicator(String trend) {
    switch (trend.toLowerCase()) {
      case 'up':
      case 'positive':
        return '↑';
      case 'down':
      case 'negative':
        return '↓';
      case 'neutral':
      case 'stable':
      default:
        return '→';
    }
  }
}
