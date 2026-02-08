import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:one_zero_eight/core/theme/app_theme.dart';

typedef OnPlaceSelected = Function(String place, double lat, double lon);

// Google Places API key (same as swara-chitta)
const _kGoogleApiKey = 'AIzaSyCw2GH0lcyNJDwDIe6hkUIE3eg1nfkV7Ww';
const _kBaseUrl = 'https://maps.googleapis.com/maps/api/place';

class PlaceSearchField extends StatefulWidget {
  final OnPlaceSelected onPlaceSelected;
  const PlaceSearchField({super.key, required this.onPlaceSelected});

  @override
  State<PlaceSearchField> createState() => _PlaceSearchFieldState();
}

class _PlaceSearchFieldState extends State<PlaceSearchField> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  final _fieldKey = GlobalKey();
  final List<_Prediction> _results = [];
  bool _loading = false;
  bool _selecting = false;
  Timer? _debounce;
  OverlayEntry? _overlay;

  @override
  void initState() {
    super.initState();
    _focusNode.addListener(() {
      if (!_focusNode.hasFocus) {
        Future.delayed(const Duration(milliseconds: 300), () {
          if (!_focusNode.hasFocus && !_selecting) _removeOverlay();
        });
      }
    });
  }

  @override
  void dispose() {
    _removeOverlay();
    _debounce?.cancel();
    _focusNode.dispose();
    _controller.dispose();
    super.dispose();
  }

  void _onChanged(String value) {
    _debounce?.cancel();
    if (value.length < 2) {
      _removeOverlay();
      _results.clear();
      return;
    }
    _debounce = Timer(const Duration(milliseconds: 350), () {
      _autocomplete(value);
    });
  }

  // Step 1: Google Places Autocomplete
  Future<void> _autocomplete(String query) async {
    if (!mounted) return;
    setState(() => _loading = true);

    try {
      final uri = Uri.parse(
        '$_kBaseUrl/autocomplete/json'
        '?input=${Uri.encodeComponent(query)}'
        '&key=$_kGoogleApiKey',
      );
      final response = await http.get(uri);

      if (!mounted) return;

      if (kDebugMode) {
        final body = jsonDecode(response.body);
        debugPrint(
            '[PlaceSearch] "$query" → ${body['status']}, '
            '${(body['predictions'] as List?)?.length ?? 0} results');
      }

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final predictions = data['predictions'] as List? ?? [];

        _results
          ..clear()
          ..addAll(predictions.map((p) {
            final structured =
                p['structured_formatting'] as Map<String, dynamic>?;
            return _Prediction(
              placeId: p['place_id'] as String,
              description: p['description'] as String,
              mainText: structured?['main_text'] as String? ?? '',
              secondaryText: structured?['secondary_text'] as String? ?? '',
            );
          }));

        if (_results.isNotEmpty) {
          _showOverlay();
        } else {
          _removeOverlay();
        }
      }
    } catch (e) {
      if (kDebugMode) debugPrint('[PlaceSearch] ERROR: $e');
    }
    if (mounted) setState(() => _loading = false);
  }

  // Step 2: Get lat/lon from place_id
  Future<void> _getDetails(_Prediction prediction) async {
    _removeOverlay();
    _selecting = false;
    _controller.text = prediction.mainText.isNotEmpty
        ? prediction.mainText
        : prediction.description;
    _focusNode.unfocus();

    setState(() => _loading = true);

    try {
      final uri = Uri.parse(
        '$_kBaseUrl/details/json'
        '?place_id=${Uri.encodeComponent(prediction.placeId)}'
        '&fields=formatted_address,geometry,utc_offset'
        '&key=$_kGoogleApiKey',
      );
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['status'] == 'OK') {
          final result = data['result'] as Map<String, dynamic>;
          final geometry = result['geometry'] as Map<String, dynamic>;
          final location = geometry['location'] as Map<String, dynamic>;
          final lat = (location['lat'] as num).toDouble();
          final lon = (location['lng'] as num).toDouble();
          final address = result['formatted_address'] as String? ??
              prediction.description;

          // Show short form in text field
          final short = prediction.mainText.isNotEmpty
              ? '${prediction.mainText}, ${prediction.secondaryText}'
              : address;
          _controller.text = short;

          widget.onPlaceSelected(short, lat, lon);
        } else {
          if (kDebugMode) {
            debugPrint('[PlaceSearch] Details error: ${data['status']}');
          }
        }
      }
    } catch (e) {
      if (kDebugMode) debugPrint('[PlaceSearch] Details ERROR: $e');
    }
    if (mounted) setState(() => _loading = false);
  }

  void _showOverlay() {
    _removeOverlay();

    final box = _fieldKey.currentContext?.findRenderObject() as RenderBox?;
    if (box == null) return;
    final size = box.size;
    final offset = box.localToGlobal(Offset.zero);

    _overlay = OverlayEntry(
      builder: (_) => Positioned(
        left: offset.dx - S.lg,
        top: offset.dy + size.height + 2,
        width: size.width + S.lg * 2,
        child: Material(
          color: Colors.transparent,
          child: Container(
            constraints: const BoxConstraints(maxHeight: 300),
            decoration: BoxDecoration(
              color: const Color(0xFF111118),
              borderRadius: R.lgBr,
              border: Border.all(
                  color: C.accent.withValues(alpha: 0.3), width: 1),
              boxShadow: [
                BoxShadow(
                  color: C.accent.withValues(alpha: 0.08),
                  blurRadius: 20,
                  offset: const Offset(0, 8),
                ),
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.6),
                  blurRadius: 16,
                  offset: const Offset(0, 6),
                ),
              ],
            ),
            child: ClipRRect(
              borderRadius: R.lgBr,
              child: ListView.separated(
                padding: EdgeInsets.zero,
                shrinkWrap: true,
                itemCount: _results.length,
                separatorBuilder: (_, __) =>
                    const Divider(height: 1, color: C.divider),
                itemBuilder: (_, i) {
                  final p = _results[i];
                  return GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTapDown: (_) {
                      _selecting = true;
                      _getDetails(p);
                    },
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: S.lg,
                        vertical: S.md,
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.location_on_outlined,
                            color: C.accent.withValues(alpha: 0.6),
                            size: 16,
                          ),
                          const SizedBox(width: S.sm),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  p.mainText.isNotEmpty
                                      ? p.mainText
                                      : p.description,
                                  style:
                                      T.bodySm.copyWith(color: C.textPrimary),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                if (p.secondaryText.isNotEmpty)
                                  Text(
                                    p.secondaryText,
                                    style: T.caption,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );

    Overlay.of(context).insert(_overlay!);
  }

  void _removeOverlay() {
    _overlay?.remove();
    _overlay = null;
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      key: _fieldKey,
      children: [
        Expanded(
          child: TextField(
            controller: _controller,
            focusNode: _focusNode,
            style: T.body,
            decoration: InputDecoration(
              hintText: 'Search city, town or village...',
              hintStyle: T.body.copyWith(color: C.textMuted),
              border: InputBorder.none,
              contentPadding: const EdgeInsets.symmetric(vertical: S.md),
            ),
            onChanged: _onChanged,
          ),
        ),
        if (_loading)
          const SizedBox(
            width: 16,
            height: 16,
            child:
                CircularProgressIndicator(strokeWidth: 2, color: C.textMuted),
          )
        else
          const Icon(Icons.search, color: C.textMuted, size: 20),
      ],
    );
  }
}

class _Prediction {
  final String placeId;
  final String description;
  final String mainText;
  final String secondaryText;
  _Prediction({
    required this.placeId,
    required this.description,
    required this.mainText,
    required this.secondaryText,
  });
}
