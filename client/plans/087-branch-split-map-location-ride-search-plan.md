# Branch Split & PR Merge Plan (087)

## Summary

Split uncommitted ride-search / location-service work from branch `Web` into **3 sequential PRs** against `master`. **Graphify was refreshed first** (`.graphifyignore` expanded, then `graphify update .`).

## Changed files inventory

### Track A — Tooling (1 file)

| File | Purpose |
|------|---------|
| `.graphifyignore` | Exclude screenshots, client `.agents`, payment gateway WIP, caches from graph noise |

### Track B — Location service / place search (8 files)

| File | Purpose |
|------|---------|
| `services/location/location/maps/query_detection.py` | **New** — coordinate-shaped query detection |
| `services/location/location/application/use_cases.py` | Local-first search, Mapbox rich fallback, reverse-on-coords |
| `services/location/location/domain/interfaces.py` | `search_places_rich` + `proximity`, repo protocols |
| `services/location/location/infrastructure/mapbox_client.py` | `search_places_rich`, proximity param, 422 logging |
| `services/location/location/infrastructure/place_repository.py` | `save_place`, `nearest_place` |
| `services/location/location/infrastructure/dependencies.py` | Reverse geocode + place repo wiring |
| `tests/location/test_place_search.py` | Updated fakes + coordinate search test |
| `tests/location/test_query_detection.py` | **New** — query detection unit tests |

### Track C — Client ride search UX (085 + 086 + loading fix) (11 files)

| File | Feature |
|------|---------|
| `client/lib/common/widgets/maps/map_models.dart` | **085** — `flyToCoordinate` on `SMapController` |
| `client/lib/common/widgets/maps/map_view.dart` | **085** — attach fly-to callback |
| `client/lib/features/location/screens/ride_search/widgets/booking_map_controls.dart` | **085** — back left, pin + my-location column |
| `client/lib/features/location/screens/ride_search/ride_search_screen.dart` | **085** — full-screen map controls stack |
| `client/lib/features/location/controllers/ride_search_controller.dart` | **085+086** — GPS fly-to, `goToMyLocation`, `displayLabel`, search guards, proximity |
| `client/lib/features/location/domain/location_models.dart` | **086** — `displayLabel`, coordinate parsing |
| `client/lib/features/location/screens/ride_search/widgets/booking_sheet.dart` | **086** — `displayLabel` in inputs; **fix** — `Obx` on search results |
| `client/lib/features/location/screens/ride_search/widgets/booking_search_results.dart` | **086** — `displayLabel` in list rows |
| `client/test/location/location_models_test.dart` | **086** — display label tests |
| `client/plans/085-map-camera-and-controls-fix-plan.md` | **New** — spec 085 plan |
| `client/plans/086-place-search-and-pin-address-labels-plan.md` | **New** — spec 086 plan |
| `client/context/feature-specs/085-map-camera-and-controls-fix.md` | **New** |
| `client/context/feature-specs/086-place-search-and-pin-address-labels.md` | **New** |

### Excluded from all PRs (noise / unrelated)

- `.agents/`, `.antigravitycli/`, `graphify-out/`
- `client/assets/images/screenshots/`
- `services/payment/payment/gateway/` (unrelated WIP)

### Why 3 branches (not 4)

`ride_search_controller.dart` combines **085** (map camera / GPS) and **086** (labels / search). Splitting it across two client PRs would require artificial partial commits and broken intermediate builds. **One client PR** keeps the app shippable after merge.

Backend (Track B) merges **before** client (Track C) so `/places/search` and `/reverse` behavior matches the Flutter integration.

## Graphify (done before branching)

1. Expanded `.graphifyignore` (screenshots, `client/.agents/`, payment gateway WIP).
2. Ran `graphify update .` — graph rebuilt (~11.8k nodes). `graphify-out/` stays gitignored.

## Branch sequence

| Order | Branch name | Tracks | Depends on |
|-------|-------------|--------|------------|
| 1 | `chore/graphify-ignore` | A | — |
| 2 | `location/place-search-mapbox-labels` | B | PR 1 (optional) |
| 3 | `client/ride-search-map-and-place-labels` | C | PR 2 |

## Per-branch workflow

For each branch:

1. `git checkout master && git pull origin master`
2. `git checkout -b <branch-name>`
3. Restore only that branch’s files from the safety stash (see execution commands below)
4. `git add` → commit (HEREDOC message) → `git push -u origin HEAD`
5. `gh pr create --base master` → `gh pr merge --squash`
6. `git checkout master && git pull origin master`

## Verification per PR

| PR | Checks |
|----|--------|
| 1 | None required (ignore file only) |
| 2 | `uv run pytest tests/location/test_place_search.py tests/location/test_query_detection.py -q` |
| 3 | `cd client && flutter test test/location/location_models_test.dart` |

## Safety

Before branching: `git stash push -u -m "087-split-safarpay-ride-search"` on `Web` preserves the full dirty tree.

If any PR fails merge or CI: **stop** and fix before continuing.

## Related plans

- [085-map-camera-and-controls-fix-plan.md](./085-map-camera-and-controls-fix-plan.md)
- [086-place-search-and-pin-address-labels-plan.md](./086-place-search-and-pin-address-labels-plan.md)
