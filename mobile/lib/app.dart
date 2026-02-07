import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
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

void main() => runApp(const App());

class App extends StatelessWidget {
  const App({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: '108',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xff0a0a1a),
        primaryColor: const Color(0xff6C63FF),
        textTheme: const TextTheme(
          headlineSmall: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w700,
            color: Colors.white,
          ),
          titleMedium: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
          titleSmall: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
          labelMedium: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: Colors.white70,
          ),
          labelSmall: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w400,
            color: Colors.white54,
          ),
          bodyMedium: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w400,
            color: Colors.white,
          ),
          bodySmall: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w400,
            color: Colors.white70,
          ),
        ),
      ),
      routerConfig: _buildRouter(),
    );
  }

  GoRouter _buildRouter() {
    return GoRouter(
      initialLocation: '/phone-auth',
      routes: [
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
        GoRoute(
          path: '/profile',
          builder: (context, state) => const ProfileScreen(),
        ),
        GoRoute(
          path: '/birth-details',
          builder: (context, state) => const BirthDetailsScreen(),
        ),
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
  }
}
