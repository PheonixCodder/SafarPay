# Client Screen Structure Normalization Prompt

Normalize the SafarPay Flutter client structure so every feature screen follows the same predictable folder pattern.

The target convention is:

```text
screens/<screen_name>/
  <screen_name>.dart
  widgets/
  screens/        # only when this screen owns subscreens
```

Rules:

- A screen folder has one main screen file.
- A Dart file should expose one primary widget class.
- Screen-local helper widgets belong under that screen's `widgets/` folder.
- Subscreens belong under that screen's `screens/` folder.
- Widgets reused across multiple screens or features belong under `client/lib/common/widgets`.
- Reusable helper functions belong under `client/lib/utils`.
- Feature data, content, and DTO/model files must not sit beside screen files; move them to `data/`, `content/`, or `models/` as appropriate.
- Preserve behavior, routes, visual output, backend contracts, and existing public screen class names.

Apply the cleanup across `client/lib/features`, with particular attention to driver registration, location screens, home widgets, personalization subpages, and trips widgets. Update imports, context docs, and plans after moving files. Verify with `flutter analyze --no-pub` and `flutter test`.
