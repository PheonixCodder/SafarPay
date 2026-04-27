# SafarPay ORM Infrastructure Audit Report

I have completed a thorough analysis of the ORM models in `auth`, `ride`, and `verification` services. Overall, the implementation follows a very high standard of design (DDD-ready, type-safe via SQLAlchemy 2.0 Mapped, and schema-isolated). However, there are a few critical areas for hardening and optimization.

## Summary of Findings

| Service | Status | Key Recommendation |
| :--- | :--- | :--- |
| **Auth** | ✅ Perfect | No changes needed. Correct mapping and schema isolation. |
| **Verification** | ⚠️ Good | Address "Today" stats anti-pattern in `DriverStats`. |
| **Ride** | 🚨 Critical | Fix missing Foreign Keys in Verification Codes and redundant relations. |

---

## 1. Auth Service (`auth.users`)
**Analysis**: The models are clean and follow best practices.
- **Strengths**: Proper unique constraints on `email` and `phone`. Correct use of `PgUUID` and `TimestampMixin`.
- **Issues**: None.

## 2. Verification Service (`verification`)
**Analysis**: Strong data integrity, but one architectural anti-pattern in stats.
- **`DriverStatsORM.online_minutes_today`**: 
  - **Issue**: Storing daily-resetting counters in a persistent ORM table is an anti-pattern. If the database is the source of truth, there's no automated mechanism shown for resetting this, leading to data drift.
  - **Recommendation**: Move "today" stats to Redis or implement a daily cleanup task.
- **`DocumentORM`**: Excellent use of polymorphic-style linking (`entity_id` + `entity_type`) with a composite index.

## 3. Ride Service (`service_request`)
**Analysis**: Highly detailed, but has several redundancy and integrity gaps.

### 🚨 Critical: Missing Foreign Keys
- **`ServiceVerificationCodeORM`**:
  - `verified_by_user_id` and `verified_by_driver_id` are defined as UUIDs but **lack `ForeignKey` constraints**.
  - **Risk**: Orphaned IDs or references to non-existent users/drivers.
  - **Fix**: Add `ForeignKey("auth.users.id")` and `ForeignKey("verification.drivers.id")`.

### ⚠️ Redundant Relations
- **`IntercityPassengerGroupORM`**:
  - Contains both `service_request_id` (linking to `service_requests`) and `intercity_service_request_id` (linking to `intercity_details`).
  - Since `intercity_details` uses `service_request_id` as its primary key, these are redundant.
  - **Fix**: Consolidate to a single `intercity_detail_id` (FK to `intercity_details`).

### ⚠️ Data Integrity & Normalization
- **`ServiceProofImageORM`**: 
  - Tracks `uploaded_by_user_id` and `uploaded_by_driver_id`.
  - **Risk**: Both could be NULL or both could be filled.
  - **Fix**: Add a `CheckConstraint` ensuring exactly one uploader type is provided.
- **`IntercityDetailORM.total_stops`**: 
  - **Risk**: May get out of sync with the actual row count in `service_stops`.
  - **Fix**: Rely on `count()` queries or update via triggers/application logic.

---

## 4. Enterprise Standards Compliance

| Standard | Status | Notes |
| :--- | :--- | :--- |
| **Schema Isolation** | ✅ Pass | All tables use explicit PostgreSQL schemas. |
| **Naming** | ✅ Pass | Consistent snake_case and pluralization. |
| **Primary Keys** | ✅ Pass | Uniform UUID v4 usage. |
| **Soft Deletes** | ❌ N/A | Using `is_active` flags where appropriate. |
| **Audit Logs** | ✅ Pass | `TimestampMixin` provides `created_at`/`updated_at`. |
| **Scalability** | ⚠️ Warning | Cross-schema Foreign Keys are used. While great for integrity in a single DB cluster, they create hard coupling that makes splitting into separate DBs harder in the future. |

## Proposed Action Plan

1. **Fix Ride Integrity**: Add missing Foreign Keys to `ServiceVerificationCodeORM`.
2. **Cleanup Redundancy**: Remove duplicate FKs in `IntercityPassengerGroupORM`.
3. **Add Constraints**: Implement uploader exclusivity checks in `ServiceProofImageORM`.
4. **Stats Optimization**: Refactor `DriverStatsORM` to handle temporal data more robustly.

**Verdict**: The models are 90% "Perfect". Implementing the suggested fixes will bring them to 100% enterprise-grade reliability.
