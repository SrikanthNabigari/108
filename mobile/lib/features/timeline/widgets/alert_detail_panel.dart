import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';

/// Bottom sheet panel showing rich details for Sade Sati / Dhaiya alerts.
///
/// Data is passed in directly (no API fetch needed).
class AlertDetailPanel extends StatelessWidget {
  final Map<String, dynamic> alert;

  const AlertDetailPanel({super.key, required this.alert});

  /// Show the alert detail panel as a modal bottom sheet.
  static void show(BuildContext context,
      {required Map<String, dynamic> alert}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => AlertDetailPanel(alert: alert),
    );
  }

  @override
  Widget build(BuildContext context) {
    final type = alert['type'] as String? ?? '';
    final isSadeSati = type == 'sade_sati';

    return DraggableScrollableSheet(
      initialChildSize: 0.72,
      minChildSize: 0.4,
      maxChildSize: 0.9,
      builder: (context, scrollController) {
        return Container(
          decoration: BoxDecoration(
            color: C.surface,
            borderRadius:
                const BorderRadius.vertical(top: Radius.circular(R.xl)),
          ),
          child: Column(
            children: [
              _buildHeader(isSadeSati),
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: S.lg),
                  children: [
                    const SizedBox(height: S.sm),
                    if (isSadeSati)
                      ..._buildSadeSatiContent()
                    else
                      ..._buildDhaiyaContent(),
                    const SizedBox(height: S.xl),
                  ],
                ),
              ),
              _buildAskAiButton(context, isSadeSati),
            ],
          ),
        );
      },
    );
  }

  // ── Header ──

  Widget _buildHeader(bool isSadeSati) {
    final phase = alert['phase'] as String? ?? '';
    final dhaiyaType = alert['dhaiya_type'] as String? ?? '';

    final String title;
    final String? badge;
    if (isSadeSati) {
      title = 'Sade Sati';
      badge = phase.isNotEmpty
          ? '${phase[0].toUpperCase()}${phase.substring(1)} Phase'
          : null;
    } else {
      title = dhaiyaType == 'kantaka_shani'
          ? 'Kantaka Shani'
          : 'Ashtama Shani';
      badge = 'Dhaiya';
    }

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius:
            const BorderRadius.vertical(top: Radius.circular(R.xl)),
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            C.saturn.withValues(alpha: 0.25),
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
          Row(
            children: [
              Text('\u2644',
                  style: TextStyle(fontSize: 28, color: C.saturn)),
              const SizedBox(width: S.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(title,
                            style: T.h2.copyWith(color: C.saturn)),
                        if (badge != null) ...[
                          const SizedBox(width: S.sm),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: S.sm, vertical: 2),
                            decoration: BoxDecoration(
                              borderRadius: R.xlBr,
                              color: C.saturn.withValues(alpha: 0.15),
                              border: Border.all(
                                  color: C.saturn.withValues(alpha: 0.3)),
                            ),
                            child: Text(badge,
                                style: T.caption.copyWith(
                                    color: C.saturn, fontSize: 10)),
                          ),
                        ],
                      ],
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

  // ── Sade Sati Content ──

  List<Widget> _buildSadeSatiContent() {
    final phase = alert['phase'] as String? ?? '';
    final effects = (alert['effects'] as List?)?.cast<String>() ?? [];
    final remedies = (alert['remedies'] as List?)?.cast<String>() ?? [];
    final houseFromMoon = alert['house_from_moon'];
    final durationYears = alert['duration_years'];

    final phaseDates = alert['phase_dates'] as Map<String, dynamic>?;
    final remaining = _remainingInPhase(phase, phaseDates);

    return [
      // Phase progress bar
      _buildPhaseProgress(phase),
      const SizedBox(height: S.sm),

      // Phase timeline with dates
      if (phaseDates != null && phaseDates.isNotEmpty)
        _buildPhaseTimeline(phase, phaseDates),
      if (phaseDates != null && phaseDates.isNotEmpty)
        const SizedBox(height: S.sm),

      // Remaining time
      if (remaining != null) ...[
        _buildInfoRow(Icons.timelapse, 'Remaining', remaining),
        const SizedBox(height: S.sm),
      ],

      // Educational card
      _buildEducationalCard(
        'What is Sade Sati?',
        'Sade Sati is a 7.5-year period when Saturn transits through the 12th, 1st, '
            'and 2nd houses from your natal Moon. It tests patience, builds resilience, '
            'and often brings significant life lessons.',
      ),
      const SizedBox(height: S.md),

      // Duration
      if (durationYears != null)
        _buildInfoRow(Icons.schedule, 'Duration',
            '2.5 years per phase \u00b7 7.5 years total'),
      if (houseFromMoon != null) ...[
        const SizedBox(height: 4),
        _buildInfoRow(Icons.home_outlined, 'Saturn Position',
            'House $houseFromMoon from your Moon'),
      ],

      // Effects
      if (effects.isNotEmpty) ...[
        const SizedBox(height: S.md),
        _buildListSection('Effects During This Phase', effects,
            icon: Icons.circle, iconColor: C.saturn),
      ],

      // Remedies
      if (remedies.isNotEmpty) ...[
        const SizedBox(height: S.md),
        _ExpandableRemedies(remedies: remedies),
      ],
    ];
  }

  // ── Dhaiya Content ──

  List<Widget> _buildDhaiyaContent() {
    final dhaiyaType = alert['dhaiya_type'] as String? ?? '';
    final effects = (alert['effects'] as List?)?.cast<String>() ?? [];
    final remedies = (alert['remedies'] as List?)?.cast<String>() ?? [];
    final houseFromMoon = alert['house_from_moon'];

    final isKantaka = dhaiyaType == 'kantaka_shani';
    final houseLabel = isKantaka ? '4th' : '8th';

    final phaseDates = alert['phase_dates'] as Map<String, dynamic>?;
    final phaseKey = isKantaka ? 'kantaka_shani' : 'ashtama_shani';
    final dates = phaseDates?[phaseKey] as Map<String, dynamic>?;
    final dateRange = _formatPhaseRange(dates);
    final remaining = _remainingFromDates(dates);

    return [
      // Educational card
      _buildEducationalCard(
        'What is Dhaiya?',
        'Dhaiya (Small Panoti) is a 2.5-year period when Saturn transits '
            'the $houseLabel house from your natal Moon. '
            '${isKantaka ? "Kantaka Shani affects domestic life, property, and mental peace." : "Ashtama Shani brings sudden obstacles, health concerns, and hidden challenges."}',
      ),
      const SizedBox(height: S.md),

      // Duration & house with dates
      _buildInfoRow(Icons.schedule, 'Duration',
          dateRange != null ? '2.5 years ($dateRange)' : '2.5 years'),
      if (remaining != null) ...[
        const SizedBox(height: 4),
        _buildInfoRow(Icons.timelapse, 'Remaining', remaining),
      ],
      if (houseFromMoon != null) ...[
        const SizedBox(height: 4),
        _buildInfoRow(Icons.home_outlined, 'Saturn Position',
            'House $houseFromMoon from your Moon'),
      ],

      // Effects
      if (effects.isNotEmpty) ...[
        const SizedBox(height: S.md),
        _buildListSection('Effects', effects,
            icon: Icons.circle, iconColor: C.saturn),
      ],

      // Remedies
      if (remedies.isNotEmpty) ...[
        const SizedBox(height: S.md),
        _ExpandableRemedies(remedies: remedies),
      ],
    ];
  }

  // ── Phase Progress (Sade Sati) ──

  Widget _buildPhaseProgress(String activePhase) {
    const phases = ['rising', 'peak', 'setting'];
    const labels = ['Rising', 'Peak', 'Setting'];
    final phaseDates = alert['phase_dates'] as Map<String, dynamic>?;

    return Row(
      children: List.generate(3, (i) {
        final isActive = phases[i] == activePhase.toLowerCase();
        final dates = phaseDates?[phases[i]] as Map<String, dynamic>?;
        final dateLabel = _formatPhaseRange(dates);
        return Expanded(
          child: Container(
            margin: EdgeInsets.only(right: i < 2 ? 4 : 0),
            padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 2),
            decoration: BoxDecoration(
              borderRadius: R.smBr,
              color: isActive
                  ? C.saturn.withValues(alpha: 0.25)
                  : C.saturn.withValues(alpha: 0.06),
              border: Border.all(
                color: isActive
                    ? C.saturn.withValues(alpha: 0.5)
                    : C.saturn.withValues(alpha: 0.12),
              ),
            ),
            child: Column(
              children: [
                Text(
                  labels[i],
                  textAlign: TextAlign.center,
                  style: T.caption.copyWith(
                    color: isActive ? C.saturn : C.textMuted,
                    fontWeight: isActive ? FontWeight.w600 : FontWeight.normal,
                    fontSize: 10,
                  ),
                ),
                if (dateLabel != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    dateLabel,
                    textAlign: TextAlign.center,
                    style: T.caption.copyWith(
                      color: isActive
                          ? C.saturn.withValues(alpha: 0.8)
                          : C.textMuted.withValues(alpha: 0.7),
                      fontSize: 8,
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      }),
    );
  }

  /// Format a phase date range like "Jan 2024 \u2014 Mar 2026".
  String? _formatPhaseRange(Map<String, dynamic>? dates) {
    if (dates == null) return null;
    final start = dates['start'] as String?;
    final end = dates['end'] as String?;
    if (start == null || start.isEmpty) return null;
    final startLabel = _shortDate(start);
    final endLabel = (end != null && end.isNotEmpty) ? _shortDate(end) : '...';
    return '$startLabel \u2014 $endLabel';
  }

  /// Convert "YYYY-MM-DD" to "Mon YYYY".
  String _shortDate(String iso) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    try {
      final dt = DateTime.parse(iso);
      return '${months[dt.month - 1]} ${dt.year}';
    } catch (_) {
      return iso;
    }
  }

  // ── Phase Timeline (vertical timeline for Sade Sati) ──

  Widget _buildPhaseTimeline(String activePhase, Map<String, dynamic> phaseDates) {
    const phases = ['rising', 'peak', 'setting'];
    const labels = ['Rising', 'Peak', 'Setting'];

    return GlassContainer(
      padding: const EdgeInsets.all(S.sm),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Timeline',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: 6),
          ...List.generate(phases.length, (i) {
            final isActive = phases[i] == activePhase.toLowerCase();
            final dates = phaseDates[phases[i]] as Map<String, dynamic>?;
            final start = dates?['start'] as String? ?? '';
            final end = dates?['end'] as String? ?? '';
            final startLabel = start.isNotEmpty ? _shortDate(start) : '';
            final endLabel = end.isNotEmpty ? _shortDate(end) : '';
            final range = startLabel.isNotEmpty
                ? '$startLabel \u2192 $endLabel'
                : '';

            return Padding(
              padding: const EdgeInsets.only(bottom: 2),
              child: Row(
                children: [
                  // Vertical bar indicator
                  Container(
                    width: 3,
                    height: 22,
                    decoration: BoxDecoration(
                      color: isActive
                          ? C.saturn
                          : C.saturn.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    width: 54,
                    child: Text(
                      labels[i],
                      style: T.caption.copyWith(
                        color: isActive ? C.saturn : C.textMuted,
                        fontWeight:
                            isActive ? FontWeight.w600 : FontWeight.normal,
                        fontSize: 10,
                      ),
                    ),
                  ),
                  Expanded(
                    child: Text(
                      range,
                      style: T.caption.copyWith(
                        color: isActive
                            ? C.textSecondary
                            : C.textMuted.withValues(alpha: 0.7),
                        fontSize: 10,
                      ),
                    ),
                  ),
                  if (isActive)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 4, vertical: 1),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(4),
                        color: C.saturn.withValues(alpha: 0.15),
                      ),
                      child: Text('active',
                          style: T.caption.copyWith(
                              color: C.saturn, fontSize: 8)),
                    ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  /// Calculate "X months remaining" for the active Sade Sati phase.
  String? _remainingInPhase(String phase, Map<String, dynamic>? phaseDates) {
    if (phaseDates == null) return null;
    final dates = phaseDates[phase.toLowerCase()] as Map<String, dynamic>?;
    return _remainingFromDates(dates);
  }

  /// Calculate "X months remaining" from a date map with 'end'.
  String? _remainingFromDates(Map<String, dynamic>? dates) {
    if (dates == null) return null;
    final end = dates['end'] as String?;
    if (end == null || end.isEmpty) return null;
    try {
      final endDt = DateTime.parse(end);
      final now = DateTime.now();
      if (endDt.isBefore(now)) return null;
      final diff = endDt.difference(now).inDays;
      if (diff > 365) {
        final years = diff ~/ 365;
        final months = (diff % 365) ~/ 30;
        return months > 0
            ? '$years yr $months mo remaining'
            : '$years yr remaining';
      }
      final months = diff ~/ 30;
      return months > 0 ? '$months months remaining' : '$diff days remaining';
    } catch (_) {
      return null;
    }
  }

  // ── Educational Card ──

  Widget _buildEducationalCard(String title, String text) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.auto_stories, color: C.saturn, size: 20),
          const SizedBox(width: S.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: T.bodySm.copyWith(
                        color: C.textPrimary, fontWeight: FontWeight.w600)),
                const SizedBox(height: 4),
                Text(text,
                    style: T.caption
                        .copyWith(color: C.textSecondary, height: 1.5)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Shared Helpers ──

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

  Widget _buildListSection(String title, List<String> items,
      {required IconData icon, required Color iconColor}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title,
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: 6),
        ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Icon(icon, size: 6, color: iconColor),
                  ),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(item,
                        style: T.caption.copyWith(
                            color: C.textSecondary, height: 1.4)),
                  ),
                ],
              ),
            )),
      ],
    );
  }

  // ── Ask AI Button ──

  Widget _buildAskAiButton(BuildContext context, bool isSadeSati) {
    final label = isSadeSati ? 'Ask about Sade Sati' : 'Ask about Dhaiya';
    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () {
            final prompt = isSadeSati
                ? 'Tell me about my Sade Sati — what phase am I in and how is it affecting me?'
                : 'Tell me about my Dhaiya (small Sade Sati) — what should I know?';
            Navigator.of(context).pop();
            context.push('/chat?prompt=${Uri.encodeComponent(prompt)}');
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: C.saturn,
            foregroundColor: C.bg,
            shape: RoundedRectangleBorder(borderRadius: R.xlBr),
          ),
          icon: const Icon(Icons.auto_awesome, size: 18),
          label: Text(label,
              style: T.bodySm.copyWith(
                  color: C.bg, fontWeight: FontWeight.w600)),
        ),
      ),
    );
  }
}

// ── Expandable Remedies ──

class _ExpandableRemedies extends StatefulWidget {
  final List<String> remedies;

  const _ExpandableRemedies({required this.remedies});

  @override
  State<_ExpandableRemedies> createState() => _ExpandableRemediesState();
}

class _ExpandableRemediesState extends State<_ExpandableRemedies> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        GestureDetector(
          onTap: () => setState(() => _expanded = !_expanded),
          child: Row(
            children: [
              Icon(Icons.healing, size: 14, color: C.positive),
              const SizedBox(width: 6),
              Text('Remedies',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600)),
              const Spacer(),
              Icon(
                _expanded ? Icons.expand_less : Icons.expand_more,
                size: 16,
                color: C.textMuted,
              ),
            ],
          ),
        ),
        if (_expanded) ...[
          const SizedBox(height: 6),
          ...widget.remedies.map((r) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Icon(Icons.circle, size: 4, color: C.positive),
                    ),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(r,
                          style: T.caption.copyWith(
                              color: C.textSecondary, height: 1.4)),
                    ),
                  ],
                ),
              )),
        ],
      ],
    );
  }
}
