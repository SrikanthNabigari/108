import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Bottom sheet panel showing detailed transit info for a single planet.
///
/// Fetches data from GET /transits/{planet} and displays position, gochara,
/// active natal aspects, upcoming events, and an "Ask AI" button.
class TransitDetailPanel extends ConsumerStatefulWidget {
  final String planet;

  const TransitDetailPanel({super.key, required this.planet});

  /// Show the detail panel as a modal bottom sheet.
  static void show(BuildContext context, {required String planet}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => TransitDetailPanel(planet: planet),
    );
  }

  @override
  ConsumerState<TransitDetailPanel> createState() => _TransitDetailPanelState();
}

class _TransitDetailPanelState extends ConsumerState<TransitDetailPanel> {
  Map<String, dynamic>? _data;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  Future<void> _fetch() async {
    try {
      final data = await ApiService().get(
        ApiConstants.transitPlanet(widget.planet),
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (mounted) setState(() { _data = data; _loading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = '$e'; _loading = false; });
    }
  }

  Color get _color => planetColor(widget.planet);

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
              _buildHeader(),
              Expanded(
                child: _loading
                    ? const Center(
                        child: CircularProgressIndicator(color: C.accent, strokeWidth: 2),
                      )
                    : _error != null
                        ? _buildError(scrollController)
                        : _buildContent(scrollController),
              ),
              _buildAskAiButton(),
            ],
          ),
        );
      },
    );
  }

  // ── A. Gradient Header ──

  Widget _buildHeader() {
    final pos = _data?['position'] as Map<String, dynamic>? ?? {};
    final rashi = pos['rashi'] as String? ?? '';
    final degree = (pos['degree_in_rashi'] as num?)?.toStringAsFixed(1) ?? '0.0';
    final isRetro = pos['is_retrograde'] as bool? ?? false;

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
            width: 40, height: 4,
            decoration: BoxDecoration(
              color: C.glassBorder,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: S.md),
          Row(
            children: [
              Text(
                planetGlyph(widget.planet),
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
                          planetName(widget.planet),
                          style: T.h2.copyWith(color: _color),
                        ),
                        const SizedBox(width: S.sm),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 2),
                          decoration: BoxDecoration(
                            borderRadius: R.xlBr,
                            color: _color.withValues(alpha: 0.15),
                            border: Border.all(color: _color.withValues(alpha: 0.3)),
                          ),
                          child: Text(
                            'Transit',
                            style: T.caption.copyWith(color: _color, fontSize: 10),
                          ),
                        ),
                        if (isRetro) ...[
                          const SizedBox(width: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                            decoration: BoxDecoration(
                              borderRadius: R.smBr,
                              color: C.warning.withValues(alpha: 0.15),
                              border: Border.all(color: C.warning.withValues(alpha: 0.3)),
                            ),
                            child: Text(
                              'Rx',
                              style: T.caption.copyWith(
                                color: C.warning, fontSize: 10, fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      rashi.isNotEmpty ? 'in $rashi $degree\u00b0' : 'Loading...',
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
        Text('Could not load transit details', style: T.h3),
        const SizedBox(height: S.sm),
        Text(_error!, style: T.caption),
        const SizedBox(height: S.lg),
        OutlinedButton(
          onPressed: () {
            setState(() { _loading = true; _error = null; });
            _fetch();
          },
          child: const Text('Retry'),
        ),
      ],
    );
  }

  // ── Scrollable Content ──

  Widget _buildContent(ScrollController controller) {
    final pos = _data?['position'] as Map<String, dynamic>? ?? {};
    final gochara = _data?['gochara'] as Map<String, dynamic>? ?? {};
    final aspects = _data?['natal_aspects'] as List? ?? [];
    final upcoming = _data?['upcoming'] as List? ?? [];
    final signInterp = _data?['sign_interpretation'] as Map<String, dynamic>?;
    final houseInterp = _data?['house_interpretation'] as Map<String, dynamic>?;
    final transitHouse = _data?['transit_house'] as int?;

    return ListView(
      controller: controller,
      padding: const EdgeInsets.symmetric(horizontal: S.lg),
      children: [
        const SizedBox(height: S.sm),

        // Educational context
        Text(
          'How ${planetName(widget.planet)} is influencing your chart right now',
          style: T.caption.copyWith(color: _color, fontStyle: FontStyle.italic),
        ),
        const SizedBox(height: S.md),

        // B. Position card
        _buildPositionCard(pos),
        const SizedBox(height: S.md),

        // Sign interpretation from knowledge
        if (signInterp != null) ...[
          _buildInterpretationCard(
            icon: Icons.auto_awesome_outlined,
            title: '${planetName(widget.planet)} in ${pos['rashi'] ?? ''}',
            interpretation: signInterp,
          ),
          const SizedBox(height: S.md),
        ],

        // House interpretation from knowledge
        if (houseInterp != null && transitHouse != null) ...[
          _buildInterpretationCard(
            icon: Icons.house_outlined,
            title: '${planetName(widget.planet)} in ${_ordinal(transitHouse)} House',
            interpretation: houseInterp,
          ),
          const SizedBox(height: S.md),
        ],

        // C. Gochara
        if (gochara.isNotEmpty) ...[
          _buildGocharaCard(gochara),
          const SizedBox(height: S.md),
        ],

        // D. Active aspects
        if (aspects.isNotEmpty) ...[
          _buildSectionLabel('Active Aspects'),
          const SizedBox(height: S.sm),
          ...aspects.take(8).map((a) => _AspectCard(aspect: a as Map<String, dynamic>)),
          const SizedBox(height: S.md),
        ],

        // E. Upcoming events
        if (upcoming.isNotEmpty) ...[
          _buildSectionLabel('Upcoming Events'),
          const SizedBox(height: S.sm),
          ...upcoming.take(6).map((u) => _UpcomingCard(event: u as Map<String, dynamic>)),
        ],

        const SizedBox(height: S.xl),
      ],
    );
  }

  // ── B. Position Card ──

  Widget _buildPositionCard(Map<String, dynamic> pos) {
    final rashi = pos['rashi'] as String? ?? '';
    final nakshatra = pos['nakshatra'] as String? ?? '';
    final pada = pos['nakshatra_pada'] as int? ?? 0;
    final degree = (pos['degree_in_rashi'] as num?)?.toStringAsFixed(2) ?? '0.00';
    final speed = (pos['speed'] as num?)?.toStringAsFixed(4) ?? '0.0000';
    final isRetro = pos['is_retrograde'] as bool? ?? false;

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.explore_outlined, color: C.accent, size: 18),
              const SizedBox(width: 6),
              Text('Position',
                style: T.bodySm.copyWith(color: C.textPrimary, fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: S.sm),
          _infoRow('Sign', rashi),
          _infoRow('Degree', '$degree\u00b0'),
          if (nakshatra.isNotEmpty) _infoRow('Nakshatra', '$nakshatra${pada > 0 ? ' Pada $pada' : ''}'),
          _infoRow('Speed', '$speed\u00b0/day'),
          _infoRow('Direction', isRetro ? 'Retrograde' : 'Direct'),
        ],
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          SizedBox(
            width: 90,
            child: Text(label, style: T.caption.copyWith(color: C.textMuted)),
          ),
          Expanded(
            child: Text(value, style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 13)),
          ),
        ],
      ),
    );
  }

  // ── C. Gochara Card ──

  Widget _buildGocharaCard(Map<String, dynamic> gochara) {
    final house = gochara['house_from_moon'] as int? ?? 0;
    final isFavorable = gochara['is_favorable'] as bool? ?? gochara['favorable'] as bool? ?? false;
    final netEffect = gochara['net_effect'] as String? ?? (isFavorable ? 'favorable' : 'unfavorable');
    final effects = gochara['effects'] as List? ?? [];
    final hasVedha = gochara['has_vedha'] as bool? ?? false;
    final vedhaBy = gochara['vedha_by'] as String? ?? '';

    final effectColor = netEffect == 'favorable' ? C.positive : C.negative;

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                netEffect == 'favorable' ? Icons.thumb_up_outlined : Icons.thumb_down_outlined,
                color: effectColor, size: 18,
              ),
              const SizedBox(width: 6),
              Text('Gochara',
                style: T.bodySm.copyWith(color: C.textPrimary, fontWeight: FontWeight.w600)),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  borderRadius: R.smBr,
                  color: effectColor.withValues(alpha: 0.15),
                ),
                child: Text(
                  netEffect[0].toUpperCase() + netEffect.substring(1),
                  style: T.caption.copyWith(color: effectColor, fontSize: 10, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
          const SizedBox(height: S.sm),
          _infoRow('House from Moon', '${_ordinal(house)} house'),
          if (hasVedha && vedhaBy.isNotEmpty)
            _infoRow('Vedha by', planetName(vedhaBy)),
          if (effects.isNotEmpty) ...[
            const SizedBox(height: 4),
            ...effects.map((e) {
              final eStr = '$e';
              final isPositive = !eStr.toLowerCase().contains('loss') &&
                  !eStr.toLowerCase().contains('obstacle') &&
                  !eStr.toLowerCase().contains('conflict') &&
                  !eStr.toLowerCase().contains('expense');
              return Padding(
                padding: const EdgeInsets.only(bottom: 2),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('\u2022 ', style: T.caption.copyWith(
                      color: isPositive ? C.positive : C.negative,
                    )),
                    Expanded(child: Text(eStr, style: T.caption.copyWith(color: C.textSecondary))),
                  ],
                ),
              );
            }),
          ],
        ],
      ),
    );
  }

  String _ordinal(int n) {
    if (n >= 11 && n <= 13) return '${n}th';
    switch (n % 10) {
      case 1: return '${n}st';
      case 2: return '${n}nd';
      case 3: return '${n}rd';
      default: return '${n}th';
    }
  }

  // ── Interpretation card (sign / house from knowledge) ──

  Widget _buildInterpretationCard({
    required IconData icon,
    required String title,
    required Map<String, dynamic> interpretation,
  }) {
    final summary = interpretation['summary'] as String? ?? '';
    final positive = (interpretation['positive'] as List?)?.cast<String>() ?? [];
    final negative = (interpretation['negative'] as List?)?.cast<String>() ?? [];
    final career = interpretation['career'] as String? ?? '';
    final health = interpretation['health'] as String? ?? '';

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: _color, size: 18),
              const SizedBox(width: 6),
              Expanded(
                child: Text(title,
                  style: T.bodySm.copyWith(color: _color, fontWeight: FontWeight.w600)),
              ),
            ],
          ),
          if (summary.isNotEmpty) ...[
            const SizedBox(height: S.sm),
            Text(summary, style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 13)),
          ],
          if (positive.isNotEmpty) ...[
            const SizedBox(height: S.sm),
            ...positive.take(3).map((e) => Padding(
              padding: const EdgeInsets.only(bottom: 2),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('+ ', style: T.caption.copyWith(color: C.positive, fontWeight: FontWeight.w700)),
                  Expanded(child: Text(e, style: T.caption.copyWith(color: C.textSecondary, fontSize: 11))),
                ],
              ),
            )),
          ],
          if (negative.isNotEmpty) ...[
            const SizedBox(height: 2),
            ...negative.take(2).map((e) => Padding(
              padding: const EdgeInsets.only(bottom: 2),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('- ', style: T.caption.copyWith(color: C.negative, fontWeight: FontWeight.w700)),
                  Expanded(child: Text(e, style: T.caption.copyWith(color: C.textSecondary, fontSize: 11))),
                ],
              ),
            )),
          ],
          if (career.isNotEmpty || health.isNotEmpty) ...[
            const SizedBox(height: S.sm),
            if (career.isNotEmpty)
              _infoRow('Career', career),
            if (health.isNotEmpty)
              _infoRow('Health', health),
          ],
        ],
      ),
    );
  }

  // ── Section label ──

  Widget _buildSectionLabel(String title) {
    return Text(title,
      style: T.bodySm.copyWith(color: _color, fontWeight: FontWeight.w600));
  }

  // ── Ask AI Button ──

  Widget _buildAskAiButton() {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.md),
        child: SizedBox(
          width: double.infinity,
          height: 44,
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.of(context).pop();
              context.push('/chat?prompt=${Uri.encodeComponent("Tell me about ${planetName(widget.planet)}'s transit right now and how it's affecting me")}');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: _color,
              foregroundColor: C.surface,
            ),
            icon: const Icon(Icons.auto_awesome, size: 16),
            label: Text('Ask about ${planetName(widget.planet)} transit'),
          ),
        ),
      ),
    );
  }
}

// ── Aspect Card ──

class _AspectCard extends StatelessWidget {
  final Map<String, dynamic> aspect;
  const _AspectCard({required this.aspect});

  @override
  Widget build(BuildContext context) {
    final transit = aspect['transit_planet'] as String? ?? '';
    final natal = aspect['natal_planet'] as String? ?? '';
    final type = aspect['aspect_type'] as String? ?? '';
    final orb = (aspect['orb'] as num?)?.toStringAsFixed(1) ?? '0.0';
    final applying = aspect['applying'] as bool? ?? false;
    final effect = aspect['effect'] as String? ?? '';
    final nature = aspect['nature'] as String? ?? '';

    final natureColor = switch (nature) {
      'harmonious' => C.positive,
      'tense' => C.negative,
      'intense' => C.warning,
      'challenging' => C.negative,
      _ => C.textSecondary,
    };

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: GlassContainer(
        padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
        blur: 0,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Transit → Natal glyph pair
                Text(planetGlyph(transit), style: TextStyle(fontSize: 16, color: planetColor(transit))),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: Text(
                    _aspectSymbol(type),
                    style: TextStyle(fontSize: 12, color: natureColor),
                  ),
                ),
                Text(planetGlyph(natal), style: TextStyle(fontSize: 16, color: planetColor(natal))),
                const SizedBox(width: S.sm),
                // Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${planetName(transit)} ${_aspectLabel(type)} ${planetName(natal)}',
                        style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 12),
                      ),
                      Text(
                        '${applying ? "Applying" : "Separating"} \u2022 Orb $orb\u00b0',
                        style: T.caption.copyWith(fontSize: 10),
                      ),
                    ],
                  ),
                ),
                // Nature badge
                if (nature.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      borderRadius: R.smBr,
                      color: natureColor.withValues(alpha: 0.15),
                    ),
                    child: Text(
                      nature,
                      style: T.caption.copyWith(
                        color: natureColor,
                        fontSize: 9,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  )
                else
                  Container(
                    width: 8, height: 8,
                    decoration: BoxDecoration(shape: BoxShape.circle, color: natureColor),
                  ),
              ],
            ),
            // WHAT effect text
            if (effect.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                effect,
                style: T.caption.copyWith(
                  color: C.textSecondary,
                  fontSize: 11,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _aspectSymbol(String type) {
    if (type.contains('conjunction')) return '\u260C';
    if (type.contains('opposition')) return '\u260D';
    if (type.contains('trine')) return '\u25B3';
    if (type.contains('square')) return '\u25A1';
    if (type.contains('sextile')) return '\u2731';
    return '\u2022';
  }

  String _aspectLabel(String type) {
    if (type.contains('conjunction')) return 'conjunct';
    if (type.contains('opposition')) return 'opposite';
    if (type.contains('trine')) return 'trine';
    if (type.contains('square')) return 'square';
    if (type.contains('sextile')) return 'sextile';
    if (type.contains('parashari')) return 'aspects';
    return type;
  }
}

// ── Upcoming Event Card ──

class _UpcomingCard extends StatefulWidget {
  final Map<String, dynamic> event;
  const _UpcomingCard({required this.event});

  @override
  State<_UpcomingCard> createState() => _UpcomingCardState();
}

class _UpcomingCardState extends State<_UpcomingCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final event = widget.event;
    final date = event['date'] as String? ?? '';
    final daysFromNow = event['days_from_now'] as int? ?? event['days'] as int? ?? 0;
    final significance = event['significance'] as String? ?? 'medium';

    // Construct trigger text from fields if 'trigger' is missing
    var trigger = event['trigger'] as String? ?? event['description'] as String? ?? '';
    if (trigger.isEmpty) {
      final tp = event['transit_planet'] as String? ?? '';
      final np = event['natal_planet'] as String? ?? '';
      final at = event['aspect_type'] as String? ?? '';
      if (tp.isNotEmpty && np.isNotEmpty) {
        final aspectLabel = _aspectLabel(at);
        trigger = '${planetName(tp)} $aspectLabel ${planetName(np)}';
      }
    }

    final effect = event['what'] as String? ?? event['effect'] as String? ?? '';
    final nature = event['nature'] as String? ?? '';

    final Color sigColor;
    switch (significance) {
      case 'high': sigColor = C.warning;
      case 'low': sigColor = C.textMuted;
      default: sigColor = C.textSecondary;
    }

    final natureColor = switch (nature) {
      'harmonious' => C.positive,
      'tense' => C.negative,
      'intense' => C.warning,
      'challenging' => C.negative,
      _ => C.textSecondary,
    };

    return GestureDetector(
      onTap: effect.isNotEmpty ? () => setState(() => _expanded = !_expanded) : null,
      child: Padding(
        padding: const EdgeInsets.only(bottom: S.sm),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Days countdown
            SizedBox(
              width: 44,
              child: Column(
                children: [
                  Text(
                    '$daysFromNow',
                    style: T.h3.copyWith(fontSize: 16, color: sigColor),
                  ),
                  Text(
                    daysFromNow == 1 ? 'day' : 'days',
                    style: T.caption.copyWith(fontSize: 9),
                  ),
                ],
              ),
            ),
            // Vertical line + dot
            Column(
              children: [
                Container(
                  width: 8, height: 8,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: sigColor,
                  ),
                ),
                Container(
                  width: 1, height: _expanded ? 56 : 36,
                  color: C.glassBorder,
                ),
              ],
            ),
            const SizedBox(width: S.sm),
            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          trigger,
                          style: T.bodySm.copyWith(color: C.textPrimary, fontSize: 13),
                        ),
                      ),
                      if (nature.isNotEmpty)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                          decoration: BoxDecoration(
                            borderRadius: R.smBr,
                            color: natureColor.withValues(alpha: 0.15),
                          ),
                          child: Text(
                            nature,
                            style: T.caption.copyWith(
                              color: natureColor, fontSize: 8, fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      if (effect.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(left: 4),
                          child: Icon(
                            _expanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                            size: 16,
                            color: C.textMuted,
                          ),
                        ),
                    ],
                  ),
                  if (effect.isNotEmpty && _expanded) ...[
                    const SizedBox(height: 3),
                    Text(
                      effect,
                      style: T.caption.copyWith(
                        color: C.textSecondary,
                        fontSize: 10,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                  if (date.isNotEmpty)
                    Text(
                      _formatDate(date),
                      style: T.caption.copyWith(fontSize: 10),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _aspectLabel(String type) {
    if (type.contains('conjunction')) return 'conjunct';
    if (type.contains('opposition')) return 'opposite';
    if (type.contains('trine')) return 'trine';
    if (type.contains('square')) return 'square';
    if (type.contains('sextile')) return 'sextile';
    if (type.contains('parashari')) return 'aspects';
    return type.isEmpty ? 'aspects' : type;
  }

  String _formatDate(String iso) {
    try {
      final dt = DateTime.parse(iso);
      const months = [
        '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
      ];
      return '${months[dt.month]} ${dt.day}, ${dt.year}';
    } catch (_) {
      return iso;
    }
  }
}
