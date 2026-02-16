import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/data/services/knowledge_service.dart';

const _signGlyphs = {
  1: '\u2648', 2: '\u2649', 3: '\u264A', 4: '\u264B',
  5: '\u264C', 6: '\u264D', 7: '\u264E', 8: '\u264F',
  9: '\u2650', 10: '\u2651', 11: '\u2652', 12: '\u2653',
};

const _elementColors = {
  'fire': C.mars,
  'earth': C.saturn,
  'air': C.mercury,
  'water': C.moon,
};

/// Bottom sheet panel showing rich sign (rashi) details from bundled knowledge.
class SignInfoPanel extends StatefulWidget {
  final String signId;

  const SignInfoPanel({super.key, required this.signId});

  static void show(BuildContext context, {required String signId}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => SignInfoPanel(signId: signId),
    );
  }

  @override
  State<SignInfoPanel> createState() => _SignInfoPanelState();
}

class _SignInfoPanelState extends State<SignInfoPanel> {
  Map<String, dynamic>? _data;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final result = await KnowledgeService.instance.getRashi(widget.signId);
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
      initialChildSize: 0.65,
      minChildSize: 0.4,
      maxChildSize: 0.85,
      builder: (context, scrollController) {
        return Container(
          decoration: const BoxDecoration(
            color: C.surface,
            borderRadius: BorderRadius.vertical(top: Radius.circular(R.xl)),
          ),
          child: _loading
              ? const Center(child: CircularProgressIndicator(color: C.accent))
              : _data == null
                  ? Center(
                      child: Text('Sign not found',
                          style: T.bodySm.copyWith(color: C.textMuted)))
                  : _buildContent(scrollController),
        );
      },
    );
  }

  Widget _buildContent(ScrollController scrollController) {
    final d = _data!;
    final name = d['name'] as String? ?? '';
    final sanskrit = d['sanskrit'] as String? ?? '';
    final number = d['number'] as int? ?? 1;
    final element = (d['element'] as String? ?? '').toLowerCase();
    final quality = d['quality'] as String? ?? '';
    final gender = d['gender'] as String? ?? '';
    final ruler = (d['ruler'] as String? ?? '').toLowerCase();
    final direction = d['direction'] as String? ?? '';
    final exalted = d['exalted_planet'] as String?;
    final debilitated = d['debilitated_planet'] as String?;
    final bodyPart = d['body_part'] as String? ?? '';
    final rulerColor = planetColor(ruler);
    final elemColor = _elementColors[element] ?? C.accent;

    return Column(
      children: [
        _buildHeader(name, sanskrit, number, elemColor),
        Expanded(
          child: ListView(
            controller: scrollController,
            padding: const EdgeInsets.symmetric(horizontal: S.lg),
            children: [
              const SizedBox(height: S.sm),
              _buildBasics(element, quality, gender, direction, elemColor),
              const SizedBox(height: S.md),
              _buildRuler(ruler, rulerColor),
              if (exalted != null || debilitated != null) ...[
                const SizedBox(height: S.md),
                _buildDignity(exalted, debilitated),
              ],
              if (bodyPart.isNotEmpty) ...[
                const SizedBox(height: S.md),
                _buildBodyPart(bodyPart, elemColor),
              ],
              const SizedBox(height: S.xl),
            ],
          ),
        ),
        _buildAskAiButton(context, name, elemColor),
      ],
    );
  }

  // -- Header --

  Widget _buildHeader(String name, String sanskrit, int number, Color color) {
    final glyph = _signGlyphs[number] ?? '?';

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
              // Large zodiac glyph
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: color.withValues(alpha: 0.15),
                  border: Border.all(color: color.withValues(alpha: 0.4)),
                ),
                child: Center(
                  child: Text(
                    glyph,
                    style: TextStyle(fontSize: 28, color: color),
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
                          style: T.caption.copyWith(
                              color: C.textSecondary, fontSize: 13)),
                  ],
                ),
              ),
              // Number badge
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.sm, vertical: 4),
                decoration: BoxDecoration(
                  borderRadius: R.xlBr,
                  color: color.withValues(alpha: 0.12),
                  border: Border.all(color: color.withValues(alpha: 0.3)),
                ),
                child: Text(
                  '#$number',
                  style: T.caption.copyWith(
                      color: color,
                      fontSize: 11,
                      fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // -- Basics --

  Widget _buildBasics(
      String element, String quality, String gender, String direction,
      Color elemColor) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.category_outlined, color: elemColor, size: 18),
              const SizedBox(width: S.sm),
              Text('Basics',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: S.sm),
          Wrap(
            spacing: S.sm,
            runSpacing: S.sm,
            children: [
              if (element.isNotEmpty)
                _chip(
                  _capitalize(element),
                  elemColor,
                  icon: Icons.local_fire_department,
                ),
              if (quality.isNotEmpty)
                _chip(_capitalize(quality), C.accent),
              if (gender.isNotEmpty)
                _chip(_capitalize(gender), C.textSecondary),
              if (direction.isNotEmpty)
                _chip(
                  _capitalize(direction),
                  C.textSecondary,
                  icon: Icons.explore_outlined,
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _chip(String label, Color color, {IconData? icon}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 4),
      decoration: BoxDecoration(
        borderRadius: R.xlBr,
        color: color.withValues(alpha: 0.10),
        border: Border.all(color: color.withValues(alpha: 0.20)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 12, color: color),
            const SizedBox(width: 4),
          ],
          Text(label,
              style: T.caption.copyWith(
                  color: color, fontSize: 11, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  // -- Ruler --

  Widget _buildRuler(String ruler, Color rulerColor) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(S.md),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: rulerColor.withValues(alpha: 0.06),
        border: Border.all(color: rulerColor.withValues(alpha: 0.15)),
      ),
      child: Row(
        children: [
          Text(planetGlyph(ruler),
              style: TextStyle(fontSize: 22, color: rulerColor)),
          const SizedBox(width: S.sm),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Ruling Planet',
                  style: T.caption.copyWith(color: C.textMuted)),
              Text(planetName(ruler),
                  style: T.bodySm.copyWith(
                      color: rulerColor, fontWeight: FontWeight.w600)),
            ],
          ),
        ],
      ),
    );
  }

  // -- Dignity --

  Widget _buildDignity(String? exalted, String? debilitated) {
    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.swap_vert_circle_outlined,
                  color: C.jupiter, size: 18),
              const SizedBox(width: S.sm),
              Text('Planetary Dignity',
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: S.sm),
          if (exalted != null) _dignityRow('Exalted', exalted, C.positive),
          if (debilitated != null)
            _dignityRow('Debilitated', debilitated, C.warning),
        ],
      ),
    );
  }

  Widget _dignityRow(String label, String planet, Color color) {
    final p = planet.toLowerCase();
    final pc = planetColor(p);
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              borderRadius: R.xlBr,
              color: color.withValues(alpha: 0.12),
            ),
            child: Text(label,
                style: T.caption.copyWith(
                    color: color,
                    fontSize: 10,
                    fontWeight: FontWeight.w600)),
          ),
          const SizedBox(width: S.sm),
          Text(planetGlyph(p),
              style: TextStyle(fontSize: 16, color: pc)),
          const SizedBox(width: 4),
          Text(planetName(p),
              style: T.bodySm.copyWith(
                  color: pc, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  // -- Body Part --

  Widget _buildBodyPart(String bodyPart, Color color) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(S.md),
      decoration: BoxDecoration(
        borderRadius: R.mdBr,
        color: color.withValues(alpha: 0.04),
        border: Border.all(color: color.withValues(alpha: 0.10)),
      ),
      child: Row(
        children: [
          Icon(Icons.accessibility_new, size: 18, color: color),
          const SizedBox(width: S.sm),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Body Part',
                  style: T.caption.copyWith(color: C.textMuted)),
              Text(_capitalize(bodyPart),
                  style: T.bodySm.copyWith(
                      color: C.textPrimary, fontWeight: FontWeight.w500)),
            ],
          ),
        ],
      ),
    );
  }

  // -- Ask AI --

  Widget _buildAskAiButton(BuildContext context, String name, Color color) {
    final prompt =
        'Tell me about $name sign in my chart and how it influences me';
    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pop();
            context.push('/chat?prompt=${Uri.encodeComponent(prompt)}');
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: C.bg,
            shape: RoundedRectangleBorder(borderRadius: R.xlBr),
          ),
          icon: const Icon(Icons.auto_awesome, size: 18),
          label: Text(
            'Ask about $name',
            style:
                T.bodySm.copyWith(color: C.bg, fontWeight: FontWeight.w600),
          ),
        ),
      ),
    );
  }

  // -- Helpers --

  String _capitalize(String s) {
    if (s.isEmpty) return s;
    return s[0].toUpperCase() + s.substring(1);
  }
}
