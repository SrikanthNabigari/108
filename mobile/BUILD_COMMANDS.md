# Flutter Build & Code Generation Commands

## Initial Setup

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies
flutter pub get

# Upgrade packages if needed
flutter pub upgrade
```

## Code Generation

All Freezed models and Riverpod providers require code generation via `build_runner`.

### Generate all code (models + providers + router)

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

**What this generates:**
- `*.freezed.dart` files (Freezed immutable models)
- `*.g.dart` files (JSON serialization)
- `app_router.g.dart` (GoRouter code)
- Generated provider files with proper typing

### Watch mode (for development)

```bash
flutter pub run build_runner watch
```

This automatically regenerates when you modify:
- `@freezed` annotated classes
- `@riverpod` annotated providers
- Router definitions

## Run Application

### Development (with hot reload)

```bash
flutter run
```

### Release build

```bash
# iOS
flutter build ios

# Android (APK)
flutter build apk

# Android (App Bundle for Play Store)
flutter build appbundle
```

## Format & Lint

```bash
# Format all Dart files
dart format .

# Run linter
flutter analyze

# Fix linting issues automatically
dart fix --apply
```

## Testing

```bash
# Run all tests
flutter test

# Run specific test file
flutter test test/data/services/api_service_test.dart

# Run with coverage
flutter test --coverage
```

## Troubleshooting

### If code generation fails or is incomplete

```bash
# Clean generated files and rebuild
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### If you get "Missing generated code" errors

Make sure all files have the correct annotations:
- Models: `@freezed class ... with _$ClassName`
- Providers: `@riverpod` or `@riverpod FutureProvider<T> name(...)`

Example:
```dart
@freezed
class UserModel with _$UserModel {
  const factory UserModel({required String id}) = _UserModel;
  factory UserModel.fromJson(Map<String, dynamic> json) => _$UserModelFromJson(json);
}
```

### If Riverpod generator skips providers

Ensure proper imports and part directives:
```dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
part 'provider_name.g.dart';

@riverpod
Future<MyModel> myProvider(MyProviderRef ref) async {
  // implementation
}
```

## Important Notes

1. **Always run code generation after:**
   - Adding new `@freezed` models
   - Adding new `@riverpod` providers
   - Modifying router configuration
   - Pulling changes from git

2. **Generated files should NOT be edited manually**
   - All generated files have `.g.dart` or `.freezed.dart` suffixes
   - Edit the source file and regenerate

3. **Commit generated files to version control**
   - Include `*.freezed.dart`, `*.g.dart`, and `app_router.g.dart` in git
   - This ensures consistency across team members

4. **Build runner performance**
   - First build takes longer (30-60 seconds)
   - Subsequent builds are faster
   - Watch mode rebuilds only affected files

## Environment Setup

Ensure you have the correct SDK versions in `pubspec.yaml`:

```yaml
environment:
  sdk: ^3.5.0
  flutter: ">=3.24.0"
```

Update your local Flutter:
```bash
flutter upgrade
```

Check your Dart version:
```bash
dart --version
```
