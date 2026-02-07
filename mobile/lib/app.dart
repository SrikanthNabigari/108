import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'core/theme/app_theme.dart';
import 'features/auth/screens/phone_auth_screen.dart';
import 'features/auth/screens/otp_verify_screen.dart';
import 'features/onboarding/screens/profile_screen.dart';
import 'features/onboarding/screens/birth_details_screen.dart';
import 'features/home/screens/home_screen.dart';
import 'features/chart/screens/chart_screen.dart';
import 'features/chat/screens/chat_screen.dart';
import 'features/timeline/screens/timeline_screen.dart';
import 'features/calendar/screens/calendar_screen.dart';
import 'features/settings/screens/settings_screen.dart';
import 'features/reports/screens/reports_store_screen.dart';
import 'features/muhurta/screens/muhurta_screen.dart';
import 'features/remedies/screens/remedies_screen.dart';
import 'features/paywall/screens/paywall_screen.dart';
import 'features/paywall/screens/credit_store_screen.dart';

/// Supabase auth state provider — streams auth changes for router redirect
final supabaseAuthProvider = StreamProvider<AuthState>((ref) {
  return Supabase.instance.client.auth.onAuthStateChange;
});

/// GoRouter provider that reacts to auth state
final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(supabaseAuthProvider);

  return GoRouter(
    initialLocation: '/phone-auth',
    redirect: (context, state) {
      final isOnAuthRoute = state.uri.path == '/phone-auth' ||
          state.uri.path == '/otp-verify';
      final isOnOnboarding = state.uri.path == '/profile' ||
          state.uri.path == '/birth-details';

      final isLoggedIn = authState.maybeWhen(
        data: (auth) => auth.session != null,
        orElse: () => false,
      );

      // Not logged in → force to auth (unless already on auth or onboarding)
      if (!isLoggedIn && !isOnAuthRoute && !isOnOnboarding) {
        return '/phone-auth';
      }

      // Logged in and on auth route → go to home
      if (isLoggedIn && isOnAuthRoute) {
        return '/home';
      }

      return null;
    },
    routes: [
      // Auth
      GoRoute(
        path: '/phone-auth',
        builder: (context, state) => const PhoneAuthScreen(),
      ),
      GoRoute(
        path: '/otp-verify',
        builder: (context, state) => OtpVerifyScreen(
          phoneNumber: state.extra as String? ?? '',
        ),
      ),

      // Onboarding
      GoRoute(
        path: '/profile',
        builder: (context, state) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/birth-details',
        builder: (context, state) => const BirthDetailsScreen(),
      ),

      // Main app routes
      GoRoute(
        path: '/home',
        builder: (context, state) => const HomeScreen(),
      ),
      GoRoute(
        path: '/chart',
        builder: (context, state) => const ChartScreen(),
      ),
      GoRoute(
        path: '/chat',
        builder: (context, state) => const ChatScreen(),
      ),
      GoRoute(
        path: '/calendar',
        builder: (context, state) => const CalendarScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(
        path: '/timeline',
        builder: (context, state) => const TimelineScreen(),
      ),
      GoRoute(
        path: '/reports',
        builder: (context, state) => const ReportsStoreScreen(),
      ),
      GoRoute(
        path: '/muhurta',
        builder: (context, state) => const MuhurtaScreen(),
      ),
      GoRoute(
        path: '/remedies',
        builder: (context, state) => const RemediesScreen(),
      ),
      GoRoute(
        path: '/paywall',
        builder: (context, state) => const PaywallScreen(),
      ),
      GoRoute(
        path: '/credit-store',
        builder: (context, state) => const CreditStoreScreen(),
      ),
    ],
  );
});

class App extends ConsumerWidget {
  const App({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: '108',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routerConfig: router,
    );
  }
}
