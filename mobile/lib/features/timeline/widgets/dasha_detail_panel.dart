import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Bottom sheet panel showing rich dasha period details.
///
/// Opens as a draggable scrollable sheet with planet-colored gradient header,
/// educational content, area scores, effects, and an "Ask AI" button.
class DashaDetailPanel extends ConsumerStatefulWidget {
  final String level; // 'md', 'ad', 'pd'
  final String lord;
  final String mdLord;
  final String? adLord;
  final String? pdLord;
  final String startDate;
  final String endDate;
  final bool isCurrent;

  const DashaDetailPanel({
    super.key,
    required this.level,
    required this.lord,
    required this.mdLord,
    this.adLord,
    this.pdLord,
    required this.startDate,
    required this.endDate,
    required this.isCurrent,
  });

  /// Show the detail panel as a modal bottom sheet.
  static void show(
    BuildContext context, {
    required String level,
    required String lord,
    required String mdLord,
    String? adLord,
    String? pdLord,
    required String startDate,
    required String endDate,
    required bool isCurrent,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => DashaDetailPanel(
        level: level,
        lord: lord,
        mdLord: mdLord,
        adLord: adLord,
        pdLord: pdLord,
        startDate: startDate,
        endDate: endDate,
        isCurrent: isCurrent,
      ),
    );
  }

  @override
  ConsumerState<DashaDetailPanel> createState() => _DashaDetailPanelState();
}

class _DashaDetailPanelState extends ConsumerState<DashaDetailPanel> {
  Map<String, dynamic>? _data;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchEffects();
  }

  Future<void> _fetchEffects() async {
    try {
      final data = await ApiService().get(
        ApiConstants.dashaEffects(
          md: widget.mdLord,
          ad: widget.adLord,
          pd: widget.pdLord,
        ),
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (mounted) setState(() { _data = data; _loading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = '$e'; _loading = false; });
    }
  }

  Color get _color => _planetColor(widget.lord);

  String get _levelLabel {
    switch (widget.level) {
      case 'md': return 'Mahadasha';
      case 'ad': return 'Antardasha';
      case 'pd': return 'Pratyantardasha';
      default: return 'Period';
    }
  }

  String get _educationalText {
    switch (widget.level) {
      case 'md':
        return 'A Mahadasha is a major planetary period lasting 6\u201320 years. '
            'It sets the primary theme of your life during this time.';
      case 'ad':
        return 'An Antardasha is a sub-period within a Mahadasha, lasting months '
            'to years. It colors the main period with its planet\u2019s energy.';
      case 'pd':
        return 'A Pratyantardasha is the finest timing layer, lasting days to weeks. '
            'It triggers specific events within the sub-period.';
      default:
        return '';
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      minChildSize: 0.4,
      maxChildSize: 0.93,
      builder: (context, scrollController) {
        return Container(
          decoration: BoxDecoration(
            color: C.surface,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(R.xl)),
          ),
          child: Column(
            children: [
              // Gradient header (not scrollable)
              _buildHeader(),
              // Scrollable content
              Expanded(
                child: _loading
                    ? const Center(
                        child: CircularProgressIndicator(
                            color: C.accent, strokeWidth: 2),
                      )
                    : _error != null
                        ? _buildError(scrollController)
                        : _buildContent(scrollController),
              ),
              // Ask AI button (fixed at bottom)
              _buildAskAiButton(),
            ],
          ),
        );
      },
    );
  }

  // ── A. Gradient Header ──

  Widget _buildHeader() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius: const BorderRadius.vertical(top: Radius.circular(R.xl)),
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            _color.withValues(alpha: 0.25),
            Colors.transparent,
          ],
        ),
      ),
      padding: const EdgeInsets.fromLTRB(S.lg, S.md, S.lg, S.sm),
      child: Column(
        children: [
          // Drag handle
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: C.glassBorder,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: S.md),
          // Planet glyph + name + level badge
          Row(
            children: [
              Text(
                _planetGlyph(widget.lord),
                style: TextStyle(fontSize: 28, color: _color),
              ),
              const SizedBox(width: S.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          _planetName(widget.lord),
                          style: T.h2.copyWith(color: _color),
                        ),
                        const SizedBox(width: S.sm),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.sm, vertical: 2),
                          decoration: BoxDecoration(
                            borderRadius: R.xlBr,
                            color: _color.withValues(alpha: 0.15),
                            border: Border.all(
                                color: _color.withValues(alpha: 0.3)),
                          ),
                          child: Text(
                            _levelLabel,
                            style: T.caption.copyWith(
                                color: _color, fontSize: 10),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${_formatDate(widget.startDate)} \u2192 ${_formatDate(widget.endDate)}  \u00b7  ${_durationFromIso(widget.startDate, widget.endDate)}',
                      style: T.caption,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ── Error ──

  Widget _buildError(ScrollController controller) {
    return ListView(
      controller: controller,
      padding: const EdgeInsets.all(S.lg),
      children: [
        const SizedBox(height: S.xl),
        Text('Could not load effects', style: T.h3),
        const SizedBox(height: S.sm),
        Text(_error!, style: T.caption),
        const SizedBox(height: S.lg),
        OutlinedButton(
          onPressed: () {
            setState(() { _loading = true; _error = null; });
            _fetchEffects();
          },
          child: const Text('Retry'),
        ),
      ],
    );
  }

  // ── Scrollable Content ──

  Widget _buildContent(ScrollController controller) {
    final md = _data?['mahadasha'] as Map<String, dynamic>? ?? {};
    final adData = _data?['antardasha'] as Map<String, dynamic>?;
    final pdData = _data?['pratyantardasha'] as Map<String, dynamic>?;
    final cross = _data?['cross_analysis'] as Map<String, dynamic>?;
    final areaScores = _data?['area_scores'] as Map<String, dynamic>?;
    // Relationship info
    final mdAdRel = _data?['md_ad_relationship'] as Map<String, dynamic>?;
    final adPdRel = _data?['ad_pd_relationship'] as Map<String, dynamic>?;

    return ListView(
      controller: controller,
      padding: const EdgeInsets.symmetric(horizontal: S.lg),
      children: [
        const SizedBox(height: S.sm),

        // B. Educational card
        _buildEducationalCard(),
        const SizedBox(height: S.md),

        // Relationship chip (AD→MD or PD→AD)
        if (widget.level == 'ad' && mdAdRel != null)
          _buildRelationshipChip(mdAdRel, widget.mdLord, widget.lord),
        if (widget.level == 'pd' && adPdRel != null && widget.adLord != null)
          _buildRelationshipChip(adPdRel, widget.adLord!, widget.lord),

        // Dosha activation section — show activated doshas (period-specific)
        // or natal doshas (chart-wide) as fallback
        if ((_data?['activated_doshas'] as List?)?.isNotEmpty ?? false) ...[
          const SizedBox(height: S.md),
          _buildDoshaActivationSection(
              _data!['activated_doshas'] as List, activated: true),
        ] else if ((_data?['natal_doshas'] as List?)?.isNotEmpty ?? false) ...[
          const SizedBox(height: S.md),
          _buildDoshaActivationSection(
              _data!['natal_doshas'] as List, activated: false),
        ],

        // C. Theme quote
        if (md['theme'] != null && (md['theme'] as String).isNotEmpty) ...[
          _buildThemeQuote(md['theme'] as String),
          const SizedBox(height: S.md),
        ],

        // D. Area score bars
        if (areaScores != null && areaScores.isNotEmpty) ...[
          _buildAreaScores(areaScores),
          const SizedBox(height: S.md),
        ],

        // E. Effects section (varies by level)
        _buildEffectsSection(md, adData, pdData),

        // F. Current activation
        if (widget.isCurrent && cross != null) ...[
          const SizedBox(height: S.md),
          _buildCrossAnalysis(cross),
        ],

        const SizedBox(height: S.xl),
      ],
    );
  }

  // ── B. Educational Card ──

  Widget _buildEducationalCard() {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.auto_stories, color: _color, size: 20),
          const SizedBox(width: S.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'What is a $_levelLabel?',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                Text(
                  _educationalText,
                  style: T.caption.copyWith(color: C.textSecondary, height: 1.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Relationship Chip ──

  Widget _buildRelationshipChip(Map<String, dynamic> rel, String parent, String child) {
    final type = rel['type'] as String? ?? 'neutral';
    final label = rel['label'] as String? ?? '';
    final Color dotColor;
    final String emoji;
    switch (type) {
      case 'friend':
        dotColor = C.positive;
        emoji = '\u2764'; // heart
      case 'enemy':
        dotColor = C.negative;
        emoji = '\u26a0'; // warning
      default:
        dotColor = C.warning;
        emoji = '\u2022'; // bullet
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(shape: BoxShape.circle, color: dotColor),
          ),
          const SizedBox(width: 6),
          Expanded(
            child: Text(
              '$emoji $label',
              style: T.caption.copyWith(color: dotColor),
            ),
          ),
        ],
      ),
    );
  }

  // ── Dosha Activation Section ──

  Widget _buildDoshaActivationSection(List doshas, {bool activated = true}) {
    final title = activated ? 'Dosha Activation' : 'Natal Doshas';
    final icon = activated ? Icons.warning_amber_rounded : Icons.info_outline;
    final iconColor = activated ? C.warning : C.accent;
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: iconColor, size: 18),
              const SizedBox(width: 6),
              Text(title,
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: S.sm),
          ...doshas.take(5).map((d) {
            final dosha = d as Map<String, dynamic>;
            return Padding(
              padding: const EdgeInsets.only(bottom: S.sm),
              child: _DoshaActivationCard(dosha: dosha),
            );
          }),
        ],
      ),
    );
  }

  // ── C. Theme Quote ──

  Widget _buildThemeQuote(String theme) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: S.sm),
      child: Text(
        '\u201c$theme\u201d',
        style: T.body.copyWith(
          color: _color.withValues(alpha: 0.85),
          fontStyle: FontStyle.italic,
          fontSize: 15,
        ),
      ),
    );
  }

  // ── D. Area Score Bars ──

  Widget _buildAreaScores(Map<String, dynamic> scores) {
    const areaIcons = {
      'career': Icons.work_outline,
      'health': Icons.favorite_outline,
      'relationships': Icons.people_outline,
      'finances': Icons.account_balance_wallet_outlined,
      'spiritual': Icons.self_improvement,
    };
    const areaLabels = {
      'career': 'Career',
      'health': 'Health',
      'relationships': 'Relationships',
      'finances': 'Finances',
      'spiritual': 'Spiritual',
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Area Ratings',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        ...['career', 'health', 'relationships', 'finances', 'spiritual'].map((area) {
          final score = (scores[area] as num?)?.toInt() ?? 5;
          final barColor = score >= 7
              ? C.positive
              : score >= 4
                  ? C.warning
                  : C.negative;
          return Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Row(
              children: [
                Icon(areaIcons[area], size: 14, color: C.textMuted),
                const SizedBox(width: 6),
                SizedBox(
                  width: 80,
                  child: Text(
                    areaLabels[area]!,
                    style: T.caption.copyWith(color: C.textSecondary),
                  ),
                ),
                Expanded(
                  child: ClipRRect(
                    borderRadius: R.smBr,
                    child: LinearProgressIndicator(
                      value: score / 10,
                      minHeight: 4,
                      backgroundColor: C.glassBorder,
                      valueColor: AlwaysStoppedAnimation(barColor),
                    ),
                  ),
                ),
                const SizedBox(width: 6),
                SizedBox(
                  width: 20,
                  child: Text(
                    '$score',
                    style: T.caption.copyWith(
                        color: barColor, fontWeight: FontWeight.w600),
                    textAlign: TextAlign.right,
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  // ── E. Effects Section ──

  Widget _buildEffectsSection(
    Map<String, dynamic> md,
    Map<String, dynamic>? adData,
    Map<String, dynamic>? pdData,
  ) {
    switch (widget.level) {
      case 'md':
        return _buildMdEffects(md);
      case 'ad':
        return adData != null ? _buildAdEffects(adData) : const SizedBox.shrink();
      case 'pd':
        return pdData != null ? _buildPdEffects(pdData) : const SizedBox.shrink();
      default:
        return const SizedBox.shrink();
    }
  }

  Widget _buildMdEffects(Map<String, dynamic> md) {
    final focusAreas = (md['focus_areas'] as List?)?.cast<String>() ?? [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Focus areas as chips
        if (focusAreas.isNotEmpty) ...[
          Text('Focus Areas',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: focusAreas.map((area) => Container(
              padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 4),
              decoration: BoxDecoration(
                borderRadius: R.xlBr,
                color: _color.withValues(alpha: 0.1),
                border: Border.all(color: _color.withValues(alpha: 0.2)),
              ),
              child: Text(area,
                  style: T.caption.copyWith(color: _color)),
            )).toList(),
          ),
          const SizedBox(height: S.md),
        ],
        // Area detail cards
        ..._buildAreaCards({
          'Career': md['career'] as String? ?? '',
          'Health': md['health'] as String? ?? '',
          'Relationships': md['relationships'] as String? ?? '',
          'Spiritual': md['spiritual'] as String? ?? '',
        }),
        // Practical advice
        if ((md['practical_advice'] as List?)?.isNotEmpty ?? false) ...[
          const SizedBox(height: S.md),
          _buildListSection('Practical Advice', md['practical_advice'] as List,
              icon: Icons.lightbulb_outline, iconColor: C.warning),
        ],
      ],
    );
  }

  Widget _buildAdEffects(Map<String, dynamic> ad) {
    final positive = (ad['positive'] as List?)?.cast<String>() ?? [];
    final negative = (ad['negative'] as List?)?.cast<String>() ?? [];
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (positive.isNotEmpty)
          _buildListSection('Positive', positive,
              icon: Icons.check_circle_outline, iconColor: C.positive),
        if (negative.isNotEmpty) ...[
          const SizedBox(height: S.md),
          _buildListSection('Challenges', negative,
              icon: Icons.warning_amber_rounded, iconColor: C.warning),
        ],
        const SizedBox(height: S.md),
        ..._buildAreaCards({
          'Career': ad['career'] as String? ?? '',
          'Health': ad['health'] as String? ?? '',
          'Relationships': ad['relationships'] as String? ?? '',
          'Finances': ad['finances'] as String? ?? '',
        }),
      ],
    );
  }

  Widget _buildPdEffects(Map<String, dynamic> pd) {
    final theme = pd['theme'] as String? ?? '';

    // Effects can be a dict (with 'general' key) or a list
    final rawEffects = pd['effects'];
    final List<String> effects;
    if (rawEffects is Map) {
      // Flatten dict values into a list of strings
      effects = rawEffects.values
          .map((v) => v.toString())
          .where((v) => v.isNotEmpty)
          .toList();
    } else if (rawEffects is List) {
      effects = rawEffects.cast<String>();
    } else {
      effects = [];
    }

    // timing_events can be a dict (with phase keys) or a string
    final rawTiming = pd['timing_events'] ?? pd['timing'];
    final String timing;
    if (rawTiming is Map) {
      timing = rawTiming.values.join(' \u2022 ');
    } else {
      timing = rawTiming?.toString() ?? '';
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (theme.isNotEmpty) ...[
          Text('Theme',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: 4),
          Text(theme, style: T.bodySm.copyWith(color: C.textSecondary)),
          const SizedBox(height: S.md),
        ],
        if (effects.isNotEmpty)
          _buildListSection('Effects', effects,
              icon: Icons.circle, iconColor: _color),
        if (timing.isNotEmpty) ...[
          const SizedBox(height: S.md),
          _buildInfoRow(Icons.schedule, 'Timing', timing),
        ],
        const SizedBox(height: S.md),
        ..._buildAreaCards({
          'Career': _flattenField(pd['career']),
          'Health': _flattenField(pd['health']),
          'Relationships': _flattenField(pd['relationships']),
        }),
      ],
    );
  }

  // ── F. Cross Analysis ──

  Widget _buildCrossAnalysis(Map<String, dynamic> cross) {
    final themes = (cross['active_themes'] as List?)?.cast<String>() ?? [];
    final quality = cross['period_quality'] as String? ?? '';
    final score = (cross['score'] as num?)?.toInt();
    final house = cross['strongest_house'];

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.bolt, color: C.warning, size: 18),
              const SizedBox(width: 6),
              Text('Current Activation',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600)),
              const Spacer(),
              if (score != null)
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.sm, vertical: 2),
                  decoration: BoxDecoration(
                    borderRadius: R.xlBr,
                    color: _scoreColor(score).withValues(alpha: 0.15),
                  ),
                  child: Text(
                    '$score/100',
                    style: T.caption.copyWith(
                        color: _scoreColor(score),
                        fontWeight: FontWeight.w600),
                  ),
                ),
            ],
          ),
          if (quality.isNotEmpty) ...[
            const SizedBox(height: S.sm),
            _buildInfoRow(Icons.trending_up, 'Quality',
                quality[0].toUpperCase() + quality.substring(1)),
          ],
          if (house != null) ...[
            const SizedBox(height: 4),
            _buildInfoRow(Icons.home_outlined, 'Strongest House', 'House $house'),
          ],
          if (themes.isNotEmpty) ...[
            const SizedBox(height: S.sm),
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: themes.take(5).map((t) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  borderRadius: R.smBr,
                  color: C.accentDim,
                ),
                child: Text(t, style: T.caption.copyWith(color: C.accent, fontSize: 10)),
              )).toList(),
            ),
          ],
        ],
      ),
    );
  }

  // ── G. Ask AI Button ──

  Widget _buildAskAiButton() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () => Navigator.of(context).pop(),
          style: ElevatedButton.styleFrom(
            backgroundColor: _color,
            foregroundColor: C.bg,
            shape: RoundedRectangleBorder(borderRadius: R.xlBr),
          ),
          icon: const Icon(Icons.auto_awesome, size: 18),
          label: Text(
            'Ask about this period',
            style: T.bodySm.copyWith(
                color: C.bg, fontWeight: FontWeight.w600),
          ),
        ),
      ),
    );
  }

  // ── Shared Helpers ──

  Widget _buildListSection(String title, List items,
      {required IconData icon, required Color iconColor}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title,
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: 6),
        ...items.take(6).map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Icon(icon, size: 10, color: iconColor),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text('$item',
                        style: T.caption.copyWith(
                            color: C.textSecondary, height: 1.4)),
                  ),
                ],
              ),
            )),
      ],
    );
  }

  List<Widget> _buildAreaCards(Map<String, String> areas) {
    return areas.entries
        .where((e) => e.value.isNotEmpty)
        .map((e) => Padding(
              padding: const EdgeInsets.only(bottom: S.sm),
              child: _ExpandableArea(title: e.key, content: e.value, color: _color),
            ))
        .toList();
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 14, color: C.textMuted),
        const SizedBox(width: 6),
        Text('$label: ', style: T.caption.copyWith(color: C.textMuted)),
        Expanded(
          child: Text(value,
              style: T.caption.copyWith(color: C.textSecondary)),
        ),
      ],
    );
  }

  /// Flatten a field that may be a String, Map, or List into a single String.
  String _flattenField(dynamic value) {
    if (value == null) return '';
    if (value is String) return value;
    if (value is Map) {
      return value.values
          .map((v) => v.toString())
          .where((v) => v.isNotEmpty)
          .join('. ');
    }
    if (value is List) return value.join('. ');
    return value.toString();
  }

  Color _scoreColor(int score) {
    if (score >= 70) return C.positive;
    if (score >= 40) return C.warning;
    return C.negative;
  }
}

// ── Expandable Area Card ──

class _ExpandableArea extends StatefulWidget {
  final String title;
  final String content;
  final Color color;

  const _ExpandableArea({
    required this.title,
    required this.content,
    required this.color,
  });

  @override
  State<_ExpandableArea> createState() => _ExpandableAreaState();
}

class _ExpandableAreaState extends State<_ExpandableArea> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final preview = widget.content.length > 80
        ? '${widget.content.substring(0, 80)}...'
        : widget.content;

    return GestureDetector(
      onTap: () => setState(() => _expanded = !_expanded),
      child: Container(
        padding: const EdgeInsets.all(S.md),
        decoration: BoxDecoration(
          borderRadius: R.mdBr,
          color: widget.color.withValues(alpha: 0.04),
          border: Border.all(color: widget.color.withValues(alpha: 0.1)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(widget.title,
                    style: T.bodySm.copyWith(
                        color: C.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: 13)),
                const Spacer(),
                Icon(
                  _expanded ? Icons.expand_less : Icons.expand_more,
                  size: 16,
                  color: C.textMuted,
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              _expanded ? widget.content : preview,
              style: T.caption.copyWith(color: C.textSecondary, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Dosha Activation Card ──

class _DoshaActivationCard extends StatefulWidget {
  final Map<String, dynamic> dosha;

  const _DoshaActivationCard({required this.dosha});

  @override
  State<_DoshaActivationCard> createState() => _DoshaActivationCardState();
}

class _DoshaActivationCardState extends State<_DoshaActivationCard> {
  bool _showRemedies = false;

  @override
  Widget build(BuildContext context) {
    final name = widget.dosha['name'] as String? ?? 'Dosha';
    final severity = widget.dosha['severity'] as String? ?? 'moderate';
    final description = widget.dosha['description'] as String? ?? '';
    final activatedBy = widget.dosha['activated_by'] as String? ?? '';
    final remedies = (widget.dosha['remedies'] as List?)?.cast<String>() ?? [];

    final symbol = _doshaSymbol(name);
    final symbolColor = _doshaColor(name);
    final Color severityColor;
    switch (severity) {
      case 'mild':
        severityColor = C.positive;
      case 'severe':
        severityColor = C.negative;
      default:
        severityColor = C.warning;
    }

    return Container(
      padding: const EdgeInsets.all(S.sm),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: symbolColor.withValues(alpha: 0.05),
        border: Border.all(color: symbolColor.withValues(alpha: 0.15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header: symbol + name + severity badge
          Row(
            children: [
              Text(symbol, style: TextStyle(fontSize: 16, color: symbolColor)),
              const SizedBox(width: 6),
              Expanded(
                child: Text(name,
                    style: T.bodySm.copyWith(
                        color: C.textPrimary, fontWeight: FontWeight.w600)),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  borderRadius: R.xlBr,
                  color: severityColor.withValues(alpha: 0.15),
                ),
                child: Text(
                  severity[0].toUpperCase() + severity.substring(1),
                  style: T.caption.copyWith(
                      color: severityColor,
                      fontWeight: FontWeight.w600,
                      fontSize: 9),
                ),
              ),
            ],
          ),
          // Activated by caption
          if (activatedBy.isNotEmpty) ...[
            const SizedBox(height: 2),
            Text(
              'Activated by ${activatedBy[0].toUpperCase()}${activatedBy.substring(1)} in this period',
              style: T.caption.copyWith(color: C.textMuted, fontSize: 10),
            ),
          ],
          // Description
          if (description.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              description,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: T.caption.copyWith(color: C.textSecondary, height: 1.4),
            ),
          ],
          // Remedies toggle
          if (remedies.isNotEmpty) ...[
            const SizedBox(height: 4),
            GestureDetector(
              onTap: () => setState(() => _showRemedies = !_showRemedies),
              child: Row(
                children: [
                  Icon(
                    _showRemedies ? Icons.expand_less : Icons.expand_more,
                    size: 14,
                    color: C.accent,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    _showRemedies ? 'Hide Remedies' : 'Show Remedies',
                    style: T.caption.copyWith(color: C.accent, fontSize: 10),
                  ),
                ],
              ),
            ),
            if (_showRemedies) ...[
              const SizedBox(height: 4),
              ...remedies.take(5).map((r) => Padding(
                    padding: const EdgeInsets.only(bottom: 2),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Icon(Icons.circle, size: 4, color: C.accent),
                        ),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(r,
                              style: T.caption.copyWith(
                                  color: C.textSecondary, fontSize: 10)),
                        ),
                      ],
                    ),
                  )),
            ],
          ],
        ],
      ),
    );
  }
}

String _doshaSymbol(String name) {
  final n = name.toLowerCase();
  if (n.contains('mangal')) return '\u25B2';
  if (n.contains('kaal sarp')) return '\u25C6';
  if (n.contains('pitra')) return '\u2726';
  if (n.contains('grahan')) return '\u25D0';
  if (n.contains('guru chandal')) return '\u2B21';
  if (n.contains('angarak')) return '\u25B2';
  if (n.contains('vish')) return '\u25C9';
  if (n.contains('kemdrum')) return '\u25CB';
  return '\u2022';
}

Color _doshaColor(String name) {
  final n = name.toLowerCase();
  if (n.contains('mangal') || n.contains('angarak')) return C.mars;
  if (n.contains('kaal sarp') || n.contains('sarpa')) return C.rahu;
  if (n.contains('pitra')) return C.sun;
  if (n.contains('grahan')) return C.textSecondary;
  if (n.contains('guru chandal')) return C.jupiter;
  if (n.contains('vish') || n.contains('shapit')) return C.saturn;
  if (n.contains('kemdrum')) return C.moon;
  return C.warning;
}

// ── Planet helpers (duplicated from timeline_screen for encapsulation) ──

String _planetGlyph(String planet) {
  const glyphs = {
    'sun': '\u2609', 'moon': '\u263d', 'mars': '\u2642', 'mercury': '\u263f',
    'jupiter': '\u2643', 'venus': '\u2640', 'saturn': '\u2644',
    'rahu': '\u260a', 'ketu': '\u260b',
  };
  return glyphs[planet.toLowerCase()] ?? '?';
}

String _planetName(String planet) {
  if (planet.isEmpty) return '';
  return planet[0].toUpperCase() + planet.substring(1);
}

Color _planetColor(String planet) {
  const colors = {
    'sun': C.sun, 'moon': C.moon, 'mars': C.mars, 'mercury': C.mercury,
    'jupiter': C.jupiter, 'venus': C.venus, 'saturn': C.saturn,
    'rahu': C.rahu, 'ketu': C.ketu,
  };
  return colors[planet.toLowerCase()] ?? C.accent;
}

String _formatDate(String iso) {
  if (iso.isEmpty) return '';
  try {
    final dt = DateTime.parse(iso);
    const months = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[dt.month]} ${dt.year}';
  } catch (_) {
    return iso.length >= 4 ? iso.substring(0, 4) : iso;
  }
}

String _durationFromIso(String startIso, String endIso) {
  if (startIso.isEmpty || endIso.isEmpty) return '';
  try {
    final s = DateTime.parse(startIso);
    final e = DateTime.parse(endIso);
    final totalDays = e.difference(s).inDays;
    final totalMonths = (totalDays / 30.44).round();
    if (totalMonths >= 24) {
      final years = totalDays ~/ 365;
      final months = ((totalDays % 365) / 30.44).round();
      if (months > 0) return '$years years $months months';
      return '$years years';
    } else if (totalMonths > 0) {
      return '$totalMonths months';
    } else {
      return '$totalDays days';
    }
  } catch (_) {
    return '';
  }
}
