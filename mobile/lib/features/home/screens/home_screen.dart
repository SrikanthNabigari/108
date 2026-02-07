import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/colors.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../../../data/services/api_service.dart';
import '../../../data/services/supabase_service.dart';
import '../../../core/constants/api_constants.dart';
import '../widgets/today_score_card.dart';
import '../widgets/quick_cards_row.dart';
import '../widgets/area_rating_bars.dart';

/// Provider: daily forecast from gateway
final dailyForecastDataProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return await ApiService().get(
    ApiConstants.forecastDaily,
    fromJson: (json) => json as Map<String, dynamic>,
  );
});

/// Provider: chart summary from gateway
final chartSummaryDataProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  return await ApiService().get(
    ApiConstants.chartSummary,
    fromJson: (json) => json as Map<String, dynamic>,
  );
});

class HomeScreen extends ConsumerWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final now = DateTime.now();
    final forecast = ref.watch(dailyForecastDataProvider);
    final chartSummary = ref.watch(chartSummaryDataProvider);

    // Get user name from Supabase metadata or fallback
    final supaUser = SupabaseService().currentUser;
    final userName = supaUser?.userMetadata?['name'] as String? ?? 'Seeker';
    final greeting = _getGreeting();

    return StarBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: RefreshIndicator(
            color: CosmicColors.accentPurple,
            backgroundColor: const Color(0xFF1A1A2E),
            onRefresh: () async {
              ref.invalidate(dailyForecastDataProvider);
              ref.invalidate(chartSummaryDataProvider);
            },
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Greeting
                  Text(
                    '$greeting, $userName',
                    style: GoogleFonts.spaceGrotesk(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: CosmicColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    DateFormat('EEEE, MMMM d, y').format(now),
                    style: GoogleFonts.spaceGrotesk(
                      fontSize: 14,
                      color: CosmicColors.textMuted,
                    ),
                  ),

                  const SizedBox(height: 28),

                  // Today's score — from forecast or fallback
                  Center(
                    child: forecast.when(
                      data: (data) {
                        final rating = (data['day_rating'] as num?)?.toDouble() ?? 7.0;
                        return TodayScoreCard(
                          score: rating,
                          label: data['summary'] as String? ?? "Today's Cosmic Score",
                        );
                      },
                      loading: () => const TodayScoreCard(
                        score: 0,
                        label: 'Loading forecast...',
                      ),
                      error: (_, __) => const TodayScoreCard(
                        score: 7.0,
                        label: "Today's Cosmic Score",
                      ),
                    ),
                  ),

                  const SizedBox(height: 28),

                  // Chart summary card (if available)
                  chartSummary.when(
                    data: (data) => _buildChartCard(context, data),
                    loading: () => const SizedBox.shrink(),
                    error: (_, __) => const SizedBox.shrink(),
                  ),

                  const SizedBox(height: 24),

                  // Quick cards
                  Text(
                    'Quick Actions',
                    style: GoogleFonts.spaceGrotesk(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: CosmicColors.textMuted,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const QuickCardsRow(),

                  const SizedBox(height: 28),

                  // Area ratings from forecast
                  Text(
                    'Life Areas',
                    style: GoogleFonts.spaceGrotesk(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: CosmicColors.textMuted,
                    ),
                  ),
                  const SizedBox(height: 12),
                  forecast.when(
                    data: (data) {
                      final areas = _extractAreaRatings(data);
                      return AreaRatingBars(areaScores: areas);
                    },
                    loading: () => const AreaRatingBars(),
                    error: (_, __) => const AreaRatingBars(),
                  ),

                  const SizedBox(height: 28),

                  // Panchanga card from forecast
                  forecast.when(
                    data: (data) => _buildPanchangaCard(context, data),
                    loading: () => const SizedBox.shrink(),
                    error: (_, __) => const SizedBox.shrink(),
                  ),

                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),
        ),
        bottomNavigationBar: const BottomNavBar(currentIndex: 0),
      ),
    );
  }

  Widget _buildChartCard(BuildContext context, Map<String, dynamic> data) {
    final lagna = data['lagna_rashi'] as String? ?? '—';
    final moon = data['moon_rashi'] as String? ?? '—';
    final nakshatra = data['moon_nakshatra'] as String? ?? '—';

    return GlassCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Your Chart',
            style: GoogleFonts.spaceGrotesk(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: CosmicColors.textPrimary,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _chartChip('Lagna', _capitalize(lagna)),
              const SizedBox(width: 12),
              _chartChip('Moon', _capitalize(moon)),
              const SizedBox(width: 12),
              _chartChip('Nakshatra', _capitalize(nakshatra)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _chartChip(String label, String value) {
    return Expanded(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: GoogleFonts.spaceGrotesk(
              fontSize: 11,
              color: CosmicColors.textSubtle,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: GoogleFonts.spaceGrotesk(
              fontSize: 14,
              color: CosmicColors.accentPurple,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPanchangaCard(BuildContext context, Map<String, dynamic> data) {
    final panchanga = data['panchanga'] as Map<String, dynamic>?;
    if (panchanga == null || panchanga.isEmpty) return const SizedBox.shrink();

    return GlassCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Panchanga',
            style: GoogleFonts.spaceGrotesk(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: CosmicColors.textPrimary,
            ),
          ),
          const SizedBox(height: 12),
          ..._panchangaEntries(panchanga),
        ],
      ),
    );
  }

  List<Widget> _panchangaEntries(Map<String, dynamic> panchanga) {
    final entries = <Widget>[];
    final labels = {
      'tithi': 'Tithi',
      'nakshatra': 'Nakshatra',
      'yoga': 'Yoga',
      'karana': 'Karana',
      'vara': 'Vara',
    };

    for (final entry in labels.entries) {
      final value = panchanga[entry.key];
      if (value != null) {
        entries.add(
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  entry.value,
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 13,
                    color: CosmicColors.textMuted,
                  ),
                ),
                Text(
                  _capitalize(value.toString()),
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 13,
                    color: CosmicColors.textPrimary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        );
      }
    }
    return entries;
  }

  Map<String, double> _extractAreaRatings(Map<String, dynamic> data) {
    final areas = data['area_ratings'] as Map<String, dynamic>?;
    if (areas == null) {
      return {
        'Career': 7.2,
        'Finance': 6.5,
        'Health': 8.1,
        'Relationships': 7.8,
        'Spiritual': 8.5,
      };
    }

    return areas.map((key, value) {
      double score = 5.0;
      if (value is num) {
        score = value.toDouble();
      } else if (value is Map) {
        score = (value['score'] as num?)?.toDouble() ?? 5.0;
      }
      return MapEntry(_capitalize(key), score);
    });
  }

  String _capitalize(String s) {
    if (s.isEmpty) return s;
    return s[0].toUpperCase() + s.substring(1);
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }
}
