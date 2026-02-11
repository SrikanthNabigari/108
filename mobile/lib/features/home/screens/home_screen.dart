import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/data/providers/user_provider.dart';
import 'package:one_zero_eight/data/services/supabase_service.dart';
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
  bool _areasLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchAreas();
  }

  Future<void> _fetchAreas() async {
    try {
      final result = await ApiService().get<StateVector>(
        ApiConstants.stateNow,
        fromJson: (json) =>
            StateVector.fromJson(json as Map<String, dynamic>),
      );
      if (mounted) {
        setState(() {
          _areas = result.areas;
          _areasLoading = false;
        });
      }
    } catch (_) {
      // Fallback to mock data
      final mock = MockStateData.now();
      if (mounted) {
        setState(() {
          _areas = mock.areas;
          _areasLoading = false;
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
          child: ListView(
            padding: S.pagePadding,
            children: [
              const SizedBox(height: S.xl),

              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  profileAsync.when(
                    data: (p) => Text(
                      'Hello, ${p.name ?? 'Explorer'}',
                      style: T.h2,
                    ),
                    loading: () =>
                        Text('Hello...', style: T.h2),
                    error: (_, __) =>
                        Text('Hello', style: T.h2),
                  ),
                  GestureDetector(
                    onTap: () async {
                      await SupabaseService().signOut();
                      if (context.mounted) context.go('/phone-auth');
                    },
                    child: Container(
                      padding: const EdgeInsets.all(S.sm),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: C.glassBg,
                        border: Border.all(color: C.glassBorder),
                      ),
                      child: const Icon(Icons.logout,
                          color: C.textMuted, size: 18),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: S.xxxl),

              // Navigation cards
              _NavCard(
                icon: Icons.auto_awesome,
                title: 'Your Chart',
                subtitle: 'Who you are — planets, yogas, doshas, strength',
                color: C.accent,
                onTap: () => context.go('/chart'),
              ),

              const SizedBox(height: S.lg),

              _NavCard(
                icon: Icons.timeline,
                title: 'Life Timeline',
                subtitle: 'When things happen — dasha periods and life chapters',
                color: C.jupiter,
                onTap: () => context.go('/timeline'),
              ),

              const SizedBox(height: S.lg),

              _NavCard(
                icon: Icons.sync,
                title: "What's Happening Now",
                subtitle: 'Current transits, active houses, upcoming triggers',
                color: C.mercury,
                onTap: () => context.go('/transits'),
              ),

              const SizedBox(height: S.lg),

              _NavCard(
                icon: Icons.grid_on,
                title: 'State Map',
                subtitle: 'Your cosmic state — 7 factors, heat map, life areas',
                color: C.saturn,
                onTap: () => context.go('/state-map'),
              ),

              const SizedBox(height: S.lg),

              _NavCard(
                icon: Icons.auto_awesome,
                title: 'Ask Guide',
                subtitle: 'Chat with your astrologer — powered by AI',
                color: C.moon,
                onTap: () => context.go('/chat'),
              ),

              const SizedBox(height: S.lg),

              _NavCard(
                icon: Icons.menu_book_rounded,
                title: 'Learn Jyotish',
                subtitle: 'The complete Vedic Astrology guide',
                color: C.ketu,
                onTap: () => context.go('/learn'),
              ),

              // Mini life areas preview
              if (!_areasLoading && _areas.isNotEmpty) ...[
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
                      onTap: () => context.go('/state-map'),
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
    );
  }
}

class _NavCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _NavCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: GlassContainer(
        padding: const EdgeInsets.all(S.xl),
        child: Row(
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: color.withValues(alpha: 0.15),
                border: Border.all(color: color.withValues(alpha: 0.3)),
              ),
              child: Center(
                child: Icon(icon, color: color, size: 22),
              ),
            ),
            const SizedBox(width: S.lg),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: T.h3.copyWith(color: C.textPrimary)),
                  const SizedBox(height: 2),
                  Text(subtitle,
                      style: T.caption),
                ],
              ),
            ),
            Icon(Icons.chevron_right,
                color: color.withValues(alpha: 0.5), size: 22),
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
