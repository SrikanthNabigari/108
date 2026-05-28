import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:one_zero_eight/core/theme/app_theme.dart';
import 'package:one_zero_eight/shared/widgets/glass_container.dart';
import 'package:one_zero_eight/shared/widgets/ambient_background.dart';
import 'package:one_zero_eight/data/services/api_service.dart';
import 'package:one_zero_eight/core/constants/api_constants.dart';
import 'package:one_zero_eight/features/timeline/widgets/alert_detail_panel.dart';
import 'package:one_zero_eight/features/timeline/widgets/dasha_detail_panel.dart';

class TimelineScreen extends ConsumerStatefulWidget {
  const TimelineScreen({super.key});

  @override
  ConsumerState<TimelineScreen> createState() => _TimelineScreenState();
}

class _TimelineScreenState extends ConsumerState<TimelineScreen> {
  Map<String, dynamic>? _dashaData;
  bool _loading = true;
  String? _error;

  final _scrollController = ScrollController();
  final _mdScrollCtrl = ScrollController();
  final _adScrollCtrl = ScrollController();
  final _pdScrollCtrl = ScrollController();
  final _sdScrollCtrl = ScrollController();
  double _scrollHintOpacity = 1.0;

  // Selection state — which MD/AD/PD the user has tapped
  String? _selectedMdLord;
  String? _selectedAdLord;
  String? _selectedPdLord;

  // Dynamic sub-period sequences (fetched on tap)
  List<dynamic>? _adSequence;
  List<dynamic>? _pdSequence;
  List<dynamic>? _sdSequence;
  bool _loadingAd = false;
  bool _loadingPd = false;
  bool _loadingSd = false;

  // Guide section collapsed by default
  bool _guideExpanded = false;

  @override
  void initState() {
    super.initState();
    _fetchDasha();
    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    final opacity = (1.0 - (_scrollController.offset / 80)).clamp(0.0, 1.0);
    if (opacity != _scrollHintOpacity) {
      setState(() => _scrollHintOpacity = opacity);
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _mdScrollCtrl.dispose();
    _adScrollCtrl.dispose();
    _pdScrollCtrl.dispose();
    _sdScrollCtrl.dispose();
    super.dispose();
  }

  /// Scroll all horizontal dasha rows to the current/active period.
  void _scrollAllToCurrent(Map<String, dynamic> data) {
    final current = data['current'] as Map<String, dynamic>? ?? {};
    final mdSeq = data['mahadasha_sequence'] as List? ?? [];
    final adSeq = data['antardasha_sequence'] as List? ?? [];
    final pdSeq = data['pratyantardasha_sequence'] as List? ?? [];
    final sdSeq = data['sookshma_sequence'] as List? ?? [];
    _scrollToCurrentPeriod(_mdScrollCtrl, mdSeq, current['mahadasha_lord'] as String? ?? '', 100, S.sm);
    _scrollToCurrentPeriod(_adScrollCtrl, adSeq, current['antardasha_lord'] as String? ?? '', 90, S.sm);
    _scrollToCurrentPeriod(_pdScrollCtrl, pdSeq, current['pratyantardasha_lord'] as String? ?? '', 76, S.xs);
    _scrollToCurrentPeriod(_sdScrollCtrl, sdSeq, current['sookshma_lord'] as String? ?? '', 76, S.xs);
  }

  /// Scroll a horizontal ListView to center the current period card.
  void _scrollToCurrentPeriod(
    ScrollController ctrl, List<dynamic> items, String currentLord,
    double cardWidth, double separatorWidth,
  ) {
    if (items.isEmpty || currentLord.isEmpty) return;
    final idx = items.indexWhere((p) {
      final lord = (p as Map<String, dynamic>)['lord'] as String? ?? '';
      return lord.toLowerCase() == currentLord.toLowerCase();
    });
    if (idx <= 0) return; // first item or not found — no scroll needed
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!ctrl.hasClients) return;
      final offset = idx * (cardWidth + separatorWidth);
      final viewport = ctrl.position.viewportDimension;
      final centered = offset - (viewport / 2) + (cardWidth / 2);
      final target = centered.clamp(0.0, ctrl.position.maxScrollExtent);
      ctrl.animateTo(target, duration: const Duration(milliseconds: 400), curve: Curves.easeOutCubic);
    });
  }

  Future<void> _fetchDasha() async {
    try {
      final data = await ApiService().get(
        ApiConstants.analysisDasha,
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (mounted) {
        setState(() { _dashaData = data; _loading = false; });
        _scrollAllToCurrent(data);
      }
    } catch (e) {
      if (mounted) setState(() { _error = '$e'; _loading = false; });
    }
  }

  /// Fetch AD sequence for a selected MD period.
  Future<void> _fetchAdForMd(String lord, String start, String end) async {
    if (_selectedMdLord == lord) return; // already selected
    setState(() {
      _selectedMdLord = lord;
      _selectedAdLord = null;
      _selectedPdLord = null;
      _pdSequence = null;
      _sdSequence = null;
      _loadingAd = true;
    });
    try {
      final data = await ApiService().get(
        ApiConstants.dashaSubPeriods(
          parentLord: lord, parentStart: start, parentEnd: end, level: 'ad',
        ),
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (mounted) {
        setState(() {
          _adSequence = (data['periods'] as List?) ?? [];
          _loadingAd = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() { _loadingAd = false; });
    }
  }

  /// Fetch PD sequence for a selected AD period.
  Future<void> _fetchPdForAd(String lord, String start, String end) async {
    if (_selectedAdLord == lord) return;
    setState(() {
      _selectedAdLord = lord;
      _selectedPdLord = null;
      _sdSequence = null;
      _loadingPd = true;
    });
    try {
      final data = await ApiService().get(
        ApiConstants.dashaSubPeriods(
          parentLord: lord, parentStart: start, parentEnd: end, level: 'pd',
          mdLord: _selectedMdLord,
        ),
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (mounted) {
        setState(() {
          _pdSequence = (data['periods'] as List?) ?? [];
          _loadingPd = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() { _loadingPd = false; });
    }
  }

  /// Fetch SD (Sookshma Dasha) sequence for a selected PD period.
  Future<void> _fetchSdForPd(String lord, String start, String end) async {
    if (_selectedPdLord == lord) return;
    setState(() {
      _selectedPdLord = lord;
      _loadingSd = true;
    });
    try {
      final data = await ApiService().get(
        ApiConstants.dashaSubPeriods(
          parentLord: lord, parentStart: start, parentEnd: end, level: 'sd',
          mdLord: _selectedMdLord,
        ),
        fromJson: (json) => json as Map<String, dynamic>,
      );
      if (mounted) {
        setState(() {
          _sdSequence = (data['periods'] as List?) ?? [];
          _loadingSd = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() { _loadingSd = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AmbientBackground(
        child: SafeArea(
          child: _loading
              ? const Center(
                  child: CircularProgressIndicator(
                      color: C.accent, strokeWidth: 2),
                )
              : _error != null
                  ? _buildError()
                  : Stack(
                      children: [
                        _buildTimeline(),
                        if (_scrollHintOpacity > 0)
                          Positioned(
                            bottom: 16,
                            left: 0,
                            right: 0,
                            child: IgnorePointer(
                              child: Opacity(
                                opacity: _scrollHintOpacity * 0.5,
                                child: TweenAnimationBuilder<double>(
                                  tween: Tween(begin: 0, end: 1),
                                  duration: const Duration(milliseconds: 1200),
                                  builder: (_, val, child) {
                                    // Ping-pong: 0→1→0→1 via sin
                                    final bounce = sin(val * pi) * 6;
                                    return Transform.translate(
                                      offset: Offset(0, bounce),
                                      child: child,
                                    );
                                  },
                                  onEnd: () {
                                    // Re-trigger to loop
                                    if (mounted) setState(() {});
                                  },
                                  child: const Icon(
                                    Icons.keyboard_double_arrow_down,
                                    color: C.textMuted,
                                    size: 24,
                                  ),
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
        ),
      ),
    );
  }

  Widget _buildError() {
    return Padding(
      padding: S.pagePadding,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('Could not load timeline', style: T.h3),
          const SizedBox(height: S.sm),
          Text(_error!, style: T.caption, textAlign: TextAlign.center),
          const SizedBox(height: S.xl),
          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton(
              onPressed: () => context.go('/home'),
              child: const Text('Go Home'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimeline() {
    final current =
        _dashaData?['current'] as Map<String, dynamic>? ?? _dashaData ?? {};
    final mdSequence = _dashaData?['mahadasha_sequence'] as List? ?? [];
    final initialAdSeq = _dashaData?['antardasha_sequence'] as List? ?? [];
    final initialPdSeq = _dashaData?['pratyantardasha_sequence'] as List? ?? [];
    final alerts = _dashaData?['alerts'] as List? ?? [];

    final currentMdLord = current['mahadasha_lord'] as String? ?? 'mercury';
    final currentAdLord = current['antardasha_lord'] as String? ?? '';
    final currentPdLord = current['pratyantardasha_lord'] as String? ?? '';
    final currentSdLord = current['sookshma_lord'] as String? ?? '';

    // Use selected or fallback to current
    final mdLord = _selectedMdLord ?? currentMdLord;
    final adLord = _selectedAdLord ?? currentAdLord;
    final pdLord = _selectedAdLord != null ? (_selectedAdLord == currentAdLord ? currentPdLord : '') : currentPdLord;
    final adSequence = _adSequence ?? initialAdSeq;
    final pdSequence = _pdSequence ?? initialPdSeq;
    final initialSdSeq = _dashaData?['sookshma_sequence'] as List? ?? [];
    final sdSequence = _sdSequence ?? initialSdSeq;
    final bool isSelectedMdCurrent = mdLord.toLowerCase() == currentMdLord.toLowerCase();
    final bool isSelectedAdCurrent = adLord.toLowerCase() == currentAdLord.toLowerCase();
    final remaining = current['remaining_years'];
    final mdStart = current['mahadasha_start'] as String? ?? '';
    final mdEnd = current['mahadasha_end'] as String? ?? '';

    // Dasha guide data (enriched from backend)
    final mdTheme = current['theme'] as String? ?? '';
    final focusAreas = (current['focus_areas'] as List?)?.cast<String>() ?? [];
    final practicalAdvice = (current['practical_advice'] as List?)?.cast<String>() ?? [];
    final challenges = current['challenges'] as String? ?? '';
    final opportunities = current['opportunities'] as String? ?? '';

    // MD progress
    double mdProgress = 0;
    if (mdStart.isNotEmpty && mdEnd.isNotEmpty) {
      mdProgress = _calcProgress(mdStart, mdEnd);
    }

    final remainStr =
        remaining != null ? '${(remaining as num).round()}y left' : '';

    return SingleChildScrollView(
      controller: _scrollController,
      padding: S.pagePadding,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: S.lg),

          // Header
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  GestureDetector(
                    onTap: () => context.canPop()
                        ? context.pop()
                        : context.go('/home'),
                    child: const Icon(Icons.arrow_back_ios,
                        color: C.textSecondary, size: 18),
                  ),
                  const SizedBox(width: S.sm),
                  Text('Your Life Timeline', style: T.h2),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                'Vimshottari Dasha \u2014 your cosmic chapters',
                style: T.bodySm.copyWith(color: C.textMuted),
              ),
            ],
          ),

          const SizedBox(height: S.xl),

          // ── Current Period Overview (compact) ──
          GlassContainer(
            padding:
                const EdgeInsets.symmetric(horizontal: S.lg, vertical: S.md),
            child: Row(
              children: [
                // Nested rings
                SizedBox(
                  width: 100,
                  height: 100,
                  child: CustomPaint(
                    painter: _NestedRingsPainter(
                      mdProgress: mdProgress,
                      adProgress: _calcProgressFromCurrent(current, 'antardasha'),
                      pdProgress: pdLord.isNotEmpty
                          ? _calcProgressFromCurrent(current, 'pratyantardasha')
                          : 0,
                      sdProgress: currentSdLord.isNotEmpty
                          ? _calcProgressFromCurrent(current, 'sookshma')
                          : 0,
                      mdColor: _planetColor(mdLord),
                      adColor: _planetColor(adLord),
                      pdColor: pdLord.isNotEmpty
                          ? _planetColor(pdLord)
                          : C.glassBorder,
                      sdColor: currentSdLord.isNotEmpty
                          ? _planetColor(currentSdLord)
                          : C.glassBorder,
                      hasPd: pdLord.isNotEmpty,
                      hasSd: currentSdLord.isNotEmpty,
                    ),
                  ),
                ),
                const SizedBox(width: S.lg),
                // Text info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _Badge(text: 'NOW'),
                      const SizedBox(height: S.sm),
                      Text(
                        '${_planetName(mdLord)} MD',
                        style: T.h3.copyWith(
                            color: _planetColor(mdLord), fontSize: 18),
                      ),
                      if (mdTheme.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          mdTheme,
                          style: T.caption.copyWith(
                              color: _planetColor(mdLord).withValues(alpha: 0.7),
                              fontSize: 10),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                      if (adLord.isNotEmpty) ...[
                        const SizedBox(height: 2),
                        Text(
                          '${_planetGlyph(adLord)} ${_planetName(adLord)} AD  ·  ${_durationStr(current, 'antardasha')}',
                          style: T.bodySm.copyWith(color: C.textSecondary),
                        ),
                      ],
                      if (pdLord.isNotEmpty) ...[
                        const SizedBox(height: 1),
                        Text(
                          '${_planetGlyph(pdLord)} ${_planetName(pdLord)} PD  ·  ${_durationStr(current, 'pratyantardasha')}',
                          style: T.caption,
                        ),
                      ],
                      if (currentSdLord.isNotEmpty) ...[
                        const SizedBox(height: 1),
                        Text(
                          '${_planetGlyph(currentSdLord)} ${_planetName(currentSdLord)} SD  ·  ${_sdRemainingStr(current)}',
                          style: T.caption.copyWith(fontSize: 10, color: C.textMuted),
                        ),
                      ],
                      const SizedBox(height: S.sm),
                      // Progress
                      Row(
                        children: [
                          Expanded(
                            child: ClipRRect(
                              borderRadius: R.smBr,
                              child: LinearProgressIndicator(
                                value: mdProgress,
                                minHeight: 3,
                                backgroundColor: C.glassBorder,
                                valueColor: AlwaysStoppedAnimation(
                                    _planetColor(mdLord)),
                              ),
                            ),
                          ),
                          const SizedBox(width: S.sm),
                          Text(remainStr,
                              style: T.caption.copyWith(
                                  color: C.accent, fontSize: 10)),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // ── Alerts (Sade Sati, etc.) ──
          if (alerts.isNotEmpty) ...[
            const SizedBox(height: S.md),
            for (final alert in alerts)
              _AlertCard(alert: alert as Map<String, dynamic>),
          ],

          // ── Collapsible Guide Section ──
          if (focusAreas.isNotEmpty || practicalAdvice.isNotEmpty) ...[
            const SizedBox(height: S.md),
            GestureDetector(
              onTap: () => setState(() => _guideExpanded = !_guideExpanded),
              behavior: HitTestBehavior.opaque,
              child: Row(
                children: [
                  Icon(Icons.auto_stories,
                      color: _planetColor(mdLord), size: 16),
                  const SizedBox(width: 6),
                  Text('Period Guide',
                      style: T.bodySm.copyWith(
                          color: C.textPrimary,
                          fontWeight: FontWeight.w600,
                          fontSize: 13)),
                  const SizedBox(width: 4),
                  Icon(
                    _guideExpanded ? Icons.expand_less : Icons.expand_more,
                    size: 18,
                    color: C.textMuted,
                  ),
                ],
              ),
            ),
            if (_guideExpanded) ...[
              const SizedBox(height: S.sm),
              // Focus area chips
              if (focusAreas.isNotEmpty) ...[
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: focusAreas.map((area) => Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: S.sm, vertical: 4),
                    decoration: BoxDecoration(
                      borderRadius: R.xlBr,
                      color: _planetColor(mdLord).withValues(alpha: 0.08),
                      border: Border.all(
                          color: _planetColor(mdLord).withValues(alpha: 0.2)),
                    ),
                    child: Text(
                      area,
                      style: T.caption.copyWith(
                          color: _planetColor(mdLord), fontSize: 10),
                    ),
                  )).toList(),
                ),
                const SizedBox(height: S.sm),
              ],
              // Key advice
              if (practicalAdvice.isNotEmpty)
                ...practicalAdvice.take(3).map((advice) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(top: 5),
                        child: Icon(Icons.circle, size: 4,
                            color: _planetColor(mdLord)),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          advice,
                          style: T.caption.copyWith(
                              color: C.textSecondary, height: 1.4),
                        ),
                      ),
                    ],
                  ),
                )),
              // Opportunities / Challenges
              if (opportunities.isNotEmpty || challenges.isNotEmpty) ...[
                const SizedBox(height: S.sm),
                if (opportunities.isNotEmpty)
                  _InlineHint(
                    icon: Icons.trending_up,
                    color: C.positive,
                    text: opportunities,
                  ),
                if (challenges.isNotEmpty)
                  _InlineHint(
                    icon: Icons.warning_amber_rounded,
                    color: C.warning,
                    text: challenges,
                  ),
              ],
            ],
          ],

          const SizedBox(height: S.xl),

          // ── Row 1: Mahadashas ──
          _SectionLabel(title: 'Mahadasha', subtitle: 'Life Chapters'),
          const SizedBox(height: S.sm),
          SizedBox(
            height: 132,
            child: mdSequence.isNotEmpty
                ? ListView.separated(
                    controller: _mdScrollCtrl,
                    scrollDirection: Axis.horizontal,
                    itemCount: mdSequence.length,
                    separatorBuilder: (_, __) =>
                        const SizedBox(width: S.sm),
                    itemBuilder: (_, i) {
                      final p = mdSequence[i] as Map<String, dynamic>;
                      final lord = p['lord'] as String? ?? 'sun';
                      final pStart = p['start'] as String? ?? '';
                      final pEnd = p['end'] as String? ?? '';
                      final isSelected = lord.toLowerCase() == mdLord.toLowerCase();
                      final isNow = lord.toLowerCase() == currentMdLord.toLowerCase();
                      // Is this card currently driving the AD row?
                      final isShowingAds = isNow
                          ? (_selectedMdLord == null || _selectedMdLord!.toLowerCase() == lord.toLowerCase())
                          : isSelected;
                      final nature = p['functional_nature'] as String?;
                      final houses = (p['houses_ruled'] as List?)
                          ?.map((h) => h as int).toList() ?? [];
                      return _PeriodCard(
                        lord: lord,
                        duration: _yearStr(p['years']),
                        startYear: _yearFromIso(pStart),
                        endYear: _yearFromIso(pEnd),
                        isCurrent: isNow,
                        isSelected: isSelected && !isNow,
                        size: _CardSize.large,
                        doshaMarkers: _getDoshaMarkersForLord(lord),
                        functionalNature: nature,
                        housesRuled: houses,
                        onTap: () {
                          if (isShowingAds) {
                            // Already showing this MD's ADs → open detail
                            DashaDetailPanel.show(context,
                              level: 'md', lord: lord, mdLord: lord,
                              startDate: pStart, endDate: pEnd, isCurrent: isNow);
                          } else if (isNow) {
                            // Current MD but user was browsing another → go back
                            setState(() {
                              _selectedMdLord = null;
                              _selectedAdLord = null;
                              _selectedPdLord = null;
                              _adSequence = null;
                              _pdSequence = null;
                              _sdSequence = null;
                            });
                            if (_dashaData != null) _scrollAllToCurrent(_dashaData!);
                          } else if (pStart.isNotEmpty && pEnd.isNotEmpty) {
                            _fetchAdForMd(lord, pStart, pEnd);
                          }
                        },
                      );
                    },
                  )
                : _buildFallbackMD(currentMdLord),
          ),

          const SizedBox(height: S.xl),

          // ── Row 2: Antardashas ──
          _SectionLabel(
            title: 'Antardasha',
            subtitle: 'in ${_planetName(mdLord)} MD${isSelectedMdCurrent ? '' : ' (tap)'}',
          ),
          const SizedBox(height: S.sm),
          if (_loadingAd)
            const SizedBox(
              height: 100,
              child: Center(child: CircularProgressIndicator(color: C.accent, strokeWidth: 2)),
            )
          else if (adSequence.isNotEmpty) ...[
            SizedBox(
              height: 100,
              child: ListView.separated(
                controller: _adScrollCtrl,
                scrollDirection: Axis.horizontal,
                itemCount: adSequence.length,
                separatorBuilder: (_, __) =>
                    const SizedBox(width: S.sm),
                itemBuilder: (_, i) {
                  final p = adSequence[i] as Map<String, dynamic>;
                  final lord = p['lord'] as String? ?? 'sun';
                  final pStart = p['start'] as String? ?? '';
                  final pEnd = p['end'] as String? ?? '';
                  final rel = p['relationship'] as String?;
                  final isNow = isSelectedMdCurrent && lord.toLowerCase() == currentAdLord.toLowerCase();
                  final isSelected = lord.toLowerCase() == adLord.toLowerCase() && !isNow;
                  // Is this card currently driving the PD row?
                  final isShowingPds = isNow
                      ? (_selectedAdLord == null || _selectedAdLord!.toLowerCase() == lord.toLowerCase())
                      : isSelected;
                  return _PeriodCard(
                    lord: lord,
                    duration: _monthStr(p['years'], pStart, pEnd),
                    startYear: _shortDate(pStart),
                    endYear: _shortDate(pEnd),
                    isCurrent: isNow,
                    isSelected: isSelected,
                    size: _CardSize.medium,
                    relationship: rel,
                    doshaMarkers: (p['dosha_markers'] as List?)
                        ?.cast<Map<String, dynamic>>() ?? _getDoshaMarkersForLord(lord),
                    onTap: () {
                      if (isShowingPds) {
                        // Already showing this AD's PDs → open detail
                        DashaDetailPanel.show(context,
                          level: 'ad', lord: lord, mdLord: mdLord, adLord: lord,
                          startDate: pStart, endDate: pEnd, isCurrent: isNow);
                      } else if (isNow) {
                        // Current AD but user was browsing another → go back
                        setState(() {
                          _selectedAdLord = null;
                          _selectedPdLord = null;
                          _pdSequence = null;
                          _sdSequence = null;
                        });
                        if (_dashaData != null) _scrollAllToCurrent(_dashaData!);
                      } else if (pStart.isNotEmpty && pEnd.isNotEmpty) {
                        _fetchPdForAd(lord, pStart, pEnd);
                      }
                    },
                  );
                },
              ),
            ),
          ],

          const SizedBox(height: S.xl),

          // ── Row 3: Pratyantardashas ──
          if (_loadingPd)
            const SizedBox(
              height: 86,
              child: Center(child: CircularProgressIndicator(color: C.accent, strokeWidth: 2)),
            )
          else if (pdSequence.isNotEmpty) ...[
            _SectionLabel(
              title: 'Pratyantardasha',
              subtitle: 'in ${_planetName(adLord)} AD${isSelectedAdCurrent ? '' : ' (tap)'}',
            ),
            const SizedBox(height: S.sm),
            SizedBox(
              height: 86,
              child: ListView.separated(
                controller: _pdScrollCtrl,
                scrollDirection: Axis.horizontal,
                itemCount: pdSequence.length,
                separatorBuilder: (_, __) =>
                    const SizedBox(width: S.xs),
                itemBuilder: (_, i) {
                  final p = pdSequence[i] as Map<String, dynamic>;
                  final lord = p['lord'] as String? ?? 'sun';
                  final pStart = p['start'] as String? ?? '';
                  final pEnd = p['end'] as String? ?? '';
                  final rel = p['relationship'] as String?;
                  final isNow = isSelectedMdCurrent && isSelectedAdCurrent
                      && lord.toLowerCase() == currentPdLord.toLowerCase();
                  final isSelected = lord.toLowerCase() == (_selectedPdLord ?? '').toLowerCase() && !isNow;
                  // Is this card currently driving the SD row?
                  final isShowingSds = isNow
                      ? (_selectedPdLord == null || _selectedPdLord!.toLowerCase() == lord.toLowerCase())
                      : isSelected;
                  return _PeriodCard(
                    lord: lord,
                    duration: _monthStr(p['years'], pStart, pEnd),
                    startYear: '',
                    endYear: '',
                    isCurrent: isNow,
                    isSelected: isSelected,
                    size: _CardSize.small,
                    relationship: rel,
                    doshaMarkers: (p['dosha_markers'] as List?)
                        ?.cast<Map<String, dynamic>>() ?? _getDoshaMarkersForLord(lord),
                    onTap: () {
                      if (isShowingSds) {
                        // Already showing this PD's SDs → open detail
                        DashaDetailPanel.show(context,
                          level: 'pd', lord: lord, mdLord: mdLord,
                          adLord: adLord, pdLord: lord,
                          startDate: pStart, endDate: pEnd, isCurrent: isNow);
                      } else if (isNow) {
                        // Current PD but user was browsing another → go back
                        setState(() {
                          _selectedPdLord = null;
                          _sdSequence = null;
                        });
                        if (_dashaData != null) _scrollAllToCurrent(_dashaData!);
                      } else if (pStart.isNotEmpty && pEnd.isNotEmpty) {
                        _fetchSdForPd(lord, pStart, pEnd);
                      }
                    },
                  );
                },
              ),
            ),
            const SizedBox(height: S.xl),
          ],

          // ── Row 4: Sookshma Dashas ──
          if (_loadingSd)
            const SizedBox(
              height: 86,
              child: Center(child: CircularProgressIndicator(color: C.accent, strokeWidth: 2)),
            )
          else if (sdSequence.isNotEmpty) ...[
            _SectionLabel(
              title: 'Sookshma Dasha',
              subtitle: 'in ${_planetName(_selectedPdLord ?? currentPdLord)} PD',
            ),
            const SizedBox(height: S.sm),
            SizedBox(
              height: 86,
              child: ListView.separated(
                controller: _sdScrollCtrl,
                scrollDirection: Axis.horizontal,
                itemCount: sdSequence.length,
                separatorBuilder: (_, __) =>
                    const SizedBox(width: S.xs),
                itemBuilder: (_, i) {
                  final p = sdSequence[i] as Map<String, dynamic>;
                  final lord = p['lord'] as String? ?? 'sun';
                  final pStart = p['start'] as String? ?? '';
                  final pEnd = p['end'] as String? ?? '';
                  final rel = p['relationship'] as String?;
                  final isNow = isSelectedMdCurrent && isSelectedAdCurrent
                      && (_selectedPdLord ?? currentPdLord).toLowerCase() == currentPdLord.toLowerCase()
                      && lord.toLowerCase() == currentSdLord.toLowerCase();
                  return _PeriodCard(
                    lord: lord,
                    duration: _dayStr(pStart, pEnd),
                    startYear: _dayMonth(pStart),
                    endYear: _dayMonth(pEnd),
                    isCurrent: isNow,
                    size: _CardSize.compact,
                    relationship: rel,
                    onTap: () => DashaDetailPanel.show(
                      context,
                      level: 'sd',
                      lord: lord,
                      mdLord: mdLord,
                      adLord: adLord,
                      pdLord: _selectedPdLord ?? currentPdLord,
                      startDate: pStart,
                      endDate: pEnd,
                      isCurrent: isNow,
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: S.xl),
          ],

          const SizedBox(height: S.xl),
        ],
      ),
    );
  }

  /// Remaining time string for current SD (from sookshma_start/end).
  String _sdRemainingStr(Map<String, dynamic> current) {
    final start = current['sookshma_start'] as String? ?? '';
    final end = current['sookshma_end'] as String? ?? '';
    if (start.isEmpty || end.isEmpty) return '';
    try {
      final e = DateTime.parse(end);
      final now = DateTime.now();
      final remaining = e.difference(now).inDays;
      if (remaining <= 0) return '<1d left';
      return '${remaining}d left';
    } catch (_) {
      return '';
    }
  }

  /// "15 Feb" style date for SD cards.
  String _dayMonth(String iso) {
    if (iso.isEmpty) return '';
    try {
      final dt = DateTime.parse(iso);
      const months = [
        '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];
      return '${dt.day} ${months[dt.month]}';
    } catch (_) {
      return '';
    }
  }

  /// Duration in days for SD cards.
  String _dayStr(String startIso, String endIso) {
    if (startIso.isEmpty || endIso.isEmpty) return '';
    try {
      final s = DateTime.parse(startIso);
      final e = DateTime.parse(endIso);
      final days = e.difference(s).inDays;
      if (days <= 0) return '<1d';
      return '${days}d';
    } catch (_) {
      return '';
    }
  }

  List<Map<String, dynamic>> _getDoshaMarkersForLord(String lord) {
    final markers = _dashaData?['dosha_markers'] as Map<String, dynamic>?;
    if (markers == null) return [];
    final list = markers[lord.toLowerCase()] as List?;
    return list?.cast<Map<String, dynamic>>() ?? [];
  }

  Widget _buildFallbackMD(String currentLord) {
    const sequence = [
      ('sun', 6), ('moon', 10), ('mars', 7), ('rahu', 18),
      ('jupiter', 16), ('saturn', 19), ('mercury', 17),
      ('ketu', 7), ('venus', 20),
    ];
    return ListView.separated(
      scrollDirection: Axis.horizontal,
      itemCount: sequence.length,
      separatorBuilder: (_, __) => const SizedBox(width: S.sm),
      itemBuilder: (_, i) {
        final (lord, years) = sequence[i];
        return _PeriodCard(
          lord: lord,
          duration: '$years yrs',
          startYear: '',
          endYear: '',
          isCurrent: lord == currentLord.toLowerCase(),
          size: _CardSize.large,
          onTap: () => DashaDetailPanel.show(
            context,
            level: 'md',
            lord: lord,
            mdLord: lord,
            startDate: '',
            endDate: '',
            isCurrent: lord == currentLord.toLowerCase(),
          ),
        );
      },
    );
  }

  // ── Helpers ──

  double _calcProgress(String startIso, String endIso) {
    if (startIso.isEmpty || endIso.isEmpty) return 0;
    try {
      final s = DateTime.parse(startIso);
      final e = DateTime.parse(endIso);
      final total = e.difference(s).inDays;
      final elapsed = DateTime.now().difference(s).inDays;
      return total > 0 ? (elapsed / total).clamp(0.0, 1.0) : 0;
    } catch (_) {
      return 0;
    }
  }

  double _calcProgressFromCurrent(Map<String, dynamic> current, String prefix) {
    final start = current['${prefix}_start'] as String? ?? '';
    final end = current['${prefix}_end'] as String? ?? '';
    return _calcProgress(start, end);
  }

  /// "17 years" or "11 months" or "14 days" from current map's start/end.
  String _durationStr(Map<String, dynamic> current, String prefix) {
    final start = current['${prefix}_start'] as String? ?? '';
    final end = current['${prefix}_end'] as String? ?? '';
    if (start.isEmpty || end.isEmpty) return '';
    return _durationFromIso(start, end);
  }

  String _durationFromIso(String startIso, String endIso) {
    try {
      final s = DateTime.parse(startIso);
      final e = DateTime.parse(endIso);
      final totalDays = e.difference(s).inDays;
      final totalMonths = (totalDays / 30.44).round();
      if (totalMonths >= 24) {
        return '${(totalDays / 365.25).round()} years';
      } else if (totalMonths > 0) {
        return '$totalMonths months';
      } else {
        return '$totalDays days';
      }
    } catch (_) {
      return '';
    }
  }

  String _yearStr(dynamic years) {
    if (years == null) return '';
    return '${(years as num).round()} yrs';
  }

  /// For AD/PD: show months, or days if very short.
  String _monthStr(dynamic years, dynamic start, dynamic end) {
    if (start != null && end != null) {
      final s = start.toString();
      final e = end.toString();
      if (s.isNotEmpty && e.isNotEmpty) {
        return _durationFromIso(s, e);
      }
    }
    if (years == null) return '';
    final y = (years as num).toDouble();
    if (y >= 2) return '${y.round()} yrs';
    final months = (y * 12).round();
    return months > 0 ? '$months mo' : '${(y * 365.25).round()} d';
  }

  /// "Jan 2024" from ISO string.
  String _shortDate(String iso) {
    if (iso.isEmpty) return '';
    try {
      final dt = DateTime.parse(iso);
      const months = [
        '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ];
      return '${months[dt.month]} ${dt.year}';
    } catch (_) {
      return _yearFromIso(iso);
    }
  }

  String _yearFromIso(String iso) {
    if (iso.isEmpty) return '';
    try {
      return DateTime.parse(iso).year.toString();
    } catch (_) {
      return iso.length >= 4 ? iso.substring(0, 4) : iso;
    }
  }
}

// ── Shared helpers ──

String _planetGlyph(String planet) {
  const glyphs = {
    'sun': '☉', 'moon': '☽', 'mars': '♂', 'mercury': '☿',
    'jupiter': '♃', 'venus': '♀', 'saturn': '♄',
    'rahu': '☊', 'ketu': '☋',
  };
  return glyphs[planet.toLowerCase()] ?? '?';
}

String _planetName(String planet) {
  if (planet.isEmpty) return '';
  return planet[0].toUpperCase() + planet.substring(1);
}

Color _planetColor(String planet) {
  const colors = {
    'sun': C.sun, 'moon': C.moon, 'mars': C.mars, 'mercury': C.mercury,
    'jupiter': C.jupiter, 'venus': C.venus, 'saturn': C.saturn,
    'rahu': C.rahu, 'ketu': C.ketu,
  };
  return colors[planet.toLowerCase()] ?? C.accent;
}

Color _natureColor(String nature) {
  switch (nature) {
    case 'yogakaraka':
    case 'benefic':
      return C.positive;
    case 'malefic':
    case 'maraka':
      return C.negative;
    default:
      return C.warning;
  }
}

String _doshaSymbol(String name) {
  final n = name.toLowerCase();
  if (n.contains('mangal')) return '\u25B2';       // Mars triangle
  if (n.contains('kaal sarp')) return '\u25C6';     // Serpent diamond
  if (n.contains('pitra')) return '\u2726';         // Ancestral star
  if (n.contains('grahan')) return '\u25D0';        // Eclipse half-circle
  if (n.contains('guru chandal')) return '\u2B21';  // Hexagon
  if (n.contains('angarak')) return '\u25B2';       // Mars-Rahu triangle
  if (n.contains('vish')) return '\u25C9';          // Saturn-Moon target
  if (n.contains('kemdrum')) return '\u25CB';       // Empty Moon circle
  return '\u2022';                                  // Default bullet
}

Color _doshaColor(String name) {
  final n = name.toLowerCase();
  if (n.contains('mangal') || n.contains('angarak')) return C.mars;
  if (n.contains('kaal sarp') || n.contains('sarpa')) return C.rahu;
  if (n.contains('pitra')) return C.sun;
  if (n.contains('grahan')) return C.textSecondary;
  if (n.contains('guru chandal')) return C.jupiter;
  if (n.contains('vish') || n.contains('shapit')) return C.saturn;
  if (n.contains('kemdrum')) return C.moon;
  return C.warning;
}

// ── Widgets ──

class _Badge extends StatelessWidget {
  final String text;
  const _Badge({required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: S.sm, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: R.xlBr,
        color: C.accentDim,
        border: Border.all(color: C.glassBorder),
      ),
      child: Text(
        text,
        style: T.label.copyWith(
            color: C.accent, letterSpacing: 1.0, fontSize: 9),
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String title;
  final String subtitle;
  const _SectionLabel({required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(title, style: T.h3.copyWith(fontSize: 16)),
        const SizedBox(width: S.sm),
        Text(subtitle, style: T.caption),
      ],
    );
  }
}

enum _CardSize { large, medium, small, compact }

class _PeriodCard extends StatelessWidget {
  final String lord;
  final String duration;
  final String startYear;
  final String endYear;
  final bool isCurrent;
  final bool isSelected;
  final _CardSize size;
  final VoidCallback? onTap;
  final String? relationship; // 'friend', 'enemy', 'neutral', 'self'
  final List<Map<String, dynamic>> doshaMarkers;
  final String? functionalNature; // yogakaraka, benefic, neutral, malefic, maraka
  final List<int> housesRuled;

  const _PeriodCard({
    required this.lord,
    required this.duration,
    required this.startYear,
    required this.endYear,
    required this.isCurrent,
    this.isSelected = false,
    required this.size,
    this.onTap,
    this.relationship,
    this.doshaMarkers = const [],
    this.functionalNature,
    this.housesRuled = const [],
  });

  @override
  Widget build(BuildContext context) {
    final color = _planetColor(lord);
    final dateRange = (startYear.isNotEmpty && endYear.isNotEmpty)
        ? '$startYear–$endYear'
        : '';

    final double width;
    final double glyphSize;
    final double nameSize;
    final double durSize;
    final double dateSize;

    switch (size) {
      case _CardSize.large:
        width = 100;
        glyphSize = 20;
        nameSize = 13;
        durSize = 11;
        dateSize = 10;
      case _CardSize.medium:
        width = 90;
        glyphSize = 17;
        nameSize = 12;
        durSize = 10;
        dateSize = 9;
      case _CardSize.small:
        width = 76;
        glyphSize = 15;
        nameSize = 11;
        durSize = 10;
        dateSize = 9;
      case _CardSize.compact:
        width = 76;
        glyphSize = 13;
        nameSize = 10;
        durSize = 9;
        dateSize = 8;
    }

    final bool highlighted = isCurrent || isSelected;
    // Relationship dot color
    Color? relColor;
    if (relationship == 'friend') {
      relColor = C.positive;
    } else if (relationship == 'enemy') {
      relColor = C.negative;
    } else if (relationship == 'neutral') {
      relColor = C.warning;
    }

    return GestureDetector(
      onTap: onTap,
      child: Stack(
        children: [
          Container(
            width: width,
            padding: const EdgeInsets.symmetric(vertical: S.sm, horizontal: S.xs),
            decoration: BoxDecoration(
              borderRadius: R.lgBr,
              color: highlighted
                  ? color.withValues(alpha: 0.18)
                  : color.withValues(alpha: 0.04),
              border: Border.all(
                color: highlighted
                    ? color.withValues(alpha: 0.6)
                    : color.withValues(alpha: 0.15),
                width: highlighted ? 1.5 : 0.5,
              ),
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  _planetGlyph(lord),
                  style: TextStyle(fontSize: glyphSize, color: color),
                ),
                const SizedBox(height: 3),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (functionalNature != null) ...[
                      Container(
                        width: 6,
                        height: 6,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: _natureColor(functionalNature!),
                        ),
                      ),
                      const SizedBox(width: 3),
                    ],
                    Text(
                      _planetName(lord),
                      style: T.bodySm.copyWith(
                        color: C.textPrimary,
                        fontWeight: FontWeight.w600,
                        fontSize: nameSize,
                      ),
                    ),
                  ],
                ),
                if (housesRuled.isNotEmpty) ...[
                  Text(
                    housesRuled.map((h) => '${h}L').join(', '),
                    style: T.caption.copyWith(
                      color: color.withValues(alpha: 0.7),
                      fontSize: 8,
                    ),
                  ),
                ] else ...[
                  const SizedBox(height: 1),
                ],
                Text(
                  duration,
                  style: T.caption.copyWith(color: color, fontSize: durSize),
                ),
                if (dateRange.isNotEmpty) ...[
                  const SizedBox(height: 1),
                  Text(dateRange,
                      style: T.caption.copyWith(fontSize: dateSize),
                      overflow: TextOverflow.ellipsis),
                ],
                if (isCurrent && size == _CardSize.large) ...[
                  const SizedBox(height: 3),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: S.sm, vertical: 2),
                    decoration: BoxDecoration(
                      borderRadius: R.xlBr,
                      color: color.withValues(alpha: 0.2),
                    ),
                    child: Text(
                      'NOW',
                      style: TextStyle(
                        fontSize: 8,
                        fontWeight: FontWeight.w700,
                        color: color,
                        letterSpacing: 0.8,
                      ),
                    ),
                  ),
                ],
                if (isSelected && !isCurrent) ...[
                  const SizedBox(height: 2),
                  Container(
                    width: 4,
                    height: 4,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: color,
                    ),
                  ),
                ],
              ],
            ),
          ),
          // Relationship dot — overlaid top-right, no layout impact
          if (relColor != null)
            Positioned(
              top: 4,
              right: 4,
              child: Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: relColor,
                ),
              ),
            ),
          // Dosha markers — bottom-left
          if (doshaMarkers.isNotEmpty)
            Positioned(
              bottom: 4,
              left: 4,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: doshaMarkers.take(3).map((m) => Padding(
                  padding: const EdgeInsets.only(right: 1),
                  child: Text(
                    _doshaSymbol(m['name'] as String? ?? ''),
                    style: TextStyle(
                      fontSize: 8,
                      color: _doshaColor(m['name'] as String? ?? ''),
                    ),
                  ),
                )).toList(),
              ),
            ),
        ],
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final Map<String, dynamic> alert;
  const _AlertCard({required this.alert});

  @override
  Widget build(BuildContext context) {
    final type = alert['type'] as String? ?? '';
    final phase = alert['phase'] as String? ?? '';
    final desc = alert['description'] as String? ?? '';
    final dhaiyaType = alert['dhaiya_type'] as String? ?? '';

    final bool isSadeSati = type == 'sade_sati';
    final bool isDhaiya = type == 'dhaiya';
    final color = (isSadeSati || isDhaiya) ? C.saturn : C.warning;
    final icon = (isSadeSati || isDhaiya) ? '\u2644' : '\u26A0';
    final String title;
    if (isSadeSati) {
      title = 'Sade Sati \u2014 ${phase[0].toUpperCase()}${phase.substring(1)} Phase';
    } else if (isDhaiya) {
      final dName = dhaiyaType == 'kantaka_shani' ? 'Kantaka Shani' : 'Ashtama Shani';
      title = 'Dhaiya \u2014 $dName';
    } else {
      title = desc;
    }

    return GestureDetector(
      onTap: () => AlertDetailPanel.show(context, alert: alert),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: S.md, vertical: S.sm),
        decoration: BoxDecoration(
          borderRadius: R.mdBr,
          color: color.withValues(alpha: 0.08),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Row(
          children: [
            Text(icon, style: TextStyle(fontSize: 18, color: color)),
            const SizedBox(width: S.sm),
            Expanded(
              child: Text(
                title,
                style: T.bodySm.copyWith(color: color, fontWeight: FontWeight.w600),
              ),
            ),
            Icon(Icons.chevron_right, color: color.withValues(alpha: 0.5), size: 18),
          ],
        ),
      ),
    );
  }
}

class _InlineHint extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String text;

  const _InlineHint({
    required this.icon,
    required this.color,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Icon(icon, size: 12, color: color),
          ),
          const SizedBox(width: 4),
          Expanded(
            child: Text(
              text,
              style: T.caption.copyWith(
                  color: color, fontSize: 10, height: 1.3),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}

/// Paints up to four nested concentric progress rings.
class _NestedRingsPainter extends CustomPainter {
  final double mdProgress;
  final double adProgress;
  final double pdProgress;
  final double sdProgress;
  final Color mdColor;
  final Color adColor;
  final Color pdColor;
  final Color sdColor;
  final bool hasPd;
  final bool hasSd;

  _NestedRingsPainter({
    required this.mdProgress,
    required this.adProgress,
    required this.pdProgress,
    this.sdProgress = 0,
    required this.mdColor,
    required this.adColor,
    required this.pdColor,
    this.sdColor = C.glassBorder,
    required this.hasPd,
    this.hasSd = false,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final maxR = size.width / 2 - 4;

    // Equal visual weight — evenly spaced, same stroke width
    const stroke = 4.5;
    const gap = 7.0;
    final rings = <(double, double, double, Color)>[
      (maxR, stroke, mdProgress, mdColor),
      (maxR - gap - stroke, stroke, adProgress, adColor),
      if (hasPd) (maxR - 2 * (gap + stroke), stroke, pdProgress, pdColor),
      if (hasSd) (maxR - 3 * (gap + stroke), stroke, sdProgress, sdColor),
    ];

    final bgPaint = Paint()
      ..style = PaintingStyle.stroke
      ..color = C.glassBorder;

    final arcPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    for (final (radius, stroke, progress, color) in rings) {
      bgPaint.strokeWidth = stroke;
      canvas.drawCircle(center, radius, bgPaint);

      arcPaint
        ..strokeWidth = stroke
        ..color = color;
      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        -pi / 2,
        2 * pi * progress,
        false,
        arcPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _NestedRingsPainter old) =>
      old.mdProgress != mdProgress ||
      old.adProgress != adProgress ||
      old.pdProgress != pdProgress ||
      old.sdProgress != sdProgress ||
      old.mdColor != mdColor ||
      old.adColor != adColor ||
      old.pdColor != pdColor ||
      old.sdColor != sdColor;
}
