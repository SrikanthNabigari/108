import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/data/models/forecast_model.dart';
import 'package:one_zero_eight/data/providers/forecast_provider.dart';
import 'package:one_zero_eight/features/state_map/models/state_vector.dart';
import '../mock/forecast_mock_data.dart';
import '../widgets/day_rating_ring.dart';
import '../widgets/panchanga_card.dart';
import '../widgets/area_trend_card.dart';

/// Forecast screen with Daily / Weekly / Monthly tabs.
///
/// Fetches from API providers, falls back to mock data on failure.
class ForecastScreen extends ConsumerStatefulWidget {
  const ForecastScreen({super.key});

  @override
  ConsumerState<ForecastScreen> createState() => _ForecastScreenState();
}

class _ForecastScreenState extends ConsumerState<ForecastScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  // Data
  ForecastModel? _daily;
  ForecastModel? _weekly;
  ForecastModel? _monthly;
  bool _loadingDaily = true;
  bool _loadingWeekly = true;
  bool _loadingMonthly = true;

  // Date selector for daily tab
  DateTime _selectedDate = DateTime.now();
  String _dateLabel = 'Today';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _fetchDaily();
    _fetchWeekly();
    _fetchMonthly();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _fetchDaily() async {
    setState(() => _loadingDaily = true);
    try {
      final data = await ref.read(dailyForecastProvider(_selectedDate).future);
      if (mounted) setState(() { _daily = data; _loadingDaily = false; });
    } catch (_) {
      if (mounted) setState(() { _daily = ForecastMockData.daily; _loadingDaily = false; });
    }
  }

  Future<void> _fetchWeekly() async {
    setState(() => _loadingWeekly = true);
    try {
      final data = await ref.read(weeklyForecastProvider().future);
      if (mounted) setState(() { _weekly = data; _loadingWeekly = false; });
    } catch (_) {
      if (mounted) setState(() { _weekly = ForecastMockData.weekly; _loadingWeekly = false; });
    }
  }

  Future<void> _fetchMonthly() async {
    setState(() => _loadingMonthly = true);
    try {
      final data = await ref.read(monthlyForecastProvider().future);
      if (mounted) setState(() { _monthly = data; _loadingMonthly = false; });
    } catch (_) {
      if (mounted) setState(() { _monthly = ForecastMockData.monthly; _loadingMonthly = false; });
    }
  }

  Future<void> _refreshAll() async {
    await Future.wait([_fetchDaily(), _fetchWeekly(), _fetchMonthly()]);
  }

  void _selectDate(String label, DateTime date) {
    setState(() {
      _dateLabel = label;
      _selectedDate = date;
    });
    _fetchDaily();
  }

  void _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime.now().subtract(const Duration(days: 30)),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      builder: (ctx, child) => Theme(
        data: Theme.of(ctx).copyWith(
          colorScheme: const ColorScheme.dark(
            primary: C.accent,
            onPrimary: C.bg,
            surface: C.surface,
            onSurface: C.textPrimary,
          ),
        ),
        child: child!,
      ),
    );
    if (picked != null) {
      final now = DateTime.now();
      final isToday = picked.year == now.year &&
          picked.month == now.month &&
          picked.day == now.day;
      final tomorrow = now.add(const Duration(days: 1));
      final isTomorrow = picked.year == tomorrow.year &&
          picked.month == tomorrow.month &&
          picked.day == tomorrow.day;
      final label = isToday
          ? 'Today'
          : isTomorrow
              ? 'Tomorrow'
              : _formatShortDate(picked);
      _selectDate(label, picked);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: Column(
            children: [
              const SizedBox(height: S.lg),
              // Header
              Center(
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
                        Text('Forecast', style: T.h2),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'What the stars say',
                      style: T.bodySm.copyWith(color: C.textMuted),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: S.xl),
              // Tab bar
              Padding(
                padding: S.pagePadding,
                child: GlassContainer(
                  padding: const EdgeInsets.all(4),
                  borderRadius: R.md,
                  child: TabBar(
                    controller: _tabController,
                    indicator: BoxDecoration(
                      borderRadius: BorderRadius.circular(R.sm),
                      color: C.accentSurface,
                    ),
                    indicatorSize: TabBarIndicatorSize.tab,
                    dividerColor: Colors.transparent,
                    labelColor: C.accent,
                    unselectedLabelColor: C.textMuted,
                    labelStyle: T.bodySm.copyWith(fontWeight: FontWeight.w600),
                    unselectedLabelStyle: T.bodySm,
                    tabs: const [
                      Tab(text: 'Daily'),
                      Tab(text: 'Weekly'),
                      Tab(text: 'Monthly'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: S.lg),
              // Tab content
              Expanded(
                child: RefreshIndicator(
                  onRefresh: _refreshAll,
                  color: C.accent,
                  backgroundColor: C.surface,
                  child: TabBarView(
                    controller: _tabController,
                    children: [
                      _buildDailyTab(),
                      _buildWeeklyTab(),
                      _buildMonthlyTab(),
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

  // ====================================================================
  // DAILY TAB
  // ====================================================================

  Widget _buildDailyTab() {
    if (_loadingDaily) return _loader();
    final f = _daily;
    if (f == null) return _emptyState('No daily forecast available');

    final mentalState = f.details['mental_state'] as String? ?? '';
    final summary = f.details['summary'] as String? ?? '';

    return ListView(
      padding: S.pagePadding,
      children: [
        // Date selector
        _buildDateSelector(),
        const SizedBox(height: S.xl),

        // Day rating ring
        Center(child: DayRatingRing(score: f.dayRating)),
        const SizedBox(height: S.sm),
        Center(
          child: Text('Day Rating', style: T.caption),
        ),
        if (mentalState.isNotEmpty) ...[
          const SizedBox(height: S.xs),
          Center(
            child: Text(
              mentalState,
              style: T.bodySm.copyWith(
                color: _mentalStateColor(mentalState),
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
        const SizedBox(height: S.xl),

        // Panchanga
        PanchangaCard(panchanga: f.panchanga),
        const SizedBox(height: S.xl),

        // Life areas (sorted by score, highest first)
        _sectionLabel('Life Areas'),
        const SizedBox(height: S.sm),
        Builder(builder: (_) {
          final sorted = f.areaRatings.entries.toList()
            ..sort((a, b) => b.value.score.compareTo(a.value.score));
          return SizedBox(
            height: 120,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: sorted.length,
              separatorBuilder: (_, __) => const SizedBox(width: S.sm),
              itemBuilder: (_, i) {
                final entry = sorted[i];
                return AreaTrendCard(
                  areaId: entry.key,
                  score: entry.value.score,
                  trend: entry.value.trend,
                );
              },
            ),
          );
        }),
        const SizedBox(height: S.xl),

        // Summary
        if (summary.isNotEmpty) ...[
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Summary',
                  style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: S.sm),
                Text(
                  summary,
                  style: T.bodySm.copyWith(color: C.textSecondary, height: 1.6),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.xl),
        ],

        // Recommendations
        if (f.recommendations.isNotEmpty) ...[
          _sectionLabel('Recommendations'),
          const SizedBox(height: S.sm),
          _buildRecommendations(f.recommendations),
          const SizedBox(height: S.xl),
        ],

        // Ask Guide CTA
        _buildAskGuideCta('How is my day today?'),
        const SizedBox(height: S.xxxl),
      ],
    );
  }

  Widget _buildDateSelector() {
    final now = DateTime.now();
    final tomorrow = now.add(const Duration(days: 1));
    return Row(
      children: [
        _dateChip('Today', now),
        const SizedBox(width: S.sm),
        _dateChip('Tomorrow', tomorrow),
        const Spacer(),
        GestureDetector(
          onTap: _pickDate,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
            decoration: BoxDecoration(
              borderRadius: R.smBr,
              color: C.glassBg,
              border: Border.all(color: C.glassBorder, width: 0.5),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.calendar_today, size: 14, color: C.textMuted),
                const SizedBox(width: S.xs),
                Text(
                  _dateLabel == 'Today' || _dateLabel == 'Tomorrow'
                      ? 'Pick'
                      : _dateLabel,
                  style: T.caption.copyWith(color: C.textSecondary),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _dateChip(String label, DateTime date) {
    final active = _dateLabel == label;
    return GestureDetector(
      onTap: () => _selectDate(label, date),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.sm),
        decoration: BoxDecoration(
          borderRadius: R.smBr,
          color: active ? C.accentSurface : C.glassBg,
          border: Border.all(
            color: active ? C.accent : C.glassBorder,
            width: active ? 1 : 0.5,
          ),
        ),
        child: Text(
          label,
          style: T.bodySm.copyWith(
            color: active ? C.accent : C.textSecondary,
            fontWeight: active ? FontWeight.w600 : FontWeight.w400,
          ),
        ),
      ),
    );
  }

  // ====================================================================
  // WEEKLY TAB
  // ====================================================================

  Widget _buildWeeklyTab() {
    if (_loadingWeekly) return _loader();
    final f = _weekly;
    if (f == null) return _emptyState('No weekly forecast available');

    final dailyRatings = (f.details['daily_ratings'] as List?)
            ?.map((e) => (e as num).toDouble())
            .toList() ??
        [6.2, 5.8, 7.5, 7.9, 7.1, 6.5, 6.8];
    final dailyLabels = (f.details['daily_labels'] as List?)
            ?.map((e) => e as String)
            .toList() ??
        ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    final summary = f.details['summary'] as String? ?? '';

    return ListView(
      padding: S.pagePadding,
      children: [
        // Week rating
        Center(
          child: Column(
            children: [
              Text(
                f.dayRating.toStringAsFixed(1),
                style: T.h1.copyWith(
                  color: _ratingColor(f.dayRating),
                  fontSize: 36,
                ),
              ),
              Text('Week Average', style: T.caption),
            ],
          ),
        ),
        const SizedBox(height: S.xl),

        // 7-day bar chart
        _sectionLabel('Daily Breakdown'),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.lg),
          child: SizedBox(
            height: 180,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: List.generate(dailyRatings.length, (i) {
                final score = dailyRatings[i];
                final label = i < dailyLabels.length ? dailyLabels[i] : '';
                final barHeight = (score / 10).clamp(0.0, 1.0) * 120;
                final color = _ratingColor(score);

                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 3),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      children: [
                        Text(
                          score.toStringAsFixed(1),
                          style: T.caption.copyWith(
                            color: color,
                            fontWeight: FontWeight.w600,
                            fontSize: 10,
                          ),
                        ),
                        const SizedBox(height: S.xs),
                        Container(
                          height: barHeight,
                          decoration: BoxDecoration(
                            borderRadius: const BorderRadius.vertical(
                              top: Radius.circular(4),
                            ),
                            color: color.withValues(alpha: 0.7),
                          ),
                        ),
                        const SizedBox(height: S.xs),
                        Text(
                          label,
                          style: T.caption.copyWith(fontSize: 10),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ),
          ),
        ),
        const SizedBox(height: S.xl),

        // Summary
        if (summary.isNotEmpty) ...[
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Weekly Outlook',
                  style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: S.sm),
                Text(
                  summary,
                  style: T.bodySm.copyWith(color: C.textSecondary, height: 1.6),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.xl),
        ],

        // Recommendations
        if (f.recommendations.isNotEmpty) ...[
          _sectionLabel('Recommendations'),
          const SizedBox(height: S.sm),
          _buildRecommendations(f.recommendations),
          const SizedBox(height: S.xl),
        ],

        _buildAskGuideCta('How is my week looking?'),
        const SizedBox(height: S.xxxl),
      ],
    );
  }

  // ====================================================================
  // MONTHLY TAB
  // ====================================================================

  Widget _buildMonthlyTab() {
    if (_loadingMonthly) return _loader();
    final f = _monthly;
    if (f == null) return _emptyState('No monthly forecast available');

    final summary = f.details['summary'] as String? ?? '';
    final bestArea = f.details['best_area'] as String?;
    final weakestArea = f.details['weakest_area'] as String?;

    return ListView(
      padding: S.pagePadding,
      children: [
        // Monthly overview card
        GlassContainer(
          padding: const EdgeInsets.all(S.xl),
          child: Column(
            children: [
              DayRatingRing(score: f.dayRating, size: 130),
              const SizedBox(height: S.sm),
              Text('Month Rating', style: T.caption),
              const SizedBox(height: S.xl),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  if (bestArea != null)
                    _areaHighlight(
                      label: 'Strongest',
                      areaId: bestArea,
                      color: C.positive,
                    ),
                  if (weakestArea != null)
                    _areaHighlight(
                      label: 'Needs Care',
                      areaId: weakestArea,
                      color: C.warning,
                    ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: S.xl),

        // Life areas (sorted by score, highest first)
        _sectionLabel('Area Overview'),
        const SizedBox(height: S.sm),
        Builder(builder: (_) {
          final sorted = f.areaRatings.entries.toList()
            ..sort((a, b) => b.value.score.compareTo(a.value.score));
          return SizedBox(
            height: 120,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: sorted.length,
              separatorBuilder: (_, __) => const SizedBox(width: S.sm),
              itemBuilder: (_, i) {
                final entry = sorted[i];
                return AreaTrendCard(
                  areaId: entry.key,
                  score: entry.value.score,
                  trend: entry.value.trend,
                );
              },
            ),
          );
        }),
        const SizedBox(height: S.xl),

        // Summary
        if (summary.isNotEmpty) ...[
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Monthly Outlook',
                  style: T.bodySm.copyWith(
                    color: C.textPrimary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: S.sm),
                Text(
                  summary,
                  style: T.bodySm.copyWith(color: C.textSecondary, height: 1.6),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.xl),
        ],

        // Recommendations
        if (f.recommendations.isNotEmpty) ...[
          _sectionLabel('Recommendations'),
          const SizedBox(height: S.sm),
          _buildRecommendations(f.recommendations),
          const SizedBox(height: S.xl),
        ],

        // Upgrade CTA
        OutlinedButton(
          onPressed: () {},
          child: const Text('Upgrade for Yearly Forecast'),
        ),
        const SizedBox(height: S.xl),

        _buildAskGuideCta('How is my month looking?'),
        const SizedBox(height: S.xxxl),
      ],
    );
  }

  // ====================================================================
  // SHARED HELPERS
  // ====================================================================

  Widget _loader() {
    return const Center(
      child: CircularProgressIndicator(color: C.accent, strokeWidth: 2),
    );
  }

  Widget _emptyState(String msg) {
    return Center(
      child: Text(msg, style: T.bodySm.copyWith(color: C.textMuted)),
    );
  }

  Widget _sectionLabel(String title) {
    return Text(
      title,
      style: T.h3.copyWith(fontSize: 16),
    );
  }

  Widget _buildRecommendations(List<String> items) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: items.map((r) {
          return Padding(
            padding: const EdgeInsets.only(bottom: S.sm),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Padding(
                  padding: EdgeInsets.only(top: 6),
                  child: Icon(Icons.circle, size: 5, color: C.textMuted),
                ),
                const SizedBox(width: S.sm),
                Expanded(
                  child: Text(
                    r,
                    style: T.bodySm.copyWith(
                      color: C.textSecondary,
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildAskGuideCta(String prompt) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton.icon(
        onPressed: () => context.go('/chat?prompt=${Uri.encodeComponent(prompt)}'),
        icon: const Icon(Icons.auto_awesome, size: 18),
        label: const Text('Ask Guide'),
      ),
    );
  }

  Widget _areaHighlight({
    required String label,
    required String areaId,
    required Color color,
  }) {
    final icon = kAreaIcons[areaId] ?? '?';
    final name = kAreaNames[areaId] ?? areaId;
    return Column(
      children: [
        Text(label, style: T.caption.copyWith(color: color)),
        const SizedBox(height: S.xs),
        Text(icon, style: const TextStyle(fontSize: 24)),
        const SizedBox(height: S.xs),
        Text(name, style: T.bodySm.copyWith(color: C.textPrimary)),
      ],
    );
  }

  static String _formatShortDate(DateTime dt) {
    const months = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    return '${months[dt.month]} ${dt.day}';
  }

  static Color _ratingColor(double s) {
    if (s >= 7) return C.positive;
    if (s >= 4) return C.warning;
    return C.negative;
  }

  static Color _mentalStateColor(String state) {
    switch (state) {
      case 'Thriving':
      case 'Flowing':
        return C.positive;
      case 'Steady':
        return C.warning;
      case 'Challenged':
      case 'Struggling':
      case 'Turbulent':
        return C.negative;
      default:
        return C.textSecondary;
    }
  }
}
