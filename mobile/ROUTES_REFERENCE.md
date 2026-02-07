# Flutter App Routes Reference

## Complete Route Structure

All routes are defined in `lib/app.dart` using GoRouter.

### Authentication Routes

| Route | Screen | Description |
|-------|--------|-------------|
| `/phone-auth` | PhoneAuthScreen | Phone number entry + Send OTP |
| `/otp-verify` | OtpVerifyScreen | 6-digit OTP verification |

### Onboarding Routes

| Route | Screen | Description |
|-------|--------|-------------|
| `/profile` | ProfileScreen | Name + Gender (Step 1 of 2) |
| `/birth-details` | BirthDetailsScreen | Date + Time + Place (Step 2 of 2) |

### Main App Routes (Bottom Nav)

| Route | Index | Screen | Description |
|-------|-------|--------|-------------|
| `/home` | 0 | HomeScreen | Dashboard with score & quick cards |
| `/chart` | 1 | ChartScreen | Birth chart viewer with divisional charts |
| `/chat` | 2 | ChatScreen | AI assistant chat |
| `/calendar` | 3 | CalendarScreen | Event calendar + muhurta tracking |
| `/settings` | 4 | SettingsScreen | Profile, subscription, credits |

### Secondary Routes (Navigation from Main Tabs)

| Route | Accessed From | Screen | Description |
|-------|---------------|--------|-------------|
| `/timeline` | Home quick card | TimelineScreen | Life chapters (Mahadasha periods) |
| `/reports` | Chat action card | ReportsStoreScreen | Browse & purchase reports |
| `/muhurta` | Calendar FAB or Chat | MuhurtaScreen | Find auspicious times |
| `/remedies` | Remedies quick card | RemediesScreen | Active remedies & gem recommendations |

### Paywall Routes

| Route | Accessed From | Screen | Description |
|-------|---------------|--------|-------------|
| `/paywall` | Locked features | PaywallScreen | Subscription tier comparison |
| `/credit-store` | Settings or Chat | CreditStoreScreen | Buy report credits |

## Navigation Flow Diagrams

### First-Time User Flow
```
PhoneAuthScreen
    ↓ (Send OTP)
OtpVerifyScreen
    ↓ (Verify OTP)
ProfileScreen (Step 1/2)
    ↓ (Continue)
BirthDetailsScreen (Step 2/2)
    ↓ (Calculate Chart)
HomeScreen (Main App)
```

### Main App Navigation
```
Bottom Nav Bar (5 tabs):
┌─ Home (0)
├─ Chart (1)
├─ Chat (2) [Elevated, Center]
├─ Calendar (3)
└─ Settings (4)

Quick Navigation:
Home         ─→ Timeline, Reports, Muhurta
Chart        ─→ (Tap planet) → Planet Detail Sheet
Chat         ─→ (Action card) → Report/Muhurta/Remedies
Calendar     ─→ Muhurta
Settings     ─→ Paywall, Credit Store

Any Screen   ─→ Paywall (locked feature)
Any Screen   ─→ Credit Store (from locked feature)
```

## Route Parameters

### OTP Verify Screen
```dart
context.push('/otp-verify', extra: phoneNumber);
// phoneNumber is passed as String
```

### Other Screens
Most screens don't require parameters; they load data from Riverpod providers based on authenticated user.

## Navigation Patterns

### Push vs Go
- Use `context.go()` for tab navigation (replaces entire stack)
- Use `context.push()` for modal/detail screens (adds to stack)

### Examples

```dart
// Go to home (replace stack)
context.go('/home');

// Push to timeline (add to stack, allows back)
context.push('/timeline');

// Push with parameter
context.push('/otp-verify', extra: '+1234567890');

// Pop current screen
context.pop();

// Named route (implicit in GoRouter)
GoRouter.of(context).pushNamed('home');
```

## Accessible Routes from Each Screen

### HomeScreen (/home)
- Tab: /chart, /chat, /calendar, /settings (bottom nav)
- Quick card: /timeline, /reports, /muhurta, /remedies
- Locked feature: /paywall

### ChartScreen (/chart)
- Tab: /home, /chat, /calendar, /settings (bottom nav)
- Planet tap: Planet detail sheet (bottom modal)
- Locked feature: /paywall

### ChatScreen (/chat)
- Tab: /home, /chart, /calendar, /settings (bottom nav)
- Action card: /reports, /muhurta, /remedies, /paywall
- Rate limit dialog: /paywall, /credit-store

### CalendarScreen (/calendar)
- Tab: /home, /chart, /chat, /settings (bottom nav)
- Event tap: Event detail sheet
- FAB (Add event): Add event bottom sheet
- Event creation: /muhurta for auspicious time check

### SettingsScreen (/settings)
- Tab: /home, /chart, /chat, /calendar (bottom nav)
- Profile tap: Edit profile sheet
- Subscription: /paywall
- Credits: /credit-store
- Sign out: /phone-auth

### TimelineScreen (/timeline)
- Back: Previous screen
- No bottom nav (accessed from home)

### ReportsStoreScreen (/reports)
- Back: Previous screen
- Report tap: Purchase dialog or /credit-store if insufficient credits

### MuhurtaScreen (/muhurta)
- Back: Previous screen
- No bottom nav

### RemediesScreen (/remedies)
- Back: Previous screen
- No bottom nav

### PaywallScreen (/paywall)
- Back: Previous screen
- Subscribe: RevenueCat flow
- Restore: RevenueCat flow

### CreditStoreScreen (/credit-store)
- Back: Previous screen
- Pack tap: RevenueCat flow

## Deep Linking

All routes support deep linking. Example deep links:
```
myapp://home
myapp://chart
myapp://chat
myapp://otp-verify?phone=%2B1234567890
myapp://paywall
myapp://timeline
```

## Route Guards (TODO)

Should implement:
- **Auth guard**: Redirect to /phone-auth if not authenticated
- **Onboarding guard**: Redirect to /profile if onboarding incomplete
- **Tier guard**: Check entitlements before allowing access to /reports, /paywall features

Example implementation:
```dart
GoRoute(
  path: '/chart',
  redirect: (BuildContext context, GoRouterState state) async {
    // Check auth
    final auth = ref.read(authProvider);
    if (!auth.isAuthenticated) return '/phone-auth';

    // Check onboarding
    final user = ref.read(userProvider);
    if (!user.onboardingComplete) return '/profile';

    return null; // Allow navigation
  },
  builder: (context, state) => const ChartScreen(),
),
```

## Modal & Sheet Navigation

Bottom sheets are shown modally without route changes:
```dart
// Planet detail sheet
showModalBottomSheet(
  context: context,
  builder: (_) => PlanetDetailSheet(...),
);

// Event detail sheet
showModalBottomSheet(
  context: context,
  builder: (_) => EventDetailSheet(...),
);
```

## Error & Not Found Handling

Add error route in GoRouter:
```dart
errorBuilder: (context, state) => Scaffold(
  body: Center(
    child: Text('Page not found: ${state.location}'),
  ),
),
```

## Testing Routes

Test navigation:
```dart
testWidgets('Navigate to chart', (WidgetTester tester) async {
  await tester.pumpWidget(const App());

  // Tap chart in bottom nav
  await tester.tap(find.byIcon(Icons.auto_awesome_rounded));
  await tester.pumpAndSettle();

  // Verify chart screen
  expect(find.byType(ChartScreen), findsOneWidget);
});
```

## Route Summary Statistics

- **Total Routes**: 18
- **Main Tab Routes**: 5
- **Auth Routes**: 2
- **Onboarding Routes**: 2
- **Secondary Routes**: 4
- **Paywall Routes**: 2
- **Deep Linking**: Supported

## Initialization Route

Initial route (when app starts):
```dart
initialLocation: '/phone-auth',
```

Should change to `/home` after auth implementation and guards.
