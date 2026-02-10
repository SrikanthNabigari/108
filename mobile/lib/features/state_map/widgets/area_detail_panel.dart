import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import '../models/state_vector.dart';

/// Bottom sheet detail panel for a life area — opened when an area card is
/// tapped on the State Map screen.
///
/// Three tabs: NOW (current breakdown), TREND (sparkline over range),
/// LEARN (educational content about the area).
class AreaDetailPanel extends StatelessWidget {
  final AreaScore area;
  final List<StateVector> rangeVectors;
  final DateTime selectedDate;

  const AreaDetailPanel({
    super.key,
    required this.area,
    required this.rangeVectors,
    required this.selectedDate,
  });

  /// Show as a modal bottom sheet.
  static void show(
    BuildContext context, {
    required AreaScore area,
    required List<StateVector> rangeVectors,
    required DateTime selectedDate,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => AreaDetailPanel(
        area: area,
        rangeVectors: rangeVectors,
        selectedDate: selectedDate,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final planet = kAreaPlanets[area.id] ?? 'saturn';
    final color = planetColor(planet);
    final icon = kAreaIcons[area.id] ?? '';

    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      minChildSize: 0.4,
      maxChildSize: 0.9,
      builder: (context, scrollController) {
        return DefaultTabController(
          length: 3,
          child: Container(
            decoration: BoxDecoration(
              color: C.surface,
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(24)),
              border: Border.all(color: C.glassBorder),
            ),
            child: Column(
              children: [
                // Drag handle
                const SizedBox(height: 8),
                Container(
                  width: 32,
                  height: 4,
                  decoration: BoxDecoration(
                    borderRadius: R.smBr,
                    color: C.glassBorder,
                  ),
                ),
                const SizedBox(height: 4),

                // -- Gradient header --
                Container(
                  width: double.infinity,
                  padding:
                      const EdgeInsets.fromLTRB(S.xl, S.md, S.xl, S.lg),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.topCenter,
                      end: Alignment.bottomCenter,
                      colors: [
                        color.withValues(alpha: 0.12),
                        Colors.transparent,
                      ],
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(icon, style: const TextStyle(fontSize: 28)),
                          const SizedBox(width: S.md),
                          Expanded(
                            child: Text(area.name,
                                style: T.h2.copyWith(color: color)),
                          ),
                          // Score badge
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: S.md, vertical: S.sm),
                            decoration: BoxDecoration(
                              borderRadius: R.lgBr,
                              color: color.withValues(alpha: 0.15),
                              border: Border.all(
                                  color: color.withValues(alpha: 0.4)),
                            ),
                            child: Text(
                              '${area.score.toStringAsFixed(1)}/10',
                              style:
                                  T.h3.copyWith(color: color, fontSize: 20),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: S.sm),
                      // Badges row
                      Wrap(
                        spacing: S.sm,
                        runSpacing: S.xs,
                        children: [
                          if (area.doubleTransit)
                            _Badge(
                              text: 'DOUBLE',
                              color: C.jupiter,
                              filled: true,
                            ),
                          if (area.lordshipQuality.isNotEmpty &&
                              area.lordshipQuality != 'neutral')
                            _Badge(
                              text: area.lordshipQuality.toUpperCase(),
                              color: _lordshipColor(area.lordshipQuality),
                            ),
                          ...area.activeYogas.map((y) => _Badge(
                                text: y,
                                color: C.positive,
                              )),
                        ],
                      ),
                    ],
                  ),
                ),

                // -- Tab bar --
                TabBar(
                  indicatorColor: color,
                  labelColor: color,
                  unselectedLabelColor: C.textMuted,
                  labelStyle:
                      T.label.copyWith(fontSize: 12, letterSpacing: 1.4),
                  dividerHeight: 0.5,
                  dividerColor: C.glassBorder,
                  tabs: const [
                    Tab(text: 'NOW'),
                    Tab(text: 'TREND'),
                    Tab(text: 'LEARN'),
                  ],
                ),

                // -- Tab views --
                Expanded(
                  child: TabBarView(
                    children: [
                      _NowTab(
                        area: area,
                        color: color,
                        scrollController: scrollController,
                      ),
                      _TrendTab(
                        area: area,
                        rangeVectors: rangeVectors,
                        selectedDate: selectedDate,
                        color: color,
                        scrollController: scrollController,
                      ),
                      _LearnTab(
                        area: area,
                        color: color,
                        scrollController: scrollController,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Color _lordshipColor(String quality) {
    switch (quality) {
      case 'yogakaraka':
        return C.jupiter;
      case 'benefic':
        return C.positive;
      case 'malefic':
        return C.negative;
      case 'maraka':
        return C.mars;
      default:
        return C.textMuted;
    }
  }
}

// -- Badges --

class _Badge extends StatelessWidget {
  final String text;
  final Color color;
  final bool filled;
  const _Badge({required this.text, required this.color, this.filled = false});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: R.smBr,
        color: filled ? color.withValues(alpha: 0.2) : Colors.transparent,
        border: Border.all(color: color.withValues(alpha: 0.6)),
      ),
      child: Text(
        text,
        style: T.label.copyWith(
          color: color,
          fontSize: 10,
          fontWeight: filled ? FontWeight.w700 : FontWeight.w600,
        ),
      ),
    );
  }
}

// -- NOW tab --

class _NowTab extends StatelessWidget {
  final AreaScore area;
  final Color color;
  final ScrollController scrollController;
  const _NowTab({
    required this.area,
    required this.color,
    required this.scrollController,
  });

  @override
  Widget build(BuildContext context) {
    final planet = kAreaPlanets[area.id] ?? 'saturn';

    return ListView(
      controller: scrollController,
      padding: const EdgeInsets.symmetric(horizontal: S.xl, vertical: S.lg),
      children: [
        // Overall score bar
        _ScoreBar(label: area.name, score: area.score, color: color),
        const SizedBox(height: S.xl),

        // Score breakdown
        _SectionTitle(text: 'Score Breakdown'),
        const SizedBox(height: S.sm),
        ..._buildBreakdownRows(),
        const SizedBox(height: S.xl),

        // Active yogas
        if (area.activeYogas.isNotEmpty) ...[
          _SectionTitle(text: 'Active Yogas'),
          const SizedBox(height: S.sm),
          Wrap(
            spacing: S.sm,
            runSpacing: S.sm,
            children: area.activeYogas
                .map((y) => Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: S.md, vertical: S.sm),
                      decoration: BoxDecoration(
                        borderRadius: R.mdBr,
                        border: Border.all(
                            color: C.positive.withValues(alpha: 0.5)),
                        color: C.positive.withValues(alpha: 0.08),
                      ),
                      child: Text(y,
                          style: T.bodySm.copyWith(
                              color: C.positive, fontSize: 13)),
                    ))
                .toList(),
          ),
          const SizedBox(height: S.xl),
        ],

        // Double transit
        if (area.doubleTransit) ...[
          _SectionTitle(text: 'Double Transit'),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            borderColor: C.jupiter.withValues(alpha: 0.4),
            backgroundColor: C.jupiter.withValues(alpha: 0.06),
            child: Row(
              children: [
                Text(planetGlyph('jupiter'),
                    style: TextStyle(fontSize: 20, color: C.jupiter)),
                const SizedBox(width: S.sm),
                Text('+', style: T.bodySm.copyWith(color: C.textMuted)),
                const SizedBox(width: S.sm),
                Text(planetGlyph('saturn'),
                    style: TextStyle(fontSize: 20, color: C.saturn)),
                const SizedBox(width: S.md),
                Expanded(
                  child: Text(
                    'Jupiter + Saturn both activate your ${area.name.toLowerCase()} houses',
                    style: T.bodySm.copyWith(color: C.jupiter, height: 1.4),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.xl),
        ],

        // Lordship
        _SectionTitle(text: 'Lordship'),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.lg),
          child: Row(
            children: [
              Text('Quality',
                  style: T.bodySm.copyWith(color: C.textSecondary)),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.md, vertical: S.xs),
                decoration: BoxDecoration(
                  borderRadius: R.smBr,
                  color: _lordshipColor(area.lordshipQuality)
                      .withValues(alpha: 0.15),
                ),
                child: Text(
                  area.lordshipQuality.isNotEmpty
                      ? area.lordshipQuality[0].toUpperCase() +
                          area.lordshipQuality.substring(1)
                      : 'Neutral',
                  style: T.bodySm.copyWith(
                    color: _lordshipColor(area.lordshipQuality),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: S.xl),

        // Dominant planet
        if (area.dominantPlanet.isNotEmpty) ...[
          _SectionTitle(text: 'Dominant Planet'),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Row(
              children: [
                Text(
                  planetGlyph(area.dominantPlanet),
                  style: TextStyle(
                    fontSize: 24,
                    color: planetColor(area.dominantPlanet),
                  ),
                ),
                const SizedBox(width: S.md),
                Text(
                  planetName(area.dominantPlanet),
                  style: T.h3.copyWith(
                      color: planetColor(area.dominantPlanet)),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.xl),
        ],

        // Insight
        if (area.insight.isNotEmpty) ...[
          _SectionTitle(text: 'Insight'),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Text(
              area.insight,
              style: T.bodySm.copyWith(color: C.textPrimary, height: 1.6),
            ),
          ),
        ],

        // Override karaka label using planet constant
        if (area.dominantPlanet.isEmpty) ...[
          _SectionTitle(text: 'Karaka Planet'),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Row(
              children: [
                Text(
                  planetGlyph(planet),
                  style: TextStyle(fontSize: 24, color: color),
                ),
                const SizedBox(width: S.md),
                Text(planetName(planet),
                    style: T.h3.copyWith(color: color)),
              ],
            ),
          ),
        ],
        const SizedBox(height: S.xxl),
      ],
    );
  }

  List<Widget> _buildBreakdownRows() {
    const components = [
      ('House Activation', 35),
      ('Lordship Quality', 15),
      ('Transit Aspects', 10),
      ('Dasha Relevance', 20),
      ('Yoga Activation', 10),
      ('Panchanga Baseline', 10),
    ];
    return components
        .map((c) => Container(
              margin: const EdgeInsets.only(bottom: S.sm),
              padding: const EdgeInsets.symmetric(
                  horizontal: S.md, vertical: S.sm),
              decoration: BoxDecoration(
                borderRadius: R.mdBr,
                color: C.glassBg,
                border: Border.all(color: C.glassBorder, width: 0.5),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      '${c.$1} (${c.$2}%)',
                      style: T.bodySm.copyWith(
                          color: C.textPrimary, fontSize: 13),
                    ),
                  ),
                  SizedBox(
                    width: 60,
                    child: ClipRRect(
                      borderRadius: R.smBr,
                      child: LinearProgressIndicator(
                        value: c.$2 / 100,
                        minHeight: 4,
                        backgroundColor: C.glassBorder,
                        valueColor: AlwaysStoppedAnimation(color),
                      ),
                    ),
                  ),
                ],
              ),
            ))
        .toList();
  }

  Color _lordshipColor(String quality) {
    switch (quality) {
      case 'yogakaraka':
        return C.jupiter;
      case 'benefic':
        return C.positive;
      case 'malefic':
        return C.negative;
      case 'maraka':
        return C.mars;
      default:
        return C.textMuted;
    }
  }
}

// -- TREND tab --

class _TrendTab extends StatelessWidget {
  final AreaScore area;
  final List<StateVector> rangeVectors;
  final DateTime selectedDate;
  final Color color;
  final ScrollController scrollController;

  const _TrendTab({
    required this.area,
    required this.rangeVectors,
    required this.selectedDate,
    required this.color,
    required this.scrollController,
  });

  @override
  Widget build(BuildContext context) {
    // Extract scores for this area across the date range.
    final scores = <double>[];
    final dates = <DateTime>[];
    for (final v in rangeVectors) {
      final match = v.areas.where((a) => a.id == area.id);
      scores.add(match.isNotEmpty ? match.first.score : 0);
      dates.add(v.date);
    }

    // Find highlight, peak, trough indices.
    int highlightIndex = 0;
    int peakIndex = 0;
    int troughIndex = 0;
    double peakVal = -1;
    double troughVal = 11;
    for (int i = 0; i < scores.length; i++) {
      if (dates[i].year == selectedDate.year &&
          dates[i].month == selectedDate.month &&
          dates[i].day == selectedDate.day) {
        highlightIndex = i;
      }
      if (scores[i] > peakVal) {
        peakVal = scores[i];
        peakIndex = i;
      }
      if (scores[i] < troughVal) {
        troughVal = scores[i];
        troughIndex = i;
      }
    }

    // Trend: compare last 3 vs previous 3.
    String trend = 'Stable';
    if (scores.length >= 6) {
      final recent =
          scores.sublist(scores.length - 3).reduce((a, b) => a + b) / 3;
      final prior = scores
              .sublist(scores.length - 6, scores.length - 3)
              .reduce((a, b) => a + b) /
          3;
      if (recent - prior > 0.5) {
        trend = 'Rising';
      } else if (prior - recent > 0.5) {
        trend = 'Falling';
      }
    }

    return ListView(
      controller: scrollController,
      padding: const EdgeInsets.symmetric(horizontal: S.xl, vertical: S.lg),
      children: [
        // Sparkline chart
        if (scores.isNotEmpty) ...[
          _SectionTitle(text: '${area.name} Over Time'),
          const SizedBox(height: S.md),
          Container(
            height: 180,
            decoration: BoxDecoration(
              borderRadius: R.mdBr,
              color: C.glassBg,
              border: Border.all(color: C.glassBorder, width: 0.5),
            ),
            padding: const EdgeInsets.all(S.lg),
            child: CustomPaint(
              size: Size.infinite,
              painter: _SparklinePainter(
                values: scores,
                color: color,
                highlightIndex: highlightIndex,
                peakIndex: peakIndex,
                troughIndex: troughIndex,
              ),
            ),
          ),
          const SizedBox(height: S.xl),
        ],

        // Peak & trough cards
        if (dates.isNotEmpty) ...[
          Row(
            children: [
              Expanded(
                child: GlassContainer(
                  padding: const EdgeInsets.all(S.md),
                  borderColor: C.positive.withValues(alpha: 0.4),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Peak',
                          style: T.label.copyWith(color: C.positive)),
                      const SizedBox(height: S.xs),
                      Text(
                        _formatDate(dates[peakIndex]),
                        style: T.h3.copyWith(color: C.textPrimary, fontSize: 16),
                      ),
                      Text(
                        peakVal.toStringAsFixed(1),
                        style: T.h2.copyWith(color: C.positive, fontSize: 22),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: S.md),
              Expanded(
                child: GlassContainer(
                  padding: const EdgeInsets.all(S.md),
                  borderColor: C.negative.withValues(alpha: 0.4),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Low',
                          style: T.label.copyWith(color: C.negative)),
                      const SizedBox(height: S.xs),
                      Text(
                        _formatDate(dates[troughIndex]),
                        style: T.h3.copyWith(color: C.textPrimary, fontSize: 16),
                      ),
                      Text(
                        troughVal.toStringAsFixed(1),
                        style: T.h2.copyWith(color: C.negative, fontSize: 22),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: S.md),

          // Current position card
          GlassContainer(
            padding: const EdgeInsets.all(S.md),
            borderColor: color.withValues(alpha: 0.4),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Current',
                          style: T.label.copyWith(color: color)),
                      const SizedBox(height: S.xs),
                      Text(
                        _formatDate(selectedDate),
                        style: T.bodySm.copyWith(
                            color: C.textPrimary, fontSize: 14),
                      ),
                    ],
                  ),
                ),
                Text(
                  area.score.toStringAsFixed(1),
                  style: T.h2.copyWith(color: color, fontSize: 22),
                ),
                if (scores.length > 1) ...[
                  const SizedBox(width: S.md),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: S.sm, vertical: S.xs),
                    decoration: BoxDecoration(
                      borderRadius: R.smBr,
                      color: color.withValues(alpha: 0.1),
                    ),
                    child: Text(
                      _percentileLabel(area.score, scores),
                      style: T.label.copyWith(
                          color: color, fontSize: 11),
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: S.xl),
        ],

        // Trend label
        _SectionTitle(text: 'Trend'),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.lg),
          child: Row(
            children: [
              Icon(
                trend == 'Rising'
                    ? Icons.trending_up
                    : trend == 'Falling'
                        ? Icons.trending_down
                        : Icons.trending_flat,
                color: trend == 'Rising'
                    ? C.positive
                    : trend == 'Falling'
                        ? C.negative
                        : C.textSecondary,
                size: 24,
              ),
              const SizedBox(width: S.md),
              Text(
                trend,
                style: T.h3.copyWith(
                  color: trend == 'Rising'
                      ? C.positive
                      : trend == 'Falling'
                          ? C.negative
                          : C.textSecondary,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: S.xxl),
      ],
    );
  }
}

// -- Sparkline painter --

class _SparklinePainter extends CustomPainter {
  final List<double> values;
  final Color color;
  final int highlightIndex;
  final int peakIndex;
  final int troughIndex;

  _SparklinePainter({
    required this.values,
    required this.color,
    required this.highlightIndex,
    required this.peakIndex,
    required this.troughIndex,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (values.isEmpty) return;

    final linePaint = Paint()
      ..color = color
      ..strokeWidth = 2
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final fillPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [color.withValues(alpha: 0.1), Colors.transparent],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height))
      ..style = PaintingStyle.fill;

    final n = values.length;
    final dx = n > 1 ? size.width / (n - 1) : size.width;

    double toY(double v) => size.height - (v / 10.0) * size.height;

    // Build path
    final path = Path();
    path.moveTo(0, toY(values[0]));
    for (int i = 1; i < n; i++) {
      path.lineTo(i * dx, toY(values[i]));
    }

    // Fill path
    final fillPath = Path.from(path)
      ..lineTo((n - 1) * dx, size.height)
      ..lineTo(0, size.height)
      ..close();
    canvas.drawPath(fillPath, fillPaint);

    // Stroke line
    canvas.drawPath(path, linePaint);

    // Peak dot (green)
    if (peakIndex < n) {
      canvas.drawCircle(
        Offset(peakIndex * dx, toY(values[peakIndex])),
        4,
        Paint()..color = C.positive,
      );
    }

    // Trough dot (red)
    if (troughIndex < n) {
      canvas.drawCircle(
        Offset(troughIndex * dx, toY(values[troughIndex])),
        4,
        Paint()..color = C.negative,
      );
    }

    // Current day dot (white fill, color border)
    if (highlightIndex < n) {
      final cx = highlightIndex * dx;
      final cy = toY(values[highlightIndex]);
      canvas.drawCircle(cx == 0 ? Offset(cx, cy) : Offset(cx, cy), 5,
          Paint()..color = color);
      canvas.drawCircle(Offset(cx, cy), 3, Paint()..color = Colors.white);
    }
  }

  @override
  bool shouldRepaint(covariant _SparklinePainter old) =>
      old.values != values ||
      old.color != color ||
      old.highlightIndex != highlightIndex;
}

// -- LEARN tab --

class _LearnTab extends StatelessWidget {
  final AreaScore area;
  final Color color;
  final ScrollController scrollController;
  const _LearnTab({
    required this.area,
    required this.color,
    required this.scrollController,
  });

  @override
  Widget build(BuildContext context) {
    final info = _areaLearn[area.id];
    if (info == null) {
      return Center(
        child: Text('No information available.',
            style: T.bodySm.copyWith(color: C.textMuted)),
      );
    }

    final karakaPlanet = kAreaPlanets[area.id] ?? 'saturn';

    return ListView(
      controller: scrollController,
      padding: const EdgeInsets.symmetric(horizontal: S.xl, vertical: S.lg),
      children: [
        // Description
        _SectionTitle(text: 'What is ${area.name}?'),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.lg),
          child: Text(
            info['description']!,
            style: T.bodySm.copyWith(color: C.textPrimary, height: 1.6),
          ),
        ),
        const SizedBox(height: S.xl),

        // Key houses
        _SectionTitle(text: 'Key Houses'),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.lg),
          child: Text(
            info['houses']!,
            style: T.bodySm.copyWith(color: C.textPrimary, height: 1.6),
          ),
        ),
        const SizedBox(height: S.xl),

        // Karaka planet
        _SectionTitle(text: 'Karaka Planet'),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.lg),
          child: Row(
            children: [
              Text(
                planetGlyph(karakaPlanet),
                style: TextStyle(fontSize: 24, color: color),
              ),
              const SizedBox(width: S.md),
              Expanded(
                child: Text(
                  info['karaka']!,
                  style:
                      T.bodySm.copyWith(color: C.textPrimary, height: 1.5),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: S.xl),

        // Peak conditions
        _SectionTitle(text: 'When ${area.name} Peaks'),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.lg),
          child: Text(
            info['peak_conditions']!,
            style: T.bodySm.copyWith(color: C.textPrimary, height: 1.6),
          ),
        ),
        const SizedBox(height: S.xxl),
      ],
    );
  }
}

// -- Shared sub-widgets --

class _SectionTitle extends StatelessWidget {
  final String text;
  const _SectionTitle({required this.text});

  @override
  Widget build(BuildContext context) {
    return Text(
      text.toUpperCase(),
      style: T.label.copyWith(color: C.textMuted, letterSpacing: 1.2),
    );
  }
}

class _ScoreBar extends StatelessWidget {
  final String label;
  final double score;
  final Color color;
  const _ScoreBar({
    required this.label,
    required this.score,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(label, style: T.bodySm.copyWith(color: C.textPrimary)),
            const Spacer(),
            Text('${score.toStringAsFixed(1)}/10',
                style: T.bodySm
                    .copyWith(color: color, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: R.smBr,
          child: LinearProgressIndicator(
            value: (score / 10).clamp(0.0, 1.0),
            minHeight: 6,
            backgroundColor: C.glassBorder,
            valueColor: AlwaysStoppedAnimation(color),
          ),
        ),
      ],
    );
  }
}

// -- Date formatting --

String _formatDate(DateTime dt) {
  const months = [
    '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
  ];
  return '${months[dt.month]} ${dt.day}, ${dt.year}';
}

String _percentileLabel(double current, List<double> all) {
  final below = all.where((s) => s < current).length;
  final pct = (below / all.length * 100).round();
  return '${pct}th percentile';
}

// -- Educational content --

const _areaLearn = {
  'career': {
    'description':
        'Your professional life, reputation, and public standing. Career encompasses your main vocation, authority figures, and how the world perceives your contributions.',
    'houses':
        'House 10 (profession, status), House 6 (daily work, service), House 2 (earned income)',
    'karaka':
        'Saturn \u2014 discipline, structure, long-term achievement, career longevity',
    'peak_conditions':
        'Career peaks when Jupiter or Saturn activate House 10 via double transit, and dasha lords rule the 10th house.',
  },
  'relationships': {
    'description':
        'Partnerships, marriage, and close bonds. This area covers both romantic relationships and significant one-on-one connections.',
    'houses':
        'House 7 (marriage, partners), House 5 (romance, creativity), House 11 (friendships, networks)',
    'karaka':
        'Venus \u2014 love, harmony, attraction, partnership',
    'peak_conditions':
        'Relationships flourish when Venus transits favorable houses and Jupiter aspects the 7th house.',
  },
  'health': {
    'description':
        'Physical vitality, immunity, and overall well-being. Health also encompasses mental wellness and recovery from illness.',
    'houses':
        'House 1 (body, constitution), House 6 (disease, immunity), House 8 (longevity, chronic issues)',
    'karaka':
        'Sun \u2014 vitality, life force, constitution, immune strength',
    'peak_conditions':
        'Health is strongest when the Sun and Mars are well-placed, and no malefics afflict the 1st or 6th house.',
  },
  'finance': {
    'description':
        'Wealth, income, investments, and material gains. This covers both earned income and unexpected windfalls.',
    'houses':
        'House 2 (accumulated wealth), House 11 (gains, profits), House 5 (speculative gains)',
    'karaka':
        'Jupiter \u2014 abundance, expansion, wisdom in wealth management',
    'peak_conditions':
        'Finance peaks when Jupiter transits the 2nd or 11th house, especially with double transit activation.',
  },
  'spiritual': {
    'description':
        'Inner growth, meditation, higher learning, and connection to the divine. Spiritual development through dharma and moksha.',
    'houses':
        'House 9 (dharma, guru, fortune), House 12 (moksha, meditation), House 5 (past merit, mantra)',
    'karaka':
        'Ketu \u2014 detachment, liberation, mystical insight',
    'peak_conditions':
        'Spiritual growth accelerates when Jupiter transits the 9th house or Ketu activates the 12th house.',
  },
  'family': {
    'description':
        'Home life, mother, emotional security, and domestic harmony. Family encompasses property, vehicles, and ancestral connections.',
    'houses':
        'House 4 (home, mother, comfort), House 2 (family lineage, food), House 1 (self, physical body)',
    'karaka':
        'Moon \u2014 mother, nurture, emotional security, home',
    'peak_conditions':
        'Family harmony peaks when the Moon is strong, Jupiter aspects the 4th house, and no malefics disturb House 4.',
  },
  'education': {
    'description':
        'Learning, academic success, intellectual development, and skill acquisition. Covers both formal education and self-directed study.',
    'houses':
        'House 4 (formal education, degrees), House 5 (intelligence, creativity), House 9 (higher learning, wisdom)',
    'karaka':
        'Mercury \u2014 intellect, communication, analytical ability, learning speed',
    'peak_conditions':
        'Education thrives when Mercury and Jupiter are strong, and dasha lords activate the 4th, 5th, or 9th houses.',
  },
  'travel': {
    'description':
        'Short and long journeys, foreign connections, relocation, and exploration. Travel includes both physical movement and cultural exchange.',
    'houses':
        'House 3 (short trips, courage), House 9 (long journeys, pilgrimage), House 12 (foreign lands, emigration)',
    'karaka':
        'Rahu \u2014 foreign places, unconventional paths, adventure, overseas connections',
    'peak_conditions':
        'Travel is favored when Rahu or Jupiter activate the 3rd, 9th, or 12th houses, especially during Rahu dasha periods.',
  },
};
