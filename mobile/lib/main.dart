import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:firebase_core/firebase_core.dart';
import 'app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Supabase
  const supabaseUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: 'https://bblkgmgkeukctrvpvkud.supabase.co',
  );
  const supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJibGtnbWdrZXVrY3RydnB2a3VkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0NTUxMDUsImV4cCI6MjA4NjAzMTEwNX0.hAMIl-0jTDX8dfrtD6250VrJxeAs2P99JCPEUdfeTRk',
  );

  await Supabase.initialize(url: supabaseUrl, anonKey: supabaseAnonKey);

  // Initialize Firebase (skip in dev if not configured)
  try {
    await Firebase.initializeApp();
  } catch (e) {
    if (kDebugMode) {
      debugPrint('Firebase not configured, skipping: $e');
    }
  }

  // TODO: Initialize RevenueCat
  // await Purchases.setup("revenuecat_api_key");

  runApp(
    const ProviderScope(
      child: App(),
    ),
  );
}
