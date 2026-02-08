import 'package:supabase_flutter/supabase_flutter.dart';

/// Supabase client wrapper — uses Supabase.instance initialized in main.dart
class SupabaseService {
  static final SupabaseService _instance = SupabaseService._internal();

  factory SupabaseService() {
    return _instance;
  }

  SupabaseService._internal();

  /// Get Supabase client instance (lazy — uses the singleton initialized in main.dart)
  SupabaseClient get client => Supabase.instance.client;

  /// Get current user
  User? get currentUser => client.auth.currentUser;

  /// Get current session
  Session? get currentSession => client.auth.currentSession;

  /// Get auth state changes stream
  Stream<AuthState> get authStateChanges => client.auth.onAuthStateChange;

  /// Get access token from current session
  String? get accessToken => currentSession?.accessToken;

  /// Sign in with phone OTP
  Future<void> signInWithPhone(String phone) async {
    await client.auth.signInWithOtp(
      phone: phone,
      shouldCreateUser: true,
    );
  }

  /// Verify OTP
  Future<AuthResponse> verifyOtp({
    required String phone,
    required String token,
  }) async {
    return await client.auth.verifyOTP(
      type: OtpType.sms,
      phone: phone,
      token: token,
    );
  }

  /// Sign in with Google
  Future<bool> signInWithGoogle() async {
    try {
      return await client.auth.signInWithOAuth(
        OAuthProvider.google,
        redirectTo: 'io.supabase.flutter://callback',
      );
    } catch (e) {
      return false;
    }
  }

  /// Sign in with Apple
  Future<bool> signInWithApple() async {
    try {
      return await client.auth.signInWithOAuth(
        OAuthProvider.apple,
        redirectTo: 'io.supabase.flutter://callback',
      );
    } catch (e) {
      return false;
    }
  }

  /// Anonymous sign-in (dev/testing)
  Future<AuthResponse> signInAnonymously() async {
    return await client.auth.signInAnonymously();
  }

  /// Sign out
  Future<void> signOut() async {
    await client.auth.signOut();
  }

  /// Check if user is authenticated
  bool get isAuthenticated => currentUser != null;

  /// Get user ID
  String? get userId => currentUser?.id;

  /// Update user metadata
  Future<void> updateUserMetadata(Map<String, dynamic> metadata) async {
    await client.auth.updateUser(
      UserAttributes(
        data: metadata,
      ),
    );
  }
}
