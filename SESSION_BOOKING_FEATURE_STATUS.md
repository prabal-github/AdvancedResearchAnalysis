# Analyst–Investor Session Booking Feature Status (Aug 18, 2025)

## 1. Overview
A new "Connect / Book a Session" capability lets investors book 1:1 sessions with analysts. It introduces analyst connect profiles, recurring availability + time‑off, on‑the‑fly slot generation, booking lifecycle (request → confirm → complete / decline / cancel), private notes, feedback with ratings, and basic capacity / conflict controls.

## 2. Data Model Additions
- **AnalystConnectProfile**: analyst_id, is_enabled, specialties (JSON array), headline, bio_short, hourly_rate, auto_confirm (bool), max_daily_sessions, timestamps.
- **AnalystAvailability**: recurring weekly availability (weekday, start_minute, end_minute, slot_minutes, is_active).
- **AnalystTimeOff**: per‑date exclusions.
- **SessionBooking**: investor_id, analyst_id, start_utc, end_utc, status (requested|confirmed|declined|cancelled|completed), video placeholders, price_quote, timestamps. (NEW unique constraint `uq_session_slot` on (analyst_id,start_utc,end_utc)).
- **SessionBookingNote**: booking-scoped notes (author_type, author_id, note); feedback stored as prefixed note `[FEEDBACK rating=<n>]`.

## 3. Core Backend Endpoints (Implemented)
| Purpose | Method & Path | Notes |
|---------|---------------|-------|
| List connectable analysts | GET /api/analysts/connectable | Filter optional `?specialty=`; includes aggregated rating.
| Fetch availability slots | GET /api/analysts/<id>/availability?from=&to= | Generates slots from recurring availability minus time-off & existing bookings.
| Book session | POST /api/analyst_sessions/book | Auto-confirm if analyst profile.auto_confirm else requested; capacity + overlap guard + unique constraint fallback.
| Investor sessions | GET /api/analyst_sessions/mine | Latest 200.
| Analyst incoming sessions | GET /api/analyst_sessions/incoming | Latest 200.
| Confirm | POST /api/analyst_sessions/<id>/confirm | Analyst only (requested → confirmed).
| Decline | POST /api/analyst_sessions/<id>/decline | Analyst can decline (requested/confirmed → declined).
| Cancel | POST /api/analyst_sessions/<id>/cancel | Investor or analyst (requested/confirmed → cancelled).
| Complete | POST /api/analyst_sessions/<id>/complete | Analyst after end time (confirmed → completed).
| Get booking | GET /api/analyst_sessions/<id> | Auth restricted to participants/admin.
| List notes | GET /api/analyst_sessions/<id>/notes | Participants only.
| Add note | POST /api/analyst_sessions/<id>/notes | Participants/admin.
| Feedback | POST /api/analyst_sessions/<id>/feedback | Investor after (confirmed|completed|declined|cancelled).
| Analyst self profile | GET/PATCH /api/analyst/connect_profile | Manage own connect profile.
| Admin manage profile | PATCH /api/admin/analysts/<id>/connect_profile | Back-office enabling & edits.

## 4. Frontend (Investor Dashboard)
- "Book a Session" card listing connectable analysts with specialties, auto/manual badge, average rating.
- Filter by specialty, auto-load on DOMContentLoaded.
- Booking modal with live availability for next 14 days, slot selection, duration choice.
- "My Sessions" panel (auto creates if missing) listing status & actions (Cancel / View / Feedback).
- Session modal: shows details + existing notes + add note.
- Feedback modal: rating 1–5 + optional text.
- Toast helper for notifications.

## 5. Frontend (Analyst Dashboard) – Implemented Items
- Profile edit card (headline, specialties, auto_confirm, capacity, etc.).
- Availability & time‑off management UI (CRUD) – previously added.
- Incoming sessions list with confirm / decline / complete actions.
- Notes & feedback visibility and note adding.
- Ratings displayed via aggregated feedback notes.

## 6. Business Logic & Validation
- Overlap prevention: query for any requested/confirmed overlapping booking pre-insert; plus DB unique constraint catch.
- Daily capacity: counts requested+confirmed per analyst per day vs max_daily_sessions.
- Auto vs manual confirmation path.
- Feedback gating (only after non-pending states).
- Ratings aggregation: parses `[FEEDBACK rating=R]` notes (capped to 1000 for performance) → average & count.

## 7. Recently Added (Latest Changes)
- Auto-init `loadConnectAnalysts()` on page load to replace perpetual "Loading..." placeholder.
- Error handling + retry link in analysts fetch.
- Deduplicated repeated JS blocks in investor template.
- Unique constraint `uq_session_slot` & race-safe commit logic returning 409 on double-book attempt.

## 8. Completed Feature Set Summary
- Analyst connect profile CRUD (self + admin).
- Listing connectable analysts with rating & auto/manual flag.
- Recurring availability + time-off exclusion (slot generation on demand).
- Investor booking flow (modal, duration, slot selection).
- Booking lifecycle endpoints (confirm/decline/cancel/complete) with state validation.
- Conflict + capacity enforcement + DB uniqueness.
- Private session notes (bidirectional) & feedback submission.
- Ratings aggregation surfaced to investors (No ratings yet if none).
- Frontend toasts, modals, dynamic session/analyst refresh.
- Basic video URL placeholders for future integration.

## 9. Pending / Backlog Items
Priority (High / Medium / Low):
- HIGH (DONE): Robust DB migration script for existing deployments (apply unique constraint safely). Added `migrations_session_feature.py` to create unique constraint & backfill feedback.
- HIGH (DONE): Transactional locking / `SELECT ... FOR UPDATE` implemented in booking endpoint (Postgres path) to close race window beyond unique constraint.
- HIGH (DONE): Dedicated `SessionFeedback` model (rating, comment, created_at) added; serializer now prefers new table with legacy fallback. Backfill script migrates prefixed notes.
- MED: Email / notification hooks (booking requested, confirmed, cancelled, declined, upcoming reminder, feedback received).
- MED: Investor & analyst calendar (group slots by day, collapse large lists, date picker range shortcuts).
- MED: Pagination & filtering (status filters, date range) for sessions endpoints beyond 200 cap.
- MED: Reschedule endpoint & UI (update slot with conflict checks, audit trail).
- MED: Distinguish cancel origin (investor vs analyst), add reason text.
- MED: Rate limiting / abuse protection on booking & feedback endpoints.
- LOW: Caching layer for analyst ratings to avoid repeated aggregation queries.
- LOW: Batch availability editor (copy week forward, templates).
- LOW: Export session history (CSV) for analyst/investor.
- LOW: Real-time updates via WebSocket (status changes, new bookings) instead of manual refresh.
- LOW: SLA / performance metrics dash (avg confirmation time, completion rates).

## 10. Potential Enhancements (Stretch)
- Payment integration (quote calculation, pre-authorization, invoice generation).
- Multi-participant group sessions (capacity and waitlist logic).
- Analytics: heatmap of utilized availability vs posted availability.
- AI scheduling assistant (suggest optimal times, auto-balance load).
- No-show tracking & automated penalties or rebooking flows.

## 11. Migration / Deployment Notes
- Applying unique constraint: For existing table `session_bookings`, ensure no duplicate (analyst_id,start_utc,end_utc) rows before migration; then add constraint (Alembic or raw ALTER).
- If production already has bookings, create an index first then constraint with validation disabled (Postgres: NOT VALID) → validate.
- Future dedicated Feedback model will require backfill by parsing existing prefixed notes.

## 12. Testing Recommendations
- Unit: slot generation (edge days, time-off intersection, daylight boundaries if any) & booking conflict logic.
- Integration: simulate concurrent booking attempts (one should 409 via unique constraint).
- Lifecycle transitions guard: invalid transitions return 400.
- Capacity breaches: daily count limit triggers 429.
- Feedback parsing: ensure malformed prefixes ignored gracefully.

## 13. Known Limitations
- Overlap check only considers current booking statuses; very rapid overlapping different-duration bookings could still race (unique constraint covers exact same start/end only).
- Ratings aggregation scales linearly with notes until capped; lacks weighting or recency decay.
- Feedback stored in notes makes future analytics slower until refactor.
- No timezone normalization UI (UTC assumed, displayed via browser local only).

## 14. Immediate Next Steps (Suggested Order)
1. Introduce Alembic migration to formalize unique constraint + future schema changes.
2. Create dedicated Feedback model & migrate historical feedback notes.
3. Add notification hooks (email/WebSocket) for booking state changes.
4. Implement reschedule flow & cancel reason metadata.
5. Calendar/day-group UI improvements + pagination.

---
**Status:** Core MVP complete & usable; moving into hardening + UX refinement phase.
