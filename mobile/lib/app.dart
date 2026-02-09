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
import 'features/timeline/screens/timeline_screen.dart';
import 'features/transits/screens/transit_dashboard_screen.dart';
import 'features/chart/screens/chart_screen.dart';

/// Triggers GoRouter redirect re-evaluation on auth changes.
class _AuthNotifier extends ChangeNotifier {
  _AuthNotifier() {
    Supabase.instance.client.auth.onAuthStateChange.listen((_) {
      notifyListeners();
    });
  }
}

final _authNotifier = _AuthNotifier();

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/phone-auth',
    refreshListenable: _authNotifier,
    redirect: (context, state) {
      final session = Supabase.instance.client.auth.currentSession;
      final loggedIn = session != null;
      final onAuth = state.uri.path == '/phone-auth' ||
          state.uri.path == '/otp-verify';

      if (!loggedIn && !onAuth) return '/phone-auth';
      if (loggedIn && onAuth) return '/profile';
      return null;
    },
    routes: [
      GoRoute(
        path: '/phone-auth',
        builder: (_, __) => const PhoneAuthScreen(),
      ),
      GoRoute(
        path: '/otp-verify',
        builder: (_, state) => OtpVerifyScreen(
          phoneNumber: state.extra as String? ?? '',
        ),
      ),
      GoRoute(
        path: '/profile',
        builder: (_, __) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/birth-details',
        builder: (_, __) => const BirthDetailsScreen(),
      ),
      GoRoute(
        path: '/timeline',
        builder: (_, __) => const TimelineScreen(),
      ),
      GoRoute(
        path: '/transits',
        builder: (_, __) => const TransitDashboardScreen(),
      ),
      GoRoute(
        path: '/chart',
        builder: (_, __) => const ChartScreen(),
      ),
      GoRoute(
        path: '/home',
        builder: (_, __) => const HomeScreen(),
      ),
    ],
  );
});

class App extends ConsumerWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: '108',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.dark,
      routerConfig: router,
    );
  }
}
