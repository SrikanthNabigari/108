import 'package:flutter/material.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/planet_glyph.dart';

/// Bottom sheet showing detailed planet information.
class PlanetDetailSheet extends StatelessWidget {
  final String planetName;
  final String sign;
  final String nakshatra;
  final String pada;
  final String dignity;
  final int house;
  final List<String> aspects;
  final String dashaInfo;

  const PlanetDetailSheet({
    Key? key,
    required this.planetName,
    required this.sign,
    required this.nakshatra,
    required this.pada,
    required this.dignity,
    required this.house,
    this.aspects = const [],
    this.dashaInfo = '',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      expand: false,
      builder: (context, scrollController) => Container(
        decoration: BoxDecoration(
          color: const Color(0x1aFFFFFF),
          borderRadius: const BorderRadius.vertical(
            top: Radius.circular(24),
          ),
          border: Border(
            top: BorderSide(
              color: Colors.white.withOpacity(0.2),
              width: 1,
            ),
          ),
        ),
        child: ListView(
          controller: scrollController,
          padding: const EdgeInsets.all(20),
          children: [
            // Handle
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(2),
                  color: Colors.white24,
                ),
              ),
            ),
            const SizedBox(height: 20),
            // Planet header
            Center(
              child: Column(
                children: [
                  PlanetGlyph(
                    planetName: planetName,
                    size: 48,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    planetName,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.white,
                        ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            // Sign and position
            GlassCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _DetailRow('Sign', sign),
                  const SizedBox(height: 12),
                  _DetailRow('Nakshatra', nakshatra),
                  const SizedBox(height: 12),
                  _DetailRow('Pada', pada),
                  const SizedBox(height: 12),
                  _DetailRow('House', 'House $house'),
                ],
              ),
            ),
            const SizedBox(height: 16),
            // Dignity status
            GlassCard(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Dignity Status',
                    style: Theme.of(context).textTheme.labelMedium?.copyWith(
                          color: Colors.white70,
                        ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(8),
                      color: _getDignityColor(dignity).withOpacity(0.2),
                    ),
                    child: Text(
                      dignity,
                      style: TextStyle(
                        color: _getDignityColor(dignity),
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            if (aspects.isNotEmpty) ...[
              const SizedBox(height: 16),
              GlassCard(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Aspects',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            color: Colors.white70,
                          ),
                    ),
                    const SizedBox(height: 12),
                    ...aspects.map(
                      (aspect) => Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Text(
                          '• $aspect',
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall
                              ?.copyWith(
                                color: Colors.white70,
                              ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
            if (dashaInfo.isNotEmpty) ...[
              const SizedBox(height: 16),
              GlassCard(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Current Dasha',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            color: Colors.white70,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      dashaInfo,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.white70,
                          ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getDignityColor(String dignity) {
    switch (dignity.toLowerCase()) {
      case 'exalted':
        return const Color(0xFF2ECC71);
      case 'own sign':
        return const Color(0xFF3498DB);
      case 'debilitated':
        return const Color(0xFFE74C3C);
      default:
        return Colors.white70;
    }
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Colors.white54,
              ),
        ),
        Text(
          value,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.white,
              ),
        ),
      ],
    );
  }
}
