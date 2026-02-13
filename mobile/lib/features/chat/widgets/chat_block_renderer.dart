import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/features/state_map/models/state_vector.dart';

/// Renders a single chat block by type.
///
/// Supports 8 block types: score_card, factor_grid, area_list,
/// table, dasha_card, panchanga_card, alert, text.
class ChatBlockRenderer extends StatelessWidget {
  final Map<String, dynamic> block;

  const ChatBlockRenderer({super.key, required this.block});

  String get _type => block['type'] as String? ?? 'text';
  Map<String, dynamic> get _data =>
      block['data'] as Map<String, dynamic>? ?? {};

  @override
  Widget build(BuildContext context) {
    return switch (_type) {
      'score_card' => _buildScoreCard(),
      'factor_grid' => _buildFactorGrid(),
      'area_list' => _buildAreaList(),
      'table' => _buildTable(),
      'dasha_card' => _buildDashaCard(),
      'panchanga_card' => _buildPanchangaCard(),
      'alert' => _buildAlert(),
      _ => _buildText(),
    };
  }

  // ── score_card ──

  Widget _buildScoreCard() {
    final score = (_data['score'] as num?)?.toDouble() ?? 0;
    final max = (_data['max'] as num?)?.toDouble() ?? 10;
    final label = _data['label'] as String? ?? '';
    final subtitle = _data['subtitle'] as String? ?? '';
    final colorHex = _data['color'] as String? ?? '#FFC107';
    final color = _hexToColor(colorHex);

    return GlassContainer(
      borderRadius: 16,
      borderColor: color.withValues(alpha: 0.3),
      padding: const EdgeInsets.all(S.lg),
      child: Row(
        children: [
          // Circular score indicator
          SizedBox(
            width: 56,
            height: 56,
            child: Stack(
              alignment: Alignment.center,
              children: [
                CircularProgressIndicator(
                  value: (score / max).clamp(0.0, 1.0),
                  strokeWidth: 4,
                  backgroundColor: C.glassBorder,
                  color: color,
                ),
                Text(
                  score.toStringAsFixed(1),
                  style: T.h3.copyWith(color: color, fontSize: 16),
                ),
              ],
            ),
          ),
          const SizedBox(width: S.lg),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: T.h3.copyWith(fontSize: 16)),
                if (subtitle.isNotEmpty)
                  Text(subtitle, style: T.caption),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── factor_grid ──

  Widget _buildFactorGrid() {
    final factors = _data['factors'] as List<dynamic>? ?? [];

    return SizedBox(
      height: 40,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: factors.length,
        separatorBuilder: (_, __) => const SizedBox(width: S.sm),
        itemBuilder: (_, i) {
          final f = factors[i] as Map<String, dynamic>;
          final score = (f['score'] as num?)?.toDouble() ?? 0;
          final shortName = f['short_name'] as String? ?? '';
          final chipColor = _scoreColor(score);

          return Container(
            padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.xs),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              color: chipColor.withValues(alpha: 0.12),
              border: Border.all(color: chipColor.withValues(alpha: 0.25)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  shortName,
                  style: T.caption.copyWith(
                    color: C.textSecondary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(width: 4),
                Text(
                  score.toStringAsFixed(1),
                  style: T.bodySm.copyWith(
                    color: chipColor,
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  // ── area_list ──

  Widget _buildAreaList() {
    final areas = List<dynamic>.from(_data['areas'] as List<dynamic>? ?? [])
      ..sort((a, b) => ((b as Map)['score'] as num? ?? 0)
          .compareTo((a as Map)['score'] as num? ?? 0));

    return Column(
      children: areas.map<Widget>((a) {
        final area = a as Map<String, dynamic>;
        final id = area['id'] as String? ?? '';
        final score = (area['score'] as num?)?.toDouble() ?? 0;
        final doubleTx = area['double_transit'] as bool? ?? false;
        final name = kAreaNames[id] ?? id.replaceAll('_', ' ');
        final icon = kAreaIcons[id] ?? '';
        final color = _scoreColor(score);

        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 3),
          child: Row(
            children: [
              if (icon.isNotEmpty) ...[
                Text(icon, style: const TextStyle(fontSize: 14)),
                const SizedBox(width: S.sm),
              ],
              Expanded(
                flex: 2,
                child: Text(
                  name,
                  style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 13),
                ),
              ),
              if (doubleTx)
                Container(
                  margin: const EdgeInsets.only(right: S.sm),
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    color: C.jupiter.withValues(alpha: 0.15),
                  ),
                  child: Text('DT', style: T.caption.copyWith(color: C.jupiter, fontSize: 9)),
                ),
              // Score bar
              Expanded(
                flex: 3,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: (score / 10).clamp(0.0, 1.0),
                    backgroundColor: C.glassBorder,
                    color: color,
                    minHeight: 6,
                  ),
                ),
              ),
              const SizedBox(width: S.sm),
              SizedBox(
                width: 30,
                child: Text(
                  score.toStringAsFixed(1),
                  style: T.bodySm.copyWith(
                    color: color,
                    fontWeight: FontWeight.w700,
                    fontSize: 12,
                  ),
                  textAlign: TextAlign.right,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  // ── table ──

  Widget _buildTable() {
    final headers = (_data['headers'] as List<dynamic>?)
            ?.map((h) => h.toString())
            .toList() ??
        [];
    final rows = _data['rows'] as List<dynamic>? ?? [];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header row
          if (headers.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: S.xs),
              child: Row(
                children: headers
                    .map((h) => SizedBox(
                          width: 100,
                          child: Text(
                            h,
                            style: T.caption.copyWith(
                              fontWeight: FontWeight.w600,
                              color: C.textSecondary,
                            ),
                          ),
                        ))
                    .toList(),
              ),
            ),
          // Data rows
          ...rows.map((row) {
            final cells = row is List ? row : [];
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 2),
              child: Row(
                children: cells
                    .map((cell) => SizedBox(
                          width: 100,
                          child: Text(
                            cell.toString(),
                            style: T.bodySm.copyWith(
                              color: C.textPrimary,
                              fontSize: 13,
                            ),
                          ),
                        ))
                    .toList(),
              ),
            );
          }),
        ],
      ),
    );
  }

  // ── dasha_card ──

  Widget _buildDashaCard() {
    final maha = _data['maha'] as String? ?? '';
    final mahaProgress = (_data['maha_progress'] as num?)?.toDouble() ?? 0;
    final antar = _data['antar'] as String? ?? '';
    final antarProgress = (_data['antar_progress'] as num?)?.toDouble() ?? 0;

    return GlassContainer(
      borderRadius: 16,
      borderColor: C.saturn.withValues(alpha: 0.3),
      padding: const EdgeInsets.all(S.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Dasha Period',
              style: T.caption.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: S.md),
          // Mahadasha
          _DashaPeriodRow(
            label: 'Mahadasha',
            lord: maha,
            progress: mahaProgress,
          ),
          const SizedBox(height: S.sm),
          // Antardasha
          _DashaPeriodRow(
            label: 'Antardasha',
            lord: antar,
            progress: antarProgress,
          ),
        ],
      ),
    );
  }

  // ── panchanga_card ──

  Widget _buildPanchangaCard() {
    final limbs = [
      ('Tithi', _data['tithi'] as String? ?? ''),
      ('Nakshatra', _data['nakshatra'] as String? ?? ''),
      ('Yoga', _data['yoga'] as String? ?? ''),
      ('Karana', _data['karana'] as String? ?? ''),
      ('Vara', _data['vara'] as String? ?? ''),
    ];

    return GlassContainer(
      borderRadius: 16,
      padding: const EdgeInsets.all(S.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Panchanga',
              style: T.caption.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          ...limbs.map((limb) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  children: [
                    SizedBox(
                      width: 80,
                      child: Text(
                        limb.$1,
                        style: T.caption.copyWith(color: C.textSecondary),
                      ),
                    ),
                    Expanded(
                      child: Text(
                        limb.$2,
                        style: T.bodySm.copyWith(
                          color: C.textPrimary,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  // ── alert ──

  Widget _buildAlert() {
    final level = _data['level'] as String? ?? 'info';
    final title = _data['title'] as String? ?? '';
    final message = _data['message'] as String? ?? '';

    final (Color borderClr, Color iconClr, IconData icon) = switch (level) {
      'error' => (C.negative, C.negative, Icons.warning_amber_rounded),
      'warning' => (C.warning, C.warning, Icons.info_outline),
      _ => (C.mercury, C.mercury, Icons.lightbulb_outline),
    };

    return GlassContainer(
      borderRadius: 12,
      borderColor: borderClr.withValues(alpha: 0.4),
      backgroundColor: borderClr.withValues(alpha: 0.06),
      padding: const EdgeInsets.all(S.md),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: iconClr, size: 18),
          const SizedBox(width: S.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
                if (message.isNotEmpty)
                  Text(
                    message,
                    style: T.caption.copyWith(color: C.textSecondary),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── text (fallback) ──

  Widget _buildText() {
    final content = block['content'] as String? ?? '';
    return Text(
      content,
      style: T.body.copyWith(color: C.textPrimary),
    );
  }

  // ── helpers ──

  static Color _hexToColor(String hex) {
    final h = hex.replaceFirst('#', '');
    if (h.length == 6) {
      return Color(int.parse('FF$h', radix: 16));
    }
    return const Color(0xFFFFC107);
  }

  static Color _scoreColor(double score) {
    if (score >= 7) return C.positive;
    if (score >= 4) return C.warning;
    return C.negative;
  }
}

/// A single dasha period row with label, lord, and progress bar.
class _DashaPeriodRow extends StatelessWidget {
  final String label;
  final String lord;
  final double progress;

  const _DashaPeriodRow({
    required this.label,
    required this.lord,
    required this.progress,
  });

  @override
  Widget build(BuildContext context) {
    final color = lord.isNotEmpty ? planetColor(lord.toLowerCase()) : C.textMuted;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '$label: $lord',
              style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 13),
            ),
            Text(
              '${progress.toStringAsFixed(0)}%',
              style: T.caption.copyWith(color: color),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(3),
          child: LinearProgressIndicator(
            value: (progress / 100).clamp(0.0, 1.0),
            backgroundColor: C.glassBorder,
            color: color,
            minHeight: 4,
          ),
        ),
      ],
    );
  }
}
