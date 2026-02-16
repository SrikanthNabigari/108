import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/data/services/knowledge_service.dart';
import 'package:one_zero_eight/features/chart/widgets/nakshatra_info_panel.dart';
import 'package:one_zero_eight/features/chart/widgets/planet_info_panel.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Comprehensive Vedic Astrology guide — the full system explained.
class LearnScreen extends StatelessWidget {
  const LearnScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          bottom: false,
          child: Column(
            children: [
              // App bar
              Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.lg, vertical: S.sm),
                child: Row(
                  children: [
                    GestureDetector(
                      onTap: () => context.canPop()
                          ? context.pop()
                          : context.go('/home'),
                      child: const Icon(Icons.arrow_back_ios,
                          color: C.textSecondary, size: 18),
                    ),
                    const SizedBox(width: S.sm),
                    Text('Vedic Astrology', style: T.h3),
                  ],
                ),
              ),
              const Divider(height: 1),

              // Content
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.lg, vertical: S.md),
                  children: [
                    _buildHeroBanner(),
                    const SizedBox(height: S.xl),
                    _buildArchitectureBanner(),
                    const SizedBox(height: S.xl),
                    const _ExpandableSection(
                      title: 'The 9 Planets (Grahas)',
                      subtitle: '7 physical + 2 shadow nodes',
                      icon: Icons.brightness_7,
                      accentColor: C.sun,
                      child: _PlanetsSection(),
                    ),
                    const SizedBox(height: S.md),
                    const _ExpandableSection(
                      title: 'The 12 Houses (Bhavas)',
                      subtitle: 'Where in life things happen',
                      icon: Icons.grid_view_rounded,
                      accentColor: C.jupiter,
                      child: _HousesSection(),
                    ),
                    const SizedBox(height: S.md),
                    const _ExpandableSection(
                      title: '27 Nakshatras',
                      subtitle: 'Lunar mansions add personality',
                      icon: Icons.star_outline,
                      accentColor: C.moon,
                      child: _NakshatrasSection(),
                    ),
                    const SizedBox(height: S.md),
                    const _ExpandableSection(
                      title: 'Yogas (522 Combinations)',
                      subtitle: 'Planetary patterns that shape destiny',
                      icon: Icons.auto_awesome,
                      accentColor: C.venus,
                      child: _YogasSection(),
                    ),
                    const SizedBox(height: S.md),
                    const _ExpandableSection(
                      title: 'Doshas (55 Afflictions)',
                      subtitle: 'Challenges and karmic patterns',
                      icon: Icons.warning_amber_rounded,
                      accentColor: C.mars,
                      child: _DoshasSection(),
                    ),
                    const SizedBox(height: S.md),
                    const _ExpandableSection(
                      title: 'The Dasha System',
                      subtitle: 'How timing creates life chapters',
                      icon: Icons.timeline,
                      accentColor: C.saturn,
                      child: _DashaSection(),
                    ),
                    const SizedBox(height: S.md),
                    const _ExpandableSection(
                      title: 'Transits (Gochara)',
                      subtitle: 'What is happening RIGHT NOW',
                      icon: Icons.motion_photos_on,
                      accentColor: C.mercury,
                      child: _TransitsSection(),
                    ),
                    const SizedBox(height: S.md),
                    const _ExpandableSection(
                      title: 'Planetary Strength',
                      subtitle: 'Shadbala, Ashtakavarga, Vimshopaka',
                      icon: Icons.fitness_center,
                      accentColor: C.accent,
                      child: _StrengthSection(),
                    ),
                    const SizedBox(height: S.md),
                    const _ExpandableSection(
                      title: 'How a Reading Works',
                      subtitle: 'From question to answer in 5 steps',
                      icon: Icons.route,
                      accentColor: C.ketu,
                      child: _DataFlowSection(),
                    ),
                    const SizedBox(height: S.xxxl),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeroBanner() {
    return GlassContainer(
      padding: const EdgeInsets.all(S.xl),
      borderColor: C.accent.withValues(alpha: 0.3),
      child: Column(
        children: [
          Text(
            'The Complete System',
            style: T.h2.copyWith(color: C.accent),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: S.sm),
          Text(
            'Jyotish answers three questions about your life:',
            style: T.bodySm.copyWith(color: C.textSecondary),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: S.lg),
          Row(
            children: [
              _QuestionChip(label: 'WHAT', desc: 'will happen', color: C.venus),
              const SizedBox(width: S.sm),
              _QuestionChip(label: 'WHEN', desc: 'will it happen', color: C.saturn),
              const SizedBox(width: S.sm),
              _QuestionChip(label: 'WHY', desc: 'is it happening', color: C.jupiter),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildArchitectureBanner() {
    const layers = [
      ('GUIDE', 'AI that synthesizes all layers', C.accent),
      ('CONTEXT', 'WHEN: Dashas, Transits, Muhurta', C.saturn),
      ('SELF', 'WHAT: Yogas, Doshas, Strength', C.venus),
      ('COSMOS', 'Raw astronomy: planets, houses', C.sun),
      ('KNOWLEDGE', '522 yogas, 55 doshas, 729 effects', C.mercury),
    ];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('5-LAYER ARCHITECTURE',
            style: T.label
                .copyWith(color: C.textMuted, letterSpacing: 1.2)),
        const SizedBox(height: S.sm),
        ...layers.map((l) => Container(
              margin: const EdgeInsets.only(bottom: 2),
              padding:
                  const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
              decoration: BoxDecoration(
                color: l.$3.withValues(alpha: 0.06),
                border: Border(
                  left: BorderSide(color: l.$3, width: 3),
                ),
              ),
              child: Row(
                children: [
                  SizedBox(
                    width: 72,
                    child: Text(l.$1,
                        style: T.bodySm
                            .copyWith(color: l.$3, fontWeight: FontWeight.w700)),
                  ),
                  Expanded(
                    child: Text(l.$2,
                        style:
                            T.bodySm.copyWith(color: C.textSecondary, fontSize: 12)),
                  ),
                ],
              ),
            )),
      ],
    );
  }
}

// ── Question chip ──

class _QuestionChip extends StatelessWidget {
  final String label;
  final String desc;
  final Color color;
  const _QuestionChip(
      {required this.label, required this.desc, required this.color});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: S.md),
        decoration: BoxDecoration(
          borderRadius: R.mdBr,
          color: color.withValues(alpha: 0.08),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Column(
          children: [
            Text(label,
                style: T.label.copyWith(
                    color: color, fontWeight: FontWeight.w700, fontSize: 13)),
            const SizedBox(height: 2),
            Text(desc,
                style: T.caption.copyWith(color: C.textMuted, fontSize: 10)),
          ],
        ),
      ),
    );
  }
}

// ── Expandable Section ──

class _ExpandableSection extends StatefulWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color accentColor;
  final Widget child;

  const _ExpandableSection({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.accentColor,
    required this.child,
  });

  @override
  State<_ExpandableSection> createState() => _ExpandableSectionState();
}

class _ExpandableSectionState extends State<_ExpandableSection>
    with SingleTickerProviderStateMixin {
  bool _expanded = false;
  late final AnimationController _controller;
  late final Animation<double> _expandAnimation;
  late final Animation<double> _rotateAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _expandAnimation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    );
    _rotateAnimation = Tween<double>(begin: 0, end: 0.5).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _toggle() {
    setState(() => _expanded = !_expanded);
    _expanded ? _controller.forward() : _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return GlassContainer(
      padding: EdgeInsets.zero,
      borderColor: _expanded
          ? widget.accentColor.withValues(alpha: 0.3)
          : C.glassBorder,
      child: Column(
        children: [
          // Header
          GestureDetector(
            onTap: _toggle,
            behavior: HitTestBehavior.opaque,
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.lg),
              decoration: BoxDecoration(
                gradient: _expanded
                    ? LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          widget.accentColor.withValues(alpha: 0.08),
                          Colors.transparent,
                        ],
                      )
                    : null,
              ),
              child: Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: widget.accentColor.withValues(alpha: 0.12),
                    ),
                    child: Icon(widget.icon,
                        color: widget.accentColor, size: 18),
                  ),
                  const SizedBox(width: S.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(widget.title,
                            style: T.bodySm.copyWith(
                                color: C.textPrimary,
                                fontWeight: FontWeight.w600)),
                        Text(widget.subtitle,
                            style: T.caption.copyWith(
                                color: C.textMuted, fontSize: 11)),
                      ],
                    ),
                  ),
                  RotationTransition(
                    turns: _rotateAnimation,
                    child: Icon(Icons.expand_more,
                        color: C.textMuted, size: 20),
                  ),
                ],
              ),
            ),
          ),
          // Content
          SizeTransition(
            sizeFactor: _expandAnimation,
            child: Padding(
              padding: const EdgeInsets.fromLTRB(S.lg, 0, S.lg, S.lg),
              child: widget.child,
            ),
          ),
        ],
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════
// SECTION 1: The 9 Planets
// ════════════════════════════════════════════════════════════════

class _PlanetsSection extends StatefulWidget {
  const _PlanetsSection();

  @override
  State<_PlanetsSection> createState() => _PlanetsSectionState();
}

class _PlanetsSectionState extends State<_PlanetsSection> {
  List<Map<String, dynamic>>? _planets;

  static const _order = [
    'sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu'
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final all = await KnowledgeService.instance.getAllPlanets();
    // Sort by canonical order
    final sorted = <Map<String, dynamic>>[];
    for (final id in _order) {
      final p = all.where((e) => e['id'] == id).firstOrNull;
      if (p != null) sorted.add(p);
    }
    if (mounted) setState(() => _planets = sorted);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: C.glassBorder, height: 1),
        const SizedBox(height: S.lg),
        Text(
          'Each planet rules signs, represents life areas (karakas), and '
          'produces different results based on house placement and dignity.',
          style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
        ),
        const SizedBox(height: S.lg),
        if (_planets == null)
          const Center(child: CircularProgressIndicator(strokeWidth: 2))
        else
          ..._planets!.map((p) => _buildPlanetCard(context, p)),
        const SizedBox(height: S.md),
        _InfoBox(
          color: C.rahu,
          text: 'Rahu and Ketu are always exactly 180 degrees apart. '
              'They represent the karmic axis — what you are compulsively '
              'drawn toward (Rahu) vs what you have already mastered (Ketu).',
        ),
      ],
    );
  }

  Widget _buildPlanetCard(BuildContext context, Map<String, dynamic> p) {
    final id = p['id'] as String;
    final color = planetColor(id);
    final sanskrit = p['sanskrit'] as String? ?? '';
    final nature = p['nature'] as String? ?? '';
    final owns = (p['owns_signs'] as List?)?.join(', ') ?? '';
    final gem = p['gem'] as String? ?? '';
    final karakas = (p['karaka_of'] as List?)?.take(4).join(', ') ?? '';
    final exalted = p['exalted_in'] as String? ?? '';
    final debilitated = p['debilitated_in'] as String? ?? '';

    return GestureDetector(
      onTap: () => PlanetInfoPanel.show(context, planetId: id),
      child: Container(
        margin: const EdgeInsets.only(bottom: S.sm),
        padding: const EdgeInsets.all(S.md),
        decoration: BoxDecoration(
          borderRadius: R.mdBr,
          color: color.withValues(alpha: 0.04),
          border: Border.all(color: color.withValues(alpha: 0.15)),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(planetGlyph(id),
                style: TextStyle(fontSize: 24, color: color)),
            const SizedBox(width: S.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(planetName(id),
                          style: T.bodySm.copyWith(
                              color: color, fontWeight: FontWeight.w600)),
                      const SizedBox(width: S.xs),
                      Text(sanskrit,
                          style: T.caption
                              .copyWith(color: C.textMuted, fontSize: 10)),
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 1),
                        decoration: BoxDecoration(
                          borderRadius: R.smBr,
                          color: nature == 'benefic'
                              ? C.positive.withValues(alpha: 0.12)
                              : C.negative.withValues(alpha: 0.12),
                        ),
                        child: Text(nature,
                            style: T.caption.copyWith(
                                fontSize: 9,
                                color: nature == 'benefic'
                                    ? C.positive
                                    : C.negative)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  if (owns.isNotEmpty)
                    Text('Rules $owns',
                        style: T.caption
                            .copyWith(color: C.textSecondary, fontSize: 11)),
                  if (karakas.isNotEmpty)
                    Text(karakas,
                        style: T.caption.copyWith(
                            color: C.textMuted, fontSize: 11, height: 1.3)),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      if (gem.isNotEmpty) ...[
                        Icon(Icons.diamond_outlined,
                            size: 10, color: color.withValues(alpha: 0.6)),
                        const SizedBox(width: 2),
                        Text(gem,
                            style: T.caption
                                .copyWith(color: color, fontSize: 10)),
                        const SizedBox(width: S.md),
                      ],
                      if (exalted.isNotEmpty)
                        Text('Ex: $exalted',
                            style: T.caption.copyWith(
                                color: C.positive, fontSize: 10)),
                      if (exalted.isNotEmpty && debilitated.isNotEmpty)
                        const SizedBox(width: S.sm),
                      if (debilitated.isNotEmpty)
                        Text('Db: $debilitated',
                            style: T.caption.copyWith(
                                color: C.negative, fontSize: 10)),
                      const Spacer(),
                      Icon(Icons.chevron_right,
                          size: 14, color: C.textMuted.withValues(alpha: 0.5)),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════
// SECTION 2: The 12 Houses
// ════════════════════════════════════════════════════════════════

class _HousesSection extends StatefulWidget {
  const _HousesSection();

  @override
  State<_HousesSection> createState() => _HousesSectionState();
}

class _HousesSectionState extends State<_HousesSection> {
  List<Map<String, dynamic>>? _houses;

  static const _categories = [
    ('Kendra', '1, 4, 7, 10', 'Pillars of life (strongest)', C.jupiter),
    ('Trikona', '1, 5, 9', 'Fortune and dharma (most benefic)', C.venus),
    ('Dusthana', '6, 8, 12', 'Suffering and challenges', C.mars),
    ('Upachaya', '3, 6, 10, 11', 'Growth through effort', C.saturn),
    ('Maraka', '2, 7', 'Death-inflicting houses', C.ketu),
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final all = await KnowledgeService.instance.getAllHouses();
    if (mounted) setState(() => _houses = all);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: C.glassBorder, height: 1),
        const SizedBox(height: S.lg),
        Text(
          'Houses represent WHERE in life events happen. They start from your '
          'Lagna (Ascendant sign) and proceed counter-clockwise.',
          style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
        ),
        const SizedBox(height: S.lg),
        if (_houses == null)
          const Center(child: CircularProgressIndicator(strokeWidth: 2))
        else
          ..._houses!.map(_buildHouseRow),
        const SizedBox(height: S.xl),
        // Categories
        Text('HOUSE CATEGORIES',
            style:
                T.label.copyWith(color: C.textMuted, letterSpacing: 1.2)),
        const SizedBox(height: S.sm),
        ..._categories.map((c) => Container(
              margin: const EdgeInsets.only(bottom: S.xs),
              padding: const EdgeInsets.symmetric(
                  horizontal: S.md, vertical: S.sm),
              decoration: BoxDecoration(
                borderRadius: R.smBr,
                color: c.$4.withValues(alpha: 0.06),
                border: Border(
                    left: BorderSide(color: c.$4, width: 3)),
              ),
              child: Row(
                children: [
                  SizedBox(
                    width: 72,
                    child: Text(c.$1,
                        style: T.bodySm.copyWith(
                            color: c.$4, fontWeight: FontWeight.w600, fontSize: 12)),
                  ),
                  SizedBox(
                    width: 72,
                    child: Text(c.$2,
                        style: T.caption
                            .copyWith(color: C.textSecondary, fontSize: 11)),
                  ),
                  Expanded(
                    child: Text(c.$3,
                        style: T.caption
                            .copyWith(color: C.textMuted, fontSize: 11)),
                  ),
                ],
              ),
            )),
      ],
    );
  }

  static String _ordinal(int n) {
    if (n == 1) return '1st';
    if (n == 2) return '2nd';
    if (n == 3) return '3rd';
    return '${n}th';
  }

  Widget _buildHouseRow(Map<String, dynamic> h) {
    final num = h['number'] as int? ?? 0;
    final name = h['name'] as String? ?? '';
    final sanskrit = h['sanskrit'] as String? ?? '';
    final sigs = (h['significations'] as List?)?.take(4).join(', ') ?? '';
    final bodyParts = (h['body_parts'] as List?)?.join(', ') ?? '';
    final karakaStr = h['karaka'] as String? ?? '';
    // karaka may be comma-separated (e.g. "mars,saturn")
    final primaryKaraka = karakaStr.split(',').first.trim();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
      decoration: BoxDecoration(
        border: Border(
            bottom: BorderSide(color: C.glassBorder, width: 0.5)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              SizedBox(
                width: 36,
                child: Text(_ordinal(num),
                    style: T.bodySm.copyWith(
                        color: C.accent,
                        fontWeight: FontWeight.w600,
                        fontSize: 12)),
              ),
              SizedBox(
                width: 56,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(name,
                        style: T.bodySm.copyWith(
                            color: C.textPrimary, fontSize: 11)),
                    Text(sanskrit,
                        style: T.caption.copyWith(
                            color: C.textMuted, fontSize: 9)),
                  ],
                ),
              ),
              if (primaryKaraka.isNotEmpty) ...[
                Text(planetGlyph(primaryKaraka),
                    style: TextStyle(
                        fontSize: 12,
                        color: planetColor(primaryKaraka))),
                const SizedBox(width: S.xs),
              ],
              Expanded(
                child: Text(sigs,
                    style: T.bodySm.copyWith(
                        color: C.textPrimary, fontSize: 11)),
              ),
            ],
          ),
          if (bodyParts.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(left: 36, top: 2),
              child: Text('Body: $bodyParts',
                  style: T.caption.copyWith(
                      color: C.textMuted, fontSize: 9)),
            ),
        ],
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════
// SECTION 3: 27 Nakshatras
// ════════════════════════════════════════════════════════════════

class _NakshatrasSection extends StatefulWidget {
  const _NakshatrasSection();

  @override
  State<_NakshatrasSection> createState() => _NakshatrasSectionState();
}

class _NakshatrasSectionState extends State<_NakshatrasSection> {
  List<Map<String, dynamic>>? _nakshatras;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final all = await KnowledgeService.instance.getAllNakshatras();
    if (mounted) setState(() => _nakshatras = all);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: C.glassBorder, height: 1),
        const SizedBox(height: S.lg),
        Text(
          'Each zodiac sign (30 degrees) contains 2.25 nakshatras (13 degrees 20 minutes each). '
          'Nakshatras add the personality layer — signs tell you WHAT, nakshatras tell you HOW.',
          style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
        ),
        const SizedBox(height: S.lg),
        Text('ALL 27 NAKSHATRAS',
            style:
                T.label.copyWith(color: C.textMuted, letterSpacing: 1.2)),
        const SizedBox(height: S.sm),
        if (_nakshatras == null)
          const Center(child: CircularProgressIndicator(strokeWidth: 2))
        else
          ..._nakshatras!.map((n) => _buildNakshatraRow(context, n)),
        const SizedBox(height: S.md),
        _InfoBox(
          color: C.moon,
          text: 'Your Moon nakshatra determines your Vimshottari Dasha sequence. '
              'The 120-year cycle begins from the lord of the nakshatra '
              'occupied by the Moon at birth.',
        ),
      ],
    );
  }

  Widget _buildNakshatraRow(BuildContext context, Map<String, dynamic> n) {
    final id = n['id'] as String? ?? '';
    final name = n['name'] as String? ?? '';
    final num = n['number'] as int? ?? 0;
    final ruler = n['ruler'] as String? ?? '';
    final deity = n['deity'] as String? ?? '';
    final symbol = n['symbol'] as String? ?? '';
    final shakti = n['shakti'] as String? ?? '';
    final rulerColor = planetColor(ruler);

    return GestureDetector(
      onTap: () => NakshatraInfoPanel.show(context, nakshatraId: id),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
        decoration: BoxDecoration(
          border: Border(
              bottom: BorderSide(color: C.glassBorder, width: 0.5)),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Number badge
            Container(
              width: 22,
              height: 22,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: rulerColor.withValues(alpha: 0.12),
              ),
              child: Center(
                child: Text('$num',
                    style: T.caption.copyWith(
                        color: rulerColor,
                        fontSize: 9,
                        fontWeight: FontWeight.w600)),
              ),
            ),
            const SizedBox(width: S.sm),
            // Name + ruler
            Expanded(
              flex: 3,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Flexible(
                        child: Text(name,
                            style: T.bodySm.copyWith(
                                color: C.textPrimary,
                                fontWeight: FontWeight.w600,
                                fontSize: 12),
                            overflow: TextOverflow.ellipsis),
                      ),
                      const SizedBox(width: S.xs),
                      Text(planetGlyph(ruler),
                          style: TextStyle(
                              fontSize: 11, color: rulerColor)),
                    ],
                  ),
                  Text('$deity  |  $symbol',
                      style: T.caption.copyWith(
                          color: C.textMuted, fontSize: 10),
                      overflow: TextOverflow.ellipsis),
                ],
              ),
            ),
            // Shakti (truncated)
            Expanded(
              flex: 4,
              child: Text(shakti,
                  style: T.caption.copyWith(
                      color: C.textSecondary,
                      fontSize: 10,
                      height: 1.3),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis),
            ),
            Icon(Icons.chevron_right,
                size: 14,
                color: C.textMuted.withValues(alpha: 0.4)),
          ],
        ),
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════
// SECTION 4: Yogas
// ════════════════════════════════════════════════════════════════

class _YogasSection extends StatelessWidget {
  const _YogasSection();

  static const _howFormed = [
    ('Conjunction', 'Two planets in the same sign'),
    ('Aspect', 'Planet "sees" another house (special drishti)'),
    ('Lordship', 'Planet rules one house, sits in another'),
    ('Exchange', 'Two planets sitting in each other\'s signs'),
    ('Position', 'Planet in specific dignity (exalted, own sign)'),
  ];

  static const _categories = [
    ('Pancha Mahapurusha', '5', 'Planet in own/exalted in kendra', C.sun),
    ('Raja Yogas', '50+', 'Kendra lord + Trikona lord combine', C.jupiter),
    ('Dhana Yogas', '40+', 'Wealth-producing combinations', C.venus),
    ('Chandra Yogas', '30', 'Based on Moon position', C.moon),
    ('Nabhas Yogas', '32', 'Based on planetary patterns', C.mercury),
    ('Viparita Raja', '6', 'Dusthana lord in dusthana (reversal)', C.ketu),
    ('Neecha Bhanga', '8', 'Debilitation cancellation', C.mars),
    ('Nakshatra Yogas', '50+', 'Based on nakshatra positions', C.rahu),
    ('Special Yogas', '200+', 'Miscellaneous combinations', C.saturn),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: C.glassBorder, height: 1),
        const SizedBox(height: S.lg),
        Text(
          'Yogas are specific planetary combinations that produce specific results. '
          'They exist as promises in your birth chart and ACTIVATE during the dasha '
          'of the planets involved.',
          style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
        ),
        const SizedBox(height: S.lg),
        Text('HOW YOGAS FORM',
            style:
                T.label.copyWith(color: C.textMuted, letterSpacing: 1.2)),
        const SizedBox(height: S.sm),
        ..._howFormed.asMap().entries.map((e) => Padding(
              padding: const EdgeInsets.only(bottom: S.xs),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 20,
                    height: 20,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: C.accent.withValues(alpha: 0.15),
                    ),
                    child: Center(
                      child: Text('${e.key + 1}',
                          style: T.caption.copyWith(
                              color: C.accent, fontSize: 10)),
                    ),
                  ),
                  const SizedBox(width: S.sm),
                  Expanded(
                    child: RichText(
                      text: TextSpan(
                        children: [
                          TextSpan(
                            text: '${e.value.$1} — ',
                            style: T.bodySm.copyWith(
                                color: C.textPrimary,
                                fontWeight: FontWeight.w600,
                                fontSize: 12),
                          ),
                          TextSpan(
                            text: e.value.$2,
                            style: T.bodySm.copyWith(
                                color: C.textSecondary, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            )),
        const SizedBox(height: S.xl),
        Text('YOGA CATEGORIES (522 TOTAL)',
            style:
                T.label.copyWith(color: C.textMuted, letterSpacing: 1.2)),
        const SizedBox(height: S.sm),
        ..._categories.map((c) => Container(
              margin: const EdgeInsets.only(bottom: S.xs),
              padding: const EdgeInsets.symmetric(
                  horizontal: S.md, vertical: S.sm),
              decoration: BoxDecoration(
                borderRadius: R.smBr,
                color: c.$4.withValues(alpha: 0.05),
                border: Border.all(color: c.$4.withValues(alpha: 0.15)),
              ),
              child: Row(
                children: [
                  Expanded(
                    flex: 3,
                    child: Text(c.$1,
                        style: T.bodySm.copyWith(
                            color: c.$4,
                            fontWeight: FontWeight.w600,
                            fontSize: 12)),
                  ),
                  SizedBox(
                    width: 32,
                    child: Text(c.$2,
                        textAlign: TextAlign.center,
                        style: T.caption
                            .copyWith(color: C.textSecondary, fontSize: 11)),
                  ),
                  const SizedBox(width: S.sm),
                  Expanded(
                    flex: 4,
                    child: Text(c.$3,
                        style: T.caption
                            .copyWith(color: C.textMuted, fontSize: 11)),
                  ),
                ],
              ),
            )),
      ],
    );
  }
}

// ════════════════════════════════════════════════════════════════
// SECTION 5: Doshas
// ════════════════════════════════════════════════════════════════

class _DoshasSection extends StatelessWidget {
  const _DoshasSection();

  static const _categories = [
    ('Graha Doshas', '~20', [
      'Mangal Dosha — Mars in 1/2/4/7/8/12 (marriage delay)',
      'Kaal Sarp — All planets between Rahu-Ketu axis',
      'Pitra Dosha — Sun+Rahu/Saturn (ancestral karma)',
      'Guru Chandal — Jupiter+Rahu (corrupted wisdom)',
      'Kemdrum — No planets around Moon (loneliness)',
    ], C.mars),
    ('Bhava Doshas', '~9', [
      'Dhan Dosha — 2nd house affliction (wealth loss)',
      'Putra Dosha — 5th house affliction (children issues)',
      'Vivah Dosha — 7th house affliction (marriage issues)',
    ], C.saturn),
    ('Transit Doshas', '2', [
      'Sade Sati — Saturn transiting 12th/1st/2nd from Moon (7.5 years)',
      'Dhaiya — Saturn in 4th/8th from Moon (2.5 years)',
    ], C.ketu),
    ('Nakshatra Doshas', '4', [
      'Gandmool — Birth in junction nakshatras',
      'Nadi Dosha — Same nadi in matching (fatal for compatibility)',
    ], C.rahu),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: C.glassBorder, height: 1),
        const SizedBox(height: S.lg),
        Text(
          'Doshas are afflictions or challenges in a birth chart. They indicate '
          'areas where karmic patterns create difficulty, but awareness and '
          'timing can help navigate them.',
          style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
        ),
        const SizedBox(height: S.lg),
        ..._categories.map((cat) => Container(
              margin: const EdgeInsets.only(bottom: S.md),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: S.sm, vertical: 2),
                        decoration: BoxDecoration(
                          borderRadius: R.smBr,
                          color: cat.$4.withValues(alpha: 0.15),
                        ),
                        child: Text(cat.$1,
                            style: T.label.copyWith(
                                color: cat.$4, fontSize: 11)),
                      ),
                      const SizedBox(width: S.sm),
                      Text(cat.$2,
                          style: T.caption
                              .copyWith(color: C.textMuted, fontSize: 10)),
                    ],
                  ),
                  const SizedBox(height: S.xs),
                  ...cat.$3.map((d) => Padding(
                        padding: const EdgeInsets.only(left: S.sm, bottom: 3),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('\u2022 ',
                                style: T.caption
                                    .copyWith(color: cat.$4, fontSize: 10)),
                            Expanded(
                              child: Text(d,
                                  style: T.caption.copyWith(
                                      color: C.textSecondary,
                                      fontSize: 11,
                                      height: 1.3)),
                            ),
                          ],
                        ),
                      )),
                ],
              ),
            )),
      ],
    );
  }
}

// ════════════════════════════════════════════════════════════════
// SECTION 6: Dasha System
// ════════════════════════════════════════════════════════════════

class _DashaSection extends StatelessWidget {
  const _DashaSection();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: C.glassBorder, height: 1),
        const SizedBox(height: S.lg),
        Text(
          'The birth chart is static. Dashas make it dynamic. The Vimshottari '
          'system divides 120 years into 9 planetary periods based on your '
          'Moon nakshatra at birth.',
          style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
        ),
        const SizedBox(height: S.lg),
        // Hierarchy
        _InfoBox(
          color: C.saturn,
          text: 'Mahadasha (major, years) \u2192 Antardasha (sub, months) \u2192 '
              'Pratyantardasha (sub-sub, weeks)\n'
              'Total: 9 x 9 x 9 = 729 unique time periods',
        ),
        const SizedBox(height: S.lg),
        Text('DASHA DURATIONS',
            style:
                T.label.copyWith(color: C.textMuted, letterSpacing: 1.2)),
        const SizedBox(height: S.sm),
        _DashaBar(planet: 'ketu', years: 7),
        _DashaBar(planet: 'venus', years: 20),
        _DashaBar(planet: 'sun', years: 6),
        _DashaBar(planet: 'moon', years: 10),
        _DashaBar(planet: 'mars', years: 7),
        _DashaBar(planet: 'rahu', years: 18),
        _DashaBar(planet: 'jupiter', years: 16),
        _DashaBar(planet: 'saturn', years: 19),
        _DashaBar(planet: 'mercury', years: 17),
        const SizedBox(height: S.lg),
        _InfoBox(
          color: C.jupiter,
          text: 'A yoga only ACTIVATES during the dasha of its involved planets. '
              'The promise is in the birth chart; the timing is in the dasha.',
        ),
      ],
    );
  }
}

class _DashaBar extends StatelessWidget {
  final String planet;
  final int years;
  const _DashaBar({required this.planet, required this.years});

  @override
  Widget build(BuildContext context) {
    final color = planetColor(planet);
    return Padding(
      padding: const EdgeInsets.only(bottom: S.xs),
      child: Row(
        children: [
          SizedBox(
            width: 24,
            child: Text(planetGlyph(planet),
                style: TextStyle(fontSize: 14, color: color)),
          ),
          SizedBox(
            width: 60,
            child: Text(planetName(planet),
                style: T.caption
                    .copyWith(color: C.textPrimary, fontSize: 11)),
          ),
          Expanded(
            child: ClipRRect(
              borderRadius: R.smBr,
              child: LinearProgressIndicator(
                value: years / 20,
                minHeight: 12,
                backgroundColor: C.glassBorder,
                valueColor: AlwaysStoppedAnimation(color.withValues(alpha: 0.6)),
              ),
            ),
          ),
          const SizedBox(width: S.sm),
          SizedBox(
            width: 36,
            child: Text('$years yr',
                textAlign: TextAlign.right,
                style: T.caption.copyWith(color: color, fontSize: 11)),
          ),
        ],
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════
// SECTION 7: Transits
// ════════════════════════════════════════════════════════════════

class _TransitsSection extends StatelessWidget {
  const _TransitsSection();

  static const _layers = [
    ('Gochara', 'Transit planets counted from natal Moon sign. '
        'Quick emotional/mental effects.', C.moon),
    ('Over Natal', 'When a transit planet crosses exact degree of a natal planet. '
        'Activates that planet\'s significations.', C.sun),
    ('Through Houses', 'Which of YOUR 12 houses is each transit planet in? '
        'Example: Jupiter in 9th = slow-building luck.', C.jupiter),
    ('Nakshatra Level', 'Planet transiting through a specific nakshatra. '
        'Adds fine-grained timing (243 combinations).', C.mercury),
    ('Ashtakavarga', 'Each planet has 0-8 bindus per sign. High bindus = good results. '
        'Low bindus = weak/bad results.', C.saturn),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: C.glassBorder, height: 1),
        const SizedBox(height: S.lg),
        Text(
          'Transits show where planets are RIGHT NOW vs where they were at birth. '
          '108 analyzes 5 layers of transit to determine current effects.',
          style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
        ),
        const SizedBox(height: S.lg),
        ..._layers.asMap().entries.map((e) => Container(
              margin: const EdgeInsets.only(bottom: S.sm),
              padding:
                  const EdgeInsets.symmetric(horizontal: S.md, vertical: S.md),
              decoration: BoxDecoration(
                borderRadius: R.mdBr,
                border:
                    Border(left: BorderSide(color: e.value.$3, width: 3)),
                color: e.value.$3.withValues(alpha: 0.04),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 18,
                        height: 18,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: e.value.$3.withValues(alpha: 0.2),
                        ),
                        child: Center(
                          child: Text('${e.key + 1}',
                              style: T.caption.copyWith(
                                  color: e.value.$3, fontSize: 9)),
                        ),
                      ),
                      const SizedBox(width: S.sm),
                      Text(e.value.$1,
                          style: T.bodySm.copyWith(
                              color: e.value.$3,
                              fontWeight: FontWeight.w600,
                              fontSize: 12)),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(e.value.$2,
                      style: T.caption.copyWith(
                          color: C.textSecondary, fontSize: 11, height: 1.4)),
                ],
              ),
            )),
      ],
    );
  }
}

// ════════════════════════════════════════════════════════════════
// SECTION 8: Strength
// ════════════════════════════════════════════════════════════════

class _StrengthSection extends StatelessWidget {
  const _StrengthSection();

  static const _shadbala = [
    ('Sthana Bala', 'Positional — dignity, own sign, exalted'),
    ('Dig Bala', 'Directional — strongest in specific houses'),
    ('Kaala Bala', 'Temporal — day/night, season, hora'),
    ('Chesta Bala', 'Motional — retrograde adds strength'),
    ('Naisargika Bala', 'Natural — inherent planet power'),
    ('Drik Bala', 'Aspectual — benefic/malefic aspects received'),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: C.glassBorder, height: 1),
        const SizedBox(height: S.lg),
        Text(
          'Not all planets are equally effective. Strength determines how much '
          'of its promise a planet actually delivers.',
          style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
        ),
        const SizedBox(height: S.lg),
        Text('SHADBALA (SIX-FOLD STRENGTH)',
            style:
                T.label.copyWith(color: C.textMuted, letterSpacing: 1.2)),
        const SizedBox(height: S.sm),
        ..._shadbala.asMap().entries.map((e) => Container(
              margin: const EdgeInsets.only(bottom: S.xs),
              padding: const EdgeInsets.symmetric(
                  horizontal: S.md, vertical: S.sm),
              decoration: BoxDecoration(
                borderRadius: R.smBr,
                color: C.accent.withValues(alpha: 0.04),
                border: Border.all(color: C.glassBorder, width: 0.5),
              ),
              child: Row(
                children: [
                  SizedBox(
                    width: 100,
                    child: Text(e.value.$1,
                        style: T.bodySm.copyWith(
                            color: C.accent,
                            fontWeight: FontWeight.w600,
                            fontSize: 11)),
                  ),
                  Expanded(
                    child: Text(e.value.$2,
                        style: T.caption
                            .copyWith(color: C.textSecondary, fontSize: 11)),
                  ),
                ],
              ),
            )),
        const SizedBox(height: S.lg),
        _InfoBox(
          color: C.accent,
          text: 'Score > 300 = Strong (planet delivers at full power)\n'
              'Score < 200 = Weak (planet struggles to produce results)',
        ),
        const SizedBox(height: S.lg),
        // Dig Bala map
        Text('DIRECTIONAL STRENGTH (DIG BALA)',
            style:
                T.label.copyWith(color: C.textMuted, letterSpacing: 1.2)),
        const SizedBox(height: S.sm),
        Row(
          children: [
            _DigBalaChip('H1 (East)', 'Jupiter\nMercury', C.jupiter),
            const SizedBox(width: S.xs),
            _DigBalaChip('H4 (North)', 'Moon\nVenus', C.moon),
            const SizedBox(width: S.xs),
            _DigBalaChip('H7 (West)', 'Saturn', C.saturn),
            const SizedBox(width: S.xs),
            _DigBalaChip('H10 (South)', 'Sun\nMars', C.sun),
          ],
        ),
      ],
    );
  }
}

class _DigBalaChip extends StatelessWidget {
  final String house;
  final String planets;
  final Color color;
  const _DigBalaChip(this.house, this.planets, this.color);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(S.sm),
        decoration: BoxDecoration(
          borderRadius: R.smBr,
          color: color.withValues(alpha: 0.08),
          border: Border.all(color: color.withValues(alpha: 0.2)),
        ),
        child: Column(
          children: [
            Text(house,
                style: T.caption.copyWith(color: color, fontSize: 9)),
            const SizedBox(height: 2),
            Text(planets,
                textAlign: TextAlign.center,
                style: T.caption
                    .copyWith(color: C.textPrimary, fontSize: 10, height: 1.3)),
          ],
        ),
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════
// SECTION 9: How a Reading Works
// ════════════════════════════════════════════════════════════════

class _DataFlowSection extends StatelessWidget {
  const _DataFlowSection();

  static const _steps = [
    ('COSMOS', 'Calculate positions', 'Planets, houses, nakshatras, ascendant + current transits', C.sun),
    ('SELF', 'Detect patterns', 'Yogas, doshas, strength, career houses, karakas', C.venus),
    ('CONTEXT', 'Apply timing', 'Current dasha + active transits + Sade Sati phase', C.saturn),
    ('KNOWLEDGE', 'Interpret', 'Combine dasha effects + transit rules + yoga activation', C.mercury),
    ('GUIDE', 'Synthesize', 'AI combines all layers into personalized guidance', C.accent),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: C.glassBorder, height: 1),
        const SizedBox(height: S.lg),
        Text(
          'When you ask "What is happening in my career?", the system goes '
          'through 5 steps to give you a complete answer.',
          style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
        ),
        const SizedBox(height: S.lg),
        ..._steps.asMap().entries.map((e) {
          final isLast = e.key == _steps.length - 1;
          return Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Vertical line + dot
              SizedBox(
                width: 24,
                child: Column(
                  children: [
                    Container(
                      width: 20,
                      height: 20,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: e.value.$4.withValues(alpha: 0.2),
                        border: Border.all(
                            color: e.value.$4, width: 1.5),
                      ),
                      child: Center(
                        child: Text('${e.key + 1}',
                            style: T.caption.copyWith(
                                color: e.value.$4, fontSize: 9)),
                      ),
                    ),
                    if (!isLast)
                      Container(
                        width: 1.5,
                        height: 48,
                        color: e.value.$4.withValues(alpha: 0.3),
                      ),
                  ],
                ),
              ),
              const SizedBox(width: S.sm),
              Expanded(
                child: Padding(
                  padding: EdgeInsets.only(
                      bottom: isLast ? 0 : S.md),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(e.value.$1,
                              style: T.bodySm.copyWith(
                                  color: e.value.$4,
                                  fontWeight: FontWeight.w700,
                                  fontSize: 12)),
                          const SizedBox(width: S.sm),
                          Text(e.value.$2,
                              style: T.bodySm.copyWith(
                                  color: C.textPrimary, fontSize: 12)),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(e.value.$3,
                          style: T.caption.copyWith(
                              color: C.textMuted,
                              fontSize: 11,
                              height: 1.4)),
                    ],
                  ),
                ),
              ),
            ],
          );
        }),
      ],
    );
  }
}

// ════════════════════════════════════════════════════════════════
// Shared Widgets
// ════════════════════════════════════════════════════════════════

class _InfoBox extends StatelessWidget {
  final Color color;
  final String text;
  const _InfoBox({required this.color, required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(S.md),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: color.withValues(alpha: 0.06),
        border: Border(left: BorderSide(color: color, width: 3)),
      ),
      child: Text(text,
          style: T.bodySm
              .copyWith(color: C.textPrimary, fontSize: 12, height: 1.5)),
    );
  }
}
