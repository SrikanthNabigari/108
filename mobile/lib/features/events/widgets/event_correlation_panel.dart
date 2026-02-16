import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';

// ---------------------------------------------------------------------------
// Mock correlation data
// ---------------------------------------------------------------------------

final _kMockCorrelation = <String, dynamic>{
  'correlation_score': 82,
  'dasha_at_event': {
    'md': 'Mercury',
    'ad': 'Venus',
    'pd': 'Jupiter',
  },
  'transit_at_event': {
    'notable': [
      'Jupiter transiting 9th house (fortune)',
      'Saturn aspecting 10th house (career pressure)',
    ],
  },
  'yogas_active': ['Gajakesari Yoga', 'Budhaditya Yoga'],
  'explanation':
      'This event correlates strongly with your Mercury Mahadasha and Venus '
      'Antardasha — a period favoring professional recognition and financial '
      'gains. Jupiter transiting your 9th house amplified fortune, while '
      'active Gajakesari Yoga provided wisdom and social elevation.',
};

// ===========================================================================
// Bottom sheet panel
// ===========================================================================

class EventCorrelationPanel extends StatefulWidget {
  final Map<String, dynamic> event;

  const EventCorrelationPanel({super.key, required this.event});

  static void show(BuildContext context, Map<String, dynamic> event) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => EventCorrelationPanel(event: event),
    );
  }

  @override
  State<EventCorrelationPanel> createState() =>
      _EventCorrelationPanelState();
}

class _EventCorrelationPanelState extends State<EventCorrelationPanel> {
  Map<String, dynamic>? _correlation;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    // If correlation_score exists, the event was already correlated
    if (widget.event['correlation_score'] != null) {
      _correlation = _kMockCorrelation;
    }
  }

  Future<void> _correlate() async {
    setState(() => _loading = true);
    final id = widget.event['id'].toString();

    try {
      final result = await ApiService().post<Map<String, dynamic>>(
        ApiConstants.eventCorrelate(id),
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (!mounted) return;
      setState(() {
        _correlation = result;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _correlation = _kMockCorrelation;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      minChildSize: 0.4,
      maxChildSize: 0.92,
      builder: (_, scrollCtrl) => Container(
        decoration: const BoxDecoration(
          color: C.surface,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: ListView(
          controller: scrollCtrl,
          padding: S.pagePadding.copyWith(top: S.lg, bottom: S.xxxl),
          children: [
            // Drag handle
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
            const SizedBox(height: S.xl),

            // Header
            _buildHeader(),
            const SizedBox(height: S.xl),

            // Correlation content
            if (_correlation == null && !_loading)
              _buildCorrelateButton()
            else if (_loading)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: S.xxxl),
                child: Center(
                  child: CircularProgressIndicator(
                      strokeWidth: 2, color: C.accent),
                ),
              )
            else
              _buildCorrelationResult(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    final type = (widget.event['event_type'] as String?) ?? '';
    final desc = (widget.event['event_description'] as String?) ?? '';
    final date = (widget.event['event_date'] as String?) ?? '';
    final color = _colorFor(type);
    final icon = _iconFor(type);

    return Row(
      children: [
        Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withValues(alpha: 0.12),
          ),
          child: Icon(icon, color: color, size: 22),
        ),
        const SizedBox(width: S.md),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(desc,
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w500),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis),
              const SizedBox(height: S.xs),
              Text(date, style: T.caption),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCorrelateButton() {
    return Column(
      children: [
        Icon(Icons.auto_awesome, color: C.jupiter, size: 40),
        const SizedBox(height: S.md),
        Text(
          'Discover how this event connects to your chart',
          style: T.bodySm,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: S.lg),
        ElevatedButton(
          onPressed: _correlate,
          child: const Text('Correlate with Chart'),
        ),
      ],
    );
  }

  Widget _buildCorrelationResult() {
    final c = _correlation!;
    final score = (c['correlation_score'] as num?)?.toDouble() ?? 0;
    final dasha =
        (c['dasha_at_event'] as Map<String, dynamic>?) ?? {};
    final yogas =
        (c['yogas_active'] as List<dynamic>?)?.cast<String>() ?? [];
    final explanation = (c['explanation'] as String?) ?? '';
    final transits = (c['transit_at_event'] as Map<String, dynamic>?) ?? {};
    final notableTransits =
        (transits['notable'] as List<dynamic>?)?.cast<String>() ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Score ring
        Center(
          child: Column(
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _scoreColor(score).withValues(alpha: 0.12),
                  border: Border.all(
                      color: _scoreColor(score).withValues(alpha: 0.3),
                      width: 3),
                ),
                child: Center(
                  child: Text(
                    '${score.toInt()}',
                    style: T.h2.copyWith(
                      color: _scoreColor(score),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
              const SizedBox(height: S.sm),
              Text('Correlation Score', style: T.caption),
            ],
          ),
        ),
        const SizedBox(height: S.xl),

        // Dasha at event
        if (dasha.isNotEmpty) ...[
          Text('Dasha at Event',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          Wrap(
            spacing: S.sm,
            runSpacing: S.sm,
            children: [
              if (dasha['md'] != null) _dashaPill('MD', dasha['md']),
              if (dasha['ad'] != null) _dashaPill('AD', dasha['ad']),
              if (dasha['pd'] != null) _dashaPill('PD', dasha['pd']),
            ],
          ),
          const SizedBox(height: S.xl),
        ],

        // Notable transits
        if (notableTransits.isNotEmpty) ...[
          Text('Notable Transits',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          ...notableTransits.map((t) => Padding(
                padding: const EdgeInsets.only(bottom: S.xs),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      margin: const EdgeInsets.only(top: 6, right: S.sm),
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        color: C.jupiter,
                      ),
                    ),
                    Expanded(child: Text(t, style: T.bodySm)),
                  ],
                ),
              )),
          const SizedBox(height: S.xl),
        ],

        // Active yogas
        if (yogas.isNotEmpty) ...[
          Text('Active Yogas',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          Wrap(
            spacing: S.sm,
            runSpacing: S.sm,
            children: yogas
                .map((y) => Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: S.md, vertical: S.sm),
                      decoration: BoxDecoration(
                        color: C.positive.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(
                            color: C.positive.withValues(alpha: 0.15)),
                      ),
                      child: Text(y,
                          style: T.bodySm.copyWith(
                              color: C.positive,
                              fontWeight: FontWeight.w500,
                              fontSize: 12)),
                    ))
                .toList(),
          ),
          const SizedBox(height: S.xl),
        ],

        // Explanation
        if (explanation.isNotEmpty)
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Analysis',
                    style: T.bodySm.copyWith(
                        color: C.textPrimary,
                        fontWeight: FontWeight.w600)),
                const SizedBox(height: S.sm),
                Text(explanation,
                    style: T.bodySm.copyWith(height: 1.6)),
              ],
            ),
          ),
      ],
    );
  }

  // Helpers

  Widget _dashaPill(String level, String planet) {
    final p = planet.toLowerCase();
    final color = planetColor(p);
    return Container(
      padding:
          const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(planetGlyph(p),
              style: TextStyle(fontSize: 14, color: color)),
          const SizedBox(width: S.xs),
          Text(
            '$level: $planet',
            style: T.bodySm.copyWith(
                color: color,
                fontWeight: FontWeight.w600,
                fontSize: 12),
          ),
        ],
      ),
    );
  }

  Color _scoreColor(double s) {
    if (s >= 70) return C.positive;
    if (s >= 40) return C.warning;
    return C.negative;
  }

  Color _colorFor(String type) {
    const map = <String, Color>{
      'career': C.saturn, 'marriage': C.venus, 'health': C.sun,
      'money': C.jupiter, 'education': C.mercury, 'travel': C.rahu,
      'loss': C.mars, 'children': C.moon, 'property': C.ketu,
      'spiritual': C.ketu,
    };
    return map[type] ?? C.accent;
  }

  IconData _iconFor(String type) {
    const map = <String, IconData>{
      'career': Icons.work, 'marriage': Icons.favorite,
      'health': Icons.favorite_border, 'money': Icons.account_balance_wallet,
      'education': Icons.school, 'travel': Icons.flight,
      'loss': Icons.sentiment_dissatisfied, 'children': Icons.child_care,
      'property': Icons.home, 'spiritual': Icons.self_improvement,
    };
    return map[type] ?? Icons.event;
  }
}
