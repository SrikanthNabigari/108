import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import '../models/state_vector.dart';
import '../models/mock_data.dart';
import '../widgets/view_toggle.dart';
import '../widgets/heat_map_grid.dart';
import '../widgets/state_now_card.dart';
import '../widgets/area_score_card.dart';
import '../widgets/area_detail_panel.dart';
import '../widgets/factor_detail_panel.dart';
import '../widgets/add_event_sheet.dart';

/// State Map Screen — interactive heat map visualization of astrological
/// prediction factors across any timeframe.
///
/// Follows the [TimelineScreen] pattern:
/// - [ConsumerStatefulWidget] with API fetch in initState
/// - [AmbientBackground] wrapper
/// - [GlassContainer] cards
/// - Bottom-sheet drill-down on tap
class StateMapScreen extends ConsumerStatefulWidget {
  const StateMapScreen({super.key});

  @override
  ConsumerState<StateMapScreen> createState() => _StateMapScreenState();
}

class _StateMapScreenState extends ConsumerState<StateMapScreen> {
  // Data
  StateVector? _nowState;
  StateMapData? _mapData;
  bool _loading = true;
  String? _error;

  // Selected state — changes when user taps a heat map cell
  StateVector? _selectedVector;
  String _selectedLabel = 'Today';

  // View state
  String _resolution = 'daily'; // hourly, daily, monthly, yearly
  late DateTime _rangeStart;
  late DateTime _rangeEnd;

  // Events logged by user (local until backend wired)
  final List<LifeEvent> _userEvents = [];

  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _setDefaultRange('daily');
    _fetchData();
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _setDefaultRange(String resolution) {
    final now = DateTime.now();
    switch (resolution) {
      case 'hourly':
        _rangeStart = DateTime(now.year, now.month, now.day);
        _rangeEnd = DateTime(now.year, now.month, now.day, 23, 59);
        break;
      case 'monthly':
        _rangeStart = DateTime(now.year, 1, 1);
        _rangeEnd = DateTime(now.year, 12, 31);
        break;
      case 'yearly':
        _rangeStart = DateTime(now.year - 5, 1, 1);
        _rangeEnd = DateTime(now.year + 5, 12, 31);
        break;
      default: // daily
        _rangeStart = DateTime(now.year, now.month, 1);
        _rangeEnd = DateTime(now.year, now.month + 1, 0); // last day of month
    }
  }

  Future<void> _fetchData() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final startStr = _rangeStart.toIso8601String().split('T').first;
      final endStr = _rangeEnd.toIso8601String().split('T').first;

      // Fetch range data and NOW state in parallel
      final results = await Future.wait([
        ApiService().get<StateMapData>(
          ApiConstants.stateRange(
            start: startStr,
            end: endStr,
            resolution: _resolution,
          ),
          fromJson: (json) =>
              StateMapData.fromJson(json as Map<String, dynamic>),
        ),
        ApiService().get<StateVector>(
          ApiConstants.stateNow,
          fromJson: (json) =>
              StateVector.fromJson(json as Map<String, dynamic>),
        ),
      ]);

      if (mounted) {
        final mapData = results[0] as StateMapData;
        final nowState = results[1] as StateVector;
        final picked = _pickClosestVector(mapData.vectors);
        setState(() {
          _mapData = mapData;
          _nowState = nowState;
          _selectedVector = picked ?? nowState;
          _selectedLabel = picked != null
              ? _formatVectorDate(picked.date)
              : 'Today';
          _loading = false;
        });
      }
    } catch (e) {
      // Fall back to mock data when API is unavailable
      debugPrint('[StateMap] API failed, using mock data: $e');
      final mockData = MockStateData.generate(
        start: _rangeStart,
        end: _rangeEnd,
        resolution: _resolution,
      );
      final nowState = MockStateData.now();
      final picked = _pickClosestVector(mockData.vectors);

      if (mounted) {
        setState(() {
          _nowState = nowState;
          _mapData = mockData;
          _selectedVector = picked ?? nowState;
          _selectedLabel = picked != null
              ? _formatVectorDate(picked.date)
              : 'Today';
          _loading = false;
        });
      }
    }
  }

  void _onResolutionChanged(String newRes) {
    setState(() {
      _resolution = newRes;
      _setDefaultRange(newRes);
    });
    _fetchData();
  }

  void _onDateRangeTap() async {
    if (_resolution == 'hourly') {
      // Pick a single day
      final picked = await showDatePicker(
        context: context,
        initialDate: _rangeStart,
        firstDate: DateTime(2020),
        lastDate: DateTime(2035),
        builder: _datePickerTheme,
      );
      if (picked != null) {
        setState(() {
          _rangeStart = DateTime(picked.year, picked.month, picked.day);
          _rangeEnd =
              DateTime(picked.year, picked.month, picked.day, 23, 59);
        });
        _fetchData();
      }
    } else {
      // Pick date range
      final picked = await showDateRangePicker(
        context: context,
        initialDateRange: DateTimeRange(start: _rangeStart, end: _rangeEnd),
        firstDate: DateTime(2020),
        lastDate: DateTime(2035),
        builder: _datePickerTheme,
      );
      if (picked != null) {
        setState(() {
          _rangeStart = picked.start;
          _rangeEnd = picked.end;
        });
        _fetchData();
      }
    }
  }

  Widget _datePickerTheme(BuildContext context, Widget? child) {
    return Theme(
      data: Theme.of(context).copyWith(
        colorScheme: const ColorScheme.dark(
          primary: C.accent,
          onPrimary: C.bg,
          surface: C.surface,
          onSurface: C.textPrimary,
        ),
      ),
      child: child!,
    );
  }

  void _onCellTap(int factorIdx, int colIdx, StateVector vector) {
    // Update bottom sections to show tapped date's data
    setState(() {
      _selectedVector = vector;
      _selectedLabel = _formatVectorDate(vector.date);
    });

    FactorDetailPanel.show(
      context,
      vector: vector,
      factorIndex: factorIdx,
    );
  }

  /// Pick the vector closest to today from the range, or the first one.
  StateVector? _pickClosestVector(List<StateVector> vectors) {
    if (vectors.isEmpty) return null;
    final now = DateTime.now();
    StateVector closest = vectors.first;
    int minDiff = (closest.date.difference(now).inHours).abs();
    for (final v in vectors) {
      final diff = (v.date.difference(now).inHours).abs();
      if (diff < minDiff) {
        minDiff = diff;
        closest = v;
      }
    }
    return closest;
  }

  String _formatVectorDate(DateTime dt) {
    const months = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    final now = DateTime.now();
    if (dt.year == now.year && dt.month == now.month && dt.day == now.day) {
      return 'Today';
    }
    return '${months[dt.month]} ${dt.day}';
  }

  void _onAddEvent() {
    AddEventSheet.show(
      context,
      onSave: (event) {
        setState(() => _userEvents.add(event));
        // POST event to backend (fire-and-forget)
        ApiService().post(
          ApiConstants.events,
          body: {
            'date': event.date.toIso8601String(),
            'type': event.type,
            'description': event.description,
            'actual_rating': event.actualRating,
          },
          fromJson: (json) => json,
        ).catchError((e) {
          debugPrint('[StateMap] Failed to save event: $e');
        });
      },
    );
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
                  : _buildContent(),
        ),
      ),
      floatingActionButton: _loading || _error != null
          ? null
          : FloatingActionButton.small(
              onPressed: _onAddEvent,
              backgroundColor: C.glassBg,
              foregroundColor: C.accent,
              elevation: 0,
              child: const Icon(Icons.add, size: 20),
            ),
    );
  }

  Widget _buildError() {
    return Padding(
      padding: S.pagePadding,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('Could not load State Map', style: T.h3),
          const SizedBox(height: S.sm),
          Text(_error!, style: T.caption, textAlign: TextAlign.center),
          const SizedBox(height: S.xl),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: _fetchData,
              child: const Text('Retry'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    final allEvents = <LifeEvent>[
      ...(_mapData?.events ?? []),
      ..._userEvents,
    ];

    return SingleChildScrollView(
      controller: _scrollController,
      padding: S.pagePadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: S.lg),

          // ── Header ──
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
                    Text('State Map', style: T.h2),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'Your predicted state across time',
                  style: T.bodySm.copyWith(color: C.textMuted),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.xl),

          // ── Current State Card (NOW) ──
          if (_nowState != null) StateNowCard(state: _nowState!),
          const SizedBox(height: S.xl),

          // ── View Toggle ──
          ViewToggle(
            selected: _resolution,
            onChanged: _onResolutionChanged,
          ),
          const SizedBox(height: S.md),

          // ── Date Range Selector ──
          GestureDetector(
            onTap: _onDateRangeTap,
            child: Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
              decoration: BoxDecoration(
                borderRadius: R.mdBr,
                color: C.glassBg,
                border: Border.all(color: C.glassBorder, width: 0.5),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.calendar_today,
                      size: 14, color: C.textMuted),
                  const SizedBox(width: S.sm),
                  Text(
                    _formatRange(),
                    style: T.bodySm.copyWith(color: C.textSecondary),
                  ),
                  const SizedBox(width: S.xs),
                  const Icon(Icons.unfold_more,
                      size: 14, color: C.textMuted),
                ],
              ),
            ),
          ),
          const SizedBox(height: S.xl),

          // ── Heat Map Section ──
          _SectionLabel(title: 'Prediction Grid', subtitle: _resolutionLabel()),
          const SizedBox(height: S.sm),
          GlassContainer(
            padding: const EdgeInsets.all(S.sm),
            child: HeatMapGrid(
              vectors: _mapData?.vectors ?? [],
              resolution: _resolution,
              events: allEvents,
              onCellTap: _onCellTap,
            ),
          ),
          const SizedBox(height: S.xl),

          // ── Area Scores (from selected state) ──
          if (_selectedVector != null && _selectedVector!.areas.isNotEmpty) ...[
            AreaScoreCard(
              areas: _selectedVector!.areas,
              rangeVectors: _mapData?.vectors ?? [],
              selectedDate: _selectedVector!.date,
              onAreaTap: (area) => AreaDetailPanel.show(
                context,
                area: area,
                rangeVectors: _mapData?.vectors ?? [],
                selectedDate: _selectedVector!.date,
              ),
            ),
            const SizedBox(height: S.xl),
          ],

          // ── Factor Summary ──
          if (_selectedVector != null && _selectedVector!.factors.isNotEmpty) ...[
            _SectionLabel(title: 'Active Factors', subtitle: _selectedLabel),
            const SizedBox(height: S.sm),
            ..._selectedVector!.factors.map((f) => _FactorChip(factor: f)),
            const SizedBox(height: S.xl),
          ],

          // ── User Events ──
          if (allEvents.isNotEmpty) ...[
            _SectionLabel(
                title: 'Life Events',
                subtitle: '${allEvents.length} marked'),
            const SizedBox(height: S.sm),
            ...allEvents.map((e) => _EventCard(event: e)),
            const SizedBox(height: S.xl),
          ],

          // ── Explainer Card ──
          GlassContainer(
            padding: const EdgeInsets.all(S.lg),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.auto_awesome,
                        size: 16, color: C.textMuted),
                    const SizedBox(width: S.sm),
                    Text('How This Works',
                        style: T.bodySm.copyWith(
                            color: C.textPrimary,
                            fontWeight: FontWeight.w600)),
                  ],
                ),
                const SizedBox(height: S.sm),
                Text(
                  'Seven astrological factors are computed for each time '
                  'period and scored 0–10. Tap any cell to see the '
                  'breakdown. Log real events to verify how well the '
                  'predictions match your experience.',
                  style: T.bodySm.copyWith(
                      color: C.textSecondary, height: 1.6, fontSize: 13),
                ),
              ],
            ),
          ),
          const SizedBox(height: S.xxxl),
        ],
      ),
    );
  }

  String _formatRange() {
    const months = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    if (_resolution == 'hourly') {
      return '${months[_rangeStart.month]} ${_rangeStart.day}, ${_rangeStart.year}';
    }
    return '${months[_rangeStart.month]} ${_rangeStart.day} – ${months[_rangeEnd.month]} ${_rangeEnd.day}, ${_rangeEnd.year}';
  }

  String _resolutionLabel() {
    switch (_resolution) {
      case 'hourly':
        return '24 horas × 7 factors';
      case 'monthly':
        return '12 months × 7 factors';
      case 'yearly':
        return 'Years × 7 factors';
      default:
        return 'Days × 7 factors';
    }
  }
}

// ── Sub-widgets (screen-level) ──

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

class _FactorChip extends StatelessWidget {
  final FactorScore factor;
  const _FactorChip({required this.factor});

  @override
  Widget build(BuildContext context) {
    final color = factor.dominantPlanet.isNotEmpty
        ? planetColor(factor.dominantPlanet)
        : _scoreColor(factor.score);

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: GlassContainer(
        padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
        child: Row(
          children: [
            // Planet glyph
            if (factor.dominantPlanet.isNotEmpty)
              Text(
                planetGlyph(factor.dominantPlanet),
                style: TextStyle(fontSize: 16, color: color),
              ),
            if (factor.dominantPlanet.isNotEmpty)
              const SizedBox(width: S.sm),
            // Name
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    factor.name,
                    style: T.bodySm.copyWith(
                        color: C.textPrimary,
                        fontWeight: FontWeight.w500,
                        fontSize: 13),
                  ),
                  if (factor.description.isNotEmpty)
                    Text(
                      factor.description,
                      style: T.caption.copyWith(fontSize: 10),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
            // Score bar
            SizedBox(
              width: 50,
              child: ClipRRect(
                borderRadius: R.smBr,
                child: LinearProgressIndicator(
                  value: (factor.score / 10).clamp(0.0, 1.0),
                  minHeight: 4,
                  backgroundColor: C.glassBorder,
                  valueColor: AlwaysStoppedAnimation(color),
                ),
              ),
            ),
            const SizedBox(width: S.sm),
            // Score number
            Text(
              factor.score.toStringAsFixed(1),
              style: T.bodySm.copyWith(
                  color: color, fontWeight: FontWeight.w600, fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }

  Color _scoreColor(double s) {
    if (s >= 7) return C.positive;
    if (s >= 4) return C.warning;
    return C.negative;
  }
}

class _EventCard extends StatelessWidget {
  final LifeEvent event;
  const _EventCard({required this.event});

  @override
  Widget build(BuildContext context) {
    final color = _eventColor(event.type);

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
        decoration: BoxDecoration(
          borderRadius: R.mdBr,
          color: color.withValues(alpha: 0.08),
          border: Border.all(color: color.withValues(alpha: 0.25)),
        ),
        child: Row(
          children: [
            Text(_eventIcon(event.type),
                style: const TextStyle(fontSize: 16)),
            const SizedBox(width: S.sm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    event.description.isNotEmpty
                        ? event.description
                        : event.type,
                    style: T.bodySm.copyWith(
                        color: C.textPrimary, fontSize: 13),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    _formatDate(event.date),
                    style: T.caption.copyWith(fontSize: 10),
                  ),
                ],
              ),
            ),
            if (event.actualRating != null)
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.sm, vertical: 2),
                decoration: BoxDecoration(
                  borderRadius: R.smBr,
                  color: _ratingColor(event.actualRating!).withValues(alpha: 0.2),
                ),
                child: Text(
                  '${event.actualRating!.round()}/10',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: _ratingColor(event.actualRating!),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  static Color _eventColor(String type) {
    switch (type) {
      case 'career':
        return C.jupiter;
      case 'relationship':
        return C.venus;
      case 'health':
        return C.sun;
      case 'finance':
        return C.mercury;
      case 'spiritual':
        return C.saturn;
      case 'travel':
        return C.moon;
      case 'education':
        return C.mercury;
      case 'loss':
        return C.negative;
      default:
        return C.accent;
    }
  }

  static String _eventIcon(String type) {
    switch (type) {
      case 'career':
        return '💼';
      case 'relationship':
        return '❤️';
      case 'health':
        return '🏥';
      case 'finance':
        return '💰';
      case 'spiritual':
        return '🕉️';
      case 'travel':
        return '✈️';
      case 'education':
        return '📚';
      case 'loss':
        return '💔';
      default:
        return '📌';
    }
  }

  static String _formatDate(DateTime dt) {
    const months = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[dt.month]} ${dt.day}, ${dt.year}';
  }

  static Color _ratingColor(double r) {
    if (r >= 7) return C.positive;
    if (r >= 4) return C.warning;
    return C.negative;
  }
}
