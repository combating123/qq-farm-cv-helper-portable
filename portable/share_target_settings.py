# Editable exact-recipient settings for daily sharing.
import configparser
import os
import pathlib
import tempfile

_SAFE_SHARE_VALUES = {
    "share_target_type": "contact",
    "share_target_match_mode": "search",
    "share_search_enabled": "True",
    "share_send_requires_target_match": "True",
    "share_cancel_if_target_missing": "True",
    "share_allow_group": "False",
    "share_dry_run": "False",
    "share_send_unverified_search_result": "False",
}


def default_config_path():
    base = os.environ.get("LOCALAPPDATA", "")
    return pathlib.Path(base) / "qq-farm-bot-rev" / "config-multi.ini"


def normalize_share_target(value):
    return " ".join(str(value or "").strip().split())


def _read_config(path):
    cfg = configparser.ConfigParser(interpolation=None)
    target = pathlib.Path(path)
    if target.exists():
        cfg.read(target, encoding="utf-8-sig")
    return cfg


def _active_section(cfg):
    active_id = cfg.get("instances", "active_id", fallback="").strip()
    candidate = "instance.%s.bot" % active_id if active_id else ""
    if candidate and cfg.has_section(candidate):
        return candidate
    if candidate and any(section.startswith("instance.") and section.endswith(".bot") for section in cfg.sections()):
        return candidate
    return "bot"


def _status(target):
    if target:
        return "\u5f53\u524d\u5206\u4eab\u76ee\u6807\uff1a" + target
    return "\u5f53\u524d\u5206\u4eab\u76ee\u6807\uff1a\u672a\u8bbe\u7f6e\uff08\u81ea\u52a8\u5206\u4eab\u4fdd\u6301\u5173\u95ed\uff09"


def load_share_target(path=None):
    target_path = pathlib.Path(path or default_config_path())
    cfg = _read_config(target_path)
    section = _active_section(cfg)
    target = normalize_share_target(cfg.get(section, "share_target_name", fallback=""))
    return {
        "path": str(target_path),
        "section": section,
        "target": target,
        "allow_group": cfg.getboolean(section, "share_allow_group", fallback=False),
        "status_text": _status(target),
    }


def _update_ini_section(path, section, updates):
    target = pathlib.Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    had_bom = False
    newline = "\n"
    if target.exists():
        raw = target.read_bytes()
        had_bom = raw.startswith(b"\xef\xbb\xbf")
        text = raw.decode("utf-8-sig", "replace")
        if "\r\n" in text:
            newline = "\r\n"
    else:
        text = ""
    lines = text.splitlines()
    lower_updates = {str(k).strip().lower(): str(v) for k, v in updates.items()}
    found_section = False
    in_section = False
    seen = set()
    output = []

    def append_missing():
        for key, value in lower_updates.items():
            if key not in seen:
                output.append("%s = %s" % (key, value))
                seen.add(key)

    for line in lines:
        stripped = line.strip()
        is_header = stripped.startswith("[") and "]" in stripped
        if is_header:
            if in_section:
                append_missing()
                in_section = False
            header = stripped[1:stripped.find("]")].strip()
            if header.lower() == section.lower():
                found_section = True
                in_section = True
        if in_section and not is_header and "=" in line and not stripped.startswith(("#", ";")):
            key = line.split("=", 1)[0].strip().lower()
            if key in lower_updates:
                indent = line[:len(line) - len(line.lstrip())]
                output.append("%s%s = %s" % (indent, key, lower_updates[key]))
                seen.add(key)
                continue
        output.append(line)
    if in_section:
        append_missing()
    if not found_section:
        if output and output[-1].strip():
            output.append("")
        output.append("[%s]" % section)
        for key, value in lower_updates.items():
            output.append("%s = %s" % (key, value))
    rendered = newline.join(output).rstrip() + newline
    encoded = rendered.encode("utf-8")
    if had_bom:
        encoded = b"\xef\xbb\xbf" + encoded
    fd, temp_name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def save_share_target(path=None, target=None, allow_group=False):
    # Also supports save_share_target(path, target) and save_share_target(target=...).
    if target is None and path is not None and not isinstance(path, (pathlib.Path, os.PathLike)):
        target, path = path, None
    target_path = pathlib.Path(path or default_config_path())
    value = normalize_share_target(target)
    if not value:
        return clear_share_target(target_path)
    cfg = _read_config(target_path)
    section = _active_section(cfg)
    updates = dict(_SAFE_SHARE_VALUES)
    updates["share_target_name"] = value
    # The public editor is deliberately limited to a verified direct contact.
    # Keep the legacy argument for call compatibility, but never widen it to a
    # group destination from this settings path.
    updates["share_allow_group"] = "False"
    _update_ini_section(target_path, section, updates)
    return {
        "path": str(target_path),
        "section": section,
        "target": value,
        "allow_group": False,
        "status_text": _status(value),
    }


def clear_share_target(path=None):
    target_path = pathlib.Path(path or default_config_path())
    cfg = _read_config(target_path)
    section = _active_section(cfg)
    updates = dict(_SAFE_SHARE_VALUES)
    updates.update({
        "share_target_name": "",
        "share_search_enabled": "False",
        "enable_daily_share": "False",
    })
    _update_ini_section(target_path, section, updates)
    return {
        "path": str(target_path),
        "section": section,
        "target": "",
        "allow_group": False,
        "status_text": _status(""),
    }
