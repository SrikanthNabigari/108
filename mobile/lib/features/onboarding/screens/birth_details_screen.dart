import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/cosmic_loader.dart';
import '../widgets/place_search_field.dart';

/// Birth details screen with date, time, and location pickers (onboarding step 2 of 2).
class BirthDetailsScreen extends ConsumerStatefulWidget {
  const BirthDetailsScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<BirthDetailsScreen> createState() =>
      _BirthDetailsScreenState();
}

class _BirthDetailsScreenState extends ConsumerState<BirthDetailsScreen> {
  DateTime? _selectedDate;
  TimeOfDay? _selectedTime;
  String? _selectedPlace;
  double? _latitude;
  double? _longitude;
  bool _isLoading = false;
  bool _isCalculating = false;

  Future<void> _selectDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: DateTime(2000),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
      builder: (context, child) => Theme(
        data: ThemeData.dark().copyWith(
          primaryColor: const Color(0xff6C63FF),
          scaffoldBackgroundColor: const Color(0xff0a0a1a),
        ),
        child: child!,
      ),
    );
    if (date != null) {
      setState(() => _selectedDate = date);
    }
  }

  Future<void> _selectTime() async {
    final time = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
      builder: (context, child) => Theme(
        data: ThemeData.dark().copyWith(
          primaryColor: const Color(0xff6C63FF),
        ),
        child: child!,
      ),
    );
    if (time != null) {
      setState(() => _selectedTime = time);
    }
  }

  Future<void> _calculateChart() async {
    if (_selectedDate == null || _selectedTime == null || _latitude == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Please fill in all fields')),
      );
      return;
    }

    setState(() => _isCalculating = true);
    try {
      // TODO: Call chart calculation
      // await ref.read(userProvider.notifier).calculateBirthChart(
      //   birthDate: _selectedDate!,
      //   birthTime: _selectedTime!,
      //   latitude: _latitude!,
      //   longitude: _longitude!,
      // );
      if (mounted) {
        context.go('/home');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    } finally {
      setState(() => _isCalculating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isCalculating) {
      return StarBackground(
        child: Scaffold(
          backgroundColor: Colors.transparent,
          body: const CosmicLoader(
            label: 'Calculating your chart...',
          ),
        ),
      );
    }

    return StarBackground(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
            child: Column(
              children: [
                // Progress indicator
                Row(
                  children: List.generate(
                    2,
                    (index) => Expanded(
                      child: Container(
                        height: 4,
                        margin: const EdgeInsets.symmetric(horizontal: 2),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(2),
                          color: index == 1
                              ? const Color(0xff6C63FF)
                              : Colors.white24,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 40),
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Let\'s meet the real you',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          color: Colors.white,
                        ),
                  ),
                ),
                const SizedBox(height: 8),
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'Your birth details reveal your cosmic blueprint.',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.white54,
                        ),
                  ),
                ),
                const SizedBox(height: 32),
                // Birth date picker
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'BIRTH DATE',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: Colors.white54,
                        ),
                  ),
                ),
                const SizedBox(height: 8),
                GlassCard(
                  onTap: _selectDate,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 16,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        _selectedDate != null
                            ? '${_selectedDate!.day}/${_selectedDate!.month}/${_selectedDate!.year}'
                            : 'Select your birth date',
                        style: TextStyle(
                          color: _selectedDate != null
                              ? Colors.white
                              : Colors.white54,
                          fontSize: 16,
                        ),
                      ),
                      Icon(
                        Icons.calendar_today_rounded,
                        color: Colors.white54,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Birth time picker
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'BIRTH TIME',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: Colors.white54,
                        ),
                  ),
                ),
                const SizedBox(height: 8),
                GlassCard(
                  onTap: _selectTime,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 16,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _selectedTime != null
                                ? _selectedTime!.format(context)
                                : 'Select your birth time',
                            style: TextStyle(
                              color: _selectedTime != null
                                  ? Colors.white
                                  : Colors.white54,
                              fontSize: 16,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'As accurate as possible for precise calculations',
                            style: Theme.of(context)
                                .textTheme
                                .labelSmall
                                ?.copyWith(
                                  color: Colors.white38,
                                ),
                          ),
                        ],
                      ),
                      Icon(
                        Icons.lock_clock_rounded,
                        color: Colors.white54,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Birth place search
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'BIRTH PLACE',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: Colors.white54,
                        ),
                  ),
                ),
                const SizedBox(height: 8),
                PlaceSearchField(
                  onPlaceSelected: (place, lat, lon) {
                    setState(() {
                      _selectedPlace = place;
                      _latitude = lat;
                      _longitude = lon;
                    });
                  },
                ),
                if (_latitude != null && _longitude != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    '$_latitude°, $_longitude°',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          color: Colors.white54,
                        ),
                  ),
                ],
                const SizedBox(height: 48),
                // Calculate button
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: Container(
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xff6C63FF), Color(0xff8A84FF)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _calculateChart,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.transparent,
                        shadowColor: Colors.transparent,
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                              ),
                            )
                          : const Text('Calculate My Chart'),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
