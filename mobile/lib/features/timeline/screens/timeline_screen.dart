import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/features/timeline/widgets/dasha_detail_panel.dart';

class TimelineScreen extends ConsumerStatefulWidget {
  const TimelineScreen({super.key});

  @override
  ConsumerState<TimelineScreen> createState() => _TimelineScreenState();
}

class _TimelineScreenState extends ConsumerState<TimelineScreen> {
  Map<String, dynamic>? _dashaData;
  bool _loading = true;
  String? _error;

  final _scrollController = ScrollController();
  double _scrollHintOpacity = 1.0;

  @override
  void initState() {
    super.initState();
    _fetchDasha();
    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    final opacity = (1.0 - (_scrollController.offset / 80)).clamp(0.0, 1.0);
    if (opacity != _scrollHintOpacity) {
      setState(() => _scrollHintOpacity = opacity);
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _fetchDasha() async {
    try {
      final data = await ApiService().get(
        ApiConstants.analysisDasha,
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (mounted) setState(() { _dashaData = data; _loading = false; });
    } catch (e) {
      if (mounted) setState(() { _error = '$e'; _loading = false; });
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
              : _error != null
                  ? _buildError()
                  : Stack(
                      children: [
                        _buildTimeline(),
                        if (_scrollHintOpacity > 0)
                          Positioned(
                            bottom: 16,
                            left: 0,
                            right: 0,
                            child: IgnorePointer(
                              child: Opacity(
                                opacity: _scrollHintOpacity * 0.5,
                                child: TweenAnimationBuilder<double>(
                                  tween: Tween(begin: 0, end: 1),
                                  duration: const Duration(milliseconds: 1200),
                                  builder: (_, val, child) {
                                    // Ping-pong: 0→1→0→1 via sin
                                    final bounce = sin(val * pi) * 6;
                                    return Transform.translate(
                                      offset: Offset(0, bounce),
                                      child: child,
                                    );
                                  },
                                  onEnd: () {
                                    // Re-trigger to loop
                                    if (mounted) setState(() {});
                                  },
                                  child: const Icon(
                                    Icons.keyboard_double_arrow_down,
                                    color: C.textMuted,
                                    size: 24,
                                  ),
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
        ),
      ),
    );
  }

  Widget _buildError() {
    return Padding(
      padding: S.pagePadding,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('Could not load timeline', style: T.h3),
          const SizedBox(height: S.sm),
          Text(_error!, style: T.caption, textAlign: TextAlign.center),
          const SizedBox(height: S.xl),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: () => context.go('/home'),
              child: const Text('Continue to Home'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeline() {
    final current =
        _dashaData?['current'] as Map<String, dynamic>? ?? _dashaData ?? {};
    final mdSequence = _dashaData?['mahadasha_sequence'] as List? ?? [];
    final adSequence = _dashaData?['antardasha_sequence'] as List? ?? [];
    final pdSequence = _dashaData?['pratyantardasha_sequence'] as List? ?? [];
    final alerts = _dashaData?['alerts'] as List? ?? [];

    final mdLord = current['mahadasha_lord'] as String? ?? 'mercury';
    final adLord = current['antardasha_lord'] as String? ?? '';
    final pdLord = current['pratyantardasha_lord'] as String? ?? '';
    final remaining = current['remaining_years'];
    final mdStart = current['mahadasha_start'] as String? ?? '';
    final mdEnd = current['mahadasha_end'] as String? ?? '';

    // MD progress
    double mdProgress = 0;
    if (mdStart.isNotEmpty && mdEnd.isNotEmpty) {
      mdProgress = _calcProgress(mdStart, mdEnd);
    }

    final remainStr =
        remaining != null ? '${(remaining as num).round()}y left' : '';

    return SingleChildScrollView(
      controller: _scrollController,
      padding: S.pagePadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: S.lg),

          // Header
          Center(
            child: Column(
              children: [
                Text('Your Life Timeline', style: T.h2),
                const SizedBox(height: 4),
                Text(
                  'Vimshottari Dasha — your cosmic chapters',
                  style: T.bodySm.copyWith(color: C.textMuted),
                ),
              ],
            ),
          ),

          const SizedBox(height: S.xl),

          // ── Current Period Overview (compact) ──
          GlassContainer(
            padding:
                const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
            child: Row(
              children: [
                // Nested rings
                SizedBox(
                  width: 90,
                  height: 90,
                  child: CustomPaint(
                    painter: _NestedRingsPainter(
                      mdProgress: mdProgress,
                      adProgress: _calcProgressFromCurrent(current, 'antardasha'),
                      pdProgress: pdLord.isNotEmpty
                          ? _calcProgressFromCurrent(current, 'pratyantardasha')
                          : 0,
                      mdColor: _planetColor(mdLord),
                      adColor: _planetColor(adLord),
                      pdColor: pdLord.isNotEmpty
                          ? _planetColor(pdLord)
                          : C.glassBorder,
                      hasPd: pdLord.isNotEmpty,
                    ),
                  ),
                ),
                const SizedBox(width: S.lg),
                // Text info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _Badge(text: 'NOW'),
                      const SizedBox(height: S.sm),
                      Text(
                        '${_planetName(mdLord)} MD',
                        style: T.h3.copyWith(
                            color: _planetColor(mdLord), fontSize: 18),
                      ),
                      if (adLord.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          '${_planetGlyph(adLord)} ${_planetName(adLord)} AD  ·  ${_durationStr(current, 'antardasha')}',
                          style: T.bodySm.copyWith(color: C.textSecondary),
                        ),
                      ],
                      if (pdLord.isNotEmpty) ...[
                        const SizedBox(height: 1),
                        Text(
                          '${_planetGlyph(pdLord)} ${_planetName(pdLord)} PD  ·  ${_durationStr(current, 'pratyantardasha')}',
                          style: T.caption,
                        ),
                      ],
                      const SizedBox(height: S.sm),
                      // Progress
                      Row(
                        children: [
                          Expanded(
                            child: ClipRRect(
                              borderRadius: R.smBr,
                              child: LinearProgressIndicator(
                                value: mdProgress,
                                minHeight: 3,
                                backgroundColor: C.glassBorder,
                                valueColor: AlwaysStoppedAnimation(
                                    _planetColor(mdLord)),
                              ),
                            ),
                          ),
                          const SizedBox(width: S.sm),
                          Text(remainStr,
                              style: T.caption.copyWith(
                                  color: C.accent, fontSize: 10)),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // ── Alerts (Sade Sati, etc.) ──
          if (alerts.isNotEmpty) ...[
            const SizedBox(height: S.md),
            for (final alert in alerts)
              _AlertCard(alert: alert as Map<String, dynamic>),
          ],

          const SizedBox(height: S.xl),

          // ── Row 1: Mahadashas ──
          _SectionLabel(title: 'Mahadasha', subtitle: 'Life Chapters'),
          const SizedBox(height: S.sm),
          SizedBox(
            height: 120,
            child: mdSequence.isNotEmpty
                ? ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: mdSequence.length,
                    separatorBuilder: (_, __) =>
                        const SizedBox(width: S.sm),
                    itemBuilder: (_, i) {
                      final p = mdSequence[i] as Map<String, dynamic>;
                      final lord = p['lord'] as String? ?? 'sun';
                      return _PeriodCard(
                        lord: lord,
                        duration: _yearStr(p['years']),
                        startYear: _yearFromIso(p['start'] as String? ?? ''),
                        endYear: _yearFromIso(p['end'] as String? ?? ''),
                        isCurrent:
                            lord.toLowerCase() == mdLord.toLowerCase(),
                        size: _CardSize.large,
                        onTap: () => DashaDetailPanel.show(
                          context,
                          level: 'md',
                          lord: lord,
                          mdLord: lord,
                          startDate: p['start'] as String? ?? '',
                          endDate: p['end'] as String? ?? '',
                          isCurrent: lord.toLowerCase() == mdLord.toLowerCase(),
                        ),
                      );
                    },
                  )
                : _buildFallbackMD(mdLord),
          ),

          const SizedBox(height: S.xl),

          // ── Row 2: Antardashas ──
          if (adSequence.isNotEmpty) ...[
            _SectionLabel(
              title: 'Antardasha',
              subtitle: 'in ${_planetName(mdLord)} MD',
            ),
            const SizedBox(height: S.sm),
            SizedBox(
              height: 100,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: adSequence.length,
                separatorBuilder: (_, __) =>
                    const SizedBox(width: S.sm),
                itemBuilder: (_, i) {
                  final p = adSequence[i] as Map<String, dynamic>;
                  final lord = p['lord'] as String? ?? 'sun';
                  return _PeriodCard(
                    lord: lord,
                    duration: _monthStr(p['years'], p['start'], p['end']),
                    startYear: _shortDate(p['start'] as String? ?? ''),
                    endYear: _shortDate(p['end'] as String? ?? ''),
                    isCurrent:
                        lord.toLowerCase() == adLord.toLowerCase(),
                    size: _CardSize.medium,
                    onTap: () => DashaDetailPanel.show(
                      context,
                      level: 'ad',
                      lord: lord,
                      mdLord: mdLord,
                      adLord: lord,
                      startDate: p['start'] as String? ?? '',
                      endDate: p['end'] as String? ?? '',
                      isCurrent: lord.toLowerCase() == adLord.toLowerCase(),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: S.xl),
          ],

          // ── Row 3: Pratyantardashas ──
          if (pdSequence.isNotEmpty) ...[
            _SectionLabel(
              title: 'Pratyantardasha',
              subtitle: 'in ${_planetName(adLord)} AD',
            ),
            const SizedBox(height: S.sm),
            SizedBox(
              height: 86,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: pdSequence.length,
                separatorBuilder: (_, __) =>
                    const SizedBox(width: S.xs),
                itemBuilder: (_, i) {
                  final p = pdSequence[i] as Map<String, dynamic>;
                  final lord = p['lord'] as String? ?? 'sun';
                  return _PeriodCard(
                    lord: lord,
                    duration: _monthStr(p['years'], p['start'], p['end']),
                    startYear: '',
                    endYear: '',
                    isCurrent:
                        lord.toLowerCase() == pdLord.toLowerCase(),
                    size: _CardSize.small,
                    onTap: () => DashaDetailPanel.show(
                      context,
                      level: 'pd',
                      lord: lord,
                      mdLord: mdLord,
                      adLord: adLord,
                      pdLord: lord,
                      startDate: p['start'] as String? ?? '',
                      endDate: p['end'] as String? ?? '',
                      isCurrent: lord.toLowerCase() == pdLord.toLowerCase(),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: S.xl),
          ],

          // ── Continue Button ──
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: () => context.go('/home'),
              child: const Text('Continue'),
            ),
          ),
          const SizedBox(height: S.xl),
        ],
      ),
    );
  }

  Widget _buildFallbackMD(String currentLord) {
    const sequence = [
      ('sun', 6), ('moon', 10), ('mars', 7), ('rahu', 18),
      ('jupiter', 16), ('saturn', 19), ('mercury', 17),
      ('ketu', 7), ('venus', 20),
    ];
    return ListView.separated(
      scrollDirection: Axis.horizontal,
      itemCount: sequence.length,
      separatorBuilder: (_, __) => const SizedBox(width: S.sm),
      itemBuilder: (_, i) {
        final (lord, years) = sequence[i];
        return _PeriodCard(
          lord: lord,
          duration: '$years yrs',
          startYear: '',
          endYear: '',
          isCurrent: lord == currentLord.toLowerCase(),
          size: _CardSize.large,
          onTap: () => DashaDetailPanel.show(
            context,
            level: 'md',
            lord: lord,
            mdLord: lord,
            startDate: '',
            endDate: '',
            isCurrent: lord == currentLord.toLowerCase(),
          ),
        );
      },
    );
  }

  // ── Helpers ──

  double _calcProgress(String startIso, String endIso) {
    if (startIso.isEmpty || endIso.isEmpty) return 0;
    try {
      final s = DateTime.parse(startIso);
      final e = DateTime.parse(endIso);
      final total = e.difference(s).inDays;
      final elapsed = DateTime.now().difference(s).inDays;
      return total > 0 ? (elapsed / total).clamp(0.0, 1.0) : 0;
    } catch (_) {
      return 0;
    }
  }

  double _calcProgressFromCurrent(Map<String, dynamic> current, String prefix) {
    final start = current['${prefix}_start'] as String? ?? '';
    final end = current['${prefix}_end'] as String? ?? '';
    return _calcProgress(start, end);
  }

  /// "17 years" or "11 months" or "14 days" from current map's start/end.
  String _durationStr(Map<String, dynamic> current, String prefix) {
    final start = current['${prefix}_start'] as String? ?? '';
    final end = current['${prefix}_end'] as String? ?? '';
    if (start.isEmpty || end.isEmpty) return '';
    return _durationFromIso(start, end);
  }

  String _durationFromIso(String startIso, String endIso) {
    try {
      final s = DateTime.parse(startIso);
      final e = DateTime.parse(endIso);
      final totalDays = e.difference(s).inDays;
      final totalMonths = (totalDays / 30.44).round();
      if (totalMonths >= 24) {
        return '${(totalDays / 365.25).round()} years';
      } else if (totalMonths > 0) {
        return '$totalMonths months';
      } else {
        return '$totalDays days';
      }
    } catch (_) {
      return '';
    }
  }

  String _yearStr(dynamic years) {
    if (years == null) return '';
    return '${(years as num).round()} yrs';
  }

  /// For AD/PD: show months, or days if very short.
  String _monthStr(dynamic years, dynamic start, dynamic end) {
    if (start != null && end != null) {
      final s = start.toString();
      final e = end.toString();
      if (s.isNotEmpty && e.isNotEmpty) {
        return _durationFromIso(s, e);
      }
    }
    if (years == null) return '';
    final y = (years as num).toDouble();
    if (y >= 2) return '${y.round()} yrs';
    final months = (y * 12).round();
    return months > 0 ? '$months mo' : '${(y * 365.25).round()} d';
  }

  /// "Jan 2024" from ISO string.
  String _shortDate(String iso) {
    if (iso.isEmpty) return '';
    try {
      final dt = DateTime.parse(iso);
      const months = [
        '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];
      return '${months[dt.month]} ${dt.year}';
    } catch (_) {
      return _yearFromIso(iso);
    }
  }

  String _yearFromIso(String iso) {
    if (iso.isEmpty) return '';
    try {
      return DateTime.parse(iso).year.toString();
    } catch (_) {
      return iso.length >= 4 ? iso.substring(0, 4) : iso;
    }
  }
}

// ── Shared helpers ──

String _planetGlyph(String planet) {
  const glyphs = {
    'sun': '☉', 'moon': '☽', 'mars': '♂', 'mercury': '☿',
    'jupiter': '♃', 'venus': '♀', 'saturn': '♄',
    'rahu': '☊', 'ketu': '☋',
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

// ── Widgets ──

class _Badge extends StatelessWidget {
  final String text;
  const _Badge({required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: R.xlBr,
        color: C.accentDim,
        border: Border.all(color: C.glassBorder),
      ),
      child: Text(
        text,
        style: T.label.copyWith(
            color: C.accent, letterSpacing: 1.0, fontSize: 9),
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String title;
  final String subtitle;
  const _SectionLabel({required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(title, style: T.h3.copyWith(fontSize: 16)),
        const SizedBox(width: S.sm),
        Text(subtitle, style: T.caption),
      ],
    );
  }
}

enum _CardSize { large, medium, small }

class _PeriodCard extends StatelessWidget {
  final String lord;
  final String duration;
  final String startYear;
  final String endYear;
  final bool isCurrent;
  final _CardSize size;
  final VoidCallback? onTap;

  const _PeriodCard({
    required this.lord,
    required this.duration,
    required this.startYear,
    required this.endYear,
    required this.isCurrent,
    required this.size,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = _planetColor(lord);
    final dateRange = (startYear.isNotEmpty && endYear.isNotEmpty)
        ? '$startYear–$endYear'
        : '';

    final double width;
    final double glyphSize;
    final double nameSize;
    final double durSize;
    final double dateSize;

    switch (size) {
      case _CardSize.large:
        width = 100;
        glyphSize = 20;
        nameSize = 13;
        durSize = 11;
        dateSize = 10;
      case _CardSize.medium:
        width = 90;
        glyphSize = 17;
        nameSize = 12;
        durSize = 10;
        dateSize = 9;
      case _CardSize.small:
        width = 76;
        glyphSize = 15;
        nameSize = 11;
        durSize = 10;
        dateSize = 9;
    }

    return GestureDetector(
      onTap: onTap,
      child: Container(
      width: width,
      padding: const EdgeInsets.symmetric(vertical: S.sm, horizontal: S.xs),
      decoration: BoxDecoration(
        borderRadius: R.lgBr,
        color: isCurrent
            ? color.withValues(alpha: 0.18)
            : color.withValues(alpha: 0.04),
        border: Border.all(
          color: isCurrent
              ? color.withValues(alpha: 0.6)
              : color.withValues(alpha: 0.15),
          width: isCurrent ? 1.5 : 0.5,
        ),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            _planetGlyph(lord),
            style: TextStyle(fontSize: glyphSize, color: color),
          ),
          const SizedBox(height: 3),
          Text(
            _planetName(lord),
            style: T.bodySm.copyWith(
              color: C.textPrimary,
              fontWeight: FontWeight.w600,
              fontSize: nameSize,
            ),
          ),
          const SizedBox(height: 1),
          Text(
            duration,
            style: T.caption.copyWith(color: color, fontSize: durSize),
          ),
          if (dateRange.isNotEmpty) ...[
            const SizedBox(height: 1),
            Text(dateRange,
                style: T.caption.copyWith(fontSize: dateSize),
                overflow: TextOverflow.ellipsis),
          ],
          if (isCurrent && size == _CardSize.large) ...[
            const SizedBox(height: 3),
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: S.sm, vertical: 2),
              decoration: BoxDecoration(
                borderRadius: R.xlBr,
                color: color.withValues(alpha: 0.2),
              ),
              child: Text(
                'NOW',
                style: TextStyle(
                  fontSize: 8,
                  fontWeight: FontWeight.w700,
                  color: color,
                  letterSpacing: 0.8,
                ),
              ),
            ),
          ],
        ],
      ),
    ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final Map<String, dynamic> alert;
  const _AlertCard({required this.alert});

  @override
  Widget build(BuildContext context) {
    final type = alert['type'] as String? ?? '';
    final phase = alert['phase'] as String? ?? '';
    final desc = alert['description'] as String? ?? '';

    final bool isSadeSati = type == 'sade_sati';
    final color = isSadeSati ? C.saturn : C.warning;
    final icon = isSadeSati ? '♄' : '⚠';
    final title = isSadeSati
        ? 'Sade Sati — ${phase[0].toUpperCase()}${phase.substring(1)} Phase'
        : desc;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: color.withValues(alpha: 0.08),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Text(icon, style: TextStyle(fontSize: 18, color: color)),
          const SizedBox(width: S.sm),
          Expanded(
            child: Text(
              title,
              style: T.bodySm.copyWith(color: color, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}

/// Paints three nested concentric progress rings.
class _NestedRingsPainter extends CustomPainter {
  final double mdProgress;
  final double adProgress;
  final double pdProgress;
  final Color mdColor;
  final Color adColor;
  final Color pdColor;
  final bool hasPd;

  _NestedRingsPainter({
    required this.mdProgress,
    required this.adProgress,
    required this.pdProgress,
    required this.mdColor,
    required this.adColor,
    required this.pdColor,
    required this.hasPd,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final maxR = size.width / 2 - 4;

    // Equal visual weight — evenly spaced, same stroke width
    const stroke = 5.0;
    const gap = 9.0;
    final rings = <(double, double, double, Color)>[
      (maxR, stroke, mdProgress, mdColor),
      (maxR - gap - stroke, stroke, adProgress, adColor),
      if (hasPd) (maxR - 2 * (gap + stroke), stroke, pdProgress, pdColor),
    ];

    final bgPaint = Paint()
      ..style = PaintingStyle.stroke
      ..color = C.glassBorder;

    final arcPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    for (final (radius, stroke, progress, color) in rings) {
      bgPaint.strokeWidth = stroke;
      canvas.drawCircle(center, radius, bgPaint);

      arcPaint
        ..strokeWidth = stroke
        ..color = color;
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        -pi / 2,
        2 * pi * progress,
        false,
        arcPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _NestedRingsPainter old) =>
      old.mdProgress != mdProgress ||
      old.adProgress != adProgress ||
      old.pdProgress != pdProgress ||
      old.mdColor != mdColor ||
      old.adColor != adColor ||
      old.pdColor != pdColor;
}
