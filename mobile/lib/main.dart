import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: const String.fromEnvironment(
      'SUPABASE_URL',
      defaultValue: 'https://bblkgmgkeukctrvpvkud.supabase.co',
    ),
    anonKey: const String.fromEnvironment(
      'SUPABASE_ANON_KEY',
      defaultValue:
          'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJibGtnbWdrZXVrY3RydnB2a3VkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0NTUxMDUsImV4cCI6MjA4NjAzMTEwNX0.hAMIl-0jTDX8dfrtD6250VrJxeAs2P99JCPEUdfeTRk',
    ),
  );

  runApp(const ProviderScope(child: App()));
}
