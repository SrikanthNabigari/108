import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/data/services/knowledge_service.dart';

/// Bottom sheet panel showing rich nakshatra details.
///
/// Loads data from KnowledgeService and displays: basics (ruler, deity,
/// symbol, gana, animal), shakti, sounds, and 4 padas with navamsha signs.
class NakshatraInfoPanel extends StatefulWidget {
  final String nakshatraId;

  const NakshatraInfoPanel({super.key, required this.nakshatraId});

  static void show(BuildContext context, {required String nakshatraId}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => NakshatraInfoPanel(nakshatraId: nakshatraId),
    );
  }

  @override
  State<NakshatraInfoPanel> createState() => _NakshatraInfoPanelState();
}

class _NakshatraInfoPanelState extends State<NakshatraInfoPanel> {
  Map<String, dynamic>? _data;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final result =
        await KnowledgeService.instance.getNakshatra(widget.nakshatraId);
    if (mounted) {
      setState(() {
        _data = result;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      minChildSize: 0.5,
      maxChildSize: 0.92,
      builder: (context, scrollController) {
        if (_loading) {
          return Container(
            decoration: BoxDecoration(
              color: C.surface,
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(R.xl)),
            ),
            child: const Center(child: CircularProgressIndicator()),
          );
        }

        if (_data == null) {
          return Container(
            decoration: BoxDecoration(
              color: C.surface,
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(R.xl)),
            ),
            child: Center(
              child: Text('Nakshatra not found', style: T.bodySm),
            ),
          );
        }

        final d = _data!;
        final name = d['name'] as String? ?? '';
        final sanskrit = d['sanskrit'] as String? ?? '';
        final number = d['number'] as int? ?? 0;
        final ruler = (d['ruler'] as String? ?? '').toLowerCase();
        final deity = d['deity'] as String? ?? '';
        final symbol = d['symbol'] as String? ?? '';
        final shakti = d['shakti'] as String? ?? '';
        final gana = d['gana'] as String? ?? '';
        final animal = d['animal'] as String? ?? '';
        final sounds = (d['sounds'] as List?)?.cast<String>() ?? [];
        final padas = (d['padas'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        final color = planetColor(ruler);

        return Container(
          decoration: BoxDecoration(
            color: C.surface,
            borderRadius:
                const BorderRadius.vertical(top: Radius.circular(R.xl)),
          ),
          child: Column(
            children: [
              // A. Gradient header
              _buildHeader(name, sanskrit, number, ruler, color),
              // B. Scrollable content
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: S.lg),
                  children: [
                    const SizedBox(height: S.sm),
                    // Basics
                    _buildBasics(ruler, deity, symbol, gana, animal, color),
                    const SizedBox(height: S.md),
                    // Shakti
                    if (shakti.isNotEmpty) ...[
                      _buildShakti(shakti, color),
                      const SizedBox(height: S.md),
                    ],
                    // Sounds
                    if (sounds.isNotEmpty) ...[
                      _buildSounds(sounds, color),
                      const SizedBox(height: S.md),
                    ],
                    // Padas
                    if (padas.isNotEmpty) ...[
                      _buildPadas(padas, color),
                      const SizedBox(height: S.md),
                    ],
                    const SizedBox(height: S.xl),
                  ],
                ),
              ),
              // C. Ask AI button
              _buildAskAiButton(context, name, color),
            ],
          ),
        );
      },
    );
  }

  // -- A. Gradient Header --

  Widget _buildHeader(
      String name, String sanskrit, int number, String ruler, Color color) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        borderRadius:
            const BorderRadius.vertical(top: Radius.circular(R.xl)),
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            color.withValues(alpha: 0.25),
            Colors.transparent,
          ],
        ),
      ),
      padding: const EdgeInsets.fromLTRB(S.lg, S.md, S.lg, S.sm),
      child: Column(
        children: [
          // Drag handle
          Container(
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: C.glassBorder,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: S.md),
          Row(
            children: [
              // Number circle
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: color.withValues(alpha: 0.15),
                  border: Border.all(color: color.withValues(alpha: 0.4)),
                ),
                child: Center(
                  child: Text(
                    '$number',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                      color: color,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: S.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(name, style: T.h2.copyWith(color: color)),
                    if (sanskrit.isNotEmpty)
                      Text(sanskrit,
                          style: T.bodySm.copyWith(
                              color: color.withValues(alpha: 0.7))),
                  ],
                ),
              ),
              // Ruler glyph
              Text(planetGlyph(ruler),
                  style: TextStyle(fontSize: 28, color: color)),
            ],
          ),
        ],
      ),
    );
  }

  // -- Basics Section --

  Widget _buildBasics(String ruler, String deity, String symbol, String gana,
      String animal, Color color) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_stories, color: color, size: 20),
              const SizedBox(width: S.sm),
              Text(
                'Basics',
                style: T.bodySm.copyWith(
                    color: C.textPrimary, fontWeight: FontWeight.w600),
              ),
            ],
          ),
          const SizedBox(height: S.sm),
          _basicRow('Ruler', Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(planetGlyph(ruler),
                  style: TextStyle(fontSize: 16, color: planetColor(ruler))),
              const SizedBox(width: 4),
              Text(planetName(ruler),
                  style: T.bodySm.copyWith(
                      color: planetColor(ruler),
                      fontWeight: FontWeight.w600)),
            ],
          )),
          _basicRowText('Deity', deity, color),
          _basicRowText('Symbol', symbol, color),
          _basicRowText('Gana', _ganaLabel(gana), color),
          _basicRowText('Animal', animal, color),
        ],
      ),
    );
  }

  Widget _basicRow(String label, Widget value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          SizedBox(
            width: 70,
            child: Text(label,
                style: T.caption.copyWith(color: C.textMuted, fontSize: 12)),
          ),
          Expanded(child: value),
        ],
      ),
    );
  }

  Widget _basicRowText(String label, String value, Color color) {
    if (value.isEmpty) return const SizedBox.shrink();
    return _basicRow(
      label,
      Text(value,
          style: T.bodySm.copyWith(color: C.textSecondary)),
    );
  }

  String _ganaLabel(String gana) {
    switch (gana.toLowerCase()) {
      case 'deva':
        return 'Deva (Divine)';
      case 'manushya':
        return 'Manushya (Human)';
      case 'rakshasa':
        return 'Rakshasa (Demonic)';
      default:
        return gana.isNotEmpty
            ? gana[0].toUpperCase() + gana.substring(1)
            : '';
    }
  }

  // -- Shakti Section --

  Widget _buildShakti(String shakti, Color color) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      backgroundColor: color.withValues(alpha: 0.04),
      borderColor: color.withValues(alpha: 0.15),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.bolt, color: color, size: 20),
          const SizedBox(width: S.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Shakti (Power)',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 4),
                Text(
                  shakti,
                  style: T.caption
                      .copyWith(color: C.textSecondary, height: 1.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // -- Sounds Section --

  Widget _buildSounds(List<String> sounds, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.music_note, color: color, size: 18),
            const SizedBox(width: 6),
            Text('Sounds',
                style: T.bodySm.copyWith(
                    color: C.textPrimary, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: S.sm),
        Row(
          children: sounds.map((s) {
            return Padding(
              padding: const EdgeInsets.only(right: S.sm),
              child: Container(
                width: 52,
                padding:
                    const EdgeInsets.symmetric(horizontal: S.sm, vertical: S.sm),
                decoration: BoxDecoration(
                  borderRadius: R.mdBr,
                  color: color.withValues(alpha: 0.08),
                  border: Border.all(color: color.withValues(alpha: 0.2)),
                ),
                child: Center(
                  child: Text(
                    s,
                    style: T.bodySm.copyWith(
                        color: color, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  // -- Padas Section --

  Widget _buildPadas(List<Map<String, dynamic>> padas, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(Icons.grid_view_rounded, color: color, size: 18),
            const SizedBox(width: 6),
            Text('Padas',
                style: T.bodySm.copyWith(
                    color: C.textPrimary, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: S.sm),
        Row(
          children: padas.map((pada) {
            final padaNum = pada['number'] as int? ?? 0;
            final navSign = pada['navamsha_sign'] as String? ?? '';
            final degrees = pada['degrees'] as Map<String, dynamic>?;
            final start = degrees?['start'];
            final end = degrees?['end'];
            final degreeText = start != null && end != null
                ? '${_formatDeg(start)} - ${_formatDeg(end)}'
                : '';
            final signLabel = navSign.isNotEmpty
                ? navSign[0].toUpperCase() + navSign.substring(1)
                : '';

            return Expanded(
              child: Padding(
                padding: EdgeInsets.only(
                    right: padaNum < 4 ? S.sm : 0),
                child: Container(
                  padding: const EdgeInsets.all(S.sm),
                  decoration: BoxDecoration(
                    borderRadius: R.mdBr,
                    color: color.withValues(alpha: 0.05),
                    border:
                        Border.all(color: color.withValues(alpha: 0.12)),
                  ),
                  child: Column(
                    children: [
                      Text(
                        'Pada $padaNum',
                        style: T.caption.copyWith(
                            color: color,
                            fontWeight: FontWeight.w600,
                            fontSize: 11),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        signLabel,
                        style: T.bodySm.copyWith(
                            color: C.textPrimary,
                            fontWeight: FontWeight.w500,
                            fontSize: 12),
                      ),
                      if (degreeText.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          degreeText,
                          style: T.caption.copyWith(
                              color: C.textMuted, fontSize: 10),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  String _formatDeg(dynamic deg) {
    if (deg is int) return '$deg\u00B0';
    if (deg is double) {
      // Show as integer if whole number, otherwise 1 decimal
      return deg == deg.roundToDouble()
          ? '${deg.toInt()}\u00B0'
          : '${deg.toStringAsFixed(1)}\u00B0';
    }
    return '$deg\u00B0';
  }

  // -- Ask AI Button --

  Widget _buildAskAiButton(BuildContext context, String name, Color color) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pop();
            context.push(
                '/chat?prompt=${Uri.encodeComponent("Tell me about $name nakshatra and how it influences my life")}');
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: C.bg,
            shape: RoundedRectangleBorder(borderRadius: R.xlBr),
          ),
          icon: const Icon(Icons.auto_awesome, size: 18),
          label: Text(
            'Ask about $name',
            style: T.bodySm
                .copyWith(color: C.bg, fontWeight: FontWeight.w600),
          ),
        ),
      ),
    );
  }
}
