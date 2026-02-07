import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:one_zero_eight/data/services/supabase_service.dart';

part 'auth_provider.g.dart';

/// Stream provider for Supabase auth state changes
@riverpod
Stream<AuthState> authState(AuthStateRef ref) {
  return SupabaseService().authStateChanges;
}

/// Derived provider: current user from auth state
@riverpod
Future<User?> currentUser(CurrentUserRef ref) async {
  final authState = await ref.watch(authStateProvider.future);
  return authState.session?.user;
}

/// Watch if user is authenticated
@riverpod
Future<bool> isAuthenticated(IsAuthenticatedRef ref) async {
  final user = await ref.watch(currentUserProvider.future);
  return user != null;
}

/// Get access token
@riverpod
Future<String?> accessToken(AccessTokenRef ref) async {
  final user = await ref.watch(currentUserProvider.future);
  if (user != null) {
    return SupabaseService().accessToken;
  }
  return null;
}

/// Sign out notifier
@riverpod
Future<void> signOut(SignOutRef ref) async {
  await SupabaseService().signOut();
}
