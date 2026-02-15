import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/data/providers/user_provider.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import '../widgets/place_search_field.dart';

class BirthDetailsScreen extends ConsumerStatefulWidget {
  const BirthDetailsScreen({super.key});

  @override
  ConsumerState<BirthDetailsScreen> createState() =>
      _BirthDetailsScreenState();
}

class _BirthDetailsScreenState extends ConsumerState<BirthDetailsScreen> {
  DateTime? _date;
  TimeOfDay? _time;
  String? _place;
  double? _lat;
  double? _lon;
  bool _saving = false;

  // ── Cupertino date picker in bottom sheet ──
  void _pickDate() {
    DateTime tempDate = _date ?? DateTime(1990, 4, 1);

    showModalBottomSheet(
      context: context,
      backgroundColor: C.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => SizedBox(
        height: 300,
        child: Column(
          children: [
            // Cancel / Done bar
            Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.sm),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  CupertinoButton(
                    padding: EdgeInsets.zero,
                    child: Text('Cancel',
                        style: T.body.copyWith(color: C.textMuted)),
                    onPressed: () => Navigator.pop(context),
                  ),
                  CupertinoButton(
                    padding: EdgeInsets.zero,
                    child: Text('Done',
                        style: T.body.copyWith(color: C.accent)),
                    onPressed: () {
                      setState(() => _date = tempDate);
                      Navigator.pop(context);
                    },
                  ),
                ],
              ),
            ),
            const Divider(height: 1, color: C.divider),
            Expanded(
              child: CupertinoTheme(
                data: const CupertinoThemeData(
                  brightness: Brightness.dark,
                  textTheme: CupertinoTextThemeData(
                    dateTimePickerTextStyle: TextStyle(
                      color: C.textPrimary,
                      fontSize: 20,
                    ),
                  ),
                ),
                child: CupertinoDatePicker(
                  mode: CupertinoDatePickerMode.date,
                  initialDateTime: tempDate,
                  minimumDate: DateTime(1900),
                  maximumDate: DateTime.now(),
                  onDateTimeChanged: (dt) => tempDate = dt,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Cupertino time picker in bottom sheet ──
  void _pickTime() {
    DateTime tempTime = DateTime(
      2000,
      1,
      1,
      _time?.hour ?? 6,
      _time?.minute ?? 0,
    );

    showModalBottomSheet(
      context: context,
      backgroundColor: C.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => SizedBox(
        height: 300,
        child: Column(
          children: [
            Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.sm),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  CupertinoButton(
                    padding: EdgeInsets.zero,
                    child: Text('Cancel',
                        style: T.body.copyWith(color: C.textMuted)),
                    onPressed: () => Navigator.pop(context),
                  ),
                  CupertinoButton(
                    padding: EdgeInsets.zero,
                    child: Text('Done',
                        style: T.body.copyWith(color: C.accent)),
                    onPressed: () {
                      setState(() => _time =
                          TimeOfDay(hour: tempTime.hour, minute: tempTime.minute));
                      Navigator.pop(context);
                    },
                  ),
                ],
              ),
            ),
            const Divider(height: 1, color: C.divider),
            Expanded(
              child: CupertinoTheme(
                data: const CupertinoThemeData(
                  brightness: Brightness.dark,
                  textTheme: CupertinoTextThemeData(
                    dateTimePickerTextStyle: TextStyle(
                      color: C.textPrimary,
                      fontSize: 20,
                    ),
                  ),
                ),
                child: CupertinoDatePicker(
                  mode: CupertinoDatePickerMode.time,
                  initialDateTime: tempTime,
                  use24hFormat: false,
                  onDateTimeChanged: (dt) => tempTime = dt,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _calculate() async {
    if (_date == null || _time == null || _lat == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in all fields')),
      );
      return;
    }

    setState(() => _saving = true);

    final birthDt = DateTime(
        _date!.year, _date!.month, _date!.day, _time!.hour, _time!.minute);
    final tz = (_lon! / 15).round().toDouble();

    try {
      await ApiService().put(
        ApiConstants.userBirthDetails,
        body: {
          'datetime': birthDt.toIso8601String(),
          'latitude': _lat,
          'longitude': _lon,
          'timezone_offset': tz,
          'place_name': _place ?? '',
        },
        fromJson: (json) => json,
      );
      ref.invalidate(userProfileProvider);
      if (mounted) context.go('/home');
    } catch (e) {
      if (mounted) {
        setState(() => _saving = false);
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('$e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: Padding(
            padding: S.pagePadding,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: S.xl),

                // Progress
                _ProgressBar(step: 2, total: 2),

                const SizedBox(height: S.xxxl),

                Text("Let's meet the\nreal you.", style: T.h1),
                const SizedBox(height: S.sm),
                Text(
                  'Your birth details reveal your cosmic blueprint.',
                  style: T.bodySm.copyWith(color: C.textMuted),
                ),

                const SizedBox(height: S.xxl),

                // Date
                GlassContainer(
                  padding: const EdgeInsets.all(S.lg),
                  child: GestureDetector(
                    onTap: _pickDate,
                    behavior: HitTestBehavior.opaque,
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('BIRTH DATE', style: T.label),
                              const SizedBox(height: S.xs),
                              Text(
                                _date != null
                                    ? DateFormat('d MMMM yyyy').format(_date!)
                                    : 'Select your birth date',
                                style: T.body.copyWith(
                                  color: _date != null
                                      ? C.textPrimary
                                      : C.textMuted,
                                ),
                              ),
                            ],
                          ),
                        ),
                        const Icon(Icons.chevron_right,
                            color: C.textMuted, size: 20),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: S.md),

                // Time
                GlassContainer(
                  padding: const EdgeInsets.all(S.lg),
                  child: GestureDetector(
                    onTap: _pickTime,
                    behavior: HitTestBehavior.opaque,
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('BIRTH TIME', style: T.label),
                              const SizedBox(height: S.xs),
                              Text(
                                _time != null
                                    ? _time!.format(context)
                                    : 'Select your birth time',
                                style: T.body.copyWith(
                                  color: _time != null
                                      ? C.textPrimary
                                      : C.textMuted,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'As accurate as possible for precise calculations',
                                style: T.caption,
                              ),
                            ],
                          ),
                        ),
                        Icon(
                          _time != null
                              ? Icons.check_circle
                              : Icons.lock_outline,
                          color: _time != null ? C.accent : C.textMuted,
                          size: 18,
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: S.md),

                // Place
                GlassContainer(
                  padding: const EdgeInsets.symmetric(
                      horizontal: S.lg, vertical: S.sm),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(top: S.sm),
                        child: Text('BIRTH PLACE', style: T.label),
                      ),
                      PlaceSearchField(
                        onPlaceSelected: (place, lat, lon) {
                          setState(() {
                            _place = place;
                            _lat = lat;
                            _lon = lon;
                          });
                        },
                      ),
                    ],
                  ),
                ),
                if (_lat != null)
                  Padding(
                    padding: const EdgeInsets.only(top: S.xs, left: S.sm),
                    child: Text(
                      '${_lat!.toStringAsFixed(4)}, ${_lon!.toStringAsFixed(4)}',
                      style: T.caption.copyWith(color: C.accent),
                    ),
                  ),

                const Spacer(),

                // Calculate
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _saving ? null : _calculate,
                    child: _saving
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: C.textOnAccent),
                          )
                        : const Text('Calculate My Chart'),
                  ),
                ),
                const SizedBox(height: S.xxl),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ProgressBar extends StatelessWidget {
  final int step;
  final int total;
  const _ProgressBar({required this.step, required this.total});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(
        total,
        (i) => Expanded(
          child: Container(
            height: 3,
            margin: const EdgeInsets.symmetric(horizontal: 3),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(2),
              color: i < step ? C.accent : C.glassBorder,
            ),
          ),
        ),
      ),
    );
  }
}
