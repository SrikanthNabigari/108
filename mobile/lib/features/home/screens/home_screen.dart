import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/data/providers/user_provider.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/features/state_map/models/state_vector.dart';
import 'package:one_zero_eight/features/state_map/models/mock_data.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  List<AreaScore> _areas = [];
  double _composite = 0;
  String _mentalState = '';
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetchState();
  }

  Future<void> _fetchState() async {
    try {
      final result = await ApiService().get<StateVector>(
        ApiConstants.stateNow,
        fromJson: (json) =>
            StateVector.fromJson(json as Map<String, dynamic>),
      );
      if (mounted) {
        final sorted = List<AreaScore>.from(result.areas)
          ..sort((a, b) => b.score.compareTo(a.score));
        setState(() {
          _areas = sorted;
          _composite = result.composite;
          _mentalState = result.mentalState;
          _loading = false;
        });
      }
    } catch (_) {
      final mock = MockStateData.now();
      if (mounted) {
        final sorted = List<AreaScore>.from(mock.areas)
          ..sort((a, b) => b.score.compareTo(a.score));
        setState(() {
          _areas = sorted;
          _composite = mock.composite;
          _mentalState = mock.mentalState;
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(userProfileProvider);

    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: RefreshIndicator(
            onRefresh: _fetchState,
            color: C.accent,
            backgroundColor: C.surface,
            child: ListView(
              padding: S.pagePadding,
              children: [
                const SizedBox(height: S.xl),

                // Greeting
                profileAsync.when(
                  data: (p) => Text(
                    'Hello, ${p.name ?? 'Explorer'}',
                    style: T.h2,
                  ),
                  loading: () => Text('Hello...', style: T.h2),
                  error: (_, __) => Text('Hello', style: T.h2),
                ),

                const SizedBox(height: S.xl),

                // Day rating mini card
                if (!_loading)
                  GlassContainer(
                    padding: const EdgeInsets.all(S.xl),
                    borderColor: _scoreColor(_composite).withValues(alpha: 0.3),
                    child: Row(
                      children: [
                        // Score circle
                        Container(
                          width: 56,
                          height: 56,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: _scoreColor(_composite).withValues(alpha: 0.12),
                            border: Border.all(
                              color: _scoreColor(_composite).withValues(alpha: 0.4),
                            ),
                          ),
                          child: Center(
                            child: Text(
                              _composite.toStringAsFixed(1),
                              style: T.h3.copyWith(
                                color: _scoreColor(_composite),
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: S.lg),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text("Today's State",
                                  style: T.bodySm.copyWith(color: C.textMuted)),
                              const SizedBox(height: 2),
                              Text(
                                _mentalState.isNotEmpty ? _mentalState : 'Steady',
                                style: T.h3.copyWith(
                                  color: _scoreColor(_composite),
                                ),
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          Icons.chevron_right,
                          color: C.textMuted.withValues(alpha: 0.5),
                          size: 22,
                        ),
                      ],
                    ),
                  ),
                if (_loading)
                  GlassContainer(
                    padding: const EdgeInsets.all(S.xl),
                    child: Row(
                      children: [
                        Container(
                          width: 56,
                          height: 56,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: C.glassBg,
                          ),
                        ),
                        const SizedBox(width: S.lg),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                width: 80,
                                height: 12,
                                decoration: BoxDecoration(
                                  color: C.glassBg,
                                  borderRadius: R.smBr,
                                ),
                              ),
                              const SizedBox(height: S.sm),
                              Container(
                                width: 120,
                                height: 16,
                                decoration: BoxDecoration(
                                  color: C.glassBg,
                                  borderRadius: R.smBr,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                const SizedBox(height: S.xl),

                // Quick actions
                Text('Quick Actions',
                    style: T.h3.copyWith(fontSize: 16)),
                const SizedBox(height: S.sm),
                GridView.count(
                  crossAxisCount: 3,
                  mainAxisSpacing: S.sm,
                  crossAxisSpacing: S.sm,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  childAspectRatio: 1.0,
                  children: [
                    _QuickAction(
                      icon: Icons.grid_on,
                      label: 'State Map',
                      color: C.saturn,
                      onTap: () => context.push('/state-map'),
                    ),
                    _QuickAction(
                      icon: Icons.timeline,
                      label: 'Timeline',
                      color: C.jupiter,
                      onTap: () => context.push('/timeline'),
                    ),
                    _QuickAction(
                      icon: Icons.sync,
                      label: 'Transits',
                      color: C.mercury,
                      onTap: () => context.push('/transits'),
                    ),
                    _QuickAction(
                      icon: Icons.menu_book_rounded,
                      label: 'Learn',
                      color: C.ketu,
                      onTap: () => context.push('/learn'),
                    ),
                    _QuickAction(
                      icon: Icons.people_outline,
                      label: 'Compatibility',
                      color: C.venus,
                      onTap: () => context.push('/compatibility'),
                    ),
                    _QuickAction(
                      icon: Icons.description_outlined,
                      label: 'Reports',
                      color: C.sun,
                      onTap: () => context.push('/reports'),
                    ),
                  ],
                ),

                // Mini life areas preview
                if (!_loading && _areas.isNotEmpty) ...[
                  const SizedBox(height: S.xl),
                  Row(
                    children: [
                      Text('Life Areas',
                          style: T.h3.copyWith(fontSize: 16)),
                      const SizedBox(width: S.sm),
                      Text('today', style: T.caption),
                    ],
                  ),
                  const SizedBox(height: S.sm),
                  SizedBox(
                    height: 36,
                    child: ListView.separated(
                      scrollDirection: Axis.horizontal,
                      itemCount: _areas.length,
                      separatorBuilder: (_, __) =>
                          const SizedBox(width: S.sm),
                      itemBuilder: (_, i) => _MiniAreaChip(
                        area: _areas[i],
                        onTap: () => context.push('/state-map'),
                      ),
                    ),
                  ),
                ],

                const SizedBox(height: S.xxxl),

                // Footer
                Center(
                  child: Text(
                    'v1.0 — built with cosmic intention',
                    style: T.caption,
                  ),
                ),
                const SizedBox(height: S.lg),
              ],
            ),
          ),
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

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _QuickAction({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: GlassContainer(
        padding: const EdgeInsets.all(S.md),
        borderRadius: 14,
        borderColor: color.withValues(alpha: 0.15),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: color.withValues(alpha: 0.12),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(height: S.sm),
            Text(
              label,
              style: T.bodySm.copyWith(
                color: C.textPrimary,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

class _MiniAreaChip extends StatelessWidget {
  final AreaScore area;
  final VoidCallback onTap;

  const _MiniAreaChip({required this.area, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final planet = kAreaPlanets[area.id] ?? 'saturn';
    final color = planetColor(planet);
    final icon = kAreaIcons[area.id] ?? '\u2022';

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.xs),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(18),
          color: color.withValues(alpha: 0.08),
          border: Border.all(color: color.withValues(alpha: 0.15)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(icon, style: const TextStyle(fontSize: 12)),
            const SizedBox(width: 4),
            Text(
              area.name,
              style: T.bodySm.copyWith(
                color: C.textPrimary,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(width: 4),
            Text(
              area.score.toStringAsFixed(1),
              style: T.bodySm.copyWith(
                color: color,
                fontSize: 12,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
