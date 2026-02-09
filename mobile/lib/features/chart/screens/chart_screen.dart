import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/features/chart/widgets/yoga_detail_panel.dart';
import 'package:one_zero_eight/features/chart/widgets/dosha_detail_panel.dart';
import 'package:one_zero_eight/features/chart/widgets/strength_detail_panel.dart';
import 'package:one_zero_eight/features/chart/widgets/soul_purpose_detail_panel.dart';

/// "Your Chart" screen — the WHO layer.
///
/// Shows personality, yogas, doshas, strength, soul purpose, and gems.
/// Completes the screen trio: WHO (Chart) / WHEN (Timeline) / NOW (Today Board).
class ChartScreen extends ConsumerStatefulWidget {
  const ChartScreen({super.key});

  @override
  ConsumerState<ChartScreen> createState() => _ChartScreenState();
}

class _ChartScreenState extends ConsumerState<ChartScreen> {
  Map<String, dynamic>? _chartData;
  List<dynamic>? _yogas;
  List<dynamic>? _doshas;
  List<dynamic>? _strength;
  Map<String, dynamic>? _atmakarakaData;
  Map<String, dynamic>? _gemsData;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchAll();
  }

  Future<void> _fetchAll() async {
    final futures = await Future.wait([
      _safeFetch(ApiConstants.chartSummary),
      _safeFetch(ApiConstants.analysisYogas),
      _safeFetch(ApiConstants.analysisDoshas),
      _safeFetch(ApiConstants.analysisStrength),
      _safeFetch(ApiConstants.analysisAtmakaraka),
      _safeFetch(ApiConstants.remediesGems),
    ]);

    if (mounted) {
      setState(() {
        _chartData = futures[0] ?? _demoChart;
        _yogas = (futures[1]?['yogas'] as List?) ?? _demoYogas;
        _doshas = (futures[2]?['doshas'] as List?) ?? _demoDoshas;
        _strength = (futures[3]?['planets'] as List?) ?? _demoStrength;
        _atmakarakaData = futures[4] ?? _demoAtmakaraka;
        _gemsData = futures[5] ?? _demoGems;
        _loading = false;
      });
    }
  }

  Future<Map<String, dynamic>?> _safeFetch(String url) async {
    try {
      return await ApiService()
          .get(url, fromJson: (json) => json as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: _loading
              ? const Center(
                  child: CircularProgressIndicator(
                      color: C.accent, strokeWidth: 2),
                )
              : _buildContent(),
        ),
      ),
    );
  }

  // ===============================================================
  // MAIN CONTENT
  // ===============================================================

  Widget _buildContent() {
    return SingleChildScrollView(
      padding: S.pagePadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: S.lg),
          _buildHeader(),
          const SizedBox(height: S.xl),
          _buildBirthChart(),
          const SizedBox(height: S.xl),
          _buildYogasSection(),
          const SizedBox(height: S.xl),
          _buildDoshasSection(),
          const SizedBox(height: S.xl),
          _buildStrengthSection(),
          const SizedBox(height: S.xl),
          _buildSoulPurposeSection(),
          const SizedBox(height: S.xl),
          _buildGemsSection(),
          const SizedBox(height: S.xl),
          // Continue button
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: () => context.push('/timeline'),
              child: const Text('Continue'),
            ),
          ),
          const SizedBox(height: S.xl),
        ],
      ),
    );
  }

  // ===============================================================
  // HEADER — centered like timeline
  // ===============================================================

  Widget _buildHeader() {
    final lagna = _chartData?['lagna_rashi'] as String? ?? 'Libra';
    final moonSign = _chartData?['moon_rashi'] as String? ?? 'Aquarius';

    return Center(
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              GestureDetector(
                onTap: () => context.go('/home'),
                child: const Padding(
                  padding: EdgeInsets.only(right: S.sm),
                  child: Icon(Icons.arrow_back_ios,
                      color: C.textSecondary, size: 18),
                ),
              ),
              const Text('Your Chart', style: T.h2),
            ],
          ),
          const SizedBox(height: S.sm),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _badge('Lagna: $lagna', C.accent),
              const SizedBox(width: S.sm),
              _badge('Moon: $moonSign', C.moon),
            ],
          ),
        ],
      ),
    );
  }

  Widget _badge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: R.xlBr,
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Text(
        text,
        style: T.caption.copyWith(
            color: color, fontWeight: FontWeight.w600, fontSize: 10),
      ),
    );
  }

  // ===============================================================
  // BIRTH CHART — South Indian style
  // ===============================================================

  Widget _buildBirthChart() {
    final planets = _chartData?['planets'] as Map<String, dynamic>? ??
        _demoChart['planets'] as Map<String, dynamic>;
    final lagnaRashi =
        (_chartData?['lagna_rashi'] as String? ?? 'Libra').toLowerCase();
    final lagnaSign = _rashiToSign(lagnaRashi);

    // Group planets by sign number
    final signPlanets = <int, List<String>>{};
    for (final entry in planets.entries) {
      final pData = entry.value as Map<String, dynamic>;
      final rashi = (pData['rashi'] as String? ?? '').toLowerCase();
      if (rashi.isNotEmpty) {
        final signNum = _rashiToSign(rashi);
        signPlanets.putIfAbsent(signNum, () => []).add(entry.key);
      }
    }

    // South Indian chart: fixed sign positions (row, col)
    const positions = <int, (int, int)>{
      12: (0, 0), 1: (0, 1), 2: (0, 2), 3: (0, 3),
      11: (1, 0), 4: (1, 3),
      10: (2, 0), 5: (2, 3),
      9: (3, 0), 8: (3, 1), 7: (3, 2), 6: (3, 3),
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionLabel('Birth Chart', 'South Indian'),
        const SizedBox(height: S.sm),
        LayoutBuilder(
          builder: (context, constraints) {
            final size = constraints.maxWidth;
            final cell = size / 4;
            return Container(
              width: size,
              height: size,
              decoration: BoxDecoration(
                borderRadius: R.lgBr,
                border: Border.all(color: C.glassBorder),
              ),
              clipBehavior: Clip.antiAlias,
              child: Stack(
                children: [
                  // 12 rashi cells
                  ...positions.entries.map((e) {
                    final sign = e.key;
                    final row = e.value.$1;
                    final col = e.value.$2;
                    return Positioned(
                      left: col * cell,
                      top: row * cell,
                      child: _chartCell(
                          sign, cell, lagnaSign, signPlanets),
                    );
                  }),
                  // Center area
                  Positioned(
                    left: cell,
                    top: cell,
                    child: _chartCenter(cell * 2, cell * 2, lagnaRashi),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _chartCell(int signNum, double size, int lagnaSign,
      Map<int, List<String>> signPlanets) {
    final houseNum = _signToHouse(signNum, lagnaSign);
    final isLagna = houseNum == 1;
    final planetsHere = signPlanets[signNum] ?? [];

    return GestureDetector(
      onTap: () => _showHouseInfo(signNum, houseNum, planetsHere),
      child: Container(
        width: size,
        height: size,
        decoration: BoxDecoration(
          border: Border.all(
            color: isLagna
                ? C.accent.withValues(alpha: 0.6)
                : C.glassBorder,
            width: isLagna ? 1.5 : 0.5,
          ),
          color: isLagna
              ? C.accent.withValues(alpha: 0.08)
              : planetsHere.isNotEmpty
                  ? Colors.white.withValues(alpha: 0.03)
                  : Colors.transparent,
        ),
        padding: const EdgeInsets.all(4),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Sign glyph + house number / ASC badge
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _signGlyphs[signNum] ?? '',
                  style: TextStyle(
                    fontSize: 10,
                    color: isLagna ? C.accent : C.textMuted,
                  ),
                ),
                if (isLagna)
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 3, vertical: 1),
                    decoration: BoxDecoration(
                      color: C.accent.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(3),
                    ),
                    child: const Text(
                      'ASC',
                      style: TextStyle(
                        fontSize: 7,
                        fontWeight: FontWeight.w700,
                        color: C.accent,
                        letterSpacing: 0.5,
                      ),
                    ),
                  )
                else
                  Text('$houseNum',
                      style: const TextStyle(
                          fontSize: 9, color: C.textMuted)),
              ],
            ),
            // Planet glyphs
            Expanded(
              child: Center(
                child: Wrap(
                  alignment: WrapAlignment.center,
                  spacing: 2,
                  runSpacing: 0,
                  children: planetsHere.map((p) {
                    final retro = _isPlanetRetro(p);
                    return Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(planetGlyph(p),
                            style: TextStyle(
                                fontSize: 16, color: planetColor(p))),
                        if (retro)
                          const Text('R',
                              style: TextStyle(
                                  fontSize: 6,
                                  color: C.warning,
                                  fontWeight: FontWeight.w700)),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _chartCenter(double width, double height, String lagnaRashi) {
    final display = lagnaRashi.isNotEmpty
        ? lagnaRashi[0].toUpperCase() + lagnaRashi.substring(1)
        : '';
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.4),
        border: Border.all(color: C.glassBorder, width: 0.5),
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.auto_awesome, color: C.textMuted, size: 20),
            const SizedBox(height: S.xs),
            const Text('Rashi Chart',
                style: TextStyle(
                    fontSize: 13,
                    color: C.textSecondary,
                    fontWeight: FontWeight.w600)),
            const SizedBox(height: 2),
            Text('Lagna: $display',
                style: const TextStyle(fontSize: 11, color: C.accent)),
          ],
        ),
      ),
    );
  }

  void _showHouseInfo(
      int signNum, int houseNum, List<String> planetsHere) {
    final signName = _signNames[signNum] ?? '';
    final lord = _signLords[signNum] ?? '';
    final lifeArea = _houseAreas[houseNum] ?? '';
    final lordColor = planetColor(lord);

    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (_) => Container(
        decoration: BoxDecoration(
          color: C.surface,
          borderRadius: const BorderRadius.vertical(
              top: Radius.circular(R.xl)),
        ),
        padding: const EdgeInsets.fromLTRB(S.lg, S.md, S.lg, S.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: C.glassBorder,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: S.md),
            Row(
              children: [
                Text('House $houseNum',
                    style: T.h2.copyWith(fontSize: 20)),
                const SizedBox(width: S.sm),
                _badge(signName, C.accent),
              ],
            ),
            const SizedBox(height: 4),
            Text(lifeArea,
                style: T.bodySm.copyWith(color: C.textSecondary)),
            const SizedBox(height: S.lg),
            // Lord card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(S.md),
              decoration: BoxDecoration(
                borderRadius: R.mdBr,
                color: lordColor.withValues(alpha: 0.06),
                border: Border.all(
                    color: lordColor.withValues(alpha: 0.15)),
              ),
              child: Row(
                children: [
                  Text(planetGlyph(lord),
                      style:
                          TextStyle(fontSize: 22, color: lordColor)),
                  const SizedBox(width: S.sm),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('House Lord',
                          style: T.caption
                              .copyWith(color: C.textMuted)),
                      Text(planetName(lord),
                          style: T.bodySm.copyWith(
                              color: lordColor,
                              fontWeight: FontWeight.w600)),
                    ],
                  ),
                ],
              ),
            ),
            if (planetsHere.isNotEmpty) ...[
              const SizedBox(height: S.md),
              Text('Planets Present',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary,
                      fontWeight: FontWeight.w600)),
              const SizedBox(height: S.sm),
              Wrap(
                spacing: S.sm,
                runSpacing: S.sm,
                children: planetsHere.map((p) {
                  final pc = planetColor(p);
                  final retro = _isPlanetRetro(p);
                  return Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: S.sm, vertical: 4),
                    decoration: BoxDecoration(
                      borderRadius: R.xlBr,
                      color: pc.withValues(alpha: 0.1),
                      border: Border.all(
                          color: pc.withValues(alpha: 0.2)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(planetGlyph(p),
                            style:
                                TextStyle(fontSize: 16, color: pc)),
                        const SizedBox(width: 4),
                        Text(
                          '${planetName(p)}${retro ? ' Rx' : ''}',
                          style: T.bodySm.copyWith(
                              color: pc,
                              fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ] else ...[
              const SizedBox(height: S.md),
              Text('No planets in this house',
                  style: T.caption.copyWith(color: C.textMuted)),
            ],
            const SizedBox(height: S.lg),
          ],
        ),
      ),
    );
  }

  bool _isPlanetRetro(String planet) {
    final planets = _chartData?['planets'] as Map<String, dynamic>? ??
        _demoChart['planets'] as Map<String, dynamic>;
    final data = planets[planet] as Map<String, dynamic>? ?? {};
    return data['is_retrograde'] == true;
  }

  // ===============================================================
  // YOGAS — category-colored cards
  // ===============================================================

  Widget _buildYogasSection() {
    final yogas = _yogas ?? [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionLabel('Yogas', '${yogas.length} detected'),
        const SizedBox(height: S.sm),
        SizedBox(
          height: 120,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: yogas.length,
            separatorBuilder: (_, __) => const SizedBox(width: S.sm),
            itemBuilder: (_, idx) {
              final yoga = yogas[idx] as Map<String, dynamic>;
              return _yogaCard(yoga);
            },
          ),
        ),
      ],
    );
  }

  Widget _yogaCard(Map<String, dynamic> yoga) {
    final name = yoga['name'] as String? ?? '';
    final category = (yoga['category'] as String? ?? '').toLowerCase();
    final color = _yogaCategoryColor(category);
    final involved = yoga['involved_planets'] as List? ?? [];

    return GestureDetector(
      onTap: () => YogaDetailPanel.show(context, yoga: yoga),
      child: Container(
        width: 150,
        padding: const EdgeInsets.all(S.md),
        decoration: BoxDecoration(
          borderRadius: R.lgBr,
          color: color.withValues(alpha: 0.08),
          border: Border.all(color: color.withValues(alpha: 0.25), width: 0.5),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: S.sm, vertical: 2),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.2),
                borderRadius: R.xlBr,
              ),
              child: Text(
                category.isNotEmpty
                    ? category[0].toUpperCase() + category.substring(1)
                    : 'Yoga',
                style: TextStyle(
                    fontSize: 9,
                    color: color,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5),
              ),
            ),
            const SizedBox(height: S.sm),
            Text(name,
                style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 13),
                maxLines: 2,
                overflow: TextOverflow.ellipsis),
            const Spacer(),
            if (involved.isNotEmpty)
              Row(
                children: involved.take(4).map((p) {
                  final pStr = p.toString().toLowerCase();
                  return Padding(
                    padding: const EdgeInsets.only(right: 3),
                    child: Text(planetGlyph(pStr),
                        style: TextStyle(
                            fontSize: 13, color: planetColor(pStr))),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  Color _yogaCategoryColor(String category) {
    switch (category) {
      case 'raja':
        return C.jupiter;
      case 'dhana':
        return const Color(0xFFFFD700);
      case 'pancha_mahapurusha':
        return C.mars;
      case 'nabhasa':
        return C.mercury;
      case 'chandra':
      case 'lunar':
        return C.moon;
      case 'solar':
        return C.sun;
      default:
        return C.accent;
    }
  }

  // ===============================================================
  // DOSHAS — severity-colored cards
  // ===============================================================

  Widget _buildDoshasSection() {
    final doshas = _doshas ?? [];
    if (doshas.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionLabel('Doshas', 'none'),
          const SizedBox(height: S.sm),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(S.lg),
            decoration: BoxDecoration(
              borderRadius: R.lgBr,
              color: C.positive.withValues(alpha: 0.06),
              border: Border.all(
                  color: C.positive.withValues(alpha: 0.15), width: 0.5),
            ),
            child: Text('No doshas detected',
                style: T.bodySm.copyWith(color: C.positive)),
          ),
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionLabel('Doshas', '${doshas.length} found'),
        const SizedBox(height: S.sm),
        SizedBox(
          height: 110,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: doshas.length,
            separatorBuilder: (_, __) => const SizedBox(width: S.sm),
            itemBuilder: (_, idx) {
              final dosha = doshas[idx] as Map<String, dynamic>;
              return _doshaCard(dosha);
            },
          ),
        ),
      ],
    );
  }

  Widget _doshaCard(Map<String, dynamic> dosha) {
    final name = dosha['name'] as String? ?? '';
    final severity = (dosha['severity'] as String? ?? 'mild').toLowerCase();
    final remedies = dosha['remedies'] as List? ?? [];
    final color = severity == 'severe'
        ? C.negative
        : severity == 'moderate'
            ? C.warning
            : C.positive;

    return GestureDetector(
      onTap: () => DoshaDetailPanel.show(context, dosha: dosha),
      child: Container(
        width: 150,
        padding: const EdgeInsets.all(S.md),
        decoration: BoxDecoration(
          borderRadius: R.lgBr,
          color: color.withValues(alpha: 0.08),
          border: Border.all(color: color.withValues(alpha: 0.25), width: 0.5),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: S.sm, vertical: 2),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.2),
                borderRadius: R.xlBr,
              ),
              child: Text(
                severity[0].toUpperCase() + severity.substring(1),
                style: TextStyle(
                    fontSize: 9,
                    color: color,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5),
              ),
            ),
            const SizedBox(height: S.sm),
            Text(name,
                style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 13),
                maxLines: 2,
                overflow: TextOverflow.ellipsis),
            const Spacer(),
            if (remedies.isNotEmpty)
              Text('${remedies.length} remedies',
                  style: T.caption.copyWith(color: color, fontSize: 10)),
          ],
        ),
      ),
    );
  }

  // ===============================================================
  // STRENGTH — planet-colored cards with bars
  // ===============================================================

  Widget _buildStrengthSection() {
    final planets = _strength ?? [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionLabel('Strength', 'Shadbala'),
        const SizedBox(height: S.sm),
        SizedBox(
          height: 110,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: planets.length,
            separatorBuilder: (_, __) => const SizedBox(width: S.sm),
            itemBuilder: (_, idx) {
              final p = planets[idx] as Map<String, dynamic>;
              return _strengthCard(p);
            },
          ),
        ),
      ],
    );
  }

  Widget _strengthCard(Map<String, dynamic> data) {
    final name = data['planet'] as String? ?? '';
    final grade = (data['grade'] as String? ?? 'average').toLowerCase();
    final total = (data['total_shadbala'] as num?)?.toDouble() ?? 0.5;
    final color = planetColor(name);
    final gradeColor = grade == 'very_strong' || grade == 'strong'
        ? C.positive
        : grade == 'average'
            ? C.warning
            : C.negative;
    final barWidth = (total / 2.0).clamp(0.0, 1.0);

    return GestureDetector(
      onTap: () => StrengthDetailPanel.show(context, data: data),
      child: Container(
        width: 90,
        padding: const EdgeInsets.symmetric(vertical: S.sm, horizontal: S.xs),
        decoration: BoxDecoration(
          borderRadius: R.lgBr,
          color: color.withValues(alpha: 0.06),
          border: Border.all(color: color.withValues(alpha: 0.2), width: 0.5),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(planetGlyph(name),
                style: TextStyle(fontSize: 18, color: color)),
            const SizedBox(height: 2),
            Text(planetName(name),
                style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w600,
                    fontSize: 12)),
            const SizedBox(height: S.sm),
            // Strength bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: S.xs),
              child: ClipRRect(
                borderRadius: R.smBr,
                child: SizedBox(
                  height: 4,
                  child: LinearProgressIndicator(
                    value: barWidth,
                    backgroundColor: C.glassBorder,
                    valueColor: AlwaysStoppedAnimation<Color>(color),
                  ),
                ),
              ),
            ),
            const SizedBox(height: S.xs),
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: S.sm, vertical: 1),
              decoration: BoxDecoration(
                color: gradeColor.withValues(alpha: 0.15),
                borderRadius: R.xlBr,
              ),
              child: Text(
                grade.replaceAll('_', ' ').toUpperCase(),
                style: TextStyle(
                    fontSize: 8,
                    color: gradeColor,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.5),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ===============================================================
  // SOUL PURPOSE — AK planet-colored card
  // ===============================================================

  Widget _buildSoulPurposeSection() {
    final ak =
        _atmakarakaData?['atmakaraka'] as Map<String, dynamic>? ?? {};
    final akPlanet = ak['planet'] as String? ?? '';
    final ishta =
        _atmakarakaData?['ishta_devata'] as Map<String, dynamic>?;
    final meaning = ak['soul_purpose'] as String? ??
        ak['meaning'] as String? ??
        'Discover your soul\'s deeper purpose';
    final color = planetColor(akPlanet);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionLabel('Soul Purpose', 'Atmakaraka'),
        const SizedBox(height: S.sm),
        GestureDetector(
          onTap: () => SoulPurposeDetailPanel.show(context,
              data: _atmakarakaData ?? {}),
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.all(S.lg),
            decoration: BoxDecoration(
              borderRadius: R.lgBr,
              color: color.withValues(alpha: 0.08),
              border:
                  Border.all(color: color.withValues(alpha: 0.25), width: 0.5),
            ),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: color.withValues(alpha: 0.15),
                    border:
                        Border.all(color: color.withValues(alpha: 0.4)),
                  ),
                  child: Center(
                    child: Text(
                      planetGlyph(akPlanet),
                      style: TextStyle(fontSize: 22, color: color),
                    ),
                  ),
                ),
                const SizedBox(width: S.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Atmakaraka: ${planetName(akPlanet)}',
                        style: T.bodySm.copyWith(
                            color: C.textPrimary,
                            fontWeight: FontWeight.w600),
                      ),
                      if (ishta != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          'Ishta Devata: ${ishta['deity'] ?? ''}',
                          style: T.caption.copyWith(
                              color: color, fontSize: 10),
                        ),
                      ],
                      const SizedBox(height: S.xs),
                      Text(
                        meaning,
                        style: T.caption,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Icon(Icons.chevron_right,
                    color: color.withValues(alpha: 0.5), size: 20),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // ===============================================================
  // GEMS & REMEDIES — planet-colored cards
  // ===============================================================

  Widget _buildGemsSection() {
    final gems =
        _gemsData?['recommendations'] as List? ?? _demoGemsList;
    if (gems.isEmpty) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionLabel('Gems & Remedies', 'none'),
          const SizedBox(height: S.sm),
          GlassContainer(
            blur: 0,
            padding: const EdgeInsets.all(S.lg),
            child: Text('No gem recommendations', style: T.bodySm),
          ),
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionLabel('Gems & Remedies', '${gems.length} recommended'),
        const SizedBox(height: S.sm),
        SizedBox(
          height: 100,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: gems.length,
            separatorBuilder: (_, __) => const SizedBox(width: S.sm),
            itemBuilder: (_, idx) {
              final gem = gems[idx] as Map<String, dynamic>;
              return _gemCard(gem);
            },
          ),
        ),
      ],
    );
  }

  Widget _gemCard(Map<String, dynamic> gem) {
    final name = gem['gem'] as String? ?? gem['name'] as String? ?? '';
    final planet = gem['planet'] as String? ?? '';
    final finger = gem['finger'] as String? ?? '';
    final color = planetColor(planet);

    return Container(
      width: 130,
      padding: const EdgeInsets.all(S.md),
      decoration: BoxDecoration(
        borderRadius: R.lgBr,
        color: color.withValues(alpha: 0.06),
        border: Border.all(color: color.withValues(alpha: 0.2), width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Text(planetGlyph(planet),
                  style: TextStyle(fontSize: 16, color: color)),
              const SizedBox(width: S.xs),
              Expanded(
                child: Text(name,
                    style: T.bodySm.copyWith(
                        color: C.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 12),
                    overflow: TextOverflow.ellipsis),
              ),
            ],
          ),
          const Spacer(),
          Text(planetName(planet),
              style: T.caption.copyWith(color: color, fontSize: 10)),
          if (finger.isNotEmpty)
            Text('Wear on $finger',
                style: T.caption.copyWith(fontSize: 9)),
        ],
      ),
    );
  }

  // ===============================================================
  // HELPERS
  // ===============================================================

  /// Section label matching timeline/transit _SectionLabel pattern.
  Widget _sectionLabel(String title, String subtitle) {
    return Row(
      children: [
        Text(title, style: T.h3.copyWith(fontSize: 16)),
        const SizedBox(width: S.sm),
        Text(subtitle, style: T.caption),
      ],
    );
  }
}

// =================================================================
// DEMO DATA (offline fallback)
// =================================================================

const Map<String, dynamic> _demoChart = {
  'lagna_rashi': 'Libra',
  'moon_rashi': 'Aquarius',
  'moon_nakshatra': 'Purva Bhadrapada',
  'planets': {
    'sun': {'rashi': 'scorpio', 'house': 2, 'is_retrograde': false},
    'moon': {'rashi': 'aquarius', 'house': 5, 'is_retrograde': false},
    'mars': {'rashi': 'cancer', 'house': 10, 'is_retrograde': true},
    'mercury': {'rashi': 'sagittarius', 'house': 3, 'is_retrograde': false},
    'jupiter': {'rashi': 'virgo', 'house': 12, 'is_retrograde': false},
    'venus': {'rashi': 'sagittarius', 'house': 3, 'is_retrograde': false},
    'saturn': {'rashi': 'capricorn', 'house': 4, 'is_retrograde': true},
    'rahu': {'rashi': 'sagittarius', 'house': 3, 'is_retrograde': true},
    'ketu': {'rashi': 'gemini', 'house': 9, 'is_retrograde': true},
  },
};

const List<Map<String, dynamic>> _demoYogas = [
  {
    'name': 'Gajakesari Yoga',
    'category': 'raja',
    'involved_planets': ['moon', 'jupiter'],
    'description':
        'Moon and Jupiter in mutual kendras \u2014 wisdom, fame, fortune.',
  },
  {
    'name': 'Budhaditya Yoga',
    'category': 'raja',
    'involved_planets': ['sun', 'mercury'],
    'description':
        'Sun-Mercury conjunction \u2014 intelligence and communication skills.',
  },
  {
    'name': 'Neecha Bhanga Raja Yoga',
    'category': 'raja',
    'involved_planets': ['mars'],
    'description':
        'Debilitated Mars retrograde \u2014 cancellation elevates to raja yoga.',
  },
  {
    'name': 'Sasa Yoga',
    'category': 'pancha_mahapurusha',
    'involved_planets': ['saturn'],
    'description':
        'Saturn in own sign in kendra \u2014 authority, discipline, leadership.',
  },
];

const List<Map<String, dynamic>> _demoDoshas = [
  {
    'name': 'Mangal Dosha',
    'severity': 'moderate',
    'is_present': true,
    'involved_planets': ['mars'],
    'description': 'Mars in 10th house affects career and partnerships.',
    'remedies': ['Hanuman Chalisa recitation', 'Red coral gemstone'],
  },
];

const List<Map<String, dynamic>> _demoStrength = [
  {'planet': 'sun', 'total_shadbala': 1.15, 'grade': 'strong'},
  {'planet': 'moon', 'total_shadbala': 0.95, 'grade': 'average'},
  {'planet': 'mars', 'total_shadbala': 0.8, 'grade': 'average'},
  {'planet': 'mercury', 'total_shadbala': 1.35, 'grade': 'strong'},
  {'planet': 'jupiter', 'total_shadbala': 1.1, 'grade': 'strong'},
  {'planet': 'venus', 'total_shadbala': 1.25, 'grade': 'strong'},
  {'planet': 'saturn', 'total_shadbala': 0.7, 'grade': 'weak'},
  {'planet': 'rahu', 'total_shadbala': 0.6, 'grade': 'weak'},
  {'planet': 'ketu', 'total_shadbala': 0.55, 'grade': 'weak'},
];

const Map<String, dynamic> _demoAtmakaraka = {
  'atmakaraka': {
    'planet': 'venus',
    'sign': 'gemini',
    'degree': 28.5,
    'meaning': 'Soul seeks love, beauty, harmony and creative expression.',
    'soul_purpose': 'Learning to balance desires with spiritual growth.',
  },
  'ishta_devata': {
    'deity': 'Lakshmi',
    'sign': 'taurus',
    'worship': 'Friday worship, white flowers, Sri Suktam.',
  },
  'chara_karakas': [
    {'karaka': 'AK', 'planet': 'venus', 'degree': 28.5},
    {'karaka': 'AmK', 'planet': 'saturn', 'degree': 27.1},
    {'karaka': 'BK', 'planet': 'mars', 'degree': 25.8},
    {'karaka': 'MK', 'planet': 'jupiter', 'degree': 22.3},
    {'karaka': 'PK', 'planet': 'sun', 'degree': 18.9},
    {'karaka': 'GK', 'planet': 'mercury', 'degree': 15.4},
    {'karaka': 'DK', 'planet': 'moon', 'degree': 12.1},
  ],
};

const Map<String, dynamic> _demoGems = {
  'recommendations': [
    {'gem': 'Diamond', 'planet': 'venus', 'finger': 'ring finger'},
    {'gem': 'Emerald', 'planet': 'mercury', 'finger': 'little finger'},
    {
      'gem': 'Yellow Sapphire',
      'planet': 'jupiter',
      'finger': 'index finger'
    },
  ],
};

const List<Map<String, dynamic>> _demoGemsList = [
  {'gem': 'Diamond', 'planet': 'venus', 'finger': 'ring finger'},
  {'gem': 'Emerald', 'planet': 'mercury', 'finger': 'little finger'},
];

// =================================================================
// CHART CONSTANTS
// =================================================================

int _rashiToSign(String rashi) {
  const map = {
    'aries': 1, 'taurus': 2, 'gemini': 3, 'cancer': 4,
    'leo': 5, 'virgo': 6, 'libra': 7, 'scorpio': 8,
    'sagittarius': 9, 'capricorn': 10, 'aquarius': 11, 'pisces': 12,
  };
  return map[rashi.toLowerCase()] ?? 1;
}

int _signToHouse(int sign, int lagna) => ((sign - lagna) % 12) + 1;

const _signGlyphs = <int, String>{
  1: '\u2648', 2: '\u2649', 3: '\u264A', 4: '\u264B',
  5: '\u264C', 6: '\u264D', 7: '\u264E', 8: '\u264F',
  9: '\u2650', 10: '\u2651', 11: '\u2652', 12: '\u2653',
};

const _signNames = <int, String>{
  1: 'Aries', 2: 'Taurus', 3: 'Gemini', 4: 'Cancer',
  5: 'Leo', 6: 'Virgo', 7: 'Libra', 8: 'Scorpio',
  9: 'Sagittarius', 10: 'Capricorn', 11: 'Aquarius', 12: 'Pisces',
};

const _signLords = <int, String>{
  1: 'mars', 2: 'venus', 3: 'mercury', 4: 'moon',
  5: 'sun', 6: 'mercury', 7: 'venus', 8: 'mars',
  9: 'jupiter', 10: 'saturn', 11: 'saturn', 12: 'jupiter',
};

const _houseAreas = <int, String>{
  1: 'Self & Personality',
  2: 'Wealth & Family',
  3: 'Siblings & Courage',
  4: 'Home & Mother',
  5: 'Children & Creativity',
  6: 'Health & Enemies',
  7: 'Marriage & Partners',
  8: 'Transformation & Longevity',
  9: 'Fortune & Dharma',
  10: 'Career & Status',
  11: 'Gains & Friends',
  12: 'Spirituality & Liberation',
};
