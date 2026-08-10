"""Small ownership gate for the v2.2.5 native farm and friend execution path.

The legacy hook still owns GUI, configuration, targeted share, counters, and
runtime infrastructure.  This module only decides whether a legacy business
wrapper may be installed around a callable that already belongs to the native
v2.2.5 engine.
"""

import os


NATIVE_V225_OWNER = "native-v225"
LEGACY_OWNER = "legacy"
OWNER_ENVIRONMENT_KEY = "QQFARM_EXECUTION_OWNER"


# These are the native v2.2.5 business entry points that must have one owner.
# Names are deliberately simple because hook.py receives both ``name`` and
# ``Class.name`` labels depending on where a callable was discovered.
NATIVE_V225_CALLABLE_NAMES = frozenset({
    "run_cycle",
    "_handle_home_auto_sell_fruit",
    "_run_warehouse_sell_button_sequence",
    "handle_home_maintenance",
    "handle_home_pre_planting_maintenance",
    "handle_home_harvest",
    "handle_home_planting",
    "process_self_farm",
    "_run_friend_daily_troublemaker",
    "process_friend_farm",
    "handle_friend_farm_actions",
    "_record_friend_help_action",
    "check_friend_help_request_entry",
    "check_friend_icon",
    "_drag_seed_over_lands",
    "_plant_seed_over_lands",
    "_run_auto_fertilize_after_planting",
    "_run_backpack_seed_priority_planting",
    "_run_planting_flow",
    "_find_quad_empty_land_groups",
    "_try_plant_quad_act_seeds",
    "get_current_player_level",
    "_detect_seed_quantity_badges_by_ocr",
    "_detect_seed_count_ocr",
    "_detect_empty_lands",
    "_check_empty_land_label_with_retry",
    "_infer_land_center_from_shovel",
    "_detect_no_seed_hint_by_ocr",
    "_is_backpack_seed_blacklisted_by_template",
    "_execute_planting_by_mode",
    "_buy_seed_for_crop",
    "_match_template_center",
    "_detect_fertilizer_template",
    "check_go_home_icon",
    "_has_go_home_icon",
    "go_home",
    "return_home",
    "_return_home",
    "check_friend_farm_bottom_help_all_entry",
    "check_friend_farm_bottom_steal_entry",
})


_LEGACY_OWNER_VALUES = frozenset({"legacy", "legacy-hook", "legacy_hook"})


def execution_owner(environ=None):
    """Return the requested business-execution owner.

    Native v2.2.5 is the default.  Setting ``QQFARM_EXECUTION_OWNER=legacy``
    is the explicit rollback path while a production observation is underway.
    """
    values = os.environ if environ is None else environ
    try:
        raw = str(values.get(OWNER_ENVIRONMENT_KEY, "") or "").strip().lower()
    except BaseException:
        raw = ""
    if raw in _LEGACY_OWNER_VALUES:
        return LEGACY_OWNER
    return NATIVE_V225_OWNER


def callable_name(label):
    """Normalize either ``name`` or ``Class.name`` to a callable name."""
    try:
        value = str(label or "").strip()
    except BaseException:
        value = ""
    if "." in value:
        value = value.rsplit(".", 1)[-1]
    return value


def native_v225_owns_callable(label, environ=None):
    """Whether the default native engine owns this business callable."""
    return (
        execution_owner(environ=environ) == NATIVE_V225_OWNER
        and callable_name(label) in NATIVE_V225_CALLABLE_NAMES
    )


def legacy_wrapper_allowed(label, environ=None):
    """Return whether the legacy hook may install a business wrapper."""
    return not native_v225_owns_callable(label, environ=environ)
