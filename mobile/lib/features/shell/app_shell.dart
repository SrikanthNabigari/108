import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/features/home/screens/home_screen.dart';
import 'package:one_zero_eight/features/chart/screens/chart_screen.dart';
import 'package:one_zero_eight/features/chat/screens/chat_screen.dart';
import 'package:one_zero_eight/features/forecast/screens/forecast_screen.dart';
import 'package:one_zero_eight/features/profile/screens/profile_settings_screen.dart';

/// App shell with persistent bottom navigation across 5 main tabs.
class AppShell extends ConsumerStatefulWidget {
  final int initialIndex;
  final String? chatPrompt;

  const AppShell({super.key, this.initialIndex = 0, this.chatPrompt});

  @override
  ConsumerState<AppShell> createState() => _AppShellState();
}

class _AppShellState extends ConsumerState<AppShell> {
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: [
          const HomeScreen(),
          const ChartScreen(),
          ChatScreen(initialPrompt: _currentIndex == 2 ? widget.chatPrompt : null),
          const ForecastScreen(),
          const ProfileSettingsScreen(),
        ],
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(color: C.glassBorder, width: 0.5),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (i) => setState(() => _currentIndex = i),
          type: BottomNavigationBarType.fixed,
          backgroundColor: C.bg,
          selectedItemColor: C.accent,
          unselectedItemColor: C.textMuted,
          selectedFontSize: 11,
          unselectedFontSize: 11,
          showUnselectedLabels: true,
          items: [
            const BottomNavigationBarItem(
              icon: Icon(Icons.home_outlined),
              activeIcon: Icon(Icons.home),
              label: 'Home',
            ),
            const BottomNavigationBarItem(
              icon: Icon(Icons.auto_awesome_outlined),
              activeIcon: Icon(Icons.auto_awesome),
              label: 'Chart',
            ),
            BottomNavigationBarItem(
              icon: Container(
                padding: const EdgeInsets.all(S.sm),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: _currentIndex == 2
                      ? C.accent.withValues(alpha: 0.15)
                      : Colors.transparent,
                  border: Border.all(
                    color: _currentIndex == 2
                        ? C.accent.withValues(alpha: 0.3)
                        : C.glassBorder,
                  ),
                ),
                child: Icon(
                  Icons.chat_bubble_outline,
                  size: 20,
                  color: _currentIndex == 2 ? C.accent : C.textMuted,
                ),
              ),
              activeIcon: Container(
                padding: const EdgeInsets.all(S.sm),
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: C.accent.withValues(alpha: 0.15),
                  border: Border.all(color: C.accent.withValues(alpha: 0.3)),
                ),
                child: const Icon(Icons.chat_bubble, size: 20, color: C.accent),
              ),
              label: 'Chat',
            ),
            const BottomNavigationBarItem(
              icon: Icon(Icons.wb_sunny_outlined),
              activeIcon: Icon(Icons.wb_sunny),
              label: 'Forecast',
            ),
            const BottomNavigationBarItem(
              icon: Icon(Icons.person_outline),
              activeIcon: Icon(Icons.person),
              label: 'Profile',
            ),
          ],
        ),
      ),
    );
  }
}
