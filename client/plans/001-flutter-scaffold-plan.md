# Flutter Scaffold Plan

## Summary

Create the base Flutter project, platform scaffolds, dependencies, assets, fonts, Firebase bootstrap, and app shell.

## Key Changes

- Add Flutter platform folders and project metadata.
- Configure `pubspec.yaml` dependencies, assets, and SF Pro fonts.
- Initialize Flutter bindings, GetStorage, and Firebase before running `App`.
- Use `GetMaterialApp` with SafarPay light theme.

## Test Plan

- `flutter pub get`.
- App launches without missing asset/font declarations.
- Platform scaffolds remain separated from generated build output.

## Status

- Implemented.
