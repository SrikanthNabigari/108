import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import '../widgets/event_correlation_panel.dart';

// ---------------------------------------------------------------------------
// Event type config
// ---------------------------------------------------------------------------

class _EventType {
  final String id;
  final String label;
  final IconData icon;
  final Color color;

  const _EventType(this.id, this.label, this.icon, this.color);
}

const _kEventTypes = <_EventType>[
  _EventType('career', 'Career', Icons.work, C.saturn),
  _EventType('marriage', 'Marriage', Icons.favorite, C.venus),
  _EventType('health', 'Health', Icons.favorite_border, C.sun),
  _EventType('money', 'Money', Icons.account_balance_wallet, C.jupiter),
  _EventType('education', 'Education', Icons.school, C.mercury),
  _EventType('travel', 'Travel', Icons.flight, C.rahu),
  _EventType('loss', 'Loss', Icons.sentiment_dissatisfied, C.mars),
  _EventType('children', 'Children', Icons.child_care, C.moon),
  _EventType('property', 'Property', Icons.home, C.ketu),
  _EventType('spiritual', 'Spiritual', Icons.self_improvement, C.ketu),
];

IconData _iconForType(String type) {
  return _kEventTypes
      .firstWhere((e) => e.id == type,
          orElse: () => const _EventType('', '', Icons.event, C.accent))
      .icon;
}

Color _colorForType(String type) {
  return _kEventTypes
      .firstWhere((e) => e.id == type,
          orElse: () => const _EventType('', '', Icons.event, C.accent))
      .color;
}

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

final _kMockEvents = <Map<String, dynamic>>[
  {
    'id': '1',
    'event_date': '2025-06-15',
    'event_type': 'career',
    'event_description': 'Got promoted to Senior Engineer',
    'correlation_score': 82,
  },
  {
    'id': '2',
    'event_date': '2024-11-03',
    'event_type': 'travel',
    'event_description': 'First international trip to Singapore',
    'correlation_score': null,
  },
  {
    'id': '3',
    'event_date': '2024-03-20',
    'event_type': 'health',
    'event_description': 'Recovered from long illness',
    'correlation_score': 65,
  },
  {
    'id': '4',
    'event_date': '2023-08-10',
    'event_type': 'money',
    'event_description': 'Received unexpected bonus',
    'correlation_score': 78,
  },
];

// ===========================================================================
// Screen
// ===========================================================================

class EventsScreen extends ConsumerStatefulWidget {
  const EventsScreen({super.key});

  @override
  ConsumerState<EventsScreen> createState() => _EventsScreenState();
}

class _EventsScreenState extends ConsumerState<EventsScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  List<Map<String, dynamic>> _events = [];
  bool _loading = true;

  // Add-event form state
  final _descController = TextEditingController();
  DateTime? _eventDate;
  String? _eventType;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _fetchEvents();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _descController.dispose();
    super.dispose();
  }

  // -----------------------------------------------------------------------
  // API calls
  // -----------------------------------------------------------------------

  Future<void> _fetchEvents() async {
    try {
      final data = await ApiService().get<List<dynamic>>(
        ApiConstants.events,
        fromJson: (json) => json as List<dynamic>,
      );
      if (!mounted) return;
      setState(() {
        _events = data.cast<Map<String, dynamic>>();
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _events = _kMockEvents;
        _loading = false;
      });
    }
  }

  Future<void> _saveEvent() async {
    if (_eventDate == null || _eventType == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select date and event type')),
      );
      return;
    }
    if (_descController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a description')),
      );
      return;
    }

    setState(() => _saving = true);

    try {
      await ApiService().post<Map<String, dynamic>>(
        ApiConstants.events,
        body: {
          'event_date': _eventDate!.toIso8601String().split('T').first,
          'event_type': _eventType,
          'event_description': _descController.text.trim(),
        },
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (!mounted) return;
      _descController.clear();
      setState(() {
        _eventDate = null;
        _eventType = null;
        _saving = false;
      });
      _tabController.animateTo(0);
      _fetchEvents();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Event saved')),
        );
      }
    } catch (e) {
      if (!mounted) return;
      // Fallback: add locally
      setState(() {
        _events.insert(0, {
          'id': DateTime.now().millisecondsSinceEpoch.toString(),
          'event_date': _eventDate!.toIso8601String().split('T').first,
          'event_type': _eventType,
          'event_description': _descController.text.trim(),
          'correlation_score': null,
        });
        _descController.clear();
        _eventDate = null;
        _eventType = null;
        _saving = false;
      });
      _tabController.animateTo(0);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Event saved locally (offline)')),
        );
      }
    }
  }

  Future<void> _deleteEvent(String id) async {
    try {
      await ApiService().delete(ApiConstants.eventDetail(id));
    } catch (_) {
      // Ignore API error, still remove locally
    }
    if (!mounted) return;
    setState(() {
      _events.removeWhere((e) => e['id'].toString() == id);
    });
  }

  Future<void> _pickEventDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _eventDate ?? DateTime.now(),
      firstDate: DateTime(1940),
      lastDate: DateTime.now(),
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
    if (picked != null) setState(() => _eventDate = picked);
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
                    Text('Life Events', style: T.h3),
                  ],
                ),
              ),

              // Tab bar
              Container(
                margin: const EdgeInsets.symmetric(horizontal: S.lg),
                decoration: BoxDecoration(
                  color: C.glassBg,
                  borderRadius: R.lgBr,
                  border: Border.all(color: C.glassBorder),
                ),
                child: TabBar(
                  controller: _tabController,
                  indicator: BoxDecoration(
                    color: C.accent.withValues(alpha: 0.15),
                    borderRadius: R.lgBr,
                  ),
                  indicatorSize: TabBarIndicatorSize.tab,
                  labelColor: C.textPrimary,
                  unselectedLabelColor: C.textMuted,
                  labelStyle:
                      T.bodySm.copyWith(fontWeight: FontWeight.w600),
                  unselectedLabelStyle: T.bodySm,
                  dividerHeight: 0,
                  tabs: const [
                    Tab(text: 'My Events'),
                    Tab(text: 'Add Event'),
                  ],
                ),
              ),
              const SizedBox(height: S.md),

              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildEventsTab(),
                    _buildAddTab(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // -----------------------------------------------------------------------
  // Tab 1 — My Events
  // -----------------------------------------------------------------------

  Widget _buildEventsTab() {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(strokeWidth: 2, color: C.accent),
      );
    }

    if (_events.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.event_note, color: C.textMuted, size: 48),
            const SizedBox(height: S.md),
            Text('No events yet', style: T.bodySm),
            const SizedBox(height: S.sm),
            Text('Add your first life event to track correlations',
                style: T.caption, textAlign: TextAlign.center),
            const SizedBox(height: S.lg),
            OutlinedButton(
              onPressed: () => _tabController.animateTo(1),
              child: const Text('Add Event'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _fetchEvents,
      color: C.accent,
      backgroundColor: C.surface,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: S.lg),
        itemCount: _events.length,
        itemBuilder: (context, index) {
          final event = _events[index];
          final id = event['id'].toString();

          return Dismissible(
            key: Key(id),
            direction: DismissDirection.endToStart,
            background: Container(
              alignment: Alignment.centerRight,
              padding: const EdgeInsets.only(right: S.xl),
              decoration: BoxDecoration(
                color: C.negative.withValues(alpha: 0.15),
                borderRadius: R.lgBr,
              ),
              child: const Icon(Icons.delete_outline,
                  color: C.negative, size: 24),
            ),
            confirmDismiss: (_) async {
              return await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  backgroundColor: C.surface,
                  shape: RoundedRectangleBorder(borderRadius: R.lgBr),
                  title: const Text('Delete Event?', style: T.h3),
                  content: const Text(
                    'This action cannot be undone.',
                    style: T.bodySm,
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(ctx, false),
                      child: const Text('Cancel'),
                    ),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: C.negative,
                      ),
                      onPressed: () => Navigator.pop(ctx, true),
                      child: const Text('Delete'),
                    ),
                  ],
                ),
              );
            },
            onDismissed: (_) => _deleteEvent(id),
            child: _buildEventCard(event),
          );
        },
      ),
    );
  }

  Widget _buildEventCard(Map<String, dynamic> event) {
    final type = (event['event_type'] as String?) ?? '';
    final desc = (event['event_description'] as String?) ?? '';
    final date = (event['event_date'] as String?) ?? '';
    final corrScore = event['correlation_score'] as num?;
    final color = _colorForType(type);
    final icon = _iconForType(type);

    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: GestureDetector(
        onTap: () => EventCorrelationPanel.show(context, event),
        child: GlassContainer(
          padding: const EdgeInsets.symmetric(
              horizontal: S.lg, vertical: S.md),
          child: Row(
            children: [
              // Type icon
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: color.withValues(alpha: 0.12),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(width: S.md),

              // Description + meta
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(desc,
                        style: T.bodySm.copyWith(
                            color: C.textPrimary,
                            fontWeight: FontWeight.w500),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis),
                    const SizedBox(height: S.xs),
                    Row(
                      children: [
                        // Type badge
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.sm, vertical: 2),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.12),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            type,
                            style: T.caption.copyWith(
                                color: color,
                                fontWeight: FontWeight.w600,
                                fontSize: 10),
                          ),
                        ),
                        const SizedBox(width: S.sm),
                        Text(date, style: T.caption),
                      ],
                    ),
                  ],
                ),
              ),

              // Correlation score
              if (corrScore != null) ...[
                const SizedBox(width: S.sm),
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: _corrColor(corrScore.toDouble())
                        .withValues(alpha: 0.12),
                    border: Border.all(
                        color: _corrColor(corrScore.toDouble())
                            .withValues(alpha: 0.3)),
                  ),
                  child: Center(
                    child: Text(
                      '${corrScore.toInt()}',
                      style: T.caption.copyWith(
                        color: _corrColor(corrScore.toDouble()),
                        fontWeight: FontWeight.w700,
                        fontSize: 11,
                      ),
                    ),
                  ),
                ),
              ] else ...[
                Icon(Icons.chevron_right, color: C.textMuted, size: 20),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Color _corrColor(double s) {
    if (s >= 70) return C.positive;
    if (s >= 40) return C.warning;
    return C.negative;
  }

  // -----------------------------------------------------------------------
  // Tab 2 — Add Event
  // -----------------------------------------------------------------------

  Widget _buildAddTab() {
    return SingleChildScrollView(
      padding: S.pagePadding.copyWith(top: S.xl, bottom: S.xxxl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Record a Life Event',
              style: T.h2, textAlign: TextAlign.center),
          const SizedBox(height: S.sm),
          Text(
            'Track important moments to discover astrological correlations',
            style: T.bodySm,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: S.xl),

          // Date picker
          GestureDetector(
            onTap: _pickEventDate,
            child: GlassContainer(
              padding: const EdgeInsets.symmetric(
                  horizontal: S.lg, vertical: S.lg),
              child: Row(
                children: [
                  const Icon(Icons.calendar_today,
                      color: C.textMuted, size: 20),
                  const SizedBox(width: S.md),
                  Text(
                    _eventDate != null
                        ? '${_eventDate!.day}/${_eventDate!.month}/${_eventDate!.year}'
                        : 'When did it happen?',
                    style: _eventDate != null
                        ? T.body
                        : T.body.copyWith(color: C.textMuted),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: S.lg),

          // Event type chips
          Text('What type?', style: T.bodySm.copyWith(
              color: C.textPrimary, fontWeight: FontWeight.w500)),
          const SizedBox(height: S.sm),
          Wrap(
            spacing: S.sm,
            runSpacing: S.sm,
            children: _kEventTypes.map((t) {
              final selected = _eventType == t.id;
              return GestureDetector(
                onTap: () => setState(() => _eventType = t.id),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.md, vertical: S.sm),
                  decoration: BoxDecoration(
                    color: selected
                        ? t.color.withValues(alpha: 0.15)
                        : Colors.transparent,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: selected
                          ? t.color.withValues(alpha: 0.4)
                          : C.glassBorder,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(t.icon,
                          size: 14,
                          color: selected ? t.color : C.textMuted),
                      const SizedBox(width: S.xs),
                      Text(
                        t.label,
                        style: T.bodySm.copyWith(
                          color: selected ? t.color : C.textSecondary,
                          fontWeight:
                              selected ? FontWeight.w600 : FontWeight.w400,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: S.lg),

          // Description
          GlassContainer(
            padding: const EdgeInsets.symmetric(
                horizontal: S.lg, vertical: S.xs),
            child: TextField(
              controller: _descController,
              style: T.body,
              maxLines: 3,
              decoration: const InputDecoration(
                hintText: 'Describe what happened...',
                border: InputBorder.none,
              ),
            ),
          ),
          const SizedBox(height: S.xl),

          // Save button
          ElevatedButton(
            onPressed: _saving ? null : _saveEvent,
            child: _saving
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: C.textOnAccent),
                  )
                : const Text('Save Event'),
          ),
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
                    Icon(Icons.school, color: C.saturn, size: 18),
                    const SizedBox(width: S.sm),
                    Text(
                      'Why Track Events?',
                      style: T.bodySm.copyWith(
                        color: C.saturn,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: S.sm),
                Text(
                  'By recording life events with dates, you can correlate them '
                  'with your dasha periods, transits, and active yogas. This '
                  'helps validate predictions and discover your unique '
                  'astrological patterns. Over time, these correlations become '
                  'increasingly accurate and personally meaningful.',
                  style: T.bodySm.copyWith(height: 1.6),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
