import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../../../shared/widgets/glass_card.dart';
import '../widgets/today_score_card.dart';
import '../widgets/quick_cards_row.dart';
import '../widgets/forecast_tabs.dart';
import '../widgets/area_rating_bars.dart';

/// Home dashboard hub with greeting, score, quick cards, and forecasts.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final now = DateTime.now();
    final greeting = _getGreeting();

    return StarBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Greeting
                Text(
                  'Namaste, Seeker',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        color: Colors.white,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  DateFormat('EEEE, MMMM d, y').format(now),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.white54,
                      ),
                ),
                const SizedBox(height: 32),
                // Today's score card
                Center(
                  child: TodayScoreCard(
                    score: 7.5,
                    label: 'Today\'s Cosmic Score',
                  ),
                ),
                const SizedBox(height: 32),
                // Quick cards
                Text(
                  'Quick Actions',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white70,
                      ),
                ),
                const SizedBox(height: 12),
                const QuickCardsRow(),
                const SizedBox(height: 32),
                // Forecast section
                Text(
                  'Forecast',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white70,
                      ),
                ),
                const SizedBox(height: 12),
                const ForecastTabs(
                  tierAccess: {
                    'Daily': true,
                    'Weekly': true,
                    'Monthly': true,
                    'Yearly': false,
                  },
                ),
                const SizedBox(height: 32),
                // Area ratings
                Text(
                  'Life Areas',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white70,
                      ),
                ),
                const SizedBox(height: 12),
                const AreaRatingBars(),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
        bottomNavigationBar: const BottomNavBar(currentIndex: 0),
      ),
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }
}
