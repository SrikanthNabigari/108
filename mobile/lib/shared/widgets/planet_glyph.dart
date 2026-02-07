import 'package:flutter/material.dart';

/// Planet icon/symbol widget with astrological symbols and colors.
class PlanetGlyph extends StatelessWidget {
  final String planetName;
  final double size;
  final bool showLabel;

  // Planet colors based on Vedic tradition
  static const Map<String, Color> planetColors = {
    'sun': Color(0xFFFFD700), // Gold
    'moon': Color(0xFFEBEBEB), // Silver
    'mars': Color(0xFFE74C3C), // Red
    'mercury': Color(0xFF3498DB), // Blue-green
    'jupiter': Color(0xFFF39C12), // Orange
    'venus': Color(0xFF2ECC71), // Green
    'saturn': Color(0xFF95A5A6), // Dark gray
    'rahu': Color(0xFF9B59B6), // Purple
    'ketu': Color(0xFF34495E), // Dark slate
  };

  // Unicode astrological symbols
  static const Map<String, String> planetSymbols = {
    'sun': '☉',
    'moon': '☽',
    'mars': '♂',
    'mercury': '☿',
    'jupiter': '♃',
    'venus': '♀',
    'saturn': '♄',
    'rahu': '℞',
    'ketu': '𐌘',
  };

  const PlanetGlyph({
    Key? key,
    required this.planetName,
    this.size = 24,
    this.showLabel = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final lowercaseName = planetName.toLowerCase();
    final color = planetColors[lowercaseName] ?? Colors.white;
    final symbol = planetSymbols[lowercaseName] ?? '●';

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withOpacity(0.2),
            border: Border.all(color: color, width: 1.5),
          ),
          child: Center(
            child: Text(
              symbol,
              style: TextStyle(
                fontSize: size * 0.6,
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        if (showLabel) ...[
          const SizedBox(height: 4),
          Text(
            planetName,
            style: Theme.of(context).textTheme.labelSmall,
          ),
        ],
      ],
    );
  }
}
