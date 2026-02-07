import 'package:flutter/material.dart';
import '../../../shared/widgets/glass_card.dart';

/// Google Places autocomplete search field for birth location.
typedef OnPlaceSelected = Function(String place, double lat, double lon);

class PlaceSearchField extends StatefulWidget {
  final OnPlaceSelected onPlaceSelected;

  const PlaceSearchField({
    Key? key,
    required this.onPlaceSelected,
  }) : super(key: key);

  @override
  State<PlaceSearchField> createState() => _PlaceSearchFieldState();
}

class _PlaceSearchFieldState extends State<PlaceSearchField> {
  final _controller = TextEditingController();
  final List<_PlacePrediction> _suggestions = [];
  bool _showSuggestions = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _onSearchChanged(String value) async {
    if (value.isEmpty) {
      setState(() {
        _suggestions.clear();
        _showSuggestions = false;
      });
      return;
    }

    // TODO: Call Google Places API
    // This is a mock implementation
    final mockSuggestions = [
      _PlacePrediction(
        name: 'New York, USA',
        lat: 40.7128,
        lon: -74.0060,
      ),
      _PlacePrediction(
        name: 'London, UK',
        lat: 51.5074,
        lon: -0.1278,
      ),
      _PlacePrediction(
        name: 'Mumbai, India',
        lat: 19.0760,
        lon: 72.8777,
      ),
    ];

    setState(() {
      _suggestions.clear();
      if (value.isNotEmpty) {
        _suggestions.addAll(
          mockSuggestions
              .where(
                (p) => p.name.toLowerCase().contains(value.toLowerCase()),
              )
              .toList(),
        );
        _showSuggestions = true;
      }
    });
  }

  void _selectPlace(_PlacePrediction place) {
    _controller.text = place.name;
    widget.onPlaceSelected(place.name, place.lat, place.lon);
    setState(() => _showSuggestions = false);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        GlassCard(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _controller,
                  style: const TextStyle(color: Colors.white),
                  decoration: const InputDecoration(
                    hintText: 'Search city...',
                    hintStyle: TextStyle(color: Colors.white38),
                    border: InputBorder.none,
                  ),
                  onChanged: _onSearchChanged,
                ),
              ),
              Icon(
                Icons.location_on_rounded,
                color: Colors.white54,
              ),
            ],
          ),
        ),
        if (_showSuggestions && _suggestions.isNotEmpty)
          Container(
            margin: const EdgeInsets.only(top: 8),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              color: const Color(0x1aFFFFFF),
              border: Border.all(
                color: Colors.white.withOpacity(0.2),
              ),
            ),
            child: Column(
              children: _suggestions.map((place) {
                return GestureDetector(
                  onTap: () => _selectPlace(place),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 12,
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.location_on_rounded,
                          color: Colors.white54,
                          size: 18,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            place.name,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 14,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
      ],
    );
  }
}

class _PlacePrediction {
  final String name;
  final double lat;
  final double lon;

  _PlacePrediction({
    required this.name,
    required this.lat,
    required this.lon,
  });
}
