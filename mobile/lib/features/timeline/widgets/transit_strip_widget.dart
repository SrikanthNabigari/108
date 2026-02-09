import 'dart:math';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/features/timeline/widgets/transit_detail_panel.dart';

/// Compact 9-lane transit visualization strip.
///
/// Each planet gets a horizontal bar showing its position in the zodiac (0-360°).
/// Tap a lane to open the [TransitDetailPanel]; tap the header to navigate to /transits.
class TransitStripWidget extends StatelessWidget {
  /// Transit positions map from the API: {planet: {longitude, rashi, rashi_num, ...}}.
  final Map<String, dynamic> transitData;

  /// Summary info: {favorable_count, unfavorable_count, trend}.
  final Map<String, dynamic>? summary;

  /// If true, lanes are taller (for dashboard use).
  final bool expanded;

  const TransitStripWidget({
    super.key,
    required this.transitData,
    this.summary,
    this.expanded = false,
  });

  static const _planets = [
    'sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu',
  ];

  @override
  Widget build(BuildContext context) {
    final positions = transitData;
    if (positions.isEmpty) return const SizedBox.shrink();

    // Derive summary if not provided
    final summ = summary ?? _deriveSummary(positions);
    final trend = summ['trend'] as String? ?? 'mixed';

    return GlassContainer(
      blur: 0,
      padding: const EdgeInsets.fromLTRB(S.md, S.md, S.md, S.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header — tap to open /transits dashboard
          GestureDetector(
            onTap: () => context.push('/transits'),
            child: Row(
              children: [
                Text(
                  'Current Transits',
                  style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                const Spacer(),
                _TrendBadge(trend: trend),
                const SizedBox(width: 4),
                const Icon(Icons.chevron_right, color: C.textMuted, size: 18),
              ],
            ),
          ),
          const SizedBox(height: S.sm),

          // 9 planet lanes
          ..._planets.map((p) {
            final data = positions[p] as Map<String, dynamic>? ?? {};
            return _PlanetLane(
              planet: p,
              data: data,
              laneHeight: expanded ? 44.0 : 36.0,
            );
          }),
        ],
      ),
    );
  }

  Map<String, dynamic> _deriveSummary(Map<String, dynamic> positions) {
    // Simple count based on presence (actual favorability requires gochara)
    return {'trend': 'mixed', 'favorable_count': 0, 'unfavorable_count': 0};
  }
}

// ── Trend badge ──

class _TrendBadge extends StatelessWidget {
  final String trend;
  const _TrendBadge({required this.trend});

  @override
  Widget build(BuildContext context) {
    final Color color;
    final String label;
    switch (trend) {
      case 'positive':
        color = C.positive;
        label = 'Favorable';
      case 'challenging':
        color = C.negative;
        label = 'Challenging';
      default:
        color = C.warning;
        label = 'Mixed';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: R.smBr,
        color: color.withValues(alpha: 0.15),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Text(
        label,
        style: T.caption.copyWith(color: color, fontSize: 9, fontWeight: FontWeight.w600),
      ),
    );
  }
}

// ── Single planet lane ──

class _PlanetLane extends StatelessWidget {
  final String planet;
  final Map<String, dynamic> data;
  final double laneHeight;

  const _PlanetLane({
    required this.planet,
    required this.data,
    required this.laneHeight,
  });

  @override
  Widget build(BuildContext context) {
    final longitude = (data['longitude'] as num?)?.toDouble() ?? 0.0;
    final rashiNum = (data['rashi_num'] as num?)?.toInt() ?? (longitude ~/ 30);
    final isRetro = data['is_retrograde'] as bool? ?? false;
    final color = planetColor(planet);
    final glyph = planetGlyph(planet);
    final abbr = rashiNum >= 0 && rashiNum < rashiAbbrev.length
        ? rashiAbbrev[rashiNum]
        : '???';

    // Gochara favorability (from API if available)
    final gochara = data['gochara'] as Map<String, dynamic>?;
    final isFavorable = gochara?['is_favorable'] as bool? ??
        gochara?['favorable'] as bool?;
    final Color abbrColor;
    if (isFavorable == true) {
      abbrColor = C.positive;
    } else if (isFavorable == false) {
      abbrColor = C.textMuted;
    } else {
      abbrColor = C.textSecondary;
    }

    return GestureDetector(
      onTap: () => TransitDetailPanel.show(context, planet: planet),
      child: Padding(
        padding: const EdgeInsets.only(bottom: 2),
        child: SizedBox(
          height: laneHeight,
          child: Row(
            children: [
              // Planet glyph + abbreviation
              SizedBox(
                width: 44,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(glyph, style: TextStyle(fontSize: 14, color: color)),
                    Text(
                      planet.substring(0, min(3, planet.length)).toUpperCase(),
                      style: T.caption.copyWith(fontSize: 8, color: C.textMuted),
                    ),
                  ],
                ),
              ),

              // Bar with position dot
              Expanded(
                child: LayoutBuilder(
                  builder: (_, constraints) {
                    final barWidth = constraints.maxWidth;
                    // Position as fraction of 360°
                    final fraction = (longitude % 360) / 360;
                    final dotX = fraction * barWidth;

                    return Stack(
                      alignment: Alignment.centerLeft,
                      children: [
                        // Background bar with rashi segments
                        CustomPaint(
                          size: Size(barWidth, laneHeight - 8),
                          painter: _RashiBarPainter(),
                        ),
                        // Gradient fill up to dot position
                        Positioned(
                          left: 0,
                          width: dotX,
                          top: 4,
                          bottom: 4,
                          child: Container(
                            decoration: BoxDecoration(
                              borderRadius: R.smBr,
                              gradient: LinearGradient(
                                colors: [
                                  color.withValues(alpha: 0.05),
                                  color.withValues(alpha: 0.25),
                                ],
                              ),
                            ),
                          ),
                        ),
                        // Position dot
                        Positioned(
                          left: (dotX - 4).clamp(0, barWidth - 8),
                          child: Container(
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.white,
                              boxShadow: [
                                BoxShadow(
                                  color: color.withValues(alpha: 0.6),
                                  blurRadius: 6,
                                ),
                              ],
                            ),
                          ),
                        ),
                        // Retrograde indicator
                        if (isRetro)
                          Positioned(
                            left: (dotX + 6).clamp(0, barWidth - 14),
                            child: Text(
                              '\u25C0',
                              style: TextStyle(fontSize: 8, color: color.withValues(alpha: 0.7)),
                            ),
                          ),
                      ],
                    );
                  },
                ),
              ),

              // Rashi abbreviation
              SizedBox(
                width: 36,
                child: Text(
                  abbr,
                  textAlign: TextAlign.right,
                  style: T.caption.copyWith(
                    color: abbrColor,
                    fontSize: 10,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Rashi bar painter ──

class _RashiBarPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final bgPaint = Paint()..color = C.glassBg;
    final divPaint = Paint()
      ..color = C.glassBorder.withValues(alpha: 0.3)
      ..strokeWidth = 0.5;

    // Background
    canvas.drawRRect(
      RRect.fromRectAndRadius(Offset.zero & size, const Radius.circular(4)),
      bgPaint,
    );

    // 12 segment dividers
    final segW = size.width / 12;
    for (int i = 1; i < 12; i++) {
      final x = segW * i;
      canvas.drawLine(Offset(x, 2), Offset(x, size.height - 2), divPaint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
