import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import 'package:one_zero_eight/data/providers/auth_provider.dart';
import 'package:one_zero_eight/features/auth/screens/phone_auth_screen.dart';
import 'package:one_zero_eight/features/auth/screens/otp_verify_screen.dart';
import 'package:one_zero_eight/features/onboarding/screens/profile_screen.dart';
import 'package:one_zero_eight/features/onboarding/screens/birth_details_screen.dart';
import 'package:one_zero_eight/features/home/screens/home_screen.dart';
import 'package:one_zero_eight/features/chart/screens/chart_screen.dart';
import 'package:one_zero_eight/features/chat/screens/chat_screen.dart';
import 'package:one_zero_eight/features/calendar/screens/calendar_screen.dart';
import 'package:one_zero_eight/features/settings/screens/settings_screen.dart';
import 'package:one_zero_eight/features/timeline/screens/timeline_screen.dart';
import 'package:one_zero_eight/features/reports/screens/reports_store_screen.dart';
import 'package:one_zero_eight/features/reports/screens/report_view_screen.dart';
import 'package:one_zero_eight/features/muhurta/screens/muhurta_screen.dart';
import 'package:one_zero_eight/features/remedies/screens/remedies_screen.dart';
import 'package:one_zero_eight/features/compatibility/screens/compatibility_screen.dart';
import 'package:one_zero_eight/features/paywall/screens/paywall_screen.dart';
import 'package:one_zero_eight/features/paywall/screens/credit_store_screen.dart';
import 'package:one_zero_eight/shared/widgets/bottom_nav_bar.dart';

part 'app_router.g.dart';

/// Main router provider with auth guards and navigation
@riverpod
GoRouter appRouter(AppRouterRef ref) {
  final authState = ref.watch(authStateProvider);

  return GoRouter(
    initialLocation: '/home',
    redirect: (context, state) {
      // Check if we're on an auth route
      final isAuthRoute =
          state.uri.path.startsWith('/auth') ||
          state.uri.path.startsWith('/onboarding');

      final isAuthenticated = authState.when(
        data: (user) => user != null,
        loading: () => false,
        error: (_, __) => false,
      );

      // If not authenticated and not on auth route, redirect to auth
      if (!isAuthenticated && !isAuthRoute) {
        return '/auth';
      }

      // If authenticated and on auth route, redirect to home
      if (isAuthenticated && isAuthRoute) {
        return '/home';
      }

      return null;
    },
    routes: [
      // Auth routes
      GoRoute(
        path: '/auth',
        name: 'auth',
        builder: (context, state) => const PhoneAuthScreen(),
        routes: [
          GoRoute(
            path: 'otp',
            name: 'otp',
            builder: (context, state) => OtpVerifyScreen(
              phoneNumber: state.extra as String? ?? '',
            ),
          ),
        ],
      ),

      // Onboarding routes
      GoRoute(
        path: '/onboarding',
        name: 'onboarding',
        routes: [
          GoRoute(
            path: 'profile',
            name: 'profile',
            builder: (context, state) => const ProfileScreen(),
          ),
          GoRoute(
            path: 'birth-details',
            name: 'birth-details',
            builder: (context, state) => const BirthDetailsScreen(),
          ),
        ],
      ),

      // Shell route with bottom nav
      ShellRoute(
        builder: (context, state, child) => MainShellScreen(child: child),
        routes: [
          GoRoute(
            path: '/home',
            name: 'home',
            builder: (context, state) => const HomeScreen(),
          ),
          GoRoute(
            path: '/chart',
            name: 'chart',
            builder: (context, state) => const ChartScreen(),
          ),
          GoRoute(
            path: '/chat',
            name: 'chat',
            builder: (context, state) => const ChatScreen(),
          ),
          GoRoute(
            path: '/calendar',
            name: 'calendar',
            builder: (context, state) => const CalendarScreen(),
          ),
          GoRoute(
            path: '/settings',
            name: 'settings',
            builder: (context, state) => const SettingsScreen(),
          ),
        ],
      ),

      // Non-tab routes accessible from anywhere
      GoRoute(
        path: '/timeline',
        name: 'timeline',
        builder: (context, state) => const TimelineScreen(),
      ),
      GoRoute(
        path: '/reports',
        name: 'reports',
        builder: (context, state) => const ReportsStoreScreen(),
        routes: [
          GoRoute(
            path: ':id',
            name: 'report-detail',
            builder: (context, state) =>
                ReportViewScreen(id: state.pathParameters['id']!),
          ),
        ],
      ),
      GoRoute(
        path: '/muhurta',
        name: 'muhurta',
        builder: (context, state) => const MuhurtaScreen(),
      ),
      GoRoute(
        path: '/remedies',
        name: 'remedies',
        builder: (context, state) => const RemediesScreen(),
      ),
      GoRoute(
        path: '/compatibility',
        name: 'compatibility',
        builder: (context, state) => const CompatibilityScreen(),
      ),
      GoRoute(
        path: '/paywall',
        name: 'paywall',
        builder: (context, state) => const PaywallScreen(),
      ),
      GoRoute(
        path: '/credit-store',
        name: 'credit-store',
        builder: (context, state) => const CreditStoreScreen(),
      ),
    ],
  );
}

/// Shell screen with bottom navigation bar
class MainShellScreen extends StatelessWidget {
  final Widget child;
  const MainShellScreen({required this.child, super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: const BottomNavBar(currentIndex: 0),
    );
  }
}
