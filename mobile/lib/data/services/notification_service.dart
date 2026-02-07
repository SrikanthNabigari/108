import 'dart:ui' show Color;
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

/// Firebase Cloud Messaging setup and handling
class NotificationService {
  static final NotificationService _instance = NotificationService._internal();

  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  factory NotificationService() {
    return _instance;
  }

  NotificationService._internal();

  /// Initialize Firebase and FCM
  Future<void> initialize() async {
    try {
      // Request permissions
      await requestPermission();

      // Initialize local notifications
      const initSettingsAndroid = AndroidInitializationSettings('@mipmap/ic_launcher');
      const initSettingsIos = DarwinInitializationSettings(
        requestBadgePermission: false,
        requestSoundPermission: false,
        requestAlertPermission: false,
      );
      const initSettings = InitializationSettings(
        android: initSettingsAndroid,
        iOS: initSettingsIos,
      );
      await _localNotifications.initialize(initSettings);

      // Get FCM token
      final token = await getToken();
      print('FCM Token: $token');

      // Listen for token refresh
      _messaging.onTokenRefresh.listen((newToken) {
        print('New FCM Token: $newToken');
        // Update token on backend
        _updateTokenOnBackend(newToken);
      });

      // Handle foreground messages
      FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

      // Handle background messages
      FirebaseMessaging.onBackgroundMessage(_handleBackgroundMessage);

      // Handle notification open
      FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationOpen);
    } catch (e) {
      print('Error initializing notifications: $e');
    }
  }

  /// Request notification permissions
  Future<void> requestPermission() async {
    final settings = await _messaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );

    print('Permission status: ${settings.authorizationStatus}');
  }

  /// Get FCM token
  Future<String?> getToken() async {
    return await _messaging.getToken();
  }

  /// Show local notification
  Future<void> showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      '108-channel',
      '108 Notifications',
      importance: Importance.max,
      priority: Priority.high,
      enableLights: true,
      color: Color.fromARGB(255, 108, 99, 255),
    );
    const iosDetails = DarwinNotificationDetails();

    await _localNotifications.show(
      DateTime.now().millisecond,
      title,
      body,
      const NotificationDetails(android: androidDetails, iOS: iosDetails),
      payload: payload,
    );
  }

  /// Handle foreground message
  Future<void> _handleForegroundMessage(RemoteMessage message) async {
    print('Foreground message: ${message.notification?.title}');
    await showLocalNotification(
      title: message.notification?.title ?? '108',
      body: message.notification?.body ?? '',
      payload: message.data.toString(),
    );
  }

  /// Handle background message (static)
  static Future<void> _handleBackgroundMessage(RemoteMessage message) async {
    print('Background message: ${message.notification?.title}');
  }

  /// Handle notification open
  Future<void> _handleNotificationOpen(RemoteMessage message) async {
    print('Notification opened: ${message.notification?.title}');
    // Navigate to relevant screen based on message data
  }

  /// Update token on backend (stub)
  Future<void> _updateTokenOnBackend(String token) async {
    // Will be implemented to call API endpoint
    print('Updating token on backend: $token');
  }

  /// Unsubscribe from topic
  Future<void> unsubscribeFromTopic(String topic) async {
    await _messaging.unsubscribeFromTopic(topic);
  }

  /// Subscribe to topic
  Future<void> subscribeToTopic(String topic) async {
    await _messaging.subscribeToTopic(topic);
  }
}
