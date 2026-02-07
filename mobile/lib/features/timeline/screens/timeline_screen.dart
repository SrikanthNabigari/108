import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../../../shared/widgets/glass_card.dart';
import '../widgets/dasha_chapter_card.dart';

/// Life chapters timeline with Mahadasha periods and transits.
class TimelineScreen extends ConsumerWidget {
  const TimelineScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return StarBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Text(
                  'Life Timeline',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Your Mahadasha periods and planetary cycles',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white54,
                      ),
                ),
                const SizedBox(height: 24),
                // Sade Sati alert
                GlassCard(
                  padding: const EdgeInsets.all(12),
                  margin: EdgeInsets.zero,
                  border: Border.all(
                    color: const Color(0xFFF39C12).withOpacity(0.5),
                    width: 1,
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: const Color(0xFFF39C12).withOpacity(0.2),
                        ),
                        child: const Icon(
                          Icons.warning_rounded,
                          color: Color(0xFFF39C12),
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Sade Sati Phase',
                              style: Theme.of(context)
                                  .textTheme
                                  .labelMedium
                                  ?.copyWith(
                                    color: Colors.white,
                                  ),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'Saturn transiting 8th from Moon (2 years remaining)',
                              style: Theme.of(context)
                                  .textTheme
                                  .labelSmall
                                  ?.copyWith(
                                    color: Colors.white70,
                                  ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Dasha chapters
                DashaChapterCard(
                  planetName: 'Mercury',
                  periodLabel: 'Mercury Mahadasha',
                  dateRange: '2023 - 2040 (17 years)',
                  themes: ['Communication', 'Learning', 'Trade', 'Siblings'],
                  progressPercent: 0.3,
                  isCurrent: true,
                ),
                DashaChapterCard(
                  planetName: 'Saturn',
                  periodLabel: 'Saturn Mahadasha',
                  dateRange: '2040 - 2059 (19 years)',
                  themes: ['Discipline', 'Wisdom', 'Hard Work', 'Structure'],
                  progressPercent: 0.0,
                ),
                DashaChapterCard(
                  planetName: 'Venus',
                  periodLabel: 'Venus Mahadasha',
                  dateRange: '2059 - 2079 (20 years)',
                  themes: ['Pleasure', 'Relationships', 'Wealth', 'Arts'],
                  progressPercent: 0.0,
                ),
                DashaChapterCard(
                  planetName: 'Sun',
                  periodLabel: 'Sun Mahadasha',
                  dateRange: '2079 - 2085 (6 years)',
                  themes: ['Power', 'Authority', 'Vitality', 'Leadership'],
                  progressPercent: 0.0,
                ),
                const SizedBox(height: 24),
                // More info button
                SizedBox(
                  width: double.infinity,
                  height: 44,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white.withOpacity(0.05),
                      side: BorderSide(
                        color: Colors.white24,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    onPressed: () {},
                    child: Text(
                      'Full Timeline & Antardasha',
                      style: Theme.of(context).textTheme.labelMedium?.copyWith(
                            color: Colors.white70,
                          ),
                    ),
                  ),
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
        bottomNavigationBar: const BottomNavBar(currentIndex: -1),
      ),
    );
  }
}
