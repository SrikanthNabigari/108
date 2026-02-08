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

                // Placeholder cards
                GlassContainer(
                  padding: const EdgeInsets.all(S.xl),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            width: 40,
                            height: 40,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(color: C.accent, width: 2),
                            ),
                            child: const Center(
                              child: Text('~',
                                  style: TextStyle(
                                      color: C.accent, fontSize: 20)),
                            ),
                          ),
                          const SizedBox(width: S.lg),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Chart Calculated',
                                  style: T.h3.copyWith(color: C.accent)),
                              Text('Your cosmic blueprint is ready',
                                  style: T.caption),
                            ],
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: S.lg),

                GlassContainer(
                  padding: const EdgeInsets.all(S.xl),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Coming Soon', style: T.h3),
                      const SizedBox(height: S.sm),
                      Text(
                        'Daily forecasts, life timeline, chat with your chart, '
                        'muhurta finder, and more.',
                        style: T.bodySm.copyWith(color: C.textMuted),
                      ),
                    ],
                  ),
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
