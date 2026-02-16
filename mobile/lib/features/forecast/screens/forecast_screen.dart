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
import '../widgets/area_trend_card.dart';
import '../widgets/prana_detail_panel.dart';

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
              const SizedBox(height: S.sm),
              // Header
              Padding(
                padding: S.pagePadding,
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
                    Text('Forecast', style: T.h2),
                  ],
                ),
              ),
              const SizedBox(height: S.sm),
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
              const SizedBox(height: S.sm),
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
    final horaLord = f.details['hora_lord'] as String? ?? '';
    final isChandrashtama = f.details['is_chandrashtama'] as bool? ?? false;
    final triggers = (f.details['upcoming_triggers'] as List?)
        ?.map((t) => t as Map<String, dynamic>)
        .toList() ?? [];

    return ListView(
      padding: S.pagePadding,
      children: [
        // Date selector
        _buildDateSelector(),
        const SizedBox(height: S.md),

        // Rating + Panchanga banner (compact)
        GlassContainer(
          padding: const EdgeInsets.all(S.md),
          child: Row(
            children: [
              DayRatingRing(score: f.dayRating, size: 72),
              const SizedBox(width: S.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        if (mentalState.isNotEmpty)
                          Text(
                            mentalState,
                            style: T.bodySm.copyWith(
                              color: _mentalStateColor(mentalState),
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        if (horaLord.isNotEmpty) ...[
                          const SizedBox(width: S.sm),
                          Text(planetGlyph(horaLord), style: TextStyle(fontSize: 12, color: planetColor(horaLord))),
                          const SizedBox(width: 2),
                          Text(
                            planetName(horaLord),
                            style: T.caption.copyWith(color: planetColor(horaLord), fontSize: 10),
                          ),
                        ],
                      ],
                    ),
                    if (f.panchanga != null) ...[
                      const SizedBox(height: S.xs),
                      _panchangaInline(f.panchanga!),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: S.md),

        // Chandrashtama warning
        if (isChandrashtama) ...[
          GlassContainer(
            padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
            borderColor: C.negative.withValues(alpha: 0.5),
            backgroundColor: C.negative.withValues(alpha: 0.05),
            child: Row(
              children: [
                const Icon(Icons.warning_amber_rounded, color: C.negative, size: 16),
                const SizedBox(width: S.sm),
                Expanded(
                  child: Text(
                    'Chandrashtama active - Avoid major decisions',
                    style: T.caption.copyWith(color: C.negative),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.md),
        ],

        // Summary (moved up)
        if (summary.isNotEmpty) ...[
          Text(
            summary,
            style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
          ),
          const SizedBox(height: S.lg),
        ],

        // Recommendations (moved up)
        if (f.recommendations.isNotEmpty) ...[
          _sectionLabel('Recommendations'),
          const SizedBox(height: S.sm),
          _buildRecommendations(f.recommendations),
          const SizedBox(height: S.lg),
        ],

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
        const SizedBox(height: S.lg),

        // Upcoming Triggers
        if (triggers.isNotEmpty) ...[
          _sectionLabel('Coming Up'),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: const EdgeInsets.all(S.md),
            child: Column(
              children: triggers.map((t) {
                final days = t['days_from_now'] as int? ?? 0;
                return Padding(
                  padding: const EdgeInsets.only(bottom: S.sm),
                  child: Row(
                    children: [
                      Container(
                        width: 32,
                        height: 32,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(8),
                          color: C.accentSurface,
                        ),
                        alignment: Alignment.center,
                        child: Text(
                          '${days}d',
                          style: T.caption.copyWith(
                            color: C.accent,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      const SizedBox(width: S.sm),
                      Expanded(
                        child: Text(
                          t['trigger'] as String? ?? '',
                          style: T.bodySm.copyWith(color: C.textSecondary),
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: S.lg),
        ],

        // Active Dasha section
        Builder(builder: (_) {
          final dasha = f.details['active_dasha'] as Map<String, dynamic>?;
          if (dasha == null) return const SizedBox.shrink();
          return _buildActiveDasha(dasha);
        }),

        // Prana Timeline (micro-schedule)
        Builder(builder: (_) {
          final pranas = (f.details['prana_timeline'] as List?)
              ?.map((p) => p as Map<String, dynamic>)
              .toList();
          if (pranas == null || pranas.isEmpty) return const SizedBox.shrink();
          final sdLord = (f.details['active_dasha'] as Map<String, dynamic>?)?['sookshma'] as String? ?? '';
          return _buildPranaTimeline(pranas, sdLord);
        }),

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
  // DASHA + PRANA SECTIONS (Daily tab)
  // ====================================================================

  /// Compact active dasha hierarchy: MD > AD > PD > SD with theme.
  Widget _buildActiveDasha(Map<String, dynamic> dasha) {
    final md = dasha['mahadasha'] as String? ?? '';
    final ad = dasha['antardasha'] as String? ?? '';
    final pd = dasha['pratyantardasha'] as String? ?? '';
    final sd = dasha['sookshma'] as String? ?? '';
    final prana = dasha['prana'] as String? ?? '';
    final theme = dasha['theme'] as String? ?? '';
    final sdGuide = dasha['sookshma_guide'] as Map<String, dynamic>?;
    final sdTheme = sdGuide?['theme'] as String? ?? '';
    final bphs = dasha['bphs_analysis'] as Map<String, dynamic>?;

    if (md.isEmpty) return const SizedBox.shrink();

    // Build enriched pill labels from BPHS data
    String mdLabel = 'MD';
    String adLabel = 'AD';
    if (bphs != null) {
      final houses = (bphs['houses_ruled'] as List?)
          ?.map((h) => '${h}L')
          .join(', ');
      if (houses != null && houses.isNotEmpty) mdLabel = houses;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionLabel('Active Dasha'),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Hierarchy row: MD > AD > PD > SD
              Wrap(
                spacing: 4,
                runSpacing: 4,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  _dashaPill(md, mdLabel, isBig: true),
                  const Icon(Icons.chevron_right, size: 14, color: C.textMuted),
                  if (ad.isNotEmpty) ...[
                    _dashaPill(ad, adLabel),
                    const Icon(Icons.chevron_right, size: 14, color: C.textMuted),
                  ],
                  if (pd.isNotEmpty) ...[
                    _dashaPill(pd, 'PD'),
                    const Icon(Icons.chevron_right, size: 14, color: C.textMuted),
                  ],
                  if (sd.isNotEmpty) _dashaPill(sd, 'SD', highlight: true),
                  if (prana.isNotEmpty) ...[
                    const Icon(Icons.chevron_right, size: 14, color: C.textMuted),
                    _dashaPill(prana, 'Pr', isSmall: true),
                  ],
                ],
              ),
              // BPHS nature + dignity chips
              if (bphs != null) ...[
                const SizedBox(height: S.sm),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: [
                    _bphsChip(
                      (bphs['functional_nature'] as String? ?? 'neutral').replaceAll('_', ' '),
                      _natureColor(bphs['functional_nature'] as String? ?? 'neutral'),
                    ),
                    _bphsChip(
                      (bphs['dignity'] as String? ?? 'neutral').replaceAll('_', ' '),
                      C.textSecondary,
                    ),
                  ],
                ),
              ],
              // Theme (now chart-specific from backend)
              if (theme.isNotEmpty) ...[
                const SizedBox(height: S.sm),
                Text(theme,
                    style: T.bodySm.copyWith(
                        color: C.textSecondary, height: 1.4, fontSize: 12)),
              ],
              // BPHS summary (chart-specific reading)
              if (bphs != null && (bphs['summary'] as String? ?? '').isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(bphs['summary'] as String,
                    style: T.caption.copyWith(
                        color: C.textMuted, height: 1.4, fontSize: 10)),
              ],
              // SD micro-theme (the detailed one from guide)
              if (sdTheme.isNotEmpty && sdTheme != theme) ...[
                const SizedBox(height: 4),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('${planetGlyph(sd)} ',
                        style: TextStyle(fontSize: 11, color: planetColor(sd))),
                    Expanded(
                      child: Text(sdTheme,
                          style: T.caption.copyWith(
                              color: planetColor(sd).withValues(alpha: 0.8),
                              fontSize: 10, height: 1.3)),
                    ),
                  ],
                ),
              ],
              // SD favorable activities (top 3)
              if (sdGuide != null &&
                  (sdGuide['favorable_activities'] as List?)?.isNotEmpty == true) ...[
                const SizedBox(height: S.sm),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: ((sdGuide['favorable_activities'] as List)
                      .take(3)
                      .map((e) => e.toString())
                      .toList())
                      .map((a) => Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      color: C.positive.withValues(alpha: 0.08),
                      border: Border.all(color: C.positive.withValues(alpha: 0.2)),
                    ),
                    child: Text(a, style: T.caption.copyWith(
                        color: C.positive, fontSize: 9)),
                  )).toList(),
                ),
              ],
            ],
          ),
        ),
        const SizedBox(height: S.lg),
      ],
    );
  }

  Widget _dashaPill(String lord, String label,
      {bool isBig = false, bool isSmall = false, bool highlight = false}) {
    final color = planetColor(lord);
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: isBig ? 10 : 8,
        vertical: isBig ? 5 : 3,
      ),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: highlight
            ? color.withValues(alpha: 0.15)
            : color.withValues(alpha: 0.08),
        border: highlight
            ? Border.all(color: color.withValues(alpha: 0.4))
            : null,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(planetGlyph(lord),
              style: TextStyle(fontSize: isSmall ? 10 : 12, color: color)),
          const SizedBox(width: 3),
          Text(label,
              style: T.caption.copyWith(
                  color: color,
                  fontSize: isSmall ? 9 : (isBig ? 11 : 10),
                  fontWeight: highlight ? FontWeight.w600 : FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _bphsChip(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(10),
        color: color.withValues(alpha: 0.1),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Text(
        label[0].toUpperCase() + label.substring(1),
        style: T.caption.copyWith(color: color, fontSize: 9, fontWeight: FontWeight.w600),
      ),
    );
  }

  Color _natureColor(String nature) {
    switch (nature) {
      case 'yogakaraka': return C.positive;
      case 'benefic': return C.positive;
      case 'malefic': return C.negative;
      case 'maraka': return C.negative;
      default: return C.warning;
    }
  }

  /// Prana Timeline — hourly micro-schedule showing planetary micro-periods.
  Widget _buildPranaTimeline(List<Map<String, dynamic>> pranas, String sdLord) {
    final now = DateTime.now();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionLabel('Prana Timeline'),
        const SizedBox(height: 2),
        Text('Micro-periods through the day',
            style: T.caption.copyWith(color: C.textMuted, fontSize: 10)),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.md),
          child: Column(
            children: pranas.asMap().entries.map((entry) {
              final i = entry.key;
              final p = entry.value;
              final lord = p['lord'] as String? ?? '';
              final startStr = p['start'] as String? ?? '';
              final endStr = p['end'] as String? ?? '';
              final theme = p['theme'] as String? ?? '';
              final energy = p['energy_quality'] as String? ?? '';
              final guidance = (p['guidance'] as List?)
                  ?.take(1).map((e) => e.toString()).toList() ?? [];
              final combo = p['combination_with_sd'] as Map<String, dynamic>?;
              final comboTheme = combo?['theme'] as String? ?? '';

              // Determine if this is the current period
              bool isNow = false;
              try {
                final startDt = p['start_dt'] as String? ?? '';
                final endDt = p['end_dt'] as String? ?? '';
                if (startDt.isNotEmpty && endDt.isNotEmpty) {
                  final s = DateTime.parse(startDt);
                  final e = DateTime.parse(endDt);
                  isNow = now.isAfter(s) && now.isBefore(e);
                }
              } catch (_) {}

              final color = planetColor(lord);
              final isLast = i == pranas.length - 1;

              return GestureDetector(
                onTap: () => PranaDetailPanel.show(context, pranaData: p, sdLord: sdLord),
                child: Padding(
                  padding: EdgeInsets.only(bottom: isLast ? 0 : S.sm),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Time column
                      SizedBox(
                        width: 48,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(startStr,
                                style: T.caption.copyWith(
                                    color: isNow ? color : C.textMuted,
                                    fontWeight: isNow ? FontWeight.w700 : FontWeight.w500,
                                    fontSize: 11)),
                            Text(endStr,
                                style: T.caption.copyWith(
                                    color: C.textMuted, fontSize: 9)),
                          ],
                        ),
                      ),
                      const SizedBox(width: S.sm),
                      // Timeline dot + line
                      Column(
                        children: [
                          Container(
                            width: isNow ? 12 : 8,
                            height: isNow ? 12 : 8,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: isNow ? color : color.withValues(alpha: 0.3),
                              border: isNow
                                  ? Border.all(color: color.withValues(alpha: 0.6), width: 2)
                                  : null,
                            ),
                          ),
                          if (!isLast)
                            Container(
                              width: 1.5,
                              height: 40,
                              color: color.withValues(alpha: 0.15),
                            ),
                        ],
                      ),
                      const SizedBox(width: S.sm),
                      // Content
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.sm, vertical: 4),
                          decoration: isNow
                              ? BoxDecoration(
                                  borderRadius: BorderRadius.circular(8),
                                  color: color.withValues(alpha: 0.06),
                                  border: Border.all(
                                      color: color.withValues(alpha: 0.2)),
                                )
                              : null,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Text(planetGlyph(lord),
                                      style: TextStyle(fontSize: 13, color: color)),
                                  const SizedBox(width: 4),
                                  Text(planetName(lord),
                                      style: T.bodySm.copyWith(
                                          color: isNow ? color : C.textPrimary,
                                          fontWeight: FontWeight.w600,
                                          fontSize: 12)),
                                  if (isNow) ...[
                                    const SizedBox(width: 6),
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                          horizontal: 6, vertical: 1),
                                      decoration: BoxDecoration(
                                        borderRadius: BorderRadius.circular(8),
                                        color: color.withValues(alpha: 0.2),
                                      ),
                                      child: Text('NOW',
                                          style: T.caption.copyWith(
                                              color: color,
                                              fontSize: 8,
                                              fontWeight: FontWeight.w700)),
                                    ),
                                  ],
                                  if (energy.isNotEmpty) ...[
                                    const Spacer(),
                                    Text(energy,
                                        style: T.caption.copyWith(
                                            color: C.textMuted, fontSize: 9)),
                                  ],
                                  const SizedBox(width: 2),
                                  Icon(Icons.chevron_right, size: 14, color: color.withValues(alpha: 0.4)),
                                ],
                              ),
                              if (theme.isNotEmpty) ...[
                                const SizedBox(height: 2),
                                Text(theme,
                                    style: T.caption.copyWith(
                                        color: C.textSecondary,
                                        fontSize: 10,
                                        height: 1.3),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis),
                              ],
                              if (comboTheme.isNotEmpty) ...[
                                const SizedBox(height: 2),
                                Text(comboTheme,
                                    style: T.caption.copyWith(
                                        color: color.withValues(alpha: 0.7),
                                        fontSize: 9,
                                        fontStyle: FontStyle.italic),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis),
                              ],
                              if (guidance.isNotEmpty) ...[
                                const SizedBox(height: 2),
                                Text(guidance.first,
                                    style: T.caption.copyWith(
                                        color: C.textMuted, fontSize: 9),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis),
                              ],
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ),
        const SizedBox(height: S.lg),
      ],
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
    final chandrashtamaDays = (f.details['chandrashtama_days'] as List?)
        ?.map((d) => d as String).toList() ?? [];

    return ListView(
      padding: S.pagePadding,
      children: [
        // Week rating banner
        GlassContainer(
          padding: const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
          child: Row(
            children: [
              Text(
                f.dayRating.toStringAsFixed(1),
                style: T.h1.copyWith(
                  color: _ratingColor(f.dayRating),
                  fontSize: 28,
                ),
              ),
              const SizedBox(width: S.sm),
              Text('Week Average', style: T.caption),
            ],
          ),
        ),
        const SizedBox(height: S.md),

        // Chandrashtama days warning
        if (chandrashtamaDays.isNotEmpty) ...[
          GlassContainer(
            padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
            borderColor: C.warning.withValues(alpha: 0.4),
            backgroundColor: C.warning.withValues(alpha: 0.05),
            child: Row(
              children: [
                const Icon(Icons.warning_amber_rounded, color: C.warning, size: 16),
                const SizedBox(width: S.sm),
                Text(
                  'Chandrashtama: ${chandrashtamaDays.map((d) => d.substring(5)).join(', ')}',
                  style: T.caption.copyWith(color: C.warning),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.md),
        ],

        // Summary (moved up)
        if (summary.isNotEmpty) ...[
          Text(
            summary,
            style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
          ),
          const SizedBox(height: S.lg),
        ],

        // Recommendations (moved up)
        if (f.recommendations.isNotEmpty) ...[
          _sectionLabel('Recommendations'),
          const SizedBox(height: S.sm),
          _buildRecommendations(f.recommendations),
          const SizedBox(height: S.lg),
        ],

        // 7-day bar chart
        _sectionLabel('Daily Breakdown'),
        const SizedBox(height: S.sm),
        GlassContainer(
          padding: const EdgeInsets.all(S.lg),
          child: SizedBox(
            height: 160,
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: List.generate(dailyRatings.length, (i) {
                final score = dailyRatings[i];
                final label = i < dailyLabels.length ? dailyLabels[i] : '';
                final barHeight = (score / 10).clamp(0.0, 1.0) * 110;
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
        const SizedBox(height: S.lg),

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
    final muhurtaDates = (f.details['muhurta_dates'] as List?)
        ?.map((m) => m as Map<String, dynamic>).toList() ?? [];

    return ListView(
      padding: S.pagePadding,
      children: [
        // Monthly overview card (compact horizontal)
        GlassContainer(
          padding: const EdgeInsets.all(S.md),
          child: Row(
            children: [
              DayRatingRing(score: f.dayRating, size: 72),
              const SizedBox(width: S.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Month Rating', style: T.caption),
                    const SizedBox(height: S.sm),
                    Row(
                      children: [
                        if (bestArea != null) ...[
                          _areaHighlightCompact(
                            label: 'Strongest',
                            areaId: bestArea,
                            color: C.positive,
                          ),
                          const SizedBox(width: S.lg),
                        ],
                        if (weakestArea != null)
                          _areaHighlightCompact(
                            label: 'Needs Care',
                            areaId: weakestArea,
                            color: C.warning,
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: S.md),

        // Summary (moved up)
        if (summary.isNotEmpty) ...[
          Text(
            summary,
            style: T.bodySm.copyWith(color: C.textSecondary, height: 1.5),
          ),
          const SizedBox(height: S.lg),
        ],

        // Recommendations (moved up)
        if (f.recommendations.isNotEmpty) ...[
          _sectionLabel('Recommendations'),
          const SizedBox(height: S.sm),
          _buildRecommendations(f.recommendations),
          const SizedBox(height: S.lg),
        ],

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
        const SizedBox(height: S.lg),

        // Muhurta dates
        if (muhurtaDates.isNotEmpty) ...[
          _sectionLabel('Abhijit Muhurta'),
          const SizedBox(height: S.xs),
          Text(
            'Best time for important actions',
            style: T.caption.copyWith(color: C.textMuted),
          ),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: const EdgeInsets.all(S.md),
            child: Column(
              children: muhurtaDates.map((m) {
                final date = m['date'] as String? ?? '';
                final start = m['abhijit_start'] as String? ?? '';
                final end = m['abhijit_end'] as String? ?? '';
                return Padding(
                  padding: const EdgeInsets.only(bottom: S.sm),
                  child: Row(
                    children: [
                      Container(
                        width: 60,
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(6),
                          color: C.accentSurface,
                        ),
                        alignment: Alignment.center,
                        child: Text(
                          date.length >= 5 ? date.substring(5) : date,
                          style: T.caption.copyWith(
                            color: C.accent,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      const SizedBox(width: S.sm),
                      Text(
                        '$start - $end',
                        style: T.bodySm.copyWith(color: C.textSecondary),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: S.lg),
        ],

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

  /// Compact inline panchanga — single line per limb, no card wrapper.
  Widget _panchangaInline(PanchangaData p) {
    final items = <String>[
      if (p.tithi != null) p.tithi!,
      if (p.nakshatra != null) p.nakshatra!,
      if (p.yoga != null) p.yoga!,
      if (p.vara != null) p.vara!,
    ];
    return Wrap(
      spacing: S.sm,
      runSpacing: 2,
      children: items.map((item) {
        return Text(
          item,
          style: T.caption.copyWith(color: C.textMuted, fontSize: 10),
        );
      }).toList(),
    );
  }

  Widget _areaHighlightCompact({
    required String label,
    required String areaId,
    required Color color,
  }) {
    final icon = kAreaIcons[areaId] ?? '?';
    final name = kAreaNames[areaId] ?? areaId;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(icon, style: const TextStyle(fontSize: 18)),
        const SizedBox(width: 4),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: T.caption.copyWith(color: color, fontSize: 10)),
            Text(name, style: T.caption.copyWith(color: C.textPrimary)),
          ],
        ),
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
