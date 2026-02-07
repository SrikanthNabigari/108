import 'package:flutter/material.dart';
import '../../../shared/widgets/glass_card.dart';

/// Forecast tabs with free/pro/premium gating.
class ForecastTabs extends StatefulWidget {
  final Map<String, bool> tierAccess;

  const ForecastTabs({
    Key? key,
    this.tierAccess = const {
      'Daily': true,
      'Weekly': false,
      'Monthly': false,
      'Yearly': false,
    },
  }) : super(key: key);

  @override
  State<ForecastTabs> createState() => _ForecastTabsState();
}

class _ForecastTabsState extends State<ForecastTabs> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final tabs = widget.tierAccess.keys.toList();

    return Column(
      children: [
        // Tab bar
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: List.generate(tabs.length, (index) {
              final tab = tabs[index];
              final isSelected = index == _selectedIndex;
              final isLocked = !widget.tierAccess[tab]!;

              return Expanded(
                child: GestureDetector(
                  onTap: () {
                    if (!isLocked) {
                      setState(() => _selectedIndex = index);
                    }
                  },
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    decoration: BoxDecoration(
                      border: isSelected
                          ? const Border(
                              bottom: BorderSide(
                                color: Color(0xff6C63FF),
                                width: 2,
                              ),
                            )
                          : null,
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          tab,
                          style: TextStyle(
                            color: isSelected
                                ? const Color(0xff6C63FF)
                                : Colors.white54,
                            fontWeight: isSelected
                                ? FontWeight.w600
                                : FontWeight.w400,
                          ),
                        ),
                        if (isLocked) ...[
                          const SizedBox(width: 4),
                          const Icon(
                            Icons.lock_rounded,
                            size: 14,
                            color: Colors.white38,
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              );
            }),
          ),
        ),
        const SizedBox(height: 16),
        // Tab content
        GlassCard(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                _getTabTitle(tabs[_selectedIndex]),
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.white,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                _getTabContent(tabs[_selectedIndex]),
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.white70,
                    ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _getTabTitle(String tab) {
    final titles = {
      'Daily': 'Today\'s Forecast',
      'Weekly': 'This Week\'s Outlook',
      'Monthly': 'Monthly Trends',
      'Yearly': 'Annual Blueprint',
    };
    return titles[tab] ?? tab;
  }

  String _getTabContent(String tab) {
    final contents = {
      'Daily': 'Your daily cosmic energy and key transits',
      'Weekly': 'Upcoming planetary movements and influences (Pro+)',
      'Monthly': 'Monthly themes and major events (Pro+)',
      'Yearly': 'Yearly predictions and soul journey (Premium)',
    };
    return contents[tab] ?? '';
  }
}
