"""
Maps applied filter JSON (keys from filter_run1.csv / FiltersPage) to expectations
on semantic event-card labels: event_card|code=...|title=...|type=...|mode=...|status=...|role=...|schedule=YYYY-MM-DD|...

**“All” for a category** — use the corresponding ``*_all_checkBox`` key; validation skips that
dimension so any card value is accepted (e.g. ``filter_type_all_checkBox`` ⇒ course, meetup,
ticketed-event, …). See ``FILTER_*_ALL_KEY`` constants below.
"""

from __future__ import annotations
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)

# CSV / JSON option keys that mean "Any value allowed" for that category (matches UI All Checkbox).
FILTER_TYPE_ALL_KEY = "filter_type_all_checkBox"
FILTER_PRODUCT_TYPE_ALL_KEY = "filter_product_type_all_checkBox"
FILTER_MODE_ALL_KEY = "filter_mode_all_checkBox"
FILTER_SCHEDULE_ALL_KEY = "filter_schedule_all_checkBox"
FILTER_STATUS_ALL_KEY = "filter_status_all_checkBox"
FILTER_ROLE_ALL_KEY = "filter_role_all_checkBox"

# --- Single-select option key -> semantic value on card ---

OPTION_TO_EVENT_TYPE: Dict[str, str] = {
    "filter_type_course_checkBox": "course",
    "filter_type_meetup_checkBox": "meetup",
    "filter_type_ticketed_event_checkBox": "ticketed-event",
}

OPTION_TO_MODE: Dict[str, str] = {
    "filter_mode_in_person_checkBox": "in-person",
    "filter_mode_online_checkBox": "online",
}

OPTION_TO_STATUS: Dict[str, str] = {
    "filter_status_open_checkBox": "open",
    "filter_status_closed_checkBox": "closed",
    "filter_status_declined_checkBox": "declined",
    "filter_status_active_checkBox": "active",
    "filter_status_inactive_checkBox": "inactive",
    "filter_status_cancelled_checkBox": "cancelled",
    "filter_status_expense_submitted_checkBox": "expense-submitted",
    "filter_status_expense_declined_checkBox": "expense-declined",
    "filter_status_pending_activation_checkBox": "pending-activation",
}

OPTION_TO_ROLE: Dict[str, str] = {
    "filter_role_teacher_checkBox": "teacher",
    "filter_role_organizer_checkBox": "organizer",
}

# Substrings (lowercase) that must all appear in card title for that product filter
PRODUCT_OPTION_TITLE_MARKERS: Dict[str, Tuple[str, ...]] = {
    "filter_product_type_aol_part1_online": ("art", "living", "part", "1"),
    "filter_product_type_aol_part1_in_person": ("art", "living", "part", "1"),
    "filter_product_type_sahaj_samadhi_meditation_in_person": ("sahaj", "samadhi"),
    "filter_product_type_sahaj_samadhi_meditation_online": ("sahaj", "samadhi"),
    "filter_product_type_short_sky_meditation_meetup_online": ("sky", "meetup"),
    "filter_product_type_short_sky_meditation_meetup_in_person": ("sky", "meetup"),
    "filter_product_type_sleep_and_anxiety_protocol_in_person": ("sleep", "anxiety"),
    "filter_product_type_sahaj_samadhi_meditation_meetup_in_person": ("sahaj", "meetup"),
    "filter_product_type_long_sky_meetup_in_person": ("long", "sky"),
}

def _as_option_list(value: Union[str, List[str], None]) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    return [value]


def parse_csv_calendar_date(date_str: Optional[str]) -> Optional[date]:
    """Parse values like '1, Sunday, March 1, 2026' -> date."""
    if not date_str or not str(date_str).strip():
        return None
    s = str(date_str).strip()
    m = re.search(r"([A-Za-z]+)\s+(\d+),\s*(\d{4})\s*$", s)
    if not m:
        return None
    month, day, year = m.group(1), int(m.group(2)), int(m.group(3))
    return datetime.strptime(f"{month} {day} {year}", "%B %d %Y").date()


def parse_card_schedule_iso(schedule_val: Optional[str]) -> Optional[date]:
    if not schedule_val:
        return None
    try:
        return datetime.strptime(schedule_val.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def title_matches_product_option(title: Optional[str], option_key: str) -> bool:
    title_l = (title or "").lower()
    markers = PRODUCT_OPTION_TITLE_MARKERS.get(option_key)
    if not markers:
        return False
    return all(m in title_l for m in markers)


@dataclass
class SemanticCardConstraints:
    """AND across fields; within each set, card must match at least one allowed value (OR)."""

    allowed_types: Optional[Set[str]] = None
    allowed_modes: Optional[Set[str]] = None
    allowed_statuses: Optional[Set[str]] = None
    allowed_roles: Optional[Set[str]] = None
    product_option_keys: List[str] = field(default_factory=list)
    schedule_mode: Optional[str] = None  # upcoming | past | custom
    custom_start: Optional[date] = None
    custom_end: Optional[date] = None

    def has_product_or(self) -> bool:
        return len(self.product_option_keys) > 0


def constraints_from_applied_filters(
    filters: Dict[str, Any],
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
) -> SemanticCardConstraints:
    """
    Build expectations from the same dict shape passed to FiltersPage.apply_filter_combination.
    """
    c = SemanticCardConstraints()
    logger.debug("constraints_from_applied_filters filters=%s", filters)

    if "filter_type" in filters:
        keys = _as_option_list(filters["filter_type"])
        if FILTER_TYPE_ALL_KEY in keys:
            # Any event type: course, meetup, ticketed-event, …
            c.allowed_types = None
        else:
            types = {OPTION_TO_EVENT_TYPE[k] for k in keys if k in OPTION_TO_EVENT_TYPE}
            if types:
                c.allowed_types = types

    if "filter_mode" in filters:
        keys = _as_option_list(filters["filter_mode"])
        if FILTER_MODE_ALL_KEY in keys:
            c.allowed_modes = None
        else:
            modes = {OPTION_TO_MODE[k] for k in keys if k in OPTION_TO_MODE}
            if modes:
                c.allowed_modes = modes

    if "filter_status" in filters:
        keys = _as_option_list(filters["filter_status"])
        if FILTER_STATUS_ALL_KEY in keys:
            c.allowed_statuses = None
        else:
            statuses = {OPTION_TO_STATUS[k] for k in keys if k in OPTION_TO_STATUS}
            if statuses:
                c.allowed_statuses = statuses

    if "filter_role" in filters:
        keys = _as_option_list(filters["filter_role"])
        if FILTER_ROLE_ALL_KEY in keys:
            c.allowed_roles = None
        else:
            roles = {OPTION_TO_ROLE[k] for k in keys if k in OPTION_TO_ROLE}
            if roles:
                c.allowed_roles = roles

    if "filter_product_type" in filters:
        keys = _as_option_list(filters["filter_product_type"])
        if FILTER_PRODUCT_TYPE_ALL_KEY in keys:
            c.product_option_keys = []
        else:
            c.product_option_keys = list(keys)

    if "filter_schedule" in filters:
        sk = filters["filter_schedule"]
        if sk == FILTER_SCHEDULE_ALL_KEY:
            c.schedule_mode = None
            c.custom_start = None
            c.custom_end = None
        elif sk == "filter_schedule_upcoming_checkBox":
            c.schedule_mode = "upcoming"
        elif sk == "filter_schedule_past_checkBox":
            c.schedule_mode = "past"
        elif sk == "filter_schedule_custom_checkBox":
            c.schedule_mode = "custom"
            c.custom_start = parse_csv_calendar_date(start_date_str)
            c.custom_end = parse_csv_calendar_date(end_date_str)
        else:
            c.schedule_mode = None
    logger.debug("constraints_from_applied_filters result=%s", c)
    return c


def _schedule_ok(
    card: Dict[str, str],
    constraints: SemanticCardConstraints,
    reference_date: date,
) -> bool:
    if not constraints.schedule_mode:
        return True
    d = parse_card_schedule_iso(card.get("schedule"))
    if d is None:
        return False
    if constraints.schedule_mode == "upcoming":
        return d >= reference_date
    if constraints.schedule_mode == "past":
        return d < reference_date
    if constraints.schedule_mode == "custom":
        start, end = constraints.custom_start, constraints.custom_end
        if start is None or end is None:
            return True
        lo, hi = (start, end) if start <= end else (end, start)
        return lo <= d <= hi
    return True


def _normalize_semantic_status(actual: Optional[str], expected: str) -> bool:
    if not actual:
        return False
    a = actual.strip().lower().replace("_", "-")
    e = expected.strip().lower().replace("_", "-")
    if a == e:
        return True
    # tolerate alternate forms
    if e == "expense-submitted" and a in ("expensesubmitted", "expense_submitted"):
        return True
    if e == "expense-declined" and a in ("expensedeclined", "expense_declined"):
        return True
    if e == "pending-activation" and a in ("pendingactivation", "pending_activation"):
        return True
    if e == "ticketed-event" and a in ("ticketedevent", "ticketed_event", "ticketed"):
        return True
    return False


def _normalize_event_type(t: Optional[str]) -> str:
    if not t:
        return ""
    x = t.strip().lower().replace("_", "-")
    if x == "ticketed":
        return "ticketed-event"
    return x


def card_matches_constraints(
    card: Dict[str, str],
    constraints: SemanticCardConstraints,
    *,
    reference_date: Optional[date] = None,
    role_fallback_validator: Optional[Callable[[Dict[str, str], Set[str]], bool]] = None,
) -> Tuple[bool, str]:
    ref = reference_date or date.today()
    if constraints.allowed_types:
        an = _normalize_event_type(card.get("type"))
        allowed_norm = {_normalize_event_type(x) for x in constraints.allowed_types}
        if an not in allowed_norm:
            return False, f"type={card.get('type')!r} not in {constraints.allowed_types}"
    if constraints.allowed_modes and card.get("mode") not in constraints.allowed_modes:
        return False, f"mode={card.get('mode')!r} not in {constraints.allowed_modes}"
    if constraints.allowed_statuses:
        ok = any(
            _normalize_semantic_status(card.get("status"), s) for s in constraints.allowed_statuses
        )
        if not ok:
            return False, f"status={card.get('status')!r} not in {constraints.allowed_statuses}"
    if constraints.allowed_roles:
        role_val = (card.get("role") or "").strip().lower()
        if role_val not in constraints.allowed_roles:
            if role_fallback_validator and role_fallback_validator(card, constraints.allowed_roles):
                pass
            else:
                return False, f"role={card.get('role')!r} not in {constraints.allowed_roles}"
    if constraints.has_product_or():
        title = card.get("title", "")
        mode = card.get("mode", "")

        matched = False

        for key in constraints.product_option_keys:
            if title_matches_product_option(title, key):
                # Enforce delivery mode from option key (online vs in_person).
                if "online" in key and mode != "online":
                    continue
                if "in_person" in key and mode != "in-person":
                    continue

                matched = True
                break

        if not matched:
            return False, f"title={title!r}, mode={mode!r} mismatch"

    if not _schedule_ok(card, constraints, ref):
        return (
            False,
            f"schedule={card.get('schedule')!r} fails rule {constraints.schedule_mode!r} "
            f"(custom {constraints.custom_start}–{constraints.custom_end}, ref={ref})",
        )
    return True, ""


def validate_all_visible_cards(
    parsed_cards: List[Dict[str, str]],
    filters: Dict[str, Any],
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None,
    *,
    reference_date: Optional[date] = None,
    allow_empty: bool = False,
    role_fallback_validator: Optional[Callable[[Dict[str, str], Set[str]], bool]] = None,
    caller_logger: Optional[logging.Logger] = None,
) -> None:
    """
    Raises AssertionError with the first failing card detail.

    Pass ``caller_logger`` (e.g. the test's logger) so validation steps appear in the test log file.
    """
    log = caller_logger or logger
    log.info(
        "Semantic card validation | visible_cards=%d | filter_keys=%s | reference_date=%s",
        len(parsed_cards),
        list(filters.keys()) if filters else [],
        reference_date or date.today(),
    )
    log.debug("Semantic card validation | filters=%r | start=%r end=%r", filters, start_date_str, end_date_str)

    if not parsed_cards:
        if allow_empty:
            log.info("Semantic card validation skipped: no cards (allow_empty=True)")
            return
        log.error("Semantic card validation failed: no event_card| labels on screen")
        raise AssertionError(
            "No event cards with semantic label event_card| were found; "
            "cannot validate filters (set allow_empty=True to skip)."
        )

    constraints = constraints_from_applied_filters(filters, start_date_str, end_date_str)
    log.info(
        "Semantic constraints | schedule_mode=%r types=%s modes=%s statuses=%s roles=%s "
        "products=%s custom_range=%s..%s",
        constraints.schedule_mode,
        constraints.allowed_types,
        constraints.allowed_modes,
        constraints.allowed_statuses,
        constraints.allowed_roles,
        constraints.product_option_keys,
        constraints.custom_start,
        constraints.custom_end,
    )
    if role_fallback_validator is not None:
        log.info("Semantic card validation | role_fallback_validator=enabled")

    for i, card in enumerate(parsed_cards):
        ok, reason = card_matches_constraints(
            card,
            constraints,
            reference_date=reference_date,
            role_fallback_validator=role_fallback_validator,
        )
        if not ok:
            log.error(
                "Semantic card validation | card[%d] FAILED: %s | payload=%r",
                i,
                reason,
                card,
            )
            raise AssertionError(f"Card[{i}] failed filter validation: {reason}; card={card}")
        log.debug(
            "Semantic card validation | card[%d] OK code=%s type=%s",
            i,
            card.get("code"),
            card.get("type"),
        )

    log.info("Semantic card validation | all %d card(s) passed", len(parsed_cards))
