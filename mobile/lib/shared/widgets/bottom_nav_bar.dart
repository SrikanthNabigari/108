import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'glass_card.dart';

/// Glassmorphic bottom navigation bar with 5 main tabs.
class BottomNavBar extends StatelessWidget {
  final int currentIndex;

  const BottomNavBar({
    Key? key,
    required this.currentIndex,
  }) : super(key: key);

  void _navigateTo(BuildContext context, int index) {
    final routes = ['/home', '/chart', '/chat', '/calendar', '/settings'];
    if (index < routes.length) {
      context.go(routes[index]);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: GlassCard(
        padding: const EdgeInsets.symmetric(vertical: 8),
        margin: EdgeInsets.zero,
        borderRadius: const BorderRadius.vertical(
          top: Radius.circular(24),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _NavItem(
              icon: Icons.home_rounded,
              label: 'Home',
              index: 0,
              currentIndex: currentIndex,
              onTap: () => _navigateTo(context, 0),
            ),
            _NavItem(
              icon: Icons.auto_awesome_rounded,
              label: 'Chart',
              index: 1,
              currentIndex: currentIndex,
              onTap: () => _navigateTo(context, 1),
            ),
            // Center chat button - elevated
            Transform.translate(
              offset: const Offset(0, -12),
              child: GestureDetector(
                onTap: () => _navigateTo(context, 2),
                child: Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const LinearGradient(
                      colors: [Color(0xff6C63FF), Color(0xff8A84FF)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xff6C63FF).withOpacity(0.4),
                        blurRadius: 16,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Icon(
                    Icons.chat_rounded,
                    color: Colors.white,
                    size: 28,
                  ),
                ),
              ),
            ),
            _NavItem(
              icon: Icons.calendar_today_rounded,
              label: 'Calendar',
              index: 3,
              currentIndex: currentIndex,
              onTap: () => _navigateTo(context, 3),
            ),
            _NavItem(
              icon: Icons.person_rounded,
              label: 'Profile',
              index: 4,
              currentIndex: currentIndex,
              onTap: () => _navigateTo(context, 4),
            ),
          ],
        ),
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final int index;
  final int currentIndex;
  final VoidCallback onTap;

  const _NavItem({
    required this.icon,
    required this.label,
    required this.index,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isActive = index == currentIndex;
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            color: isActive ? const Color(0xff6C63FF) : Colors.white54,
            size: 24,
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: isActive ? const Color(0xff6C63FF) : Colors.white54,
              fontWeight: isActive ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }
}
