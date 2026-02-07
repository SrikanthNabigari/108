import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../shared/widgets/star_background.dart';

class ReportViewScreen extends ConsumerWidget {
  final String id;
  const ReportViewScreen({required this.id, super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: StarBackground(
        child: SafeArea(
          child: Center(
            child: Text(
              'Report $id',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ),
        ),
      ),
    );
  }
}
