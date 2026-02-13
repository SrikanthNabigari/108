import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/data/models/compatibility_model.dart';
import 'package:one_zero_eight/data/providers/compatibility_provider.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/features/compatibility/widgets/kuta_score_ring.dart';

class CompatibilityScreen extends ConsumerStatefulWidget {
  const CompatibilityScreen({super.key});

  @override
  ConsumerState<CompatibilityScreen> createState() =>
      _CompatibilityScreenState();
}

class _CompatibilityScreenState extends ConsumerState<CompatibilityScreen> {
  final _nameController = TextEditingController();
  final _cityController = TextEditingController();
  DateTime? _birthDate;
  TimeOfDay? _birthTime;
  bool _showResults = false;
  CompatibilityModel? _result;
  bool _loading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _cityController.dispose();
    super.dispose();
  }

  // ------------------------------------------------------------------
  // Mock data fallback
  // ------------------------------------------------------------------
  static final mockResult = CompatibilityModel(
    kutaScores: [
      const KutaScore(
          name: 'Varna',
          obtained: 1,
          maximum: 1,
          description: 'Spiritual compatibility'),
      const KutaScore(
          name: 'Vashya',
          obtained: 1,
          maximum: 2,
          description: 'Mutual attraction'),
      const KutaScore(
          name: 'Tara',
          obtained: 2,
          maximum: 3,
          description: 'Birth star harmony'),
      const KutaScore(
          name: 'Yoni',
          obtained: 3,
          maximum: 4,
          description: 'Physical compatibility'),
      const KutaScore(
          name: 'Graha Maitri',
          obtained: 4,
          maximum: 5,
          description: 'Mental compatibility'),
      const KutaScore(
          name: 'Gana',
          obtained: 5,
          maximum: 6,
          description: 'Temperament match'),
      const KutaScore(
          name: 'Bhakut',
          obtained: 5,
          maximum: 7,
          description: 'Relationship harmony'),
      const KutaScore(
          name: 'Nadi',
          obtained: 6,
          maximum: 8,
          description: 'Health & genes'),
    ],
    totalObtained: 27,
    totalMaximum: 36,
    verdict: 'Excellent Match',
    summary:
        'Strong compatibility with good harmony across most dimensions.',
  );

  // ------------------------------------------------------------------
  // Actions
  // ------------------------------------------------------------------

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime(1995, 1, 1),
      firstDate: DateTime(1940),
      lastDate: DateTime.now(),
      builder: (ctx, child) => Theme(
        data: Theme.of(ctx).copyWith(
          colorScheme: const ColorScheme.dark(
            primary: C.accent,
            surface: C.surface,
            onSurface: C.textPrimary,
          ),
        ),
        child: child!,
      ),
    );
    if (picked != null) setState(() => _birthDate = picked);
  }

  Future<void> _pickTime() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: const TimeOfDay(hour: 12, minute: 0),
      builder: (ctx, child) => Theme(
        data: Theme.of(ctx).copyWith(
          colorScheme: const ColorScheme.dark(
            primary: C.accent,
            surface: C.surface,
            onSurface: C.textPrimary,
          ),
        ),
        child: child!,
      ),
    );
    if (picked != null) setState(() => _birthTime = picked);
  }

  Future<void> _checkCompatibility() async {
    if (_nameController.text.trim().isEmpty || _birthDate == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter name and birth date')),
      );
      return;
    }

    setState(() => _loading = true);

    final time = _birthTime ?? const TimeOfDay(hour: 12, minute: 0);
    final dt = DateTime(
      _birthDate!.year,
      _birthDate!.month,
      _birthDate!.day,
      time.hour,
      time.minute,
    );

    try {
      final result =
          await ref.read(checkCompatibilityProvider.notifier).call(
                partnerName: _nameController.text.trim(),
                partnerBirthDatetime: dt,
                partnerLatitude: 0,
                partnerLongitude: 0,
                partnerTimezoneOffset: 5.5,
              );
      setState(() {
        _result = result;
        _showResults = true;
        _loading = false;
      });
    } catch (_) {
      // Fallback to mock data
      setState(() {
        _result = mockResult;
        _showResults = true;
        _loading = false;
      });
    }
  }

  void _reset() {
    setState(() {
      _showResults = false;
      _result = null;
      _nameController.clear();
      _cityController.clear();
      _birthDate = null;
      _birthTime = null;
    });
  }

  // ------------------------------------------------------------------
  // Build
  // ------------------------------------------------------------------

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          bottom: false,
          child: Column(
            children: [
              _buildAppBar(),
              const Divider(height: 1),
              Expanded(
                child: _showResults ? _buildResults() : _buildInputForm(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ------------------------------------------------------------------
  // App bar
  // ------------------------------------------------------------------

  Widget _buildAppBar() {
    return Padding(
      padding:
          const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.sm),
      child: Row(
        children: [
          GestureDetector(
            onTap: () =>
                context.canPop() ? context.pop() : context.go('/home'),
            child: Container(
              padding: const EdgeInsets.all(S.sm),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: C.glassBg,
                border: Border.all(color: C.glassBorder),
              ),
              child: const Icon(Icons.arrow_back,
                  color: C.textPrimary, size: 18),
            ),
          ),
          const Spacer(),
          Text('Compatibility', style: T.h3),
          const Spacer(),
          const SizedBox(width: 36),
        ],
      ),
    );
  }

  // ------------------------------------------------------------------
  // Step 1 — Input form
  // ------------------------------------------------------------------

  Widget _buildInputForm() {
    return SingleChildScrollView(
      padding: S.pagePadding.copyWith(top: S.xl, bottom: S.xxxl),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Check Compatibility',
              style: T.h2, textAlign: TextAlign.center),
          const SizedBox(height: S.sm),
          Text(
            'Enter your partner\'s birth details for Ashta Kuta matching',
            style: T.bodySm,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: S.xxl),

          // Partner name
          GlassContainer(
            padding:
                const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.xs),
            child: TextField(
              controller: _nameController,
              style: T.body,
              decoration: const InputDecoration(
                hintText: 'Partner name',
                border: InputBorder.none,
                prefixIcon: Icon(Icons.person_outline,
                    color: C.textMuted, size: 20),
              ),
            ),
          ),
          const SizedBox(height: S.lg),

          // Birth date
          GestureDetector(
            onTap: _pickDate,
            child: GlassContainer(
              padding: const EdgeInsets.symmetric(
                  horizontal: S.lg, vertical: S.lg),
              child: Row(
                children: [
                  const Icon(Icons.calendar_today,
                      color: C.textMuted, size: 20),
                  const SizedBox(width: S.md),
                  Text(
                    _birthDate != null
                        ? '${_birthDate!.day}/${_birthDate!.month}/${_birthDate!.year}'
                        : 'Birth date',
                    style: _birthDate != null
                        ? T.body
                        : T.body.copyWith(color: C.textMuted),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: S.lg),

          // Birth time
          GestureDetector(
            onTap: _pickTime,
            child: GlassContainer(
              padding: const EdgeInsets.symmetric(
                  horizontal: S.lg, vertical: S.lg),
              child: Row(
                children: [
                  const Icon(Icons.access_time,
                      color: C.textMuted, size: 20),
                  const SizedBox(width: S.md),
                  Text(
                    _birthTime != null
                        ? _birthTime!.format(context)
                        : 'Birth time (optional)',
                    style: _birthTime != null
                        ? T.body
                        : T.body.copyWith(color: C.textMuted),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: S.lg),

          // City
          GlassContainer(
            padding:
                const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.xs),
            child: TextField(
              controller: _cityController,
              style: T.body,
              decoration: const InputDecoration(
                hintText: 'Birth city (optional)',
                border: InputBorder.none,
                prefixIcon: Icon(Icons.location_on_outlined,
                    color: C.textMuted, size: 20),
              ),
            ),
          ),
          const SizedBox(height: S.xxl),

          // Submit button
          ElevatedButton(
            onPressed: _loading ? null : _checkCompatibility,
            child: _loading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: C.textOnAccent),
                  )
                : const Text('Check Compatibility'),
          ),
        ],
      ),
    );
  }

  // ------------------------------------------------------------------
  // Step 2 — Results
  // ------------------------------------------------------------------

  Widget _buildResults() {
    final r = _result!;
    final pct = (r.totalObtained / r.totalMaximum * 100).toStringAsFixed(0);

    return SingleChildScrollView(
      padding: S.pagePadding.copyWith(top: S.xl, bottom: S.xxxl),
      child: Column(
        children: [
          // Hero ring
          KutaScoreRing(
            score: r.totalObtained,
            maxScore: r.totalMaximum,
            size: 180,
          ),
          const SizedBox(height: S.lg),

          // Verdict
          Text(r.verdict, style: T.h3),
          const SizedBox(height: S.xs),
          Text('$pct% compatibility',
              style: T.bodySm.copyWith(color: C.textSecondary)),
          if (r.summary != null) ...[
            const SizedBox(height: S.md),
            Text(r.summary!,
                style: T.bodySm, textAlign: TextAlign.center),
          ],
          const SizedBox(height: S.xxl),

          // Kuta detail rows
          ...r.kutaScores.map((k) => _buildKutaRow(k)),

          const SizedBox(height: S.xxl),

          // Full synastry CTA
          OutlinedButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Premium feature coming soon')),
              );
            },
            child: const Text('Full Synastry Report'),
          ),
          const SizedBox(height: S.xs),
          Text('Premium feature', style: T.caption),
          const SizedBox(height: S.lg),

          // Check another
          TextButton(
            onPressed: _reset,
            child: const Text('Check Another'),
          ),
        ],
      ),
    );
  }

  // ------------------------------------------------------------------
  // Kuta detail row
  // ------------------------------------------------------------------

  Widget _buildKutaRow(KutaScore kuta) {
    final ratio = kuta.maximum > 0 ? kuta.obtained / kuta.maximum : 0.0;
    final barColor = ratio > 0.7
        ? C.positive
        : ratio > 0.4
            ? C.warning
            : C.negative;

    return Padding(
      padding: const EdgeInsets.only(bottom: S.md),
      child: GlassContainer(
        padding: const EdgeInsets.all(S.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(kuta.name,
                          style: T.bodySm
                              .copyWith(fontWeight: FontWeight.w500)),
                      if (kuta.description != null)
                        Text(kuta.description!,
                            style: T.caption),
                    ],
                  ),
                ),
                Text(
                  '${kuta.obtained.toStringAsFixed(0)}/${kuta.maximum.toStringAsFixed(0)}',
                  style: T.body.copyWith(
                    color: barColor,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: S.sm),
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: ratio.clamp(0.0, 1.0),
                backgroundColor: C.glassBorder,
                valueColor: AlwaysStoppedAnimation(barColor),
                minHeight: 4,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
