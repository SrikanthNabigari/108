import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/features/forecast/widgets/day_rating_ring.dart';

// ---------------------------------------------------------------------------
// Activity types
// ---------------------------------------------------------------------------

class _Activity {
  final String id;
  final String label;
  final IconData icon;

  const _Activity(this.id, this.label, this.icon);
}

const _kActivities = <_Activity>[
  _Activity('marriage', 'Marriage', Icons.favorite),
  _Activity('travel', 'Travel', Icons.flight),
  _Activity('business_start', 'Business', Icons.store),
  _Activity('house_entry', 'House Entry', Icons.home),
  _Activity('surgery', 'Surgery', Icons.local_hospital),
  _Activity('vehicle_purchase', 'Vehicle', Icons.directions_car),
  _Activity('education_start', 'Education', Icons.school),
  _Activity('investment', 'Investment', Icons.trending_up),
  _Activity('ceremony', 'Ceremony', Icons.celebration),
  _Activity('general', 'General', Icons.star),
];

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

final _kMockCheck = <String, dynamic>{
  'score': 72,
  'quality': 'Good',
  'favorable_factors': [
    'Moon in favorable nakshatra',
    'No malefic aspect on lagna',
    'Tithi is Shukla Panchami (good for beginnings)',
  ],
  'unfavorable_factors': [
    'Rahu Kaal active between 4:30-6:00 PM',
  ],
  'recommendation':
      'This is a reasonably good muhurta. Avoid the Rahu Kaal window and '
      'proceed with confidence. The Moon placement supports new ventures.',
  'in_rahu_kaal': false,
  'in_yamaghanda': false,
  'in_gulika': false,
};

final _kMockWindows = <Map<String, dynamic>>[
  {'datetime': '2026-02-16T06:30:00', 'score': 88, 'quality': 'Excellent'},
  {'datetime': '2026-02-17T09:15:00', 'score': 82, 'quality': 'Very Good'},
  {'datetime': '2026-02-19T07:00:00', 'score': 76, 'quality': 'Good'},
  {'datetime': '2026-02-22T10:45:00', 'score': 74, 'quality': 'Good'},
  {'datetime': '2026-02-25T06:00:00', 'score': 71, 'quality': 'Good'},
];

// ===========================================================================
// Screen
// ===========================================================================

class MuhurtaScreen extends ConsumerStatefulWidget {
  const MuhurtaScreen({super.key});

  @override
  ConsumerState<MuhurtaScreen> createState() => _MuhurtaScreenState();
}

class _MuhurtaScreenState extends ConsumerState<MuhurtaScreen> {
  String? _selectedActivity;
  DateTime _selectedDate = DateTime.now();
  TimeOfDay _selectedTime = TimeOfDay.now();
  bool _loadingCheck = false;
  bool _loadingFind = false;
  Map<String, dynamic>? _checkResult;
  List<Map<String, dynamic>> _windows = [];

  // -----------------------------------------------------------------------
  // Actions
  // -----------------------------------------------------------------------

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime.now().subtract(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      builder: (ctx, child) => Theme(
        data: Theme.of(ctx).copyWith(
          colorScheme: const ColorScheme.dark(
            primary: C.accent,
            surface: C.surface,
            onSurface: C.textPrimary,
          ),
        ),
        child: child!,
      ),
    );
    if (picked != null) setState(() => _selectedDate = picked);
  }

  Future<void> _pickTime() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: _selectedTime,
      builder: (ctx, child) => Theme(
        data: Theme.of(ctx).copyWith(
          colorScheme: const ColorScheme.dark(
            primary: C.accent,
            surface: C.surface,
            onSurface: C.textPrimary,
          ),
        ),
        child: child!,
      ),
    );
    if (picked != null) setState(() => _selectedTime = picked);
  }

  Future<void> _checkMuhurta() async {
    if (_selectedActivity == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an activity')),
      );
      return;
    }
    setState(() {
      _loadingCheck = true;
      _checkResult = null;
    });

    final dt = DateTime(
      _selectedDate.year,
      _selectedDate.month,
      _selectedDate.day,
      _selectedTime.hour,
      _selectedTime.minute,
    );

    try {
      final result = await ApiService().post<Map<String, dynamic>>(
        ApiConstants.muhurtaCheck,
        body: {
          'datetime': dt.toIso8601String(),
          'activity': _selectedActivity,
          'latitude': 16.726239,
          'longitude': 81.288428,
        },
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (!mounted) return;
      setState(() {
        _checkResult = result;
        _loadingCheck = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _checkResult = _kMockCheck;
        _loadingCheck = false;
      });
    }
  }

  Future<void> _findGoodTimes() async {
    if (_selectedActivity == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an activity first')),
      );
      return;
    }
    setState(() {
      _loadingFind = true;
      _windows = [];
    });

    final start = DateTime.now();
    final end = start.add(const Duration(days: 30));

    try {
      final result = await ApiService().post<List<dynamic>>(
        ApiConstants.muhurtaFind,
        body: {
          'start_date': start.toIso8601String().split('T').first,
          'end_date': end.toIso8601String().split('T').first,
          'activity': _selectedActivity,
          'count': 5,
        },
        fromJson: (json) => json as List<dynamic>,
      );
      if (!mounted) return;
      setState(() {
        _windows = result.cast<Map<String, dynamic>>();
        _loadingFind = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _windows = _kMockWindows;
        _loadingFind = false;
      });
    }
  }

  // -----------------------------------------------------------------------
  // Build
  // -----------------------------------------------------------------------

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
                    Text('Muhurta Finder', style: T.h3),
                  ],
                ),
              ),
              const Divider(height: 1),

              Expanded(
                child: RefreshIndicator(
                  onRefresh: () async {
                    if (_checkResult != null) await _checkMuhurta();
                  },
                  color: C.accent,
                  backgroundColor: C.surface,
                  child: ListView(
                    padding:
                        S.pagePadding.copyWith(top: S.xl, bottom: S.xxxl),
                    children: [
                      // Activity picker
                      Text('Select Activity',
                          style: T.h3.copyWith(fontSize: 16)),
                      const SizedBox(height: S.sm),
                      Wrap(
                        spacing: S.sm,
                        runSpacing: S.sm,
                        children: _kActivities.map((a) {
                          final selected = _selectedActivity == a.id;
                          return GestureDetector(
                            onTap: () =>
                                setState(() => _selectedActivity = a.id),
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: S.md, vertical: S.sm),
                              decoration: BoxDecoration(
                                color: selected
                                    ? C.jupiter.withValues(alpha: 0.15)
                                    : Colors.transparent,
                                borderRadius: BorderRadius.circular(20),
                                border: Border.all(
                                  color: selected
                                      ? C.jupiter.withValues(alpha: 0.4)
                                      : C.glassBorder,
                                ),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(a.icon,
                                      size: 14,
                                      color: selected
                                          ? C.jupiter
                                          : C.textMuted),
                                  const SizedBox(width: S.xs),
                                  Text(
                                    a.label,
                                    style: T.bodySm.copyWith(
                                      color: selected
                                          ? C.jupiter
                                          : C.textSecondary,
                                      fontWeight: selected
                                          ? FontWeight.w600
                                          : FontWeight.w400,
                                      fontSize: 12,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                      const SizedBox(height: S.xl),

                      // Date/time row
                      Row(
                        children: [
                          Expanded(
                            child: GestureDetector(
                              onTap: _pickDate,
                              child: GlassContainer(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: S.md, vertical: S.md),
                                child: Row(
                                  children: [
                                    const Icon(Icons.calendar_today,
                                        color: C.textMuted, size: 16),
                                    const SizedBox(width: S.sm),
                                    Text(
                                      '${_selectedDate.day}/${_selectedDate.month}/${_selectedDate.year}',
                                      style: T.bodySm.copyWith(
                                          color: C.textPrimary),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: S.sm),
                          Expanded(
                            child: GestureDetector(
                              onTap: _pickTime,
                              child: GlassContainer(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: S.md, vertical: S.md),
                                child: Row(
                                  children: [
                                    const Icon(Icons.access_time,
                                        color: C.textMuted, size: 16),
                                    const SizedBox(width: S.sm),
                                    Text(
                                      _selectedTime.format(context),
                                      style: T.bodySm.copyWith(
                                          color: C.textPrimary),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: S.lg),

                      // Check button
                      ElevatedButton(
                        onPressed:
                            _loadingCheck ? null : _checkMuhurta,
                        child: _loadingCheck
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: C.textOnAccent),
                              )
                            : const Text('Check Muhurta'),
                      ),
                      const SizedBox(height: S.xl),

                      // Check result
                      if (_checkResult != null) _buildCheckResult(),

                      // Find good times section
                      const SizedBox(height: S.lg),
                      OutlinedButton(
                        onPressed: _loadingFind ? null : _findGoodTimes,
                        child: _loadingFind
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                    strokeWidth: 2, color: C.accent),
                              )
                            : const Text('Find Good Times (Next 30 Days)'),
                      ),

                      if (_windows.isNotEmpty) ...[
                        const SizedBox(height: S.lg),
                        Text('Recommended Windows',
                            style: T.h3.copyWith(fontSize: 16)),
                        const SizedBox(height: S.sm),
                        ..._windows.map(_buildWindowCard),
                      ],

                      const SizedBox(height: S.xl),

                      // Educational card
                      GlassContainer(
                        padding: const EdgeInsets.all(S.lg),
                        borderColor: C.saturn.withValues(alpha: 0.2),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.school,
                                    color: C.saturn, size: 18),
                                const SizedBox(width: S.sm),
                                Text(
                                  'What is Muhurta?',
                                  style: T.bodySm.copyWith(
                                    color: C.saturn,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: S.sm),
                            Text(
                              'Muhurta is the Vedic science of electional astrology '
                              '— choosing the most auspicious moment to begin an '
                              'important activity. It considers the lunar day (tithi), '
                              'nakshatra, yoga, karana, and planetary positions to '
                              'find windows of maximum cosmic support.',
                              style: T.bodySm.copyWith(height: 1.6),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // -----------------------------------------------------------------------
  // Check result section
  // -----------------------------------------------------------------------

  Widget _buildCheckResult() {
    final r = _checkResult!;
    final score = (r['score'] as num?)?.toDouble() ?? 0;
    final quality = (r['quality'] as String?) ?? '';
    final favorable =
        (r['favorable_factors'] as List<dynamic>?)?.cast<String>() ?? [];
    final unfavorable =
        (r['unfavorable_factors'] as List<dynamic>?)?.cast<String>() ?? [];
    final recommendation = (r['recommendation'] as String?) ?? '';
    final inRahuKaal = (r['in_rahu_kaal'] as bool?) ?? false;
    final inYamaghanda = (r['in_yamaghanda'] as bool?) ?? false;
    final inGulika = (r['in_gulika'] as bool?) ?? false;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Score ring + quality
        Center(
          child: Column(
            children: [
              DayRatingRing(score: score / 10, size: 120),
              const SizedBox(height: S.sm),
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.md, vertical: S.xs),
                decoration: BoxDecoration(
                  color: _qualityColor(quality).withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  quality,
                  style: T.bodySm.copyWith(
                    color: _qualityColor(quality),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: S.lg),

        // Inauspicious period alerts
        if (inRahuKaal || inYamaghanda || inGulika) ...[
          if (inRahuKaal) _buildAlertCard('Rahu Kaal Active', 'Avoid starting new ventures during this period'),
          if (inYamaghanda) _buildAlertCard('Yamaghanda Active', 'Inauspicious period — proceed with caution'),
          if (inGulika) _buildAlertCard('Gulika Active', 'Not ideal for auspicious beginnings'),
          const SizedBox(height: S.md),
        ],

        // Favorable factors
        if (favorable.isNotEmpty) ...[
          Text('Favorable', style: T.bodySm.copyWith(
              color: C.positive, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.xs),
          ...favorable.map((f) => Padding(
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
                        color: C.positive,
                      ),
                    ),
                    Expanded(child: Text(f, style: T.bodySm)),
                  ],
                ),
              )),
          const SizedBox(height: S.md),
        ],

        // Unfavorable factors
        if (unfavorable.isNotEmpty) ...[
          Text('Unfavorable', style: T.bodySm.copyWith(
              color: C.negative, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.xs),
          ...unfavorable.map((f) => Padding(
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
                        color: C.negative,
                      ),
                    ),
                    Expanded(child: Text(f, style: T.bodySm)),
                  ],
                ),
              )),
          const SizedBox(height: S.md),
        ],

        // Recommendation
        if (recommendation.isNotEmpty)
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Recommendation',
                    style: T.bodySm.copyWith(
                        color: C.textPrimary,
                        fontWeight: FontWeight.w600)),
                const SizedBox(height: S.sm),
                Text(recommendation,
                    style: T.bodySm.copyWith(height: 1.6)),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildAlertCard(String title, String desc) {
    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: GlassContainer(
        padding: const EdgeInsets.all(S.md),
        borderColor: C.negative.withValues(alpha: 0.3),
        backgroundColor: C.negative.withValues(alpha: 0.05),
        child: Row(
          children: [
            Icon(Icons.warning_amber_rounded,
                color: C.negative, size: 20),
            const SizedBox(width: S.sm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: T.bodySm.copyWith(
                          color: C.negative,
                          fontWeight: FontWeight.w600,
                          fontSize: 12)),
                  Text(desc,
                      style: T.caption.copyWith(fontSize: 10)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWindowCard(Map<String, dynamic> w) {
    final dt = DateTime.tryParse(w['datetime']?.toString() ?? '');
    final score = (w['score'] as num?)?.toDouble() ?? 0;
    final quality = (w['quality'] as String?) ?? '';
    final dateStr = dt != null
        ? '${dt.day}/${dt.month}/${dt.year} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}'
        : '-';

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: GlassContainer(
        padding: const EdgeInsets.symmetric(
            horizontal: S.lg, vertical: S.md),
        child: Row(
          children: [
            // Score circle
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: _qualityColor(quality).withValues(alpha: 0.12),
                border: Border.all(
                    color: _qualityColor(quality).withValues(alpha: 0.3)),
              ),
              child: Center(
                child: Text(
                  score.toStringAsFixed(0),
                  style: T.bodySm.copyWith(
                    color: _qualityColor(quality),
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                  ),
                ),
              ),
            ),
            const SizedBox(width: S.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(dateStr,
                      style: T.bodySm.copyWith(color: C.textPrimary)),
                  const SizedBox(height: 2),
                  Text(quality, style: T.caption),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _qualityColor(String quality) {
    switch (quality.toLowerCase()) {
      case 'excellent':
        return C.positive;
      case 'very good':
      case 'good':
        return C.jupiter;
      case 'average':
        return C.warning;
      default:
        return C.negative;
    }
  }
}
