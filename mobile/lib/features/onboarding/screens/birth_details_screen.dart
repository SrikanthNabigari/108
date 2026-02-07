import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/colors.dart';
import '../../../shared/widgets/star_background.dart';
import '../../../shared/widgets/cosmic_loader.dart';
import '../../../data/services/api_service.dart';
import '../../../core/constants/api_constants.dart';
import '../widgets/place_search_field.dart';

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
  bool _isCalculating = false;

  Future<void> _selectDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: DateTime(2000),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
      builder: (context, child) => Theme(
        data: ThemeData.dark().copyWith(
          colorScheme: const ColorScheme.dark(
            primary: CosmicColors.accentPurple,
            surface: Color(0xFF1A1A2E),
          ),
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
      initialTime: const TimeOfDay(hour: 6, minute: 0),
      builder: (context, child) => Theme(
        data: ThemeData.dark().copyWith(
          colorScheme: const ColorScheme.dark(
            primary: CosmicColors.accentPurple,
            surface: Color(0xFF1A1A2E),
          ),
        ),
        child: child!,
      ),
    );
    if (time != null) {
      setState(() => _selectedTime = time);
    }
  }

  Future<void> _calculateChart() async {
    if (_selectedDate == null ||
        _selectedTime == null ||
        _latitude == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill in all fields')),
      );
      return;
    }

    setState(() => _isCalculating = true);

    // Build birth datetime in ISO format
    final birthDt = DateTime(
      _selectedDate!.year,
      _selectedDate!.month,
      _selectedDate!.day,
      _selectedTime!.hour,
      _selectedTime!.minute,
    );

    // Calculate timezone offset (rough estimate from longitude)
    final tzOffset = (_longitude! / 15).round().toDouble();

    try {
      await ApiService().put(
        ApiConstants.userBirthDetails,
        body: {
          'datetime': birthDt.toIso8601String(),
          'latitude': _latitude,
          'longitude': _longitude,
          'timezone_offset': tzOffset,
          'place_name': _selectedPlace ?? '',
        },
        fromJson: (json) => json,
      );
    } catch (e) {
      debugPrint('Birth details save failed (continuing): $e');
    }

    if (mounted) {
      setState(() => _isCalculating = false);
      context.go('/home');
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
        resizeToAvoidBottomInset: true,
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Progress indicator
                Row(
                  children: List.generate(
                    2,
                    (index) => Expanded(
                      child: Container(
                        height: 3,
                        margin: const EdgeInsets.symmetric(horizontal: 3),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(2),
                          color: index <= 1
                              ? CosmicColors.accentPurple
                              : CosmicColors.glassBorder,
                        ),
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 48),

                // Header
                Text(
                  "Let's meet the\nreal you",
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: CosmicColors.textPrimary,
                    height: 1.15,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Your birth details reveal your cosmic blueprint.',
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 14,
                    color: CosmicColors.textMuted,
                  ),
                ),

                const SizedBox(height: 36),

                // Birth date
                _sectionLabel('BIRTH DATE'),
                const SizedBox(height: 8),
                _pickerTile(
                  icon: Icons.calendar_today_rounded,
                  label: _selectedDate != null
                      ? DateFormat('d MMMM, yyyy').format(_selectedDate!)
                      : 'Select your birth date',
                  hasValue: _selectedDate != null,
                  onTap: _selectDate,
                ),

                const SizedBox(height: 24),

                // Birth time
                _sectionLabel('BIRTH TIME'),
                const SizedBox(height: 8),
                _pickerTile(
                  icon: Icons.access_time_rounded,
                  label: _selectedTime != null
                      ? _selectedTime!.format(context)
                      : 'Select your birth time',
                  subtitle: 'As accurate as possible for precise calculations',
                  hasValue: _selectedTime != null,
                  onTap: _selectTime,
                ),

                const SizedBox(height: 24),

                // Birth place
                _sectionLabel('BIRTH PLACE'),
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
                if (_latitude != null && _longitude != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      '${_latitude!.toStringAsFixed(4)}°, ${_longitude!.toStringAsFixed(4)}°',
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 12,
                        color: CosmicColors.textSubtle,
                      ),
                    ),
                  ),

                const SizedBox(height: 48),

                // Calculate button
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: _isCalculating ? null : _calculateChart,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: Colors.black,
                      disabledBackgroundColor: Colors.white24,
                      elevation: 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                    ),
                    child: Text(
                      'Calculate My Chart',
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),

                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _sectionLabel(String text) {
    return Text(
      text,
      style: GoogleFonts.spaceGrotesk(
        fontSize: 11,
        fontWeight: FontWeight.w600,
        color: CosmicColors.textMuted,
        letterSpacing: 1.2,
      ),
    );
  }

  Widget _pickerTile({
    required IconData icon,
    required String label,
    String? subtitle,
    required bool hasValue,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        decoration: BoxDecoration(
          color: CosmicColors.glass,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: CosmicColors.glassBorder,
            width: 1,
          ),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: GoogleFonts.spaceGrotesk(
                      color: hasValue
                          ? CosmicColors.textPrimary
                          : CosmicColors.textSubtle,
                      fontSize: 16,
                    ),
                  ),
                  if (subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 12,
                        color: CosmicColors.textSubtle,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            Icon(icon, color: CosmicColors.textMuted, size: 20),
          ],
        ),
      ),
    );
  }
}
