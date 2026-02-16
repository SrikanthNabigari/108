import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'core/theme/app_theme.dart';
import 'features/auth/screens/phone_auth_screen.dart';
import 'features/auth/screens/otp_verify_screen.dart';
import 'features/onboarding/screens/profile_screen.dart';
import 'features/onboarding/screens/birth_details_screen.dart';
import 'features/shell/app_shell.dart';
import 'features/timeline/screens/timeline_screen.dart';
import 'features/transits/screens/transit_dashboard_screen.dart';
import 'features/state_map/screens/state_map_screen.dart';
import 'features/learn/screens/learn_screen.dart';
import 'features/compatibility/screens/compatibility_screen.dart';
import 'features/reports/screens/reports_screen.dart';
import 'features/reports/widgets/report_viewer.dart';
import 'features/credits/screens/credits_screen.dart';
import 'features/muhurta/screens/muhurta_screen.dart';
import 'features/events/screens/events_screen.dart';
import 'features/chart/screens/divisional_chart_screen.dart';
import 'features/chart/screens/kp_analysis_screen.dart';

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
      if (loggedIn && onAuth) return '/profile-onboard';
      return null;
    },
    routes: [
      // Auth routes (outside shell)
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
        path: '/profile-onboard',
        builder: (_, __) => const ProfileScreen(),
      ),
      GoRoute(
        path: '/birth-details',
        builder: (_, __) => const BirthDetailsScreen(),
      ),

      // Main app shell with bottom nav
      GoRoute(
        path: '/home',
        builder: (_, __) => const AppShell(initialIndex: 0),
      ),
      GoRoute(
        path: '/chart',
        builder: (_, __) => const AppShell(initialIndex: 1),
      ),
      GoRoute(
        path: '/chat',
        builder: (context, state) {
          final prompt = state.uri.queryParameters['prompt'];
          return AppShell(initialIndex: 2, chatPrompt: prompt);
        },
      ),
      GoRoute(
        path: '/forecast',
        builder: (_, __) => const AppShell(initialIndex: 3),
      ),
      GoRoute(
        path: '/profile',
        builder: (_, __) => const AppShell(initialIndex: 4),
      ),

      // Push routes (outside shell, stack on top)
      GoRoute(
        path: '/timeline',
        builder: (_, __) => const TimelineScreen(),
      ),
      GoRoute(
        path: '/transits',
        builder: (_, __) => const TransitDashboardScreen(),
      ),
      GoRoute(
        path: '/state-map',
        builder: (_, __) => const StateMapScreen(),
      ),
      GoRoute(
        path: '/learn',
        builder: (_, __) => const LearnScreen(),
      ),
      GoRoute(
        path: '/compatibility',
        builder: (_, __) => const CompatibilityScreen(),
      ),
      GoRoute(
        path: '/reports',
        builder: (_, __) => const ReportsScreen(),
      ),
      GoRoute(
        path: '/report-view',
        builder: (_, state) {
          final report = state.extra as Map<String, dynamic>?;
          return ReportViewer(reportData: report ?? {});
        },
      ),
      GoRoute(
        path: '/credits',
        builder: (_, __) => const CreditsScreen(),
      ),
      GoRoute(
        path: '/muhurta',
        builder: (_, __) => const MuhurtaScreen(),
      ),
      GoRoute(
        path: '/events',
        builder: (_, __) => const EventsScreen(),
      ),
      GoRoute(
        path: '/divisional',
        builder: (_, __) => const DivisionalChartScreen(),
      ),
      GoRoute(
        path: '/kp-analysis',
        builder: (_, __) => const KpAnalysisScreen(),
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
