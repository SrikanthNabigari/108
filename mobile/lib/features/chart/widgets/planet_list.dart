import 'package:flutter/material.dart';
import '../../../shared/widgets/planet_glyph.dart';
import '../../../shared/widgets/glass_card.dart';

/// List of all planets with their detailed positions.
class PlanetList extends StatelessWidget {
  final List<PlanetData> planets;
  final Function(String)? onPlanetTap;

  const PlanetList({
    Key? key,
    required this.planets,
    this.onPlanetTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: planets.map((planet) {
        return GestureDetector(
          onTap: () => onPlanetTap?.call(planet.name),
          child: GlassCard(
            margin: const EdgeInsets.only(bottom: 8),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: [
                PlanetGlyph(
                  planetName: planet.name,
                  size: 32,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            planet.name,
                            style: Theme.of(context)
                                .textTheme
                                .labelMedium
                                ?.copyWith(
                                  color: Colors.white,
                                ),
                          ),
                          if (planet.isRetrograde)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(4),
                                color: Colors.orange.withOpacity(0.2),
                              ),
                              child: const Text(
                                'R',
                                style: TextStyle(
                                  color: Colors.orange,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${planet.sign} | ${planet.degree}°',
                        style:
                            Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Colors.white70,
                                ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${planet.nakshatra} | House ${planet.house}',
                        style:
                            Theme.of(context).textTheme.labelSmall?.copyWith(
                                  color: Colors.white54,
                                ),
                      ),
                    ],
                  ),
                ),
                Icon(
                  Icons.arrow_forward_ios_rounded,
                  size: 14,
                  color: Colors.white38,
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }
}

class PlanetData {
  final String name;
  final String sign;
  final String degree;
  final String nakshatra;
  final int house;
  final bool isRetrograde;

  PlanetData({
    required this.name,
    required this.sign,
    required this.degree,
    required this.nakshatra,
    required this.house,
    this.isRetrograde = false,
  });
}
