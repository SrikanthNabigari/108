import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/data/providers/user_provider.dart';
import 'package:one_zero_eight/data/services/supabase_service.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileAsync = ref.watch(userProfileProvider);

    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: Padding(
            padding: S.pagePadding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
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

                const Spacer(),

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
