import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/bottom_nav_bar.dart';
import '../../../shared/widgets/glass_card.dart';
import '../widgets/south_indian_chart.dart';
import '../widgets/planet_list.dart';
import '../widgets/planet_detail_sheet.dart';

/// Birth chart viewer with South Indian grid and planet details.
class ChartScreen extends ConsumerStatefulWidget {
  const ChartScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<ChartScreen> createState() => _ChartScreenState();
}

class _ChartScreenState extends ConsumerState<ChartScreen> {
  int _selectedDivisionalIndex = 0;
  final List<String> _divisionalCharts = ['D1', 'D9', 'D10', 'More'];

  @override
  Widget build(BuildContext context) {
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Birth Chart',
                      style: Theme.of(context)
                          .textTheme
                          .headlineSmall
                          ?.copyWith(
                            color: Colors.white,
                          ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8),
                        color: const Color(0xff6C63FF).withOpacity(0.2),
                      ),
                      child: Text(
                        'Rasi Chart (D1)',
                        style: TextStyle(
                          color: const Color(0xff6C63FF),
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                // South Indian chart
                GlassCard(
                  padding: const EdgeInsets.all(16),
                  child: Center(
                    child: SouthIndianChart(
                      housePlanets: {
                        1: ['Su'],
                        4: ['Mo'],
                        7: ['Ma'],
                        9: ['Me', 'Ve'],
                        10: ['Ju'],
                      },
                      planetSigns: {
                        'Sun': 'Scorpio',
                        'Moon': 'Aquarius',
                      },
                      ascendantHouse: 1,
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                // Divisional chart tabs
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: List.generate(_divisionalCharts.length, (index) {
                      final chart = _divisionalCharts[index];
                      final isSelected = index == _selectedDivisionalIndex;

                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: GestureDetector(
                          onTap: () =>
                              setState(() => _selectedDivisionalIndex = index),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(8),
                              color: isSelected
                                  ? const Color(0xff6C63FF)
                                  : Colors.white.withOpacity(0.05),
                              border: Border.all(
                                color: isSelected
                                    ? const Color(0xff6C63FF)
                                    : Colors.white24,
                              ),
                            ),
                            child: Text(
                              chart,
                              style: TextStyle(
                                color: isSelected
                                    ? Colors.white
                                    : Colors.white70,
                                fontWeight: isSelected
                                    ? FontWeight.w600
                                    : FontWeight.w400,
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ),
                      );
                    }),
                  ),
                ),
                const SizedBox(height: 24),
                // Planet list
                Text(
                  'Planets',
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: Colors.white70,
                      ),
                ),
                const SizedBox(height: 12),
                PlanetList(
                  planets: [
                    _createPlanet('Sun', 'Scorpio', "17° 14'", 'Vishakha', 2),
                    _createPlanet('Moon', 'Aquarius', "24° 21'", 'Purva Bhadrapada',
                        5),
                    _createPlanet(
                      'Mars',
                      'Cancer',
                      "3° 45'",
                      'Pushya',
                      10,
                      isRetrograde: true,
                    ),
                    _createPlanet('Mercury', 'Libra', "28° 40'", 'Vishakha', 1),
                    _createPlanet('Jupiter', 'Virgo', "13° 24'", 'Hasta', 12),
                  ],
                  onPlanetTap: (planet) {
                    showModalBottomSheet(
                      context: context,
                      builder: (_) => PlanetDetailSheet(
                        planetName: planet,
                        sign: 'Scorpio',
                        nakshatra: 'Vishakha',
                        pada: '3rd Pada',
                        dignity: 'Own Sign',
                        house: 2,
                        aspects: [
                          'Jupiter aspects from 12th house',
                          'Saturn aspects from 5th house',
                        ],
                        dashaInfo: 'Venus Mahadasha (0 years, 4 months remaining)',
                      ),
                    );
                  },
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
        bottomNavigationBar: const BottomNavBar(currentIndex: 1),
      ),
    );
  }

  PlanetData _createPlanet(
    String name,
    String sign,
    String degree,
    String nakshatra,
    int house, {
    bool isRetrograde = false,
  }) {
    return PlanetData(
      name: name,
      sign: sign,
      degree: degree,
      nakshatra: nakshatra,
      house: house,
      isRetrograde: isRetrograde,
    );
  }
}
