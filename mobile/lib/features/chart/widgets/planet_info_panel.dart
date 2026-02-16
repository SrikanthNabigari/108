import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/utils/planet_helpers.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/data/services/knowledge_service.dart';

/// Bottom sheet panel showing rich knowledge data for a planet.
///
/// Loads planet definitions from bundled JSON via KnowledgeService and
/// displays sections: basics, dignity, relationships, significations,
/// body/health, remedies, and dasha info.
class PlanetInfoPanel extends StatefulWidget {
  final String planetId;

  const PlanetInfoPanel({super.key, required this.planetId});

  static void show(BuildContext context, {required String planetId}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => PlanetInfoPanel(planetId: planetId),
    );
  }

  @override
  State<PlanetInfoPanel> createState() => _PlanetInfoPanelState();
}

class _PlanetInfoPanelState extends State<PlanetInfoPanel> {
  Map<String, dynamic>? _data;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final result =
        await KnowledgeService.instance.getPlanet(widget.planetId.toLowerCase());
    if (mounted) {
      setState(() {
        _data = result;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = planetColor(widget.planetId);

    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      minChildSize: 0.5,
      maxChildSize: 0.92,
      builder: (context, scrollController) {
        return Container(
          decoration: BoxDecoration(
            color: C.surface,
            borderRadius:
                const BorderRadius.vertical(top: Radius.circular(R.xl)),
          ),
          child: _loading
              ? Center(
                  child: CircularProgressIndicator(color: color),
                )
              : _data == null
                  ? Center(
                      child: Text(
                        'No data for ${planetName(widget.planetId)}',
                        style: T.bodySm,
                      ),
                    )
                  : Column(
                      children: [
                        _buildHeader(color),
                        Expanded(
                          child: ListView(
                            controller: scrollController,
                            padding:
                                const EdgeInsets.symmetric(horizontal: S.lg),
                            children: [
                              const SizedBox(height: S.sm),
                              _buildBasicsGrid(color),
                              const SizedBox(height: S.md),
                              _buildDignitySection(color),
                              const SizedBox(height: S.md),
                              _buildRelationshipsSection(color),
                              const SizedBox(height: S.md),
                              _buildSignificationsSection(color),
                              const SizedBox(height: S.md),
                              _buildBodyHealthSection(color),
                              const SizedBox(height: S.md),
                              _buildRemediesRow(color),
                              const SizedBox(height: S.md),
                              _buildDashaSection(color),
                              const SizedBox(height: S.xl),
                            ],
                          ),
                        ),
                        _buildAskAiButton(context, color),
                      ],
                    ),
        );
      },
    );
  }

  // -- Header --

  Widget _buildHeader(Color color) {
    final d = _data!;
    final name = d['name'] as String? ?? planetName(widget.planetId);
    final sanskrit = d['sanskrit'] as String? ?? '';
    final nature = (d['nature'] as String? ?? '').toLowerCase();
    final natureColor = nature == 'benefic' ? C.positive : C.negative;

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
              Text(
                planetGlyph(widget.planetId),
                style: TextStyle(fontSize: 36, color: color),
              ),
              const SizedBox(width: S.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            name,
                            style: T.h2.copyWith(color: color),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: S.sm),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: S.sm, vertical: 2),
                          decoration: BoxDecoration(
                            borderRadius: R.xlBr,
                            color: natureColor.withValues(alpha: 0.15),
                            border: Border.all(
                                color: natureColor.withValues(alpha: 0.3)),
                          ),
                          child: Text(
                            nature.isNotEmpty
                                ? nature[0].toUpperCase() + nature.substring(1)
                                : '',
                            style: T.caption
                                .copyWith(color: natureColor, fontSize: 10),
                          ),
                        ),
                      ],
                    ),
                    if (sanskrit.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        sanskrit,
                        style: T.caption.copyWith(color: C.textSecondary),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // -- Basics Grid --

  Widget _buildBasicsGrid(Color color) {
    final d = _data!;
    final rows = <_BasicRow>[
      _BasicRow('Element', d['element'] as String? ?? '-'),
      _BasicRow('Gender', d['gender'] as String? ?? '-'),
      _BasicRow('Cabinet', d['cabinet'] as String? ?? '-'),
      _BasicRow('Day', d['day'] as String? ?? '-'),
      _BasicRow('Direction', d['direction'] as String? ?? '-'),
    ];

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Basics',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          ...rows.map((r) => Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Row(
                  children: [
                    SizedBox(
                      width: 80,
                      child: Text(
                        r.label,
                        style: T.caption.copyWith(color: C.textMuted),
                      ),
                    ),
                    Expanded(
                      child: Text(
                        _capitalize(r.value),
                        style: T.caption.copyWith(color: C.textPrimary),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  // -- Dignity Section --

  Widget _buildDignitySection(Color color) {
    final d = _data!;
    final ownsSigns = (d['owns_signs'] as List?)?.cast<String>() ?? [];
    final exalted = d['exalted_in'] as String? ?? '-';
    final debilitated = d['debilitated_in'] as String? ?? '-';
    final moolatrikona = d['moolatrikona'] as Map<String, dynamic>?;
    final mtSign = moolatrikona?['sign'] as String? ?? '-';
    final mtDeg = moolatrikona?['degrees'] as List?;
    final mtLabel = mtDeg != null ? '$mtSign (${mtDeg[0]}-${mtDeg[1]})' : mtSign;

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Dignity',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          _dignityRow('Owns', ownsSigns.join(', '), color),
          _dignityRow('Exalted in', exalted, C.positive),
          _dignityRow('Debilitated in', debilitated, C.negative),
          _dignityRow('Moolatrikona', mtLabel, color),
        ],
      ),
    );
  }

  Widget _dignityRow(String label, String value, Color valueColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          SizedBox(
            width: 100,
            child:
                Text(label, style: T.caption.copyWith(color: C.textMuted)),
          ),
          Expanded(
            child: Text(
              value,
              style: T.caption.copyWith(color: valueColor),
            ),
          ),
        ],
      ),
    );
  }

  // -- Relationships Section --

  Widget _buildRelationshipsSection(Color color) {
    final d = _data!;
    final friends = (d['friends'] as List?)?.cast<String>() ?? [];
    final enemies = (d['enemies'] as List?)?.cast<String>() ?? [];
    final neutral = (d['neutral'] as List?)?.cast<String>() ?? [];

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Relationships',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          if (friends.isNotEmpty) _relationRow('Friends', friends, C.positive),
          if (enemies.isNotEmpty) _relationRow('Enemies', enemies, C.negative),
          if (neutral.isNotEmpty) _relationRow('Neutral', neutral, C.textMuted),
        ],
      ),
    );
  }

  Widget _relationRow(String label, List<String> planets, Color labelColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: S.sm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label,
              style: T.caption
                  .copyWith(color: labelColor, fontWeight: FontWeight.w600)),
          const SizedBox(height: 4),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: planets.map((p) {
              final pId = p.toLowerCase();
              final pColor = planetColor(pId);
              return Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: S.sm, vertical: 3),
                decoration: BoxDecoration(
                  borderRadius: R.xlBr,
                  color: pColor.withValues(alpha: 0.1),
                  border:
                      Border.all(color: pColor.withValues(alpha: 0.2)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(planetGlyph(pId),
                        style: TextStyle(fontSize: 12, color: pColor)),
                    const SizedBox(width: 4),
                    Text(planetName(pId),
                        style: T.caption
                            .copyWith(color: pColor, fontSize: 11)),
                  ],
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  // -- Significations --

  Widget _buildSignificationsSection(Color color) {
    final karakaOf =
        (_data!['karaka_of'] as List?)?.cast<String>() ?? [];
    if (karakaOf.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Significations (Karaka)',
            style: T.bodySm.copyWith(
                color: C.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: S.sm),
        Wrap(
          spacing: 6,
          runSpacing: 6,
          children: karakaOf.map((k) {
            return Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: S.sm, vertical: 4),
              decoration: BoxDecoration(
                borderRadius: R.xlBr,
                color: color.withValues(alpha: 0.1),
                border: Border.all(color: color.withValues(alpha: 0.2)),
              ),
              child: Text(
                _capitalize(k),
                style: T.caption.copyWith(color: color, fontSize: 11),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  // -- Body & Health --

  Widget _buildBodyHealthSection(Color color) {
    final bodyParts =
        (_data!['body_parts'] as List?)?.cast<String>() ?? [];
    final diseases =
        (_data!['diseases'] as List?)?.cast<String>() ?? [];
    if (bodyParts.isEmpty && diseases.isEmpty) return const SizedBox.shrink();

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Body & Health',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          if (bodyParts.isNotEmpty) ...[
            Text('Body Parts',
                style: T.caption
                    .copyWith(color: C.textMuted, fontWeight: FontWeight.w600)),
            const SizedBox(height: 4),
            ...bodyParts.map((bp) => _bulletItem(bp, color)),
            const SizedBox(height: S.sm),
          ],
          if (diseases.isNotEmpty) ...[
            Text('Health Vulnerabilities',
                style: T.caption
                    .copyWith(color: C.textMuted, fontWeight: FontWeight.w600)),
            const SizedBox(height: 4),
            ...diseases.map((d) => _bulletItem(d, C.negative)),
          ],
        ],
      ),
    );
  }

  Widget _bulletItem(String text, Color dotColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 5),
            child: Container(
              width: 4,
              height: 4,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: dotColor,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              _capitalize(text),
              style: T.caption.copyWith(color: C.textSecondary, height: 1.4),
            ),
          ),
        ],
      ),
    );
  }

  // -- Remedies Row --

  Widget _buildRemediesRow(Color color) {
    final d = _data!;
    final gem = d['gem'] as String? ?? '-';
    final metal = d['metal'] as String? ?? '-';
    final gemColor = d['color'] as String? ?? '-';

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Remedies',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          Row(
            children: [
              _remedyItem(Icons.diamond, 'Gem', gem, color),
              const SizedBox(width: S.lg),
              _remedyItem(Icons.circle, 'Metal', metal, color),
              const SizedBox(width: S.lg),
              _remedyItem(Icons.palette, 'Color', gemColor, color),
            ],
          ),
        ],
      ),
    );
  }

  Widget _remedyItem(IconData icon, String label, String value, Color color) {
    return Expanded(
      child: Column(
        children: [
          Icon(icon, size: 18, color: color.withValues(alpha: 0.7)),
          const SizedBox(height: 4),
          Text(label,
              style: T.caption
                  .copyWith(color: C.textMuted, fontSize: 9)),
          const SizedBox(height: 2),
          Text(value,
              style: T.caption.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w500),
              textAlign: TextAlign.center),
        ],
      ),
    );
  }

  // -- Dasha Section --

  Widget _buildDashaSection(Color color) {
    final d = _data!;
    final dashaYears = d['dasha_years'] as int? ?? 0;
    final aspects = (d['aspects'] as List?)?.cast<int>() ?? [];

    return GlassContainer(
      padding: const EdgeInsets.all(S.md),
      blur: 0,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Dasha & Aspects',
              style: T.bodySm.copyWith(
                  color: C.textPrimary, fontWeight: FontWeight.w600)),
          const SizedBox(height: S.sm),
          Row(
            children: [
              SizedBox(
                width: 100,
                child: Text('Dasha Period',
                    style: T.caption.copyWith(color: C.textMuted)),
              ),
              Text(
                '$dashaYears years',
                style: T.caption.copyWith(
                    color: color, fontWeight: FontWeight.w600),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Row(
            children: [
              SizedBox(
                width: 100,
                child: Text('Aspects',
                    style: T.caption.copyWith(color: C.textMuted)),
              ),
              Expanded(
                child: Wrap(
                  spacing: 6,
                  children: aspects.map((a) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        borderRadius: R.xlBr,
                        color: color.withValues(alpha: 0.1),
                        border: Border.all(
                            color: color.withValues(alpha: 0.2)),
                      ),
                      child: Text(
                        '${a}th',
                        style: T.caption.copyWith(
                            color: color, fontSize: 10),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // -- Ask AI Button --

  Widget _buildAskAiButton(BuildContext context, Color color) {
    final name = _data!['name'] as String? ?? planetName(widget.planetId);

    return Padding(
      padding: const EdgeInsets.fromLTRB(S.lg, S.sm, S.lg, S.lg),
      child: SizedBox(
        width: double.infinity,
        height: 44,
        child: ElevatedButton.icon(
          onPressed: () {
            Navigator.of(context).pop();
            context.push(
                '/chat?prompt=${Uri.encodeComponent("Tell me about $name in my chart - its strength, dignity, and what it signifies for me")}');
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

  // -- Helpers --

  String _capitalize(String s) {
    if (s.isEmpty) return s;
    return s[0].toUpperCase() + s.substring(1);
  }
}

class _BasicRow {
  final String label;
  final String value;
  const _BasicRow(this.label, this.value);
}
