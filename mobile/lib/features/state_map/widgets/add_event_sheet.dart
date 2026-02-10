import 'package:flutter/material.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import '../models/state_vector.dart';

/// Bottom sheet to log a real life event for verification.
///
/// The user taps the FAB → this sheet slides up → they pick a type,
/// write a description, rate how they felt (1-10), and save.
class AddEventSheet extends StatefulWidget {
  final DateTime? initialDate;
  final ValueChanged<LifeEvent> onSave;

  const AddEventSheet({
    super.key,
    this.initialDate,
    required this.onSave,
  });

  static void show(
    BuildContext context, {
    DateTime? initialDate,
    required ValueChanged<LifeEvent> onSave,
  }) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => AddEventSheet(
        initialDate: initialDate,
        onSave: onSave,
      ),
    );
  }

  @override
  State<AddEventSheet> createState() => _AddEventSheetState();
}

class _AddEventSheetState extends State<AddEventSheet> {
  late DateTime _date;
  String _type = 'career';
  final _descController = TextEditingController();
  double _rating = 5;

  @override
  void initState() {
    super.initState();
    _date = widget.initialDate ?? DateTime.now();
  }

  @override
  void dispose() {
    _descController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding:
          EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Container(
        decoration: const BoxDecoration(
          color: C.surface,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        padding: const EdgeInsets.fromLTRB(S.xl, S.md, S.xl, S.xl),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Handle
            Center(
              child: Container(
                width: 32,
                height: 4,
                decoration: BoxDecoration(
                  borderRadius: R.smBr,
                  color: C.glassBorder,
                ),
              ),
            ),
            const SizedBox(height: S.lg),

            Text('Log Life Event', style: T.h3),
            const SizedBox(height: 4),
            Text(
              'Mark what actually happened so you can verify predictions',
              style: T.bodySm.copyWith(color: C.textMuted),
            ),
            const SizedBox(height: S.xl),

            // Date picker row
            GestureDetector(
              onTap: _pickDate,
              child: GlassContainer(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.md, vertical: S.sm),
                child: Row(
                  children: [
                    const Icon(Icons.calendar_today,
                        size: 16, color: C.textSecondary),
                    const SizedBox(width: S.sm),
                    Text(
                      _formatDate(_date),
                      style: T.bodySm.copyWith(color: C.textPrimary),
                    ),
                    const Spacer(),
                    const Icon(Icons.chevron_right,
                        size: 16, color: C.textMuted),
                  ],
                ),
              ),
            ),
            const SizedBox(height: S.md),

            // Type chips
            Text('TYPE',
                style: T.label.copyWith(color: C.textMuted)),
            const SizedBox(height: S.sm),
            Wrap(
              spacing: S.sm,
              runSpacing: S.sm,
              children: kEventTypes.map((t) {
                final isSelected = t == _type;
                return GestureDetector(
                  onTap: () => setState(() => _type = t),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: S.md, vertical: S.sm),
                    decoration: BoxDecoration(
                      borderRadius: R.xlBr,
                      color: isSelected ? C.accentDim : C.glassBg,
                      border: Border.all(
                        color: isSelected ? C.accent : C.glassBorder,
                        width: isSelected ? 1.5 : 0.5,
                      ),
                    ),
                    child: Text(
                      t[0].toUpperCase() + t.substring(1),
                      style: T.bodySm.copyWith(
                        color: isSelected ? C.accent : C.textSecondary,
                        fontSize: 12,
                        fontWeight:
                            isSelected ? FontWeight.w600 : FontWeight.w400,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: S.md),

            // Description
            Text('WHAT HAPPENED',
                style: T.label.copyWith(color: C.textMuted)),
            const SizedBox(height: S.sm),
            GlassContainer(
              blur: 0,
              padding: const EdgeInsets.symmetric(horizontal: S.md),
              child: TextField(
                controller: _descController,
                style: T.body.copyWith(fontSize: 14),
                decoration: InputDecoration(
                  hintText: 'e.g., Got a promotion, felt anxious...',
                  hintStyle: T.bodySm.copyWith(color: C.textMuted),
                  border: InputBorder.none,
                ),
                maxLines: 2,
              ),
            ),
            const SizedBox(height: S.md),

            // Rating slider
            Text('HOW DID YOU FEEL? (1-10)',
                style: T.label.copyWith(color: C.textMuted)),
            const SizedBox(height: S.sm),
            Row(
              children: [
                Text(
                  _rating.round().toString(),
                  style: T.h2.copyWith(
                    color: _ratingColor(_rating),
                    fontSize: 20,
                  ),
                ),
                Expanded(
                  child: SliderTheme(
                    data: SliderThemeData(
                      activeTrackColor: _ratingColor(_rating),
                      inactiveTrackColor: C.glassBorder,
                      thumbColor: _ratingColor(_rating),
                      overlayColor:
                          _ratingColor(_rating).withValues(alpha: 0.15),
                      trackHeight: 4,
                      thumbShape:
                          const RoundSliderThumbShape(enabledThumbRadius: 8),
                    ),
                    child: Slider(
                      value: _rating,
                      min: 1,
                      max: 10,
                      divisions: 9,
                      onChanged: (v) => setState(() => _rating = v),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: S.xl),

            // Save button
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: _save,
                child: const Text('Save Event'),
              ),
            ),
            const SizedBox(height: S.sm),
          ],
        ),
      ),
    );
  }

  void _save() {
    final event = LifeEvent(
      date: _date,
      type: _type,
      description: _descController.text.trim(),
      actualRating: _rating,
    );
    widget.onSave(event);
    Navigator.pop(context);
  }

  Future<void> _pickDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _date,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.dark(
              primary: C.accent,
              onPrimary: C.bg,
              surface: C.surface,
              onSurface: C.textPrimary,
            ),
          ),
          child: child!,
        );
      },
    );
    if (picked != null) setState(() => _date = picked);
  }

  String _formatDate(DateTime dt) {
    const months = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[dt.month]} ${dt.day}, ${dt.year}';
  }

  Color _ratingColor(double r) {
    if (r >= 7) return C.positive;
    if (r >= 4) return C.warning;
    return C.negative;
  }
}
