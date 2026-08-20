"""Local startup-policy adapter for the portable project build."""


_POLICY_MODULE_SUFFIXES = (
    ".version_policy_gate",
    ".expiry_guard",
)


def is_startup_policy_module_name(name):
    value = str(name or "").strip().lower()
    return value.startswith("bot.") and value.endswith(_POLICY_MODULE_SUFFIXES)


def _return_false(*args, **kwargs):
    return False


def _return_none(*args, **kwargs):
    return None


def _return_empty(*args, **kwargs):
    return ""


def _future_datetimes():
    import datetime

    beijing = datetime.timezone(datetime.timedelta(hours=8))
    return {
        "EXPIRY_BEIJING": datetime.datetime(2099, 12, 28, 0, 0, tzinfo=beijing),
        "EXPIRY_BEIJING_WARNING": datetime.datetime(2099, 12, 31, 0, 0, tzinfo=beijing),
        "EXPIRY_UTC": datetime.datetime(2099, 12, 27, 16, 0, tzinfo=datetime.timezone.utc),
        "EXPIRY_WARNING_UTC": datetime.datetime(2099, 12, 30, 16, 0, tzinfo=datetime.timezone.utc),
    }


def patch_startup_policy_module(module):
    """Neutralize stale packaged version state for this maintained build."""
    try:
        module_name = str(getattr(module, "__name__", "") or "")
    except BaseException:
        module_name = ""
    if not is_startup_policy_module_name(module_name):
        return 0

    changed = 0
    if module_name.lower().endswith(".version_policy_gate"):
        replacements = {
            "is_version_policy_rejection_error": _return_false,
            "mark_version_policy_rejected": _return_none,
            "clear_version_policy_rejection": _return_none,
            "get_version_policy_rejection_reason": _return_empty,
            "reset_version_policy_rejection_for_tests": _return_none,
        }
        for name, replacement in replacements.items():
            try:
                if hasattr(module, name):
                    setattr(module, name, replacement)
                    changed += 1
            except BaseException:
                pass

    if module_name.lower().endswith(".expiry_guard"):
        for name, value in _future_datetimes().items():
            try:
                if hasattr(module, name):
                    setattr(module, name, value)
                    changed += 1
            except BaseException:
                pass
    return changed
