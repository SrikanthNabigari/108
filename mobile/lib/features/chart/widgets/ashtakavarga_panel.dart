import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Bottom sheet panel showing the Ashtakavarga bindu grid.
///
/// Displays a 7-planet x 12-sign matrix of BAV (Bhinna Ashtakavarga) values
/// with SAV (Sarva Ashtakavarga) totals at the bottom.
class AshtakavargaPanel extends StatelessWidget {
  const AshtakavargaPanel({super.key});

  static void show(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => const AshtakavargaPanel(),
    );
  }

  static const _planets = [
    'sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn'
  ];

  static const _signs = [
    'Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi'
  ];

  static const _demoBav = {
    'sun':     [5, 3, 4, 6, 3, 2, 5, 4, 3, 5, 4, 6],
    'moon':    [4, 5, 3, 4, 6, 5, 3, 4, 5, 3, 6, 4],
    'mars':    [3, 4, 5, 3, 2, 4, 6, 3, 4, 5, 3, 4],
    'mercury': [5, 6, 4, 5, 3, 5, 4, 6, 5, 4, 3, 5],
    'jupiter': [6, 5, 4, 3, 5, 6, 4, 5, 3, 6, 5, 4],
    'venus':   [4, 3, 5, 6, 4, 3, 5, 4, 6, 3, 5, 4],
    'saturn':  [3, 4, 3, 5, 4, 6, 3, 5, 4, 3, 6, 5],
  };

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.6,
      maxChildSize: 0.92,
      builder: (context, scrollController) {
        return Container(
          decoration: BoxDecoration(
            color: C.surface,
            borderRadius:
                const BorderRadius.vertical(top: Radius.circular(R.xl)),
          ),
          child: Column(
            children: [
              _buildHeader(),
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: S.lg),
                  children: [
                    const SizedBox(height: S.md),
                    _buildGrid(),
                    const SizedBox(height: S.lg),
                    _buildEducationalCard(),
                    const SizedBox(height: S.xl),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(S.lg, S.md, S.lg, S.md),
      decoration: BoxDecoration(
        borderRadius:
            const BorderRadius.vertical(top: Radius.circular(R.xl)),
        gradient: LinearGradient(
          colors: [
            C.accent.withValues(alpha: 0.15),
            Colors.transparent,
          ],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
      ),
      child: Column(
        children: [
          // Drag handle
          Container(
            width: 36,
            height: 4,
            decoration: BoxDecoration(
              color: C.textMuted.withValues(alpha: 0.3),
              borderRadius: R.xlBr,
            ),
          ),
          const SizedBox(height: S.md),
          Row(
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: C.accent.withValues(alpha: 0.12),
                ),
                child:
                    const Icon(Icons.grid_on, color: C.accent, size: 18),
              ),
              const SizedBox(width: S.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Ashtakavarga',
                        style: T.h3.copyWith(fontSize: 16)),
                    Text('Bhinna & Sarva Ashtakavarga Bindus',
                        style: T.caption.copyWith(fontSize: 11)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildGrid() {
    // Compute SAV (column sums)
    final sav = List.generate(12, (col) {
      int total = 0;
      for (final planet in _planets) {
        total += _demoBav[planet]![col];
      }
      return total;
    });

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header row: corner + 12 signs
          Row(
            children: [
              _cornerCell(),
              ..._signs.map((s) => _headerCell(s)),
            ],
          ),
          // Planet rows
          ..._planets.map((planet) {
            final bindus = _demoBav[planet]!;
            return Row(
              children: [
                _planetLabelCell(planet),
                ...List.generate(
                    12, (idx) => _binduCell(bindus[idx])),
              ],
            );
          }),
          // SAV total row
          Row(
            children: [
              _savLabelCell(),
              ...List.generate(12, (idx) => _savCell(sav[idx])),
            ],
          ),
        ],
      ),
    );
  }

  Widget _cornerCell() {
    return Container(
      width: 40,
      height: 32,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        border: Border.all(color: C.glassBorder, width: 0.5),
        color: C.accent.withValues(alpha: 0.05),
      ),
      child: Text('', style: T.caption.copyWith(fontSize: 9)),
    );
  }

  Widget _headerCell(String sign) {
    return Container(
      width: 34,
      height: 32,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        border: Border.all(color: C.glassBorder, width: 0.5),
        color: C.accent.withValues(alpha: 0.05),
      ),
      child: Text(sign,
          style: T.caption.copyWith(
              fontSize: 9,
              fontWeight: FontWeight.w600,
              color: C.textSecondary)),
    );
  }

  Widget _planetLabelCell(String planet) {
    final color = planetColor(planet);
    return Container(
      width: 40,
      height: 32,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        border: Border.all(color: C.glassBorder, width: 0.5),
        color: color.withValues(alpha: 0.05),
      ),
      child: Text(planetGlyph(planet),
          style: TextStyle(fontSize: 14, color: color)),
    );
  }

  Widget _binduCell(int value) {
    final bgColor = value >= 5
        ? C.positive.withValues(alpha: 0.12)
        : value == 4
            ? C.warning.withValues(alpha: 0.10)
            : C.negative.withValues(alpha: 0.08);
    final textColor = value >= 5
        ? C.positive
        : value == 4
            ? C.warning
            : C.negative;

    return Container(
      width: 34,
      height: 32,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        border: Border.all(color: C.glassBorder, width: 0.5),
        color: bgColor,
      ),
      child: Text('$value',
          style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: textColor)),
    );
  }

  Widget _savLabelCell() {
    return Container(
      width: 40,
      height: 32,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        border: Border.all(color: C.glassBorder, width: 0.5),
        color: C.accent.withValues(alpha: 0.08),
      ),
      child: Text('SAV',
          style: T.caption.copyWith(
              fontSize: 9,
              fontWeight: FontWeight.w700,
              color: C.accent)),
    );
  }

  Widget _savCell(int value) {
    return Container(
      width: 34,
      height: 32,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        border: Border.all(color: C.glassBorder, width: 0.5),
        color: C.accent.withValues(alpha: 0.06),
      ),
      child: Text('$value',
          style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: C.accent)),
    );
  }

  Widget _buildEducationalCard() {
    return GlassContainer(
      padding: const EdgeInsets.all(S.lg),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.school_outlined,
                  size: 14, color: C.accent.withValues(alpha: 0.7)),
              const SizedBox(width: S.sm),
              Text('What is Ashtakavarga?',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary,
                      fontWeight: FontWeight.w600,
                      fontSize: 12)),
            ],
          ),
          const SizedBox(height: S.sm),
          Text(
            'Ashtakavarga is a unique Vedic system that assigns strength points '
            '(bindus) to each planet in each sign. Each planet receives 0-8 bindus '
            'based on contributions from all 7 planets plus the Ascendant.',
            style: T.caption.copyWith(fontSize: 11, height: 1.4),
          ),
          const SizedBox(height: S.sm),
          Text(
            'BAV (Bhinna Ashtakavarga) shows individual planet bindus per sign. '
            'SAV (Sarva Ashtakavarga) is the total across all planets. '
            'Signs with 5+ bindus are strong for that planet; 0-3 are weak.',
            style: T.caption.copyWith(fontSize: 11, height: 1.4),
          ),
          const SizedBox(height: S.sm),
          Row(
            children: [
              _legendDot(C.positive, '5-8 Strong'),
              const SizedBox(width: S.md),
              _legendDot(C.warning, '4 Neutral'),
              const SizedBox(width: S.md),
              _legendDot(C.negative, '0-3 Weak'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _legendDot(Color color, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withValues(alpha: 0.6),
          ),
        ),
        const SizedBox(width: 4),
        Text(label, style: T.caption.copyWith(fontSize: 10)),
      ],
    );
  }
}
