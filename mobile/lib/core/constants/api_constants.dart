/// API configuration and endpoint constants
class ApiConstants {
  ApiConstants._();

  // Base configuration
  static const String baseUrl = 'http://localhost:8001';
  static const String apiVersion = '/api/v1';

  // Auth endpoints (Supabase handles directly)
  static const String authSignupPhone = '/auth/signup-phone';
  static const String authVerifyOtp = '/auth/verify-otp';
  static const String authLoginGoogle = '/auth/login-google';
  static const String authLoginApple = '/auth/login-apple';

  // User profile endpoints
  static const String userMe = '$apiVersion/me';
  static const String userBirthDetails = '$apiVersion/me/birth-details';

  // Config
  static const String config = '$apiVersion/config';

  // Chart endpoints
  static const String chartSummary = '$apiVersion/chart/summary';
  static const String chartFull = '$apiVersion/chart/full';
  static String chartDivisional(String d) => '$apiVersion/chart/divisional/$d';

  // Forecast endpoints
  static const String forecastDaily = '$apiVersion/forecast/daily';
  static const String forecastWeekly = '$apiVersion/forecast/weekly';
  static const String forecastMonthly = '$apiVersion/forecast/monthly';
  static const String forecastYearly = '$apiVersion/forecast/yearly';

  // Analysis endpoints
  static const String analysisYogas = '$apiVersion/analysis/yogas';
  static const String analysisDoshas = '$apiVersion/analysis/doshas';
  static const String analysisDasha = '$apiVersion/analysis/dasha';
  static const String analysisTransits = '$apiVersion/analysis/transits';
  static String transitPlanet(String planet) => '$apiVersion/analysis/transits/$planet';
  static const String transitSnapshot = '$apiVersion/analysis/transits/snapshot';
  static const String transitAspects = '$apiVersion/analysis/transits/aspects';
  static String transitTriggers({int days = 30}) => '$apiVersion/analysis/transits/triggers?days=$days';
  static const String analysisStrength = '$apiVersion/analysis/strength';
  static const String analysisAtmakaraka = '$apiVersion/analysis/atmakaraka';
  static const String analysisKp = '$apiVersion/analysis/kp';

  /// Dasha effects endpoint with MD/AD/PD query params
  static String dashaEffects({required String md, String? ad, String? pd}) {
    var url = '$apiVersion/analysis/dasha/effects?md=$md';
    if (ad != null) url += '&ad=$ad';
    if (pd != null) url += '&pd=$pd';
    return url;
  }

  /// Dasha sub-periods (AD for an MD, or PD for an AD)
  static String dashaSubPeriods({
    required String parentLord,
    required String parentStart,
    required String parentEnd,
    required String level,
    String? mdLord,
  }) {
    var url = '$apiVersion/analysis/dasha/sub-periods'
        '?parent_lord=$parentLord&parent_start=$parentStart'
        '&parent_end=$parentEnd&level=$level';
    if (mdLord != null) url += '&md_lord=$mdLord';
    return url;
  }

  // Chat
  static const String chat = '$apiVersion/chat';
  static const String chatHistory = '$apiVersion/chat/history';
  static const String chatRemaining = '$apiVersion/chat/remaining';

  // Compatibility
  static const String compatibilityQuick = '$apiVersion/compatibility/quick';
  static const String compatibilityFull = '$apiVersion/compatibility/full';

  // Muhurta
  static const String muhurtaCheck = '$apiVersion/muhurta/check';
  static const String muhurtaFind = '$apiVersion/muhurta/find';

  // Reports
  static const String reports = '$apiVersion/reports';
  static String reportDetail(String id) => '$apiVersion/reports/$id';
  static String reportPdf(String id) => '$apiVersion/reports/$id/pdf';

  // Events
  static const String events = '$apiVersion/events';
  static String eventDetail(String id) => '$apiVersion/events/$id';
  static const String eventsCorrelate = '$apiVersion/events/correlate';

  // Credits
  static const String creditsBalance = '$apiVersion/credits/balance';
  static const String creditsHistory = '$apiVersion/credits/history';

  // Remedies
  static const String remedies = '$apiVersion/remedies';
  static const String remediesGems = '$apiVersion/remedies/gems';

  // State Map
  static const String stateNow = '$apiVersion/state/now';
  static String stateDate(String date) => '$apiVersion/state/date/$date';
  static String stateRange({
    required String start,
    required String end,
    String resolution = 'daily',
  }) =>
      '$apiVersion/state/range?start=$start&end=$end&resolution=$resolution';

  // Webhooks
  static const String webhooksRevenuecat = '/webhooks/revenuecat';

  /// Default headers for API requests
  static Map<String, String> get defaultHeaders => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  /// Build authorization header with Bearer token
  static Map<String, String> authHeader(String token) => {
    ...defaultHeaders,
    'Authorization': 'Bearer $token',
  };
}
