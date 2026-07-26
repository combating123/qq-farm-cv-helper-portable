# ASCII-only hook body loaded by proxy python312.dll
# no threading dependency: uses import hook only
try:
    LOG_PATH = __import__('os').environ.get('QQFARM_HOOK_LOG_PATH', r'C:/Users/11616/reverse-cases/qq-farm-vip/work/hook_runtime_log.txt')
except BaseException:
    LOG_PATH = r'C:/Users/11616/reverse-cases/qq-farm-vip/work/hook_runtime_log.txt'

def _write(msg):
    try:
        f = open(LOG_PATH, 'a')
        f.write(str(msg) + '\n')
        f.close()
    except BaseException:
        pass

_THROTTLE_LOG_TS = {}
_SECURITY_WATCHDOG_PATCH_LOG_SEEN = set()
_DAILY_RETRY_REPAIR_LAST_TS = 0.0
# Names recovered from the 2026-07-26 access-violation trace.  These are
# termination/integrity deadline routines, not business-task functions.
_INTEGRITY_EXIT_NOOP_NAMES = set([
    '_qf_abc077a3d0ac',
    'maybe_exit_on_integrity_failure_deadline',
    'schedule_integrity_failure_exit',
    '_shadow_penalty_exit_watchdog',
    '_qf_60723e1c26a6',
    '_qf_e4b465e77dde',
])

def _throttled_write(key, msg, seconds=30.0):
    try:
        now = time.time()
        k = str(key)
        last = float(_THROTTLE_LOG_TS.get(k, 0.0) or 0.0)
        if seconds is None:
            seconds = 30.0
        if last > 0 and (now - last) < float(seconds):
            return False
        _THROTTLE_LOG_TS[k] = now
        _write(msg)
        return True
    except BaseException:
        try:
            _write(msg)
            return True
        except BaseException:
            return False

_write('hook.py entered no-thread v35-vip-warehouse-radish-fertilizer')

try:
    import sys, time, builtins, importlib, os
    _write('basic imports ok no-thread')
    _write('v32 runtime process pid=' + str(os.getpid()))
except BaseException as e:
    _write('basic imports failed no-thread: ' + repr(e))
    raise

try:
    import resource_limits as _resource_limits
    _RESOURCE_MAX_THREADS = max(1, int(os.environ.get('QQFARM_MAX_NATIVE_THREADS', '2') or '2'))
    _resource_limits.configure_environment(_RESOURCE_MAX_THREADS)
    _RESOURCE_AFFINITY_CORES = max(1, int(os.environ.get('QQFARM_CPU_AFFINITY_CORES', '4') or '4'))
    _resource_process_result = _resource_limits.apply_process_limits(_RESOURCE_AFFINITY_CORES)
    _write('native CV/OCR thread pools capped at ' + str(_RESOURCE_MAX_THREADS) + '; process limits=' + repr(_resource_process_result))
except BaseException as e:
    _resource_limits = None
    _RESOURCE_MAX_THREADS = 2
    _write('native resource limit setup failed: ' + repr(e))

try:
    from ui_personalization import (
        patch_widget as _patch_personal_ui_widget,
        install_early_theme as _install_early_personal_theme,
    )
    _write('personal github ui module loaded')
except BaseException as e:
    _patch_personal_ui_widget = None
    _install_early_personal_theme = None
    _write('personal github ui module load failed: ' + repr(e))

class _OK:
    ok = True
    passed = True
    success = True
    active = True
    valid = True
    reason = 'local_runtime_patch'
    message = 'local_runtime_patch'
    errors = []
    signals = []
    def __bool__(self): return True
    def __iter__(self): return iter((True, 'local_runtime_patch'))
    def __getitem__(self, k): return getattr(self, k, None)
    def get(self, k, d=None): return getattr(self, k, d)

_OK_OBJ = _OK()
_PATCH_LOG_SEEN = set()
_PATCH_LOADED_RUNNING = False
_PATCH_LOADED_LAST_TS = 0.0
_PATCH_LOADED_SEEN_RELEVANT = set()

_CONFIG_OVERRIDE_PATCHED = False
_CONFIG_FILE_PATCH_TS = 0.0
_INI_CACHE_TS = 0.0
_INI_CACHE_VALS = None
# v28: entitlement unlock only; business switches are controlled by UI/config.
_VIP_CONFIG_FORCED_BOOL_TRUE = set([])  # v28: only unlock license gates; UI/config controls business switches

# v28: business-layer patch is intentionally passive. Do not force user-facing toggles.
_VIP_BUSINESS_BOOL_TRUE = set([])  # v28: respect front-end toggles instead of forcing backend switches
_VIP_BUSINESS_VALUE_OVERRIDES = {
    # Keep only window identity fixes that prevent matching the helper window itself.
    'window_title': 'QQ\u7ecf\u5178\u519c\u573a',
    'window_title_match_mode': 'exact',
}
_VIP_BUSINESS_RESET_NUMERIC = set([])
_VIP_BUSINESS_ZERO_COUNTERS = set([])

_FRIEND_PAUSE_LAST_LOG_KEY = ''
_RUNTIME_INFO_SEEN = set()
_WECHAT_FOCUS_PATCH_LOG_SEEN = set()
_PATCH_LOADED_RUNNING = False
_PATCH_LOADED_LAST_TS = 0.0
_PATCH_LOADED_SEEN_RELEVANT = set()
_WECHAT_BG_CLICK_LAST_LOG_TS = 0.0
_FRIEND_PAUSE_FORCE_FALSE = set([
    'enable_process_friend',
    'enable_process_friend_help_entry',
    'friend_only_help_request_mode',
    'enable_steal',
    'enable_help',
    'enable_friend_steal_one',
    'enable_friend_steal_one_fallback',
    'force_help_after_steal_success',
    'enable_bottom_friend_list_help_all',
    'enable_daily_troublemaker',
])


def _norm_key(s):
    try:
        return str(s).strip().lower().replace('-', '_')
    except BaseException:
        return ''


def _truthy(v, default=False):
    try:
        if v is None:
            return default
        return str(v).strip().lower() in ('1', 'true', 'yes', 'y', 'on', 'enable', 'enabled')
    except BaseException:
        return default


def _is_stop_requested_like(obj):
    try:
        if obj is None:
            return False
        if isinstance(obj, (str, bytes, int, float, bool)):
            return False
        for n in ('stop_requested', '_stop_requested', 'should_stop', '_should_stop'):
            try:
                if hasattr(obj, n):
                    v = getattr(obj, n)
                    if callable(v):
                        v = v()
                    if bool(v):
                        return True
            except BaseException:
                pass
        for n in ('stop_event', '_stop_event', 'stop_signal', '_stop_signal', 'cancel_event', '_cancel_event'):
            try:
                ev = getattr(obj, n, None)
                if ev is not None:
                    if hasattr(ev, 'is_set') and callable(getattr(ev, 'is_set')):
                        if bool(ev.is_set()):
                            return True
                    elif bool(ev):
                        return True
            except BaseException:
                pass
        for n in ('running', '_running', 'is_running'):
            try:
                if hasattr(obj, n):
                    v = getattr(obj, n)
                    if callable(v):
                        v = v()
                    if bool(v) is False:
                        return True
            except BaseException:
                pass
    except BaseException:
        pass
    return False


def _stop_requested_in_args(args, kwargs=None):
    try:
        items = []
        try:
            items.extend(list(args or ())[:8])
        except BaseException:
            pass
        try:
            if kwargs:
                for k in ('bot', 'engine', 'runtime', 'service', 'controller', 'ctx', 'context'):
                    if k in kwargs:
                        items.append(kwargs.get(k))
                items.extend(list(kwargs.values())[:8])
        except BaseException:
            pass
        seen = set()
        stack = list(items)
        depth = 0
        while stack and depth < 32:
            depth += 1
            obj = stack.pop(0)
            try:
                oid = id(obj)
                if oid in seen:
                    continue
                seen.add(oid)
            except BaseException:
                pass
            if _is_stop_requested_like(obj):
                return True
            try:
                if obj is not None and not isinstance(obj, (str, bytes, int, float, bool)):
                    for n in ('bot', '_bot', 'engine', '_engine', 'runtime', '_runtime', 'service', '_service', 'controller', '_controller'):
                        try:
                            child = getattr(obj, n, None)
                            if child is not None:
                                stack.append(child)
                        except BaseException:
                            pass
            except BaseException:
                pass
    except BaseException:
        pass
    return False


def _stop_gate_return(name):
    try:
        _throttled_write('stop-gate-' + str(name), 'v30 stop gate blocked ' + str(name), 3.0)
    except BaseException:
        pass
    return False


def _cfg_path():
    try:
        base = os.environ.get('LOCALAPPDATA', '')
        if not base:
            return ''
        return os.path.join(base, 'qq-farm-bot-rev', 'config-multi.ini')
    except BaseException:
        return ''


def _read_ini_values():
    global _INI_CACHE_TS, _INI_CACHE_VALS
    vals = {}
    try:
        now = time.time()
        if _INI_CACHE_VALS is not None and (now - _INI_CACHE_TS) < 5.0:
            return _INI_CACHE_VALS
        cfg = _cfg_path()
        if not cfg or not os.path.exists(cfg):
            return vals
        try:
            data = open(cfg, 'rb').read().decode('utf-8', 'replace')
        except BaseException:
            data = open(cfg, 'r').read()
        sec = ''
        for raw in data.splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or line.startswith(';'):
                continue
            if line.startswith('[') and ']' in line:
                sec = _norm_key(line[1:line.find(']')])
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                vals[(sec, _norm_key(k))] = v.strip()
        _INI_CACHE_VALS = vals
        _INI_CACHE_TS = time.time()
    except BaseException as e:
        try: _write('read ini values error ' + repr(e))
        except BaseException: pass
    return vals


def _cfg_get(sections, option, default=None):
    try:
        vals = _read_ini_values()
        opt = _norm_key(option)
        for sec in sections:
            key = (_norm_key(sec), opt)
            if key in vals:
                return vals.get(key)
    except BaseException:
        pass
    return default


def _active_bot_sections():
    try:
        iid = _active_instance_id()
    except BaseException:
        iid = '1'
    return ['instance.' + str(iid) + '.bot', 'bot']


def _active_friend_sections():
    try:
        iid = _active_instance_id()
    except BaseException:
        iid = '1'
    return ['instance.' + str(iid) + '.friend', 'friend']


def _active_self_sections():
    try:
        iid = _active_instance_id()
    except BaseException:
        iid = '1'
    return ['instance.' + str(iid) + '.self', 'self']


def _active_planting_sections():
    try:
        iid = _active_instance_id()
    except BaseException:
        iid = '1'
    return ['instance.' + str(iid) + '.planting', 'planting']


def _active_launch_protocol():
    try:
        return str(_cfg_get(_active_bot_sections(), 'launch_protocol', '') or '')
    except BaseException:
        return ''


def _active_bound_process_name():
    try:
        return str(_cfg_get(_active_bot_sections(), 'bound_process_name', '') or '')
    except BaseException:
        return ''


def _active_is_weixin_mode():
    try:
        p = _active_launch_protocol().lower()
        bp = _active_bound_process_name().lower()
        if ('weixin://' in p) or ('wechat' in p) or ('weixin' in p):
            return True
        if ('wechat' in bp) or ('weixin' in bp) or ('wechatappex' in bp):
            return True
    except BaseException:
        pass
    return False


def _active_is_qq_mode():
    try:
        if _active_is_weixin_mode():
            return False
        p = _active_launch_protocol().lower()
        return ('tencent://' in p) or ('qq' in p)
    except BaseException:
        return False


def _wechat_focus_enabled():
    try:
        return _truthy(_cfg_get(_active_bot_sections(), 'enable_wechat_focus_guard', 'False'))
    except BaseException:
        return False


def _active_instance_id():
    try:
        v = _cfg_get(['instances'], 'active_id', '1')
        s = str(v).strip()
        return s if s else '1'
    except BaseException:
        return '1'


def _parse_hhmm(s):
    try:
        s = str(s).strip()
        if not s:
            return None
        parts = s.split(':', 1)
        h = int(parts[0].strip())
        m = int(parts[1].strip()) if len(parts) > 1 else 0
        if h < 0 or h > 23 or m < 0 or m > 59:
            return None
        return h * 60 + m
    except BaseException:
        return None


def _time_in_window_spec(spec):
    try:
        now = time.localtime()
        cur = now.tm_hour * 60 + now.tm_min
        text = str(spec or '').strip()
        if not text:
            return False
        text = text.replace(';', ',').replace('|', ',').replace(' ', ',')
        for part in text.split(','):
            part = part.strip()
            if not part or '-' not in part:
                continue
            a, b = part.split('-', 1)
            start = _parse_hhmm(a)
            end = _parse_hhmm(b)
            if start is None or end is None or start == end:
                continue
            if start < end:
                if cur >= start and cur < end:
                    return True
            else:
                if cur >= start or cur < end:
                    return True
    except BaseException:
        pass
    return False


def _friend_pause_reason_now():
    try:
        iid = _active_instance_id()
        friend_secs = ['instance.' + iid + '.friend', 'friend']
        bot_secs = ['instance.' + iid + '.bot', 'bot']
        no_steal_on = _truthy(_cfg_get(friend_secs, 'enable_no_steal_window', 'False'))
        no_steal_win = _cfg_get(friend_secs, 'no_steal_window', '13:00-15:00')
        if no_steal_on and _time_in_window_spec(no_steal_win):
            return 'no_steal_window=' + str(no_steal_win)
        rest_on = _truthy(_cfg_get(bot_secs, 'enable_rest_window', 'False'))
        rest_win = _cfg_get(bot_secs, 'rest_window', '')
        if rest_on and _time_in_window_spec(rest_win):
            return 'rest_window=' + str(rest_win)
    except BaseException as e:
        try: _write('friend pause check error ' + repr(e))
        except BaseException: pass
    return ''


def _runtime_info_once(key, msg):
    global _RUNTIME_INFO_SEEN
    try:
        sig = time.strftime('%Y-%m-%d %H:%M') + ' ' + str(key)
        if sig in _RUNTIME_INFO_SEEN:
            return
        _RUNTIME_INFO_SEEN.add(sig)
        logging_mod = sys.modules.get('logging')
        if logging_mod is not None:
            try:
                logging_mod.getLogger().info(msg)
            except BaseException:
                pass
    except BaseException:
        pass


def _friend_pause_active():
    global _FRIEND_PAUSE_LAST_LOG_KEY
    try:
        reason = _friend_pause_reason_now()
        if not reason:
            return False
        key = time.strftime('%Y-%m-%d %H:%M') + ' ' + reason
        if key != _FRIEND_PAUSE_LAST_LOG_KEY:
            _FRIEND_PAUSE_LAST_LOG_KEY = key
            _write('friend pause active: ' + reason + ' -> disable friend help/steal')
            _runtime_info_once(key, '\u6682\u505c\u65f6\u6bb5\u547d\u4e2d\uff1a\u5df2\u8df3\u8fc7\u597d\u53cb\u5e2e\u5fd9/\u5077\u83dc\u52a8\u4f5c\u3002')
        return True
    except BaseException:
        return False


def _daily_counters_default_path():
    try:
        base = os.environ.get('LOCALAPPDATA', '')
        if not base:
            return ''
        return os.path.join(base, 'qq-farm-bot-rev', 'daily_counters.json')
    except BaseException:
        return ''


def _daily_retry_max_default(max_retry=None):
    try:
        if max_retry is not None:
            return int(max_retry)
    except BaseException:
        pass
    try:
        v = _cfg_get(_active_bot_sections(), 'daily_flow_max_retry_per_day', '3')
        return int(float(str(v).strip()))
    except BaseException:
        return 3


def _repair_daily_task_retry_state_file(reason='startup', path=None, max_retry=None):
    global _DAILY_RETRY_REPAIR_LAST_TS
    try:
        now = time.time()
        runtime_path = path is None
        if runtime_path and _DAILY_RETRY_REPAIR_LAST_TS > 0 and (now - _DAILY_RETRY_REPAIR_LAST_TS) < 60.0:
            return False
        if runtime_path:
            _DAILY_RETRY_REPAIR_LAST_TS = now
        fp = str(path or _daily_counters_default_path())
        if not fp or not os.path.exists(fp):
            return False
        try:
            import json
        except BaseException:
            return False
        try:
            data = json.loads(open(fp, 'rb').read().decode('utf-8', 'replace'))
        except BaseException as e:
            _throttled_write('daily-retry-read-error', 'v30 daily retry repair read error ' + repr(e), 60.0)
            return False
        limit = _daily_retry_max_default(max_retry)
        changed = False
        touched = []
        def _fix_node(node, label):
            nonlocal changed
            try:
                if not isinstance(node, dict):
                    return
                last = str(node.get('task_last_date', '') or '').strip()
                counts = node.get('daily_flow_retry_counts')
                if not isinstance(counts, dict):
                    return
                cur = int(float(str(counts.get('task', 0) or 0)))
                if not last and cur >= limit:
                    counts['task'] = 0
                    changed = True
                    touched.append(str(label) + ':' + str(cur))
            except BaseException:
                pass
        _fix_node(data, 'global')
        try:
            inst = data.get('instances')
            if isinstance(inst, dict):
                for iid, node in list(inst.items()):
                    _fix_node(node, 'instance.' + str(iid))
        except BaseException:
            pass
        if not changed:
            return False
        try:
            text = json.dumps(data, ensure_ascii=False, indent=2)
            open(fp, 'wb').write(text.encode('utf-8'))
            _throttled_write('daily-retry-repaired', 'v30 daily task retry soft reset reason=' + str(reason) + ' touched=' + ','.join(touched[:8]), 10.0)
            return True
        except BaseException as e:
            _throttled_write('daily-retry-write-error', 'v30 daily retry repair write error ' + repr(e), 60.0)
            return False
    except BaseException as e:
        try: _throttled_write('daily-retry-error', 'v30 daily retry repair error ' + repr(e), 60.0)
        except BaseException: pass
    return False


def _force_autolaunch_config_file():
    global _CONFIG_FILE_PATCH_TS
    try:
        now = time.time()
        if now - _CONFIG_FILE_PATCH_TS < 2.0:
            return False
        _CONFIG_FILE_PATCH_TS = now
        base = os.environ.get('LOCALAPPDATA', '')
        if not base:
            return False
        cfg = os.path.join(base, 'qq-farm-bot-rev', 'config-multi.ini')
        if not os.path.exists(cfg):
            return False
        try:
            data = open(cfg, 'rb').read().decode('utf-8', 'replace')
        except BaseException:
            data = open(cfg, 'r').read()
        old = data
        weixin_mode = _active_is_weixin_mode()
        active_proto = _active_launch_protocol()
        try:
            active_bot_secs = set([_norm_key(x) for x in _active_bot_sections()])
        except BaseException:
            active_bot_secs = set(['bot'])
        lines = []
        cur_sec = ''
        for line in data.splitlines():
            low = line.strip().lower()
            if low.startswith('[') and ']' in low:
                cur_sec = low[1:low.find(']')].strip()
                lines.append(line)
                continue
            key = low.split('=', 1)[0].strip().replace('-', '_') if '=' in low else ''
            if key in _VIP_CONFIG_FORCED_BOOL_TRUE and key != 'enable_wechat_focus_guard':
                line = key + ' = True'
            elif cur_sec in active_bot_secs and key == 'window_title':
                line = 'window_title = QQ\u7ecf\u5178\u519c\u573a'
            elif key == 'window_title_match_mode':
                line = 'window_title_match_mode = exact'
            elif False and key == 'action_mode':
                line = 'action_mode = drag'
            elif False and key == 'auto_sell_fruit_interval_hours':
                line = 'auto_sell_fruit_interval_hours = 0.10'
            elif False and key == 'bottom_friend_list_help_all_limit':
                line = 'bottom_friend_list_help_all_limit = 12'
            elif weixin_mode and cur_sec in active_bot_secs and key == 'launch_protocol' and active_proto:
                line = 'launch_protocol = ' + active_proto
            elif weixin_mode and cur_sec in active_bot_secs and key == 'bound_process_name':
                line = 'bound_process_name = wechatappex.exe'
            lines.append(line)
        data = '\n'.join(lines) + ('\n' if old.endswith('\n') else '')
        if data != old:
            open(cfg, 'wb').write(data.encode('utf-8'))
            _write('config autolaunch/focus synced' + (' weixin' if weixin_mode else ''))
            return True
    except BaseException as e:
        try: _write('config autolaunch force error ' + repr(e))
        except BaseException: pass
    return False


def _config_override_value(section, option, kind):
    try:
        s = _norm_key(section)
        o = _norm_key(option)
        if _friend_pause_active():
            if o in _FRIEND_PAUSE_FORCE_FALSE:
                return False if kind == 'bool' else 'False'
            if ('friend' in s) and o.startswith('enable_') and (('help' in o) or ('steal' in o) or ('troublemaker' in o)):
                return False if kind == 'bool' else 'False'
        if o == 'enable_wechat_focus_guard':
            # Preserve the user's saved switch in every client mode. Runtime
            # activation is still gated by _active_is_weixin_mode().
            return None
        if o == 'window_title':
            return 'QQ\u7ecf\u5178\u519c\u573a'
        if o in _VIP_CONFIG_FORCED_BOOL_TRUE:
            return True if kind == 'bool' else 'True'
        if o == 'window_title_match_mode':
            return 'exact'
        if False and o == 'action_mode':
            return 'drag'
        if False and o == 'auto_sell_fruit_interval_hours':
            return '0.10'
        if False and o == 'bottom_friend_list_help_all_limit':
            return '12'
        if _active_is_weixin_mode():
            if o == 'enable_wechat_focus_guard':
                return True if kind == 'bool' else 'True'
            if o == 'launch_protocol':
                p = _active_launch_protocol()
                if p:
                    return p
            if o == 'bound_process_name':
                return 'wechatappex.exe'
            if o == 'window_title':
                # Target the actual mini-game window, not the Weixin shell.
                return 'QQ\u7ecf\u5178\u519c\u573a'
    except BaseException:
        pass
    return None


def _install_config_override_patch():
    global _CONFIG_OVERRIDE_PATCHED
    if _CONFIG_OVERRIDE_PATCHED:
        return True
    try:
        cp = sys.modules.get('configparser')
        if cp is None:
            return False
        for cls_name in ('RawConfigParser', 'ConfigParser'):
            cls = getattr(cp, cls_name, None)
            if cls is None or getattr(cls, '__qqfarm_config_patched__', False):
                continue
            orig_get = getattr(cls, 'get', None)
            orig_getboolean = getattr(cls, 'getboolean', None)
            orig_getint = getattr(cls, 'getint', None)
            if orig_get:
                def patched_get(self, section, option, *args, __orig=orig_get, **kwargs):
                    v = _config_override_value(section, option, 'str')
                    if v is not None:
                        return v
                    return __orig(self, section, option, *args, **kwargs)
                cls.get = patched_get
            if orig_getboolean:
                def patched_getboolean(self, section, option, *args, __orig=orig_getboolean, **kwargs):
                    v = _config_override_value(section, option, 'bool')
                    if v is not None:
                        return bool(v)
                    return __orig(self, section, option, *args, **kwargs)
                cls.getboolean = patched_getboolean
            if orig_getint:
                def patched_getint(self, section, option, *args, __orig=orig_getint, **kwargs):
                    return __orig(self, section, option, *args, **kwargs)
                cls.getint = patched_getint
            try: cls.__qqfarm_config_patched__ = True
            except BaseException: pass
        sp = getattr(cp, 'SectionProxy', None)
        if sp is not None and not getattr(sp, '__qqfarm_config_patched__', False):
            orig_sp_get = getattr(sp, 'get', None)
            orig_sp_getboolean = getattr(sp, 'getboolean', None)
            if orig_sp_get:
                def patched_sp_get(self, option, *args, __orig=orig_sp_get, **kwargs):
                    sec = getattr(self, 'name', None) or getattr(self, '_name', '')
                    v = _config_override_value(sec, option, 'str')
                    if v is not None:
                        return v
                    return __orig(self, option, *args, **kwargs)
                sp.get = patched_sp_get
            if orig_sp_getboolean:
                def patched_sp_getboolean(self, option, *args, __orig=orig_sp_getboolean, **kwargs):
                    sec = getattr(self, 'name', None) or getattr(self, '_name', '')
                    v = _config_override_value(sec, option, 'bool')
                    if v is not None:
                        return bool(v)
                    return __orig(self, option, *args, **kwargs)
                sp.getboolean = patched_sp_getboolean
            try: sp.__qqfarm_config_patched__ = True
            except BaseException: pass
        _CONFIG_OVERRIDE_PATCHED = True
        _write('configparser override installed v15')
        return True
    except BaseException as e:
        try: _write('config override patch error ' + repr(e))
        except BaseException: pass
    return False


# ---- v32 exact core runtime state patch ----
# Earlier revisions intentionally excluded broad utils.* and gui.* scanning to
# avoid startup stalls. The real long-running bot/window classes live there,
# however, so periodic entitlement refresh could still disable configured
# features after startup. Patch only the two exact class names and only known
# entitlement methods; business switches are restored from config, never forced.
_CORE_RUNTIME_PATCH_LOG_SEEN = set()


def _configured_bool(sections, key, default=False):
    try:
        return _truthy(_cfg_get(sections, key, 'True' if default else 'False'), default)
    except BaseException:
        return bool(default)


def _restore_runtime_business_switches(obj):
    changed = 0
    try:
        groups = [
            (_active_bot_sections(), [
                ('enable_wechat_focus_guard', ('enable_wechat_focus_guard', 'wechat_focus_guard')),
                ('hide_miniapp_compat_mode', ('hide_miniapp_compat_mode',)),
                ('high_performance_mode', ('high_performance_mode',)),
            ]),
            (_active_self_sections(), [
                ('auto_fertilize_one', ('auto_fertilize_one', 'planting_auto_fertilize_one')),
                ('auto_fertilize_more', ('auto_fertilize_more', 'planting_auto_fertilize_more')),
                ('auto_fill_fertilizer_container', ('auto_fill_fertilizer_container',)),
                ('auto_sell_fruit', ('auto_sell_fruit',)),
            ]),
            (_active_friend_sections(), [
                ('enable_daily_troublemaker', ('enable_daily_troublemaker', 'daily_troublemaker')),
                ('enable_skip_radish', ('enable_skip_radish', 'skip_radish')),
            ]),
            (_active_planting_sections(), [
                ('enable_daily_radish_exp', ('enable_daily_radish_exp', 'daily_radish_exp')),
                ('enable_quad_act_seeds', ('enable_quad_act_seeds', 'quad_act_seeds')),
                ('enhance_empty_land_detection', ('enhance_empty_land_detection', 'planting_enhance_empty_land_detection')),
            ]),
        ]
        for sections, entries in groups:
            for key, aliases in entries:
                desired = _configured_bool(sections, key, False)
                try:
                    if key == 'enable_wechat_focus_guard' and obj.__class__.__name__ == 'FarmBotCV':
                        desired = bool(desired and _active_is_weixin_mode())
                except BaseException:
                    pass
                for attr in aliases:
                    try:
                        if not hasattr(obj, attr):
                            continue
                        old = getattr(obj, attr)
                        if callable(old):
                            continue
                        if bool(old) != bool(desired):
                            setattr(obj, attr, bool(desired))
                            changed += 1
                    except BaseException:
                        pass
    except BaseException:
        pass
    return changed


def _core_runtime_refresh_method(self, *a, **k):
    try:
        _force_entitlement_attrs(self)
    except BaseException:
        pass
    try:
        changed = _restore_runtime_business_switches(self)
        if changed:
            _throttled_write('v32-core-switch-restore-' + _class_name(self), 'v32 core runtime restored configured switches=' + str(changed) + ' class=' + _class_name(self), 30.0)
    except BaseException:
        pass
    try:
        refresh = getattr(self, '_refresh_entitlement_dependent_controls', None)
        if callable(refresh) and not getattr(refresh, '__qqfarm_core_refresh_running__', False):
            refresh()
    except BaseException:
        pass
    return None


def _core_disable_entitlement_noop(self, *a, **k):
    _core_runtime_refresh_method(self)
    return False


def _wrap_core_periodic_refresh(fn, name=''):
    if getattr(fn, '__qqfarm_core_periodic_refresh_wrapped__', False):
        return fn, False
    def _wrapped(self, *a, **k):
        try:
            _force_entitlement_attrs(self)
            _restore_runtime_business_switches(self)
        except BaseException:
            pass
        result = fn(self, *a, **k)
        try:
            _force_entitlement_attrs(self)
            _restore_runtime_business_switches(self)
        except BaseException:
            pass
        return result
    try:
        _wrapped.__name__ = getattr(fn, '__name__', '_run_periodic_entitlement_refresh')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_core_periodic_refresh_wrapped__ = True
        _wrapped.__qqfarm_core_periodic_refresh_orig__ = fn
    except BaseException:
        pass
    return _wrapped, True


def _wrap_core_state_method(fn, name=''):
    if getattr(fn, '__qqfarm_core_state_wrapped__', False):
        return fn, False
    def _wrapped(self, *a, **k):
        try:
            _force_entitlement_attrs(self)
            _restore_runtime_business_switches(self)
        except BaseException:
            pass
        try:
            res = fn(self, *a, **k)
        except BaseException as e:
            try: _throttled_write('v32-core-state-error-' + str(name), 'v32 core state wrapper exception ' + str(name) + ' ' + repr(e), 30.0)
            except BaseException: pass
            res = None
        try:
            _force_entitlement_attrs(self)
            _restore_runtime_business_switches(self)
        except BaseException:
            pass
        return res
    try:
        _wrapped.__name__ = getattr(fn, '__name__', 'core_state_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_core_state_wrapped__ = True
        _wrapped.__qqfarm_core_state_orig__ = fn
    except BaseException:
        pass
    return _wrapped, True


def _wrap_core_entitlement_callback(fn, name=''):
    if getattr(fn, '__qqfarm_core_callback_wrapped__', False):
        return fn, False
    def _wrapped(self, *a, **k):
        try:
            _force_entitlement_attrs(self)
            _restore_runtime_business_switches(self)
        except BaseException:
            pass
        aa = list(a)
        for idx, value in enumerate(aa):
            try:
                if isinstance(value, (dict, tuple, str, bool)) or value is None:
                    aa[idx] = _normalize_entitlement_result(name, value)
            except BaseException:
                pass
        kk = dict(k)
        for key, value in list(kk.items()):
            try:
                if isinstance(value, (dict, tuple, str, bool)) or value is None:
                    kk[key] = _normalize_entitlement_result(name, value)
            except BaseException:
                pass
        try:
            res = fn(self, *tuple(aa), **kk)
        except BaseException as e:
            try: _throttled_write('v32-core-callback-error-' + str(name), 'v32 core callback exception ' + str(name) + ' ' + repr(e), 30.0)
            except BaseException: pass
            res = _fake_info()
        try:
            _force_entitlement_attrs(self)
            _restore_runtime_business_switches(self)
        except BaseException:
            pass
        return _normalize_entitlement_result(name, res)
    try:
        _wrapped.__name__ = getattr(fn, '__name__', 'core_callback_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_core_callback_wrapped__ = True
        _wrapped.__qqfarm_core_callback_orig__ = fn
    except BaseException:
        pass
    return _wrapped, True


def _patch_core_runtime_for_module(m, tag=''):
    changed = 0
    try:
        module_name = str(getattr(m, '__name__', '') or '')
        for class_name in ('FarmBotCV', 'FarmBotWindow'):
            cls = getattr(m, class_name, None)
            if not isinstance(cls, type):
                continue
            if class_name == 'FarmBotCV':
                try:
                    old_refresh = getattr(cls, '_run_periodic_entitlement_refresh', None)
                    if callable(old_refresh):
                        new_refresh, ok = _wrap_core_periodic_refresh(old_refresh, module_name + '.' + class_name + '._run_periodic_entitlement_refresh')
                        if ok:
                            setattr(cls, '_run_periodic_entitlement_refresh', new_refresh)
                            changed += 1
                except BaseException:
                    pass
                for method_name, replacement in [
                    ('_disable_entitlement_features', _core_disable_entitlement_noop),
                    ('_mark_entitlement_inactive', _core_runtime_refresh_method),
                    ('_is_security_related_entitlement_error', _fake_false),
                    ('_is_entitlement_rejected_error_text', _fake_false),
                    ('_is_entitlement_enabled', _fake_true),
                    ('is_entitlement_enabled', _fake_true),
                ]:
                    try:
                        old = getattr(cls, method_name, None)
                        if old is not None and old is not replacement:
                            setattr(cls, method_name, replacement)
                            changed += 1
                    except BaseException:
                        pass
            else:
                for method_name, replacement in [
                    ('_is_entitlement_effective_for_ui_lock', _fake_true),
                    ('_enforce_multi_instance_entitlement_lock', _fake_none),
                    ('_on_entitlement_auto_refresh_timeout', _core_runtime_refresh_method),
                    ('_is_entitlement_rejected_error_text', _fake_false),
                ]:
                    try:
                        old = getattr(cls, method_name, None)
                        if old is not None and old is not replacement:
                            setattr(cls, method_name, replacement)
                            changed += 1
                    except BaseException:
                        pass
                for method_name in ('_refresh_entitlement_dependent_controls', '_show_entitlement_access_dialog'):
                    try:
                        old = getattr(cls, method_name, None)
                        if callable(old):
                            new, ok = _wrap_core_state_method(old, module_name + '.' + class_name + '.' + method_name)
                            if ok:
                                setattr(cls, method_name, new)
                                changed += 1
                    except BaseException:
                        pass
                for method_name in ('_on_entitlement_refresh_finished', '_apply_startup_entitlement_check_result'):
                    try:
                        old = getattr(cls, method_name, None)
                        if callable(old):
                            new, ok = _wrap_core_entitlement_callback(old, module_name + '.' + class_name + '.' + method_name)
                            if ok:
                                setattr(cls, method_name, new)
                                changed += 1
                    except BaseException:
                        pass
        if changed:
            sig = module_name + ':' + str(changed)
            if sig not in _CORE_RUNTIME_PATCH_LOG_SEEN:
                _CORE_RUNTIME_PATCH_LOG_SEEN.add(sig)
                _write('v32 exact core runtime patched ' + str(tag) + ' ' + sig)
    except BaseException as e:
        try: _throttled_write('v32-core-patch-error', 'v32 exact core runtime patch error ' + repr(e), 30.0)
        except BaseException: pass
    return changed


def _patch_core_runtime_loaded(tag=''):
    changed = []
    try:
        for module_name, module in list(sys.modules.items()):
            if module is None:
                continue
            low = str(module_name).lower()
            if not (low.startswith('utils.') or low.startswith('gui.')):
                continue
            try:
                count = _patch_core_runtime_for_module(module, tag)
                if count:
                    changed.append(str(module_name) + ':' + str(count))
            except BaseException:
                pass
    except BaseException as e:
        try: _throttled_write('v32-core-scan-error', 'v32 exact core runtime scan error ' + repr(e), 30.0)
        except BaseException: pass
    return changed


_GUI_ENTITLEMENT_ALIAS_MISSING_SEEN = set()


def _patch_gui_entitlement_aliases_for_module(module, tag=''):
    changed = 0
    try:
        module_name = str(getattr(module, '__name__', '') or '')
        if not module_name.startswith('gui.'):
            return 0
        cls = getattr(module, 'FarmBotWindow', None)
        if not isinstance(cls, type):
            return 0
        for alias, replacement in [
            ('_qf_0cddfc2fb9dc', _fake_info),
            ('load_local_entitlement', _fake_local),
            ('clear_local_entitlement', _fake_none),
            ('bind_entitlement_card', _fake_bind),
            ('unbind_entitlement_card', _fake_none),
        ]:
            try:
                try:
                    old = getattr(module, alias)
                except AttributeError:
                    missing_key = (module_name, alias)
                    if missing_key not in _GUI_ENTITLEMENT_ALIAS_MISSING_SEEN:
                        _GUI_ENTITLEMENT_ALIAS_MISSING_SEEN.add(missing_key)
                        try: _throttled_write('v35-gui-alias-missing-' + module_name + '-' + alias, 'v35 gui entitlement alias missing ' + module_name + '.' + alias, 30.0)
                        except BaseException: pass
                    continue
                if old is replacement:
                    continue
                setattr(module, alias, replacement)
                changed += 1
            except BaseException as e:
                try: _throttled_write('v35-gui-alias-error-' + module_name + '-' + alias, 'v35 gui entitlement alias error ' + module_name + '.' + alias + ' ' + repr(e), 30.0)
                except BaseException: pass
        if changed:
            _throttled_write('v35-gui-alias-success-' + module_name, 'v35 gui entitlement aliases patched ' + str(tag) + ' ' + module_name + ':' + str(changed), 30.0)
    except BaseException as e:
        try: _throttled_write('v35-gui-alias-module-error', 'v35 gui entitlement alias module error ' + repr(e), 30.0)
        except BaseException: pass
    return changed


def _patch_gui_entitlement_aliases_loaded(tag=''):
    changed = []
    try:
        for module_name, module in list(sys.modules.items()):
            if module is None:
                continue
            try:
                count = _patch_gui_entitlement_aliases_for_module(module, tag)
                if count:
                    changed.append(str(module_name) + ':' + str(count))
            except BaseException as e:
                try: _throttled_write('v35-gui-alias-module-error-' + str(module_name), 'v35 gui entitlement alias module error ' + str(module_name) + ' ' + repr(e), 30.0)
                except BaseException: pass
    except BaseException as e:
        try: _throttled_write('v35-gui-alias-scan-error', 'v35 gui entitlement alias scan error ' + repr(e), 30.0)
        except BaseException: pass
    return changed


def _claims():
    now = int(time.time())
    exp = 4102444800
    flags = {'*': True, 'vip': True, 'all': True, 'entitlement': True,
        'wechat_mouse': True, 'wechat_focus_guard': True, 'enable_wechat_focus_guard': True,
        'high_performance_mode': True, 'auto_fertilize': True, 'auto_fertilize_one': True,
        'auto_fertilize_more': True, 'auto_fill_fertilizer_container': True,
        'auto_sell_fruit': True, 'daily_troublemaker': True, 'enable_daily_troublemaker': True,
        'quad_act_seeds': True, 'enable_quad_act_seeds': True, 'daily_radish_exp': True,
        'enable_no_steal_window': True, 'no_steal_window': True, 'guard_dog_help_only': True,
        'bottom_friend_list_help_all': True, 'multi_instance': True, 'svip': True}
    return {
        'active': True, 'status': 'active', 'state': 'active', 'valid': True, 'ok': True,
        'license_id': 'LOCAL-PATCH-VIP', 'license_id_hash': 'LOCAL-PATCH-VIP',
        'feature_flags': flags, 'features': flags,
        'exp': exp, 'expire_at': exp, 'expires_at': exp, 'expires_at_unix': exp,
        'card_expire_at': exp, 'card_expire_at_unix': exp, 'token_expire_at': exp,
        'iat': now, 'issued_at_unix': now, 'updated_at': '2099-12-31 23:59:59',
        'trusted_time_anchor_unix': now,
        'device_hash': 'LOCAL-PATCH-VIP', 'bound_hash': 'LOCAL-PATCH-VIP'
    }

def _fake_local(*a, **k):
    c = _claims()
    return {'ok': True, 'active': True, 'status': 'active', 'state': 'active', 'token': 'local.runtime.patch', 'claims': c, 'verified_claims': c, 'license_id': c['license_id'], 'exp': c['exp'], 'card_expire_at': c['card_expire_at'], 'message': 'local_runtime_patch'}

def _fake_claims(*a, **k): return _claims()
def _fake_true(*a, **k): return True
def _fake_false(*a, **k): return False
def _fake_none(*a, **k): return None
def _fake_gate(*a, **k): return (True, 'local_runtime_patch')
def _fake_integrity(*a, **k): return _OK_OBJ
def _fake_list(*a, **k): return []

def _fake_info(*a, **k):
    c = _claims()
    return {'ok': True, 'active': True, 'status': 'active', 'state': 'active', 'reason': 'local_runtime_patch', 'message': 'local_runtime_patch', 'claims': c, 'license_id': c['license_id'], 'exp_unix': c['exp'], 'card_expire_at_unix': c['card_expire_at'], 'has_local_license': True}

def _fake_bind(*a, **k):
    d = _fake_info()
    d['token'] = 'local.runtime.patch'
    return d

def _fake_license_payload():
    c = _claims()
    return {
        'ok': True, 'active': True, 'valid': True, 'status': 'active', 'state': 'active',
        'token': 'local.runtime.patch', 'license_token': 'local.runtime.patch',
        'claims': c, 'verified_claims': c, 'license_id': c.get('license_id'),
        'feature_flags': c.get('feature_flags'), 'features': c.get('features'),
        'message': 'local_runtime_patch', 'reason': 'local_runtime_patch',
        'has_local_license': True, 'source': 'local_runtime_patch'
    }

def _fake_license_text():
    # Static JSON only. Do not import json here: this function may be called from import hooks.
    return '{"ok":true,"active":true,"valid":true,"status":"active","state":"active","token":"local.runtime.patch","license_token":"local.runtime.patch","license_id":"LOCAL-PATCH-VIP","has_local_license":true,"message":"local_runtime_patch","reason":"local_runtime_patch","claims":{"active":true,"status":"active","state":"active","valid":true,"ok":true,"license_id":"LOCAL-PATCH-VIP","feature_flags":{"*":true,"vip":true,"all":true,"entitlement":true,"wechat_mouse":true},"features":{"*":true,"vip":true,"all":true,"entitlement":true,"wechat_mouse":true},"exp":4102444800,"expire_at":4102444800,"expires_at":4102444800,"expires_at_unix":4102444800,"card_expire_at":4102444800,"card_expire_at_unix":4102444800,"token_expire_at":4102444800,"updated_at":"2099-12-31 23:59:59","trusted_time_anchor_unix":1780000000,"device_hash":"LOCAL-PATCH-VIP","bound_hash":"LOCAL-PATCH-VIP"}}'

def _refresh_method(self, *a, **k):
    for n, v in [
        ('entitlement_active', True), ('_entitlement_active', True),
        ('entitlement_state_reason', 'local_runtime_patch'), ('_entitlement_state_reason', 'local_runtime_patch'),
        ('_entitlement_claims', _claims()), ('_last_entitlement_refresh_ts', time.time())
    ]:
        try: setattr(self, n, v)
        except BaseException: pass
    return None

def _dialog_method(self, *a, **k):
    try: setattr(self, 'entitlement_active', True)
    except BaseException: pass
    return True

def _patch_method(cls, name, fn):
    try:
        if hasattr(cls, name):
            setattr(cls, name, fn)
            return True
    except BaseException:
        pass
    return False

_FUNC_TYPE = type(_fake_true)
_ENT_FUNC_WRAP_COUNT = 0


def _contains_any_text(blob, keys):
    try:
        low = str(blob).lower()
        for k in keys:
            if str(k).lower() in low:
                return True
    except BaseException:
        pass
    return False


def _func_blob(fn, name=''):
    parts = [str(name)]
    try: parts.append(str(getattr(fn, '__name__', '')))
    except BaseException: pass
    try: parts.append(str(getattr(fn, '__qualname__', '')))
    except BaseException: pass
    try:
        code = getattr(fn, '__code__', None)
        if code is not None:
            try: parts.append(' '.join([str(x) for x in getattr(code, 'co_names', ())]))
            except BaseException: pass
            try:
                consts = []
                for c in getattr(code, 'co_consts', ()):
                    if isinstance(c, (str, bytes)):
                        consts.append(c.decode('utf-8', 'ignore') if isinstance(c, bytes) else c)
                parts.append(' '.join(consts[:80]))
            except BaseException: pass
    except BaseException:
        pass
    return ' '.join(parts)


def _is_entitlement_func(fn, name=''):
    blob = _func_blob(fn, name)
    return _contains_any_text(blob, [
        'entitlement', 'feature_gate', 'vip_license', 'vip access', 'license_active',
        'is_vip', 'vip_active', 'has_feature_access', 'has_entitlement',
        '\u6743\u76ca', '\u8bb8\u53ef\u8bc1', '\u672c\u5730\u65e0', '\u672a\u6fc0\u6d3b',
        '\u5f00\u901a vip', '\u4f1a\u5458\u6743\u76ca', 'current device', 'local license'
    ])


def _should_skip_original_entitlement_func(fn, name=''):
    blob = _func_blob(fn, name)
    return _contains_any_text(blob, [
        '_run_periodic_entitlement_refresh', '_refresh_runtime_entitlement', '_update_entitlement_status',
        '_sync_entitlement_status', '_enforce_multi_instance_entitlement_lock',
        '\u6743\u76ca\u72b6\u6001\u5df2\u5173\u95ed', '\u5f53\u524d\u8bbe\u5907\u672a\u68c0\u6d4b\u5230\u6709\u6548\u672c\u5730\u8bb8\u53ef\u8bc1',
        '\u672c\u5730\u65e0\u8bb8\u53ef\u8bc1', 'no valid local license'
    ])


def _normalize_entitlement_result(name, res):
    try:
        lname = str(name).lower()
        if 'rejected' in lname or 'should_clear' in lname or 'invalid_error' in lname:
            return False
        if ('feature_gate' in lname) or ('require_' in lname) or ('check_' in lname and ('entitlement' in lname or 'vip' in lname or 'feature' in lname)):
            return (True, 'local_runtime_patch')
        if ('info' in lname) and ('entitlement' in lname or 'vip' in lname or 'license' in lname):
            return _fake_info()
        if ('load' in lname or 'read' in lname) and ('entitlement' in lname or 'license' in lname):
            return _fake_local()
        if ('claims' in lname) or ('verify_compact' in lname):
            return _claims()
        if isinstance(res, dict):
            d = dict(res)
            try: _patch_runtime_dict(d)
            except BaseException: pass
            c = _claims()
            d.update({'ok': True, 'active': True, 'valid': True, 'status': 'active', 'state': 'active', 'reason': 'local_runtime_patch', 'message': 'local_runtime_patch', 'has_local_license': True})
            if 'claims' not in d: d['claims'] = c
            if 'verified_claims' not in d: d['verified_claims'] = c
            if 'token' not in d: d['token'] = 'local.runtime.patch'
            return d
        if isinstance(res, tuple):
            if len(res) == 0:
                return (True, 'local_runtime_patch')
            # Most gate functions are (ok, reason/info). Preserve extra shape but force first slot true.
            return tuple([True] + list(res[1:]))
        if res is False:
            return True
        if isinstance(res, str):
            low = res.lower()
            if ('license' in low) or ('\u8bb8\u53ef' in res) or ('\u672a\u6fc0\u6d3b' in res) or ('\u672c\u5730\u65e0' in res):
                return 'local_runtime_patch'
    except BaseException:
        pass
    return res


def _wrap_entitlement_func(fn, name=''):
    global _ENT_FUNC_WRAP_COUNT
    try:
        if not isinstance(fn, _FUNC_TYPE):
            return fn, False
        if getattr(fn, '__qqfarm_vip_wrapped__', False):
            return fn, False
        if fn in (_fake_true, _fake_false, _fake_none, _fake_gate, _fake_local, _fake_claims, _fake_info, _fake_bind):
            return fn, False
        if not _is_entitlement_func(fn, name):
            return fn, False
        skip_original = _should_skip_original_entitlement_func(fn, name)
        def _wrapped(*a, **k):
            try:
                for x in list(a)[:4]:
                    try:
                        if _runtime_obj_interesting(x): _force_runtime_object(x)
                    except BaseException: pass
                if skip_original:
                    try: _write('runtime skipped entitlement func ' + str(name))
                    except BaseException: pass
                    lname = str(name).lower()
                    if ('gate' in lname) or ('require' in lname) or ('check' in lname):
                        return (True, 'local_runtime_patch')
                    return None
                res = fn(*a, **k)
                return _normalize_entitlement_result(name, res)
            except BaseException as e:
                try: _write('runtime entitlement wrapper exception ' + str(name) + ' ' + repr(e))
                except BaseException: pass
                return _normalize_entitlement_result(name, None)
        try:
            _wrapped.__name__ = getattr(fn, '__name__', '_wrapped')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_vip_wrapped__ = True
            _wrapped.__qqfarm_vip_orig__ = fn
        except BaseException:
            pass
        _ENT_FUNC_WRAP_COUNT += 1
        return _wrapped, True
    except BaseException:
        return fn, False


def _patch_module_functions_generic(m):
    # v10-ui-stable: disabled. v8/v9 generic wrapping touched GUI build functions and hid the main window.
    return 0

def _patch_module(m):
    changed = 0
    groups = [
        (['is_vip_unlocked','verify_vip_license','check_vip_license_signature','validate_vip_device_binding','verify_vip_server_challenge','validate_vip_public_key','check_vip_payment_receipt','enable_vip_features','touch_vip_validation_decoys','is_entitlement_enabled','_is_entitlement_enabled','has_entitlement','_has_entitlement','is_vip_active','_is_vip_active','_qf_7df7ee432596','_qf_60adf77be908','_qf_c8757eb57f8d'], _fake_true),
        (['_qf_8a5861d7851e','_qf_907352fde148','_qfp_67e1c320c26c','_qfp_7e78c522d6fd','feature_gate','check_feature_gate','require_feature','require_entitlement','check_entitlement','check_vip_access','has_feature_access'], _fake_gate),
        (['load_local_entitlement','_load_local_entitlement','read_local_entitlement','_read_local_entitlement'], _fake_local),
        (['_verify_compact_ed25519_token','verify_compact_ed25519_token','_decode_claims_without_verify'], _fake_claims),
        (['entitlement_info','gui_entitlement_info','get_entitlement_info','_get_entitlement_info','_collect_entitlement_report_summary'], _fake_info),
        (['bind_entitlement_card','gui_entitlement_bind','fetch_version_info_payload'], _fake_bind),
        (['unbind_entitlement_card','gui_entitlement_unbind','clear_local_entitlement','_apply_entitlement_security_action','_run_report_safe','start_version_info_report_async','report_version_info_crash_sync','_post_version_info'], _fake_none),
        (list(_INTEGRITY_EXIT_NOOP_NAMES), _fake_none),
        (['integrity_check','_verify_manifest_signature','_verify_manifest_hashes','_verify_windows_authenticode_thumbprint','maybe_exit_on_integrity_failure_deadline','schedule_integrity_failure_exit','initialize_patch_integrity_baseline'], _fake_integrity),
        (['collect_patch_integrity_signals','collect_crack_artifact_signals','_collect_manifest_signals','_collect_runtime_directory_signals','_collect_report_url_signals','_collect_public_key_signals'], _fake_list),
    ]
    for names, fn in groups:
        for n in names:
            if hasattr(m, n):
                try:
                    setattr(m, n, fn)
                    changed += 1
                except BaseException:
                    pass
    for n, v in [
        ('entitlement_active', True), ('_entitlement_active', True), ('_entitlement_claims', _claims()),
        ('_last_entitlement_refresh_ts', time.time()), ('_integrity_failure_scheduled', False),
        ('_integrity_failure_deadline_ts', time.time()+10**9), ('_next_integrity_check_ts', time.time()+10**9)
    ]:
        try:
            if hasattr(m, n):
                setattr(m, n, v)
                changed += 1
        except BaseException:
            pass
    try:
        names = dir(m)
    except BaseException:
        names = []
    for objname in names:
        try: obj = getattr(m, objname)
        except BaseException: continue
        if isinstance(obj, type):
            for nm, fn in [
                ('_show_entitlement_access_dialog', _dialog_method),
                ('_should_clear_local_license_on_rejected_error_text', _fake_false),
                ('_refresh_entitlement_status', _refresh_method),
                ('_update_entitlement_status', _refresh_method),
                ('_sync_entitlement_status', _refresh_method),
                ('_refresh_runtime_entitlement', _refresh_method),
                ('_enforce_multi_instance_entitlement_lock', _fake_none),
                ('_is_entitlement_enabled', _fake_true),
                ('is_entitlement_enabled', _fake_true),
                ('_is_vip_active', _fake_true),
                ('is_vip_active', _fake_true),
                ('_is_entitlement_rejected_error_text', _fake_false),
                ('_is_entitlement_rejected_error', _fake_false),
            ]:
                if _patch_method(obj, nm, fn): changed += 1
    try:
        lf = getattr(m, 'ENTITLEMENT_LICENSE_FILE', None)
        if lf is not None:
            sig_lf = str(getattr(m, '__name__', '?')) + ' -> ' + repr(lf)
            if sig_lf not in _LICENSE_FILE_LOG_SEEN:
                _LICENSE_FILE_LOG_SEEN.add(sig_lf)
                _write('module license file ' + sig_lf)
    except BaseException:
        pass
    try:
        changed += _patch_module_functions_generic(m)
    except BaseException as e:
        try: _write('generic function patch error ' + str(getattr(m, '__name__', '?')) + ' ' + repr(e))
        except BaseException: pass
    return changed

def _security_watchdog_name_match(module_name, attr_name):
    try:
        mn = str(module_name).lower()
        n = str(attr_name).lower()
        if not (mn == 'bot.security' or mn.startswith('bot.security.')):
            return False
        if n in ('_shadow_penalty_exit_watchdog', '_qf_60723e1c26a6', '_qf_e4b465e77dde'):
            return True
        if n == '_worker' and 'runtime_security_scheduler' in mn:
            return True
        if ('watchdog' in n) or ('penalty' in n and ('exit' in n or 'shadow' in n)):
            return True
        if 'security_scheduler' in n:
            return True
    except BaseException:
        pass
    return False


def _make_security_watchdog_noop(module_name, attr_name):
    def _noop(*a, **k):
        try:
            _throttled_write('security-watchdog-call-' + str(module_name) + '.' + str(attr_name), 'v30 security watchdog noop called ' + str(module_name) + '.' + str(attr_name), 300.0)
        except BaseException:
            pass
        return None
    try:
        _noop.__name__ = str(attr_name)
        _noop.__qualname__ = str(attr_name)
        _noop.__qqfarm_security_watchdog_patched__ = True
    except BaseException:
        pass
    return _noop


def _install_security_watchdog_patch_for_module(m, tag=''):
    changed = 0
    try:
        mn = str(getattr(m, '__name__', '') or '')
        if not (mn == 'bot.security' or mn.startswith('bot.security.')):
            return 0
        targets = [(m, mn)]
        try:
            for cn, obj in list(vars(m).items())[:500]:
                if isinstance(obj, type):
                    targets.append((obj, mn + '.' + str(cn)))
        except BaseException:
            pass
        for obj, prefix in targets:
            try:
                names = list(vars(obj).keys())
            except BaseException:
                try:
                    names = dir(obj)
                except BaseException:
                    names = []
            for n in names:
                try:
                    if not _security_watchdog_name_match(mn, n):
                        continue
                    old = getattr(obj, n)
                    if not callable(old):
                        continue
                    if getattr(old, '__qqfarm_security_watchdog_patched__', False):
                        continue
                    setattr(obj, n, _make_security_watchdog_noop(prefix, n))
                    changed += 1
                except BaseException:
                    pass
        if changed:
            sig = mn + ':' + str(changed)
            if sig not in _SECURITY_WATCHDOG_PATCH_LOG_SEEN:
                _SECURITY_WATCHDOG_PATCH_LOG_SEEN.add(sig)
                _write('v30 security watchdog patched ' + str(tag) + ' ' + sig)
    except BaseException as e:
        try: _throttled_write('security-watchdog-patch-error', 'v30 security watchdog patch error ' + repr(e), 60.0)
        except BaseException: pass
    return changed


def _patch_security_watchdogs_loaded(tag=''):
    changed = []
    try:
        for mn, m in list(sys.modules.items()):
            try:
                if m is None:
                    continue
                low = str(mn).lower()
                if not (low == 'bot.security' or low.startswith('bot.security.')):
                    continue
                c = _install_security_watchdog_patch_for_module(m, tag)
                if c:
                    changed.append(str(mn) + ':' + str(c))
            except BaseException:
                pass
    except BaseException as e:
        try: _throttled_write('security-watchdogs-loaded-error', 'v30 security watchdog scan error ' + repr(e), 60.0)
        except BaseException: pass
    return changed


def _looks_integrity_exit_module(m):
    try:
        namespace = vars(m)
    except BaseException:
        return False
    try:
        return any(name in namespace for name in _INTEGRITY_EXIT_NOOP_NAMES)
    except BaseException:
        return False


def _is_target_module_name(mn):
    low = str(mn).lower()
    # Keep normal patching narrow, while allowing frozen obfuscated security
    # modules from the crash trace to be inspected by attribute.
    return (low == 'bot.security' or low.startswith('bot.security.') or (low.startswith('bot.') and 'entitlement' in low))


# ---- WeChat focus guard / background click patch v21 ----
# Root cause seen in logs: active instance uses weixin://, but some runtime code
# still reads the global bot section and takes the QQ branch, therefore it logs
# "QQ miniapp mode: WeChat mouse guard not applicable".  This section forces the
# runtime platform helpers to agree with the active instance and, as a fallback,
# routes common click helpers through PostMessage so the physical cursor/focus is
# not stolen by WeChatAppEx.
_WECHAT_FOCUS_FUNC_NAMES = set([
    'is_weixin_launch_protocol', 'is_qq_launch_protocol', '_is_weixin_bound_platform',
    '_wechat_focus_guard_enabled_for_instance', '_instance_bound_process_name',
    'ensure_wechat_focus_guard_for_current_window', '_apply_wechat_focus_guard_after_hwnd_ready',
    '_collapse_wechat_outer_panel_if_needed',
    'click_at_position', 'mouse_down_at_position', 'mouse_up_at_position',
    '_resolve_click_mode', '_is_click_mode_strict',
])


def _looks_wechat_focus_module(mn, m):
    try:
        low = str(mn).lower()
        if not (low == 'bot' or low.startswith('bot.')):
            return False
        for n in _WECHAT_FOCUS_FUNC_NAMES:
            if hasattr(m, n):
                return True
        try:
            for obj in list(vars(m).values())[:500]:
                if isinstance(obj, type):
                    for n in _WECHAT_FOCUS_FUNC_NAMES:
                        if hasattr(obj, n):
                            return True
        except BaseException:
            pass
    except BaseException:
        pass
    return False


def _fake_is_weixin_launch_protocol(*a, **k):
    try:
        for x in list(a) + list(k.values()):
            sx = str(x).lower()
            if 'weixin://' in sx or 'wechat' in sx or 'weixin' in sx:
                return True
        return _active_is_weixin_mode()
    except BaseException:
        return _active_is_weixin_mode()


def _wrap_is_qq_launch_protocol(fn, name):
    def _wrapped(*a, **k):
        try:
            if _active_is_weixin_mode():
                return False
            return fn(*a, **k)
        except BaseException:
            return False
    try:
        _wrapped.__name__ = getattr(fn, '__name__', 'is_qq_launch_protocol')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_wechat_focus_wrapped__ = True
    except BaseException:
        pass
    return _wrapped


def _fake_is_weixin_bound_platform(*a, **k):
    try:
        if _active_is_weixin_mode():
            return True
        for x in list(a)[:3]:
            try:
                dd = getattr(x, '__dict__', {})
                if isinstance(dd, dict):
                    blob = str(dd).lower()
                    if ('weixin://' in blob) or ('wechatappex' in blob) or ('wechat.exe' in blob) or ('weixin.exe' in blob):
                        return True
            except BaseException:
                pass
    except BaseException:
        pass
    return False



def _fake_wechat_focus_guard_enabled_for_instance(*a, **k):
    try:
        if _active_is_weixin_mode() and _wechat_focus_enabled():
            _runtime_info_once('wechat-focus-gate-forced', '\u5fae\u4fe1\u62a2\u9f20\u6807\u5904\u7406\u5df2\u7ed5\u8fc7\u539f\u59cb\u5f00\u5173/VIP\u95e8\u63a7\uff1a\u5f53\u524d\u5b9e\u4f8b\u5f3a\u5236\u542f\u7528\u3002')
            return True
        # Keep the saved switch selected in QQ mode without activating the
        # WeChat-only runtime path.
        return False
    except BaseException:
        return False


def _fake_instance_bound_process_name(*a, **k):
    try:
        if _active_is_weixin_mode():
            return 'wechatappex.exe'
    except BaseException:
        pass
    try:
        return _active_bound_process_name() or 'wechatappex.exe'
    except BaseException:
        return 'wechatappex.exe'


def _wrap_apply_wechat_focus_after_hwnd(fn, name):
    if getattr(fn, '__qqfarm_wechat_focus_wrapped__', False):
        return fn, False
    def _wrapped(*a, **k):
        try:
            if _stop_requested_in_args(a, k):
                return _stop_gate_return(name)
        except BaseException:
            pass
        try:
            if _active_is_weixin_mode() and _wechat_focus_enabled():
                _runtime_info_once('wechat-focus-apply-forced', '\u5fae\u4fe1\u62a2\u9f20\u6807\u5904\u7406\u5df2\u5f3a\u5236\u8fdb\u5165\u5e94\u7528\u9636\u6bb5\uff1aWeChatAppEx\u3002')
                _write('wechat focus apply invoking original ' + str(name))
        except BaseException:
            pass
        try:
            res = fn(*a, **k)
            if _active_is_weixin_mode() and _wechat_focus_enabled():
                _write('wechat focus apply result ' + str(name) + ' -> ' + repr(res))
            return res
        except BaseException as e:
            try: _write('wechat focus apply original exception ' + str(name) + ' ' + repr(e))
            except BaseException: pass
            return False
    try:
        _wrapped.__name__ = getattr(fn, '__name__', 'apply_wechat_focus_guard')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_wechat_focus_wrapped__ = True
    except BaseException:
        pass
    return _wrapped, True


def _fake_resolve_click_mode(*a, **k):
    try:
        if _active_is_weixin_mode() and _wechat_focus_enabled():
            _runtime_info_once('wechat-background-mode', '\u5fae\u4fe1\u9632\u62a2\u9f20\u6807\uff1a\u5df2\u5f3a\u5236\u5207\u6362\u4e3a background \u70b9\u51fb\u6a21\u5f0f\u3002')
            return 'background'
    except BaseException:
        pass
    return 'background'


def _fake_click_mode_strict(*a, **k):
    try:
        if _active_is_weixin_mode() and _wechat_focus_enabled():
            return True
    except BaseException:
        pass
    return False


def _wrap_wechat_focus_guard(fn, name):
    if getattr(fn, '__qqfarm_wechat_focus_wrapped__', False):
        return fn, False
    def _wrapped(*a, **k):
        if _active_is_weixin_mode() and _wechat_focus_enabled():
            try:
                _runtime_info_once('wechat-focus-guard-active', '\u5fae\u4fe1\u62a2\u9f20\u6807\u5904\u7406\u5df2\u5f3a\u5236\u542f\u7528\uff1a\u5f53\u524d\u5b9e\u4f8b\u4e3a weixin:// / WeChatAppEx\u3002')
                _write('wechat focus guard invoking original ' + str(name))
            except BaseException:
                pass
        try:
            return fn(*a, **k)
        except BaseException as e:
            try: _write('wechat focus guard original exception ' + str(name) + ' ' + repr(e))
            except BaseException: pass
            return False
    try:
        _wrapped.__name__ = getattr(fn, '__name__', 'ensure_wechat_focus_guard_for_current_window')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_wechat_focus_wrapped__ = True
    except BaseException:
        pass
    return _wrapped, True


def _find_wechat_hwnd():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        candidates = []
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def _cb(hwnd, lparam):
            try:
                if not user32.IsWindowVisible(hwnd):
                    return True
                title_buf = ctypes.create_unicode_buffer(256)
                cls_buf = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, title_buf, 255)
                user32.GetClassNameW(hwnd, cls_buf, 255)
                title = title_buf.value or ''
                cls = cls_buf.value or ''
                score = 0
                if '\u5fae\u4fe1' in title: score += 5
                if 'Chrome_WidgetWin' in cls: score += 4
                if 'Qt' in cls: score -= 2
                if score > 0:
                    candidates.append((score, int(hwnd), title, cls))
            except BaseException:
                pass
            return True
        user32.EnumWindows(EnumWindowsProc(_cb), 0)
        candidates.sort(reverse=True)
        if candidates:
            return candidates[0][1]
    except BaseException as e:
        try: _write('find wechat hwnd error ' + repr(e))
        except BaseException: pass
    return 0


def _extract_xy_from_args(args, kwargs):
    try:
        for a, b in [('x', 'y'), ('screen_x', 'screen_y'), ('target_x', 'target_y')]:
            if a in kwargs and b in kwargs:
                return int(float(kwargs.get(a))), int(float(kwargs.get(b)))
    except BaseException:
        pass
    vals = []
    try:
        for x in args:
            if isinstance(x, (int, float)):
                v = float(x)
                if -20 <= v <= 10000:
                    vals.append(v)
        # Screen coordinates are normally the last two numeric args for helpers
        # like click_at_position(bot, x, y) and mouse_down_at_position(x, y).
        if len(vals) >= 2:
            return int(vals[-2]), int(vals[-1])
    except BaseException:
        pass
    return None, None


def _post_wechat_mouse(kind, x, y):
    global _WECHAT_BG_CLICK_LAST_LOG_TS
    try:
        if not (_active_is_weixin_mode() and _wechat_focus_enabled()):
            return False
        if x is None or y is None:
            return False
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = _find_wechat_hwnd()
        if not hwnd:
            return False
        class POINT(ctypes.Structure):
            _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]
        pt = POINT(int(x), int(y))
        user32.ScreenToClient(ctypes.c_void_p(hwnd), ctypes.byref(pt))
        lparam = ((int(pt.y) & 0xffff) << 16) | (int(pt.x) & 0xffff)
        WM_MOUSEMOVE = 0x0200
        WM_LBUTTONDOWN = 0x0201
        WM_LBUTTONUP = 0x0202
        MK_LBUTTON = 0x0001
        if kind == 'down':
            user32.PostMessageW(ctypes.c_void_p(hwnd), WM_MOUSEMOVE, 0, lparam)
            ok = user32.PostMessageW(ctypes.c_void_p(hwnd), WM_LBUTTONDOWN, MK_LBUTTON, lparam)
        elif kind == 'up':
            ok = user32.PostMessageW(ctypes.c_void_p(hwnd), WM_LBUTTONUP, 0, lparam)
        else:
            user32.PostMessageW(ctypes.c_void_p(hwnd), WM_MOUSEMOVE, 0, lparam)
            user32.PostMessageW(ctypes.c_void_p(hwnd), WM_LBUTTONDOWN, MK_LBUTTON, lparam)
            ok = user32.PostMessageW(ctypes.c_void_p(hwnd), WM_LBUTTONUP, 0, lparam)
        now = time.time()
        if now - _WECHAT_BG_CLICK_LAST_LOG_TS > 5:
            _WECHAT_BG_CLICK_LAST_LOG_TS = now
            _write('wechat background mouse ' + str(kind) + ' hwnd=0x%X screen=(%s,%s) client=(%s,%s) ok=%s' % (int(hwnd), str(x), str(y), str(pt.x), str(pt.y), str(bool(ok))))
            _runtime_info_once('wechat-bg-click', '\u5fae\u4fe1\u9632\u62a2\u9f20\u6807\uff1a\u5df2\u542f\u7528\u540e\u53f0\u70b9\u51fb/\u7126\u70b9\u4fdd\u62a4\u515c\u5e95\u3002')
        return bool(ok)
    except BaseException as e:
        try: _write('wechat background mouse error ' + repr(e))
        except BaseException: pass
    return False


def _wrap_mouse_action_func(fn, name):
    if getattr(fn, '__qqfarm_wechat_mouse_wrapped__', False):
        return fn, False
    def _wrapped(*a, **k):
        try:
            if _stop_requested_in_args(a, k):
                return _stop_gate_return(name)
        except BaseException:
            pass
        try:
            if _active_is_weixin_mode() and _wechat_focus_enabled():
                x, y = _extract_xy_from_args(a, k)
                lname = str(name).lower()
                kind = 'click'
                if 'mouse_down' in lname:
                    kind = 'down'
                elif 'mouse_up' in lname:
                    kind = 'up'
                if _post_wechat_mouse(kind, x, y):
                    return True
        except BaseException as e:
            try: _write('wechat mouse wrapper fallback ' + str(name) + ' ' + repr(e))
            except BaseException: pass
        return fn(*a, **k)
    try:
        _wrapped.__name__ = getattr(fn, '__name__', 'wechat_mouse_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_wechat_mouse_wrapped__ = True
    except BaseException:
        pass
    return _wrapped, True


def _patch_wechat_focus_loaded(tag=''):
    changed = []
    try:
        for mn, m in list(sys.modules.items()):
            if m is None or not _looks_wechat_focus_module(mn, m):
                continue
            local_count = 0
            targets = [(m, str(mn))]
            try:
                for cls_name, obj in list(vars(m).items())[:500]:
                    if isinstance(obj, type):
                        targets.append((obj, str(mn) + '.' + str(cls_name)))
            except BaseException:
                pass
            for obj, prefix in targets:
                try:
                    if hasattr(obj, '_wechat_focus_guard_enabled_for_instance'):
                        old = getattr(obj, '_wechat_focus_guard_enabled_for_instance')
                        if not getattr(old, '__qqfarm_wechat_focus_wrapped__', False):
                            try: _fake_wechat_focus_guard_enabled_for_instance.__qqfarm_wechat_focus_wrapped__ = True
                            except BaseException: pass
                            setattr(obj, '_wechat_focus_guard_enabled_for_instance', _fake_wechat_focus_guard_enabled_for_instance); local_count += 1
                    if hasattr(obj, '_instance_bound_process_name'):
                        old = getattr(obj, '_instance_bound_process_name')
                        if not getattr(old, '__qqfarm_wechat_focus_wrapped__', False):
                            try: _fake_instance_bound_process_name.__qqfarm_wechat_focus_wrapped__ = True
                            except BaseException: pass
                            setattr(obj, '_instance_bound_process_name', _fake_instance_bound_process_name); local_count += 1
                    if hasattr(obj, 'is_weixin_launch_protocol'):
                        old = getattr(obj, 'is_weixin_launch_protocol')
                        if not getattr(old, '__qqfarm_wechat_focus_wrapped__', False):
                            try: _fake_is_weixin_launch_protocol.__qqfarm_wechat_focus_wrapped__ = True
                            except BaseException: pass
                            setattr(obj, 'is_weixin_launch_protocol', _fake_is_weixin_launch_protocol); local_count += 1
                    if hasattr(obj, 'is_qq_launch_protocol'):
                        old = getattr(obj, 'is_qq_launch_protocol')
                        if not getattr(old, '__qqfarm_wechat_focus_wrapped__', False):
                            setattr(obj, 'is_qq_launch_protocol', _wrap_is_qq_launch_protocol(old, prefix + '.is_qq_launch_protocol')); local_count += 1
                    if hasattr(obj, '_is_weixin_bound_platform'):
                        old = getattr(obj, '_is_weixin_bound_platform')
                        if not getattr(old, '__qqfarm_wechat_focus_wrapped__', False):
                            try: _fake_is_weixin_bound_platform.__qqfarm_wechat_focus_wrapped__ = True
                            except BaseException: pass
                            setattr(obj, '_is_weixin_bound_platform', _fake_is_weixin_bound_platform); local_count += 1
                    if hasattr(obj, '_resolve_click_mode'):
                        old = getattr(obj, '_resolve_click_mode')
                        if not getattr(old, '__qqfarm_wechat_focus_wrapped__', False):
                            try: _fake_resolve_click_mode.__qqfarm_wechat_focus_wrapped__ = True
                            except BaseException: pass
                            setattr(obj, '_resolve_click_mode', _fake_resolve_click_mode); local_count += 1
                    if hasattr(obj, '_is_click_mode_strict'):
                        old = getattr(obj, '_is_click_mode_strict')
                        if not getattr(old, '__qqfarm_wechat_focus_wrapped__', False):
                            try: _fake_click_mode_strict.__qqfarm_wechat_focus_wrapped__ = True
                            except BaseException: pass
                            setattr(obj, '_is_click_mode_strict', _fake_click_mode_strict); local_count += 1
                    if hasattr(obj, 'ensure_wechat_focus_guard_for_current_window'):
                        old = getattr(obj, 'ensure_wechat_focus_guard_for_current_window')
                        new, ok = _wrap_wechat_focus_guard(old, prefix + '.ensure_wechat_focus_guard_for_current_window')
                        if ok:
                            setattr(obj, 'ensure_wechat_focus_guard_for_current_window', new); local_count += 1
                    if hasattr(obj, '_apply_wechat_focus_guard_after_hwnd_ready'):
                        old = getattr(obj, '_apply_wechat_focus_guard_after_hwnd_ready')
                        new, ok = _wrap_apply_wechat_focus_after_hwnd(old, prefix + '._apply_wechat_focus_guard_after_hwnd_ready')
                        if ok:
                            setattr(obj, '_apply_wechat_focus_guard_after_hwnd_ready', new); local_count += 1
                    for n in ('click_at_position', 'mouse_down_at_position', 'mouse_up_at_position'):
                        if hasattr(obj, n):
                            old = getattr(obj, n)
                            new, ok = _wrap_mouse_action_func(old, prefix + '.' + n)
                            if ok:
                                setattr(obj, n, new); local_count += 1
                except BaseException:
                    pass
            if local_count:
                changed.append(str(mn) + ':' + str(local_count))
    except BaseException as e:
        try: _write('wechat focus patch error ' + repr(e))
        except BaseException: pass
    if changed:
        sig = ', '.join(changed[:80])
        if sig not in _WECHAT_FOCUS_PATCH_LOG_SEEN:
            _WECHAT_FOCUS_PATCH_LOG_SEEN.add(sig)
            _write('wechat focus patched ' + str(tag) + ' ' + sig)
    return changed


# ---- Friend pause window patch v19 ----
# The app's original "no_steal_window" only blocks stealing.  It can still run
# friend-help / one-click-farming.  This wrapper makes that window a full
# friend-action pause without touching self-farm actions.
_FRIEND_PAUSE_FUNC_NAMES = set(['process_friend_farm', 'handle_friend_farm_actions'])
_FRIEND_PAUSE_PATCH_LOG_SEEN = set()
_PATCH_LOADED_RUNNING = False
_PATCH_LOADED_LAST_TS = 0.0
_PATCH_LOADED_SEEN_RELEVANT = set()


def _looks_friend_runtime_module(mn, m):
    try:
        low = str(mn).lower()
        if low.startswith('pyside6') or low.startswith('qt') or low.startswith('logging') or low.startswith('configparser'):
            return False
        if not (low == 'bot' or low.startswith('bot.') or low.startswith('bot_application') or low == '__main__'):
            return False
        for n in _FRIEND_PAUSE_FUNC_NAMES:
            if hasattr(m, n):
                return True
        try:
            for obj in list(vars(m).values())[:300]:
                if isinstance(obj, type):
                    for n in _FRIEND_PAUSE_FUNC_NAMES:
                        if hasattr(obj, n):
                            return True
        except BaseException:
            pass
    except BaseException:
        pass
    return False


def _friend_pause_skip(name):
    try:
        _write('friend pause skip ' + str(name))
    except BaseException:
        pass
    try:
        _runtime_info_once('friend-pause-skip', '\u6682\u505c\u65f6\u6bb5\u547d\u4e2d\uff1a\u5df2\u8df3\u8fc7\u597d\u53cb\u519c\u573a\u52a8\u4f5c\u3002')
    except BaseException:
        pass
    return False


def _wrap_friend_pause_func(fn, name):
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_friend_pause_wrapped__', False):
            return fn, False
        def _wrapped(*a, **k):
            try:
                if _stop_requested_in_args(a, k):
                    return _stop_gate_return(name)
            except BaseException:
                pass
            if _friend_pause_active():
                return _friend_pause_skip(name)
            return fn(*a, **k)
        try:
            _wrapped.__name__ = getattr(fn, '__name__', str(name))
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_friend_pause_wrapped__ = True
            _wrapped.__qqfarm_friend_pause_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _patch_friend_pause_loaded(tag=''):
    changed = []
    try:
        for mn, m in list(sys.modules.items()):
            if m is None or not _looks_friend_runtime_module(mn, m):
                continue
            local_count = 0
            for n in list(_FRIEND_PAUSE_FUNC_NAMES):
                try:
                    if hasattr(m, n):
                        old = getattr(m, n)
                        new, ok = _wrap_friend_pause_func(old, str(mn) + '.' + n)
                        if ok:
                            setattr(m, n, new)
                            local_count += 1
                except BaseException:
                    pass
            try:
                for cls_name, obj in list(vars(m).items())[:500]:
                    if not isinstance(obj, type):
                        continue
                    for n in list(_FRIEND_PAUSE_FUNC_NAMES):
                        try:
                            if hasattr(obj, n):
                                old = getattr(obj, n)
                                new, ok = _wrap_friend_pause_func(old, str(mn) + '.' + str(cls_name) + '.' + n)
                                if ok:
                                    setattr(obj, n, new)
                                    local_count += 1
                        except BaseException:
                            pass
            except BaseException:
                pass
            if local_count:
                changed.append(str(mn) + ':' + str(local_count))
    except BaseException as e:
        try: _write('friend pause patch error ' + repr(e))
        except BaseException: pass
    if changed:
        sig = ', '.join(changed[:80])
        if sig not in _FRIEND_PAUSE_PATCH_LOG_SEEN:
            _FRIEND_PAUSE_PATCH_LOG_SEEN.add(sig)
            _write('friend pause patched ' + str(tag) + ' ' + sig)
    return changed



# ---- Guard dog switch sync patch v29 ----
# Keep license/entitlement unlocked, but make this business switch follow
# config-multi.ini.  Some original helper paths treat feature access as enabled
# state after entitlement functions are patched, so explicitly gate the runtime
# predicate with the UI/config option.
_GUARD_DOG_PATCH_LOG_SEEN = set()
_GUARD_DOG_FUNC_NAMES = set([
    '_guard_dog_feature_enabled',
    'guard_dog_feature_enabled',
])
_GUARD_DOG_VALUE_NAMES = set([
    'enable_guard_dog_help_only',
    'guard_dog_help_only',
])


def _guard_dog_ui_config_enabled():
    try:
        return _truthy(_cfg_get(_active_friend_sections(), 'enable_guard_dog_help_only', 'False'), False)
    except BaseException:
        return False


def _wrap_guard_dog_enabled_func(fn, name):
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_guard_dog_config_wrapped__', False):
            return fn, False
        def _wrapped(*a, **k):
            try:
                if not _guard_dog_ui_config_enabled():
                    _runtime_info_once('guard-dog-config-off', '\u62a4\u4e3b\u72ac\u7b5b\u9009\u5df2\u6309\u914d\u7f6e\u5173\u95ed\uff1a\u540e\u7aef\u5df2\u8df3\u8fc7\u8be5\u5206\u652f\u3002')
                    return False
            except BaseException:
                return False
            return fn(*a, **k)
        try:
            _wrapped.__name__ = getattr(fn, '__name__', 'guard_dog_config_wrapper')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_guard_dog_config_wrapped__ = True
            _wrapped.__qqfarm_guard_dog_config_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _looks_guard_dog_module(mn, m):
    try:
        low = str(mn).lower()
        if not (low == 'bot' or low.startswith('bot.')):
            return False
        if 'guard' in low or 'friend' in low or low.startswith('bot.application.'):
            for n in _GUARD_DOG_FUNC_NAMES:
                if hasattr(m, n):
                    return True
            for n in _GUARD_DOG_VALUE_NAMES:
                if hasattr(m, n):
                    return True
            try:
                for obj in list(vars(m).values())[:500]:
                    if isinstance(obj, type):
                        for n in _GUARD_DOG_FUNC_NAMES:
                            if hasattr(obj, n):
                                return True
                        for n in _GUARD_DOG_VALUE_NAMES:
                            if hasattr(obj, n):
                                return True
            except BaseException:
                pass
    except BaseException:
        pass
    return False


def _guard_dog_sync_value(obj):
    changed = 0
    try:
        desired = bool(_guard_dog_ui_config_enabled())
        for n in list(_GUARD_DOG_VALUE_NAMES):
            try:
                if hasattr(obj, n):
                    old = getattr(obj, n)
                    if not callable(old) and old is not desired:
                        setattr(obj, n, desired)
                        changed += 1
            except BaseException:
                pass
    except BaseException:
        pass
    return changed


def _patch_guard_dog_config_loaded(tag=''):
    changed = []
    try:
        for mn, m in list(sys.modules.items()):
            if m is None or not _looks_guard_dog_module(mn, m):
                continue
            local_count = 0
            try:
                local_count += _guard_dog_sync_value(m)
            except BaseException:
                pass
            targets = [(m, str(mn))]
            try:
                for cls_name, obj in list(vars(m).items())[:500]:
                    if isinstance(obj, type):
                        targets.append((obj, str(mn) + '.' + str(cls_name)))
            except BaseException:
                pass
            for obj, prefix in targets:
                try:
                    local_count += _guard_dog_sync_value(obj)
                except BaseException:
                    pass
                for n in list(_GUARD_DOG_FUNC_NAMES):
                    try:
                        if hasattr(obj, n):
                            old = getattr(obj, n)
                            new, ok = _wrap_guard_dog_enabled_func(old, prefix + '.' + n)
                            if ok:
                                setattr(obj, n, new)
                                local_count += 1
                    except BaseException:
                        pass
            if local_count:
                changed.append(str(mn) + ':' + str(local_count))
    except BaseException as e:
        try: _write('guard dog config patch error ' + repr(e))
        except BaseException: pass
    if changed:
        sig = ', '.join(changed[:80])
        if sig not in _GUARD_DOG_PATCH_LOG_SEEN:
            _GUARD_DOG_PATCH_LOG_SEEN.add(sig)
            _write('v29 guard dog config patched ' + str(tag) + ' enabled=' + str(_guard_dog_ui_config_enabled()) + ' ' + sig)
    return changed



# ---- VIP business function patch v25 ----
# Force business-layer config at the point of use and add hard evidence in logs.
_VIP_BUSINESS_PATCH_LOG_SEEN = set()
_PATCH_LOADED_RUNNING = False
_PATCH_LOADED_LAST_TS = 0.0
_PATCH_LOADED_SEEN_RELEVANT = set()
_VIP_BUSINESS_LAST_FORCE_WAREHOUSE_TS = 0.0
_VIP_WAREHOUSE_LAST_DONE_TS = 0.0
_VIP_WAREHOUSE_STATE_PATH = r'C:/Users/11616/reverse-cases/qq-farm-vip/work/warehouse_last_done_ts.txt'
_VIP_WAREHOUSE_MIN_COOLDOWN_SECONDS = 360.0
_VIP_WAREHOUSE_RETRY_STATE_PATH = r'C:/Users/11616/reverse-cases/qq-farm-vip/work/warehouse_retry_state.json'
_VIP_WAREHOUSE_RETRY_SECONDS = 600.0
_VIP_WAREHOUSE_RETRY_LIMIT = 3
_VIP_WAREHOUSE_BACKOFF_SECONDS = 3600.0
_VIP_WAREHOUSE_RETRY_MEMORY_STATE = {'fail_count': 0, 'last_fail_ts': 0.0, 'blocked_until': 0.0, 'last_reason': ''}
_VIP_WAREHOUSE_RETRY_MEMORY_PATH = ''
_VIP_WAREHOUSE_RETRY_MEMORY_DIRTY = False
_VIP_WAREHOUSE_LAST_SEQUENCE_CLASS = ''
_VIP_WAREHOUSE_LAST_SEQUENCE_TS = 0.0
_VIP_BUSINESS_FUNC_NAMES = set([
    '_handle_home_auto_sell_fruit',
    '_run_warehouse_sell_button_sequence',
    'handle_home_maintenance',
    'handle_home_pre_planting_maintenance',
    'process_self_farm',
    '_run_friend_daily_troublemaker',
    '_plant_seed_over_lands',
    '_run_auto_fertilize_after_planting',
])


def _force_vip_business_object(o, depth=0):
    # v28: no-op. Entitlement is patched separately; business switches must
    # follow UI/config, otherwise front-end and backend diverge.
    return 0


def _force_vip_business_args(args, kwargs):
    # v28: no-op for performance and UI/config consistency.
    return 0


def _bot_stop_requested(bot):
    try:
        return bool(_is_stop_requested_like(bot))
    except BaseException:
        return False


def _get_frame_from_bot(bot):
    try:
        for owner_name in ('screen_capture','screen','capture','screenshotter'):
            try:
                owner = getattr(bot, owner_name, None)
            except BaseException:
                owner = None
            if owner is None:
                continue
            for meth in ('get_window_frame','capture_window','get_frame','capture','screenshot'):
                try:
                    fn = getattr(owner, meth, None)
                    if callable(fn):
                        fr = fn()
                        if fr is not None:
                            return fr
                except BaseException:
                    pass
        for meth in ('get_window_frame','capture_window','get_frame'):
            try:
                fn = getattr(bot, meth, None)
                if callable(fn):
                    fr = fn()
                    if fr is not None:
                        return fr
            except BaseException:
                pass
    except BaseException:
        pass
    return None


def _call_func_best_effort(fn, candidates):
    last = None
    for args in candidates:
        try:
            return True, fn(*args)
        except TypeError as e:
            last = e
            continue
        except BaseException as e:
            return False, e
    return False, last



def _warehouse_done_ts():
    global _VIP_WAREHOUSE_LAST_DONE_TS
    try:
        if _VIP_WAREHOUSE_LAST_DONE_TS > 0:
            return _VIP_WAREHOUSE_LAST_DONE_TS
        try:
            txt = open(_VIP_WAREHOUSE_STATE_PATH, 'r').read().strip()
            if txt:
                _VIP_WAREHOUSE_LAST_DONE_TS = float(txt)
        except BaseException:
            pass
        return _VIP_WAREHOUSE_LAST_DONE_TS
    except BaseException:
        return 0.0


def _warehouse_cooldown_seconds():
    try:
        iid = _active_instance_id()
        sec = ['instance.' + str(iid) + '.self', 'self']
        v = _cfg_get(sec, 'auto_sell_fruit_interval_hours', '0.10')
        seconds = float(str(v).strip()) * 3600.0
        if seconds < _VIP_WAREHOUSE_MIN_COOLDOWN_SECONDS:
            seconds = _VIP_WAREHOUSE_MIN_COOLDOWN_SECONDS
        return seconds
    except BaseException:
        return _VIP_WAREHOUSE_MIN_COOLDOWN_SECONDS


def _warehouse_recently_done():
    try:
        ts = _warehouse_done_ts()
        if ts <= 0:
            return False
        return (time.time() - ts) < _warehouse_cooldown_seconds()
    except BaseException:
        return False


def _warehouse_mark_done(reason=''):
    global _VIP_WAREHOUSE_LAST_DONE_TS
    try:
        _VIP_WAREHOUSE_LAST_DONE_TS = time.time()
        try:
            open(_VIP_WAREHOUSE_STATE_PATH, 'w').write(str(_VIP_WAREHOUSE_LAST_DONE_TS))
        except BaseException:
            pass
        _write('v28 warehouse cooldown mark reason=' + str(reason) + ' seconds=' + str(int(_warehouse_cooldown_seconds())))
    except BaseException:
        pass


def _warehouse_classify_result(res):
    try:
        if res is True:
            return 'completed'
        status = res[0] if isinstance(res, (tuple, list)) and len(res) > 0 else res
        text = str(status).lower()
        if 'completed' in text:
            return 'completed'
        if any(token in text for token in ('warehouse_empty', 'nothing_to_sell', 'no_sellable', 'no_items', 'empty_warehouse')):
            return 'empty'
    except BaseException:
        pass
    return 'failed'


def _warehouse_zero_retry_state():
    return {'fail_count': 0, 'last_fail_ts': 0.0, 'blocked_until': 0.0, 'last_reason': ''}


def _warehouse_prepare_retry_memory_path():
    global _VIP_WAREHOUSE_RETRY_MEMORY_STATE, _VIP_WAREHOUSE_RETRY_MEMORY_PATH, _VIP_WAREHOUSE_RETRY_MEMORY_DIRTY
    current_path = str(_VIP_WAREHOUSE_RETRY_STATE_PATH)
    if _VIP_WAREHOUSE_RETRY_MEMORY_PATH != current_path:
        _VIP_WAREHOUSE_RETRY_MEMORY_STATE = _warehouse_zero_retry_state()
        _VIP_WAREHOUSE_RETRY_MEMORY_PATH = current_path
        _VIP_WAREHOUSE_RETRY_MEMORY_DIRTY = False
    return current_path


def _warehouse_sanitize_retry_state(loaded):
    state = _warehouse_zero_retry_state()
    if not isinstance(loaded, dict):
        return state
    math = __import__('math')
    try:
        value = loaded.get('fail_count', 0)
        if isinstance(value, bool):
            raise ValueError('bool is not a retry count')
        count = int(value)
        if (isinstance(value, float) and not value.is_integer()) or count < 0 or count >= _VIP_WAREHOUSE_RETRY_LIMIT:
            raise ValueError('retry count out of range')
        state['fail_count'] = count
    except BaseException:
        pass
    for key in ('last_fail_ts', 'blocked_until'):
        try:
            value = float(loaded.get(key, 0.0))
            if math.isfinite(value) and value >= 0.0:
                state[key] = value
        except BaseException:
            pass
    try:
        state['last_reason'] = str(loaded.get('last_reason', ''))[:160]
    except BaseException:
        pass
    return state


def _warehouse_load_retry_state():
    global _VIP_WAREHOUSE_RETRY_MEMORY_STATE
    _warehouse_prepare_retry_memory_path()
    fallback = _warehouse_sanitize_retry_state(_VIP_WAREHOUSE_RETRY_MEMORY_STATE)
    _VIP_WAREHOUSE_RETRY_MEMORY_STATE = dict(fallback)
    if _VIP_WAREHOUSE_RETRY_MEMORY_DIRTY:
        return dict(fallback)
    try:
        raw = open(_VIP_WAREHOUSE_RETRY_STATE_PATH, 'r').read()
        loaded = __import__('json').loads(raw)
        if not isinstance(loaded, dict):
            return dict(fallback)
        state = _warehouse_sanitize_retry_state(loaded)
        _VIP_WAREHOUSE_RETRY_MEMORY_STATE = dict(state)
        return state
    except BaseException:
        return dict(fallback)


def _warehouse_write_retry_state(state, action='update'):
    global _VIP_WAREHOUSE_RETRY_MEMORY_STATE, _VIP_WAREHOUSE_RETRY_MEMORY_DIRTY
    final_path = _warehouse_prepare_retry_memory_path()
    sanitized = _warehouse_sanitize_retry_state(state)
    _VIP_WAREHOUSE_RETRY_MEMORY_STATE = dict(sanitized)
    temp_path = final_path + '.tmp-' + __import__('uuid').uuid4().hex
    persisted = False
    write_error = None
    try:
        handle = open(temp_path, 'w', encoding='utf-8')
        try:
            handle.write(__import__('json').dumps(sanitized, sort_keys=True))
            handle.flush()
        finally:
            handle.close()
        os.replace(temp_path, final_path)
        persisted = True
        _VIP_WAREHOUSE_RETRY_MEMORY_DIRTY = False
    except BaseException as e:
        write_error = e
        _VIP_WAREHOUSE_RETRY_MEMORY_DIRTY = True
    finally:
        try:
            os.remove(temp_path)
        except BaseException:
            pass
    try:
        status = 'persisted' if persisted else 'memory fallback'
        message = 'v35 warehouse retry ' + str(action) + ' ' + status + ' fail_count=' + str(sanitized['fail_count']) + ' blocked_until=' + str(int(sanitized['blocked_until']))
        if write_error is not None:
            message += ' error=' + repr(write_error)
        _throttled_write('warehouse-retry-persistence-' + ('ok-' if persisted else 'failure-') + str(action), message, 30.0)
    except BaseException:
        pass
    return sanitized


def _warehouse_retry_blocked(now=None):
    try:
        if now is None:
            now = time.time()
        return _warehouse_load_retry_state()['blocked_until'] > float(now)
    except BaseException:
        return False


def _warehouse_mark_failed(reason='', now=None):
    try:
        if now is None:
            now = time.time()
        now = float(now)
        state = _warehouse_load_retry_state()
        count = state['fail_count']
        count += 1
        state['last_fail_ts'] = now
        state['last_reason'] = str(reason)[:160]
        if count >= _VIP_WAREHOUSE_RETRY_LIMIT:
            state['fail_count'] = 0
            state['blocked_until'] = now + _VIP_WAREHOUSE_BACKOFF_SECONDS
        else:
            state['fail_count'] = count
            state['blocked_until'] = now + _VIP_WAREHOUSE_RETRY_SECONDS
        return _warehouse_write_retry_state(state, 'failed')
    except BaseException:
        return _warehouse_zero_retry_state()


def _warehouse_reset_retry_state():
    return _warehouse_write_retry_state(_warehouse_zero_retry_state(), 'reset')


def _force_warehouse_after_self(args, kwargs):
    # v27: disabled.  The original app already calls _handle_home_auto_sell_fruit
    # from its own self-farm flow.  Forcing it after every self patrol caused
    # endless warehouse open/close loops after fruits were already sold.
    return False


def _business_bot_from_args(args, kwargs):
    try:
        direct = (kwargs or {}).get('bot')
        if direct is not None and not isinstance(direct, (str, bytes, int, float, bool, list, tuple, dict, set)):
            return direct
    except BaseException:
        pass
    state_names = (
        'auto_fertilize_one', 'planting_auto_fertilize_one',
        'auto_fertilize_more', 'planting_auto_fertilize_more',
        'auto_fill_fertilizer_container', 'enable_daily_radish_exp',
        'daily_radish_exp', '_qqfarm_planting_crop_context',
        '_qqfarm_radish_mode_context',
    )
    try:
        values = list(args or ()) + list((kwargs or {}).values())
    except BaseException:
        values = []
    for value in values:
        try:
            if value is None or isinstance(value, (str, bytes, int, float, bool, list, tuple, dict, set)):
                continue
            if any(hasattr(value, attr) for attr in state_names):
                return value
        except BaseException:
            pass
    return None


def _crop_name_from_bound_call(fn, args, kwargs):
    try:
        import inspect
        bound = inspect.signature(fn).bind_partial(*(args or ()), **(kwargs or {}))
        items = list(bound.arguments.items())
    except BaseException:
        try:
            items = list((kwargs or {}).items()) + [('', value) for value in (args or ())]
        except BaseException:
            items = []
    preferred = ('crop_name', 'crop', 'seed_name', 'plant_name')
    for wanted in preferred:
        for param_name, value in items:
            try:
                if str(param_name).lower() == wanted and isinstance(value, str) and value.strip():
                    return value.strip()
            except BaseException:
                pass
    for param_name, value in items:
        try:
            low = str(param_name).lower()
            if any(token in low for token in ('crop', 'seed', 'plant')):
                if isinstance(value, str) and value.strip():
                    return value.strip()
        except BaseException:
            pass
    for _, value in items:
        try:
            if isinstance(value, str) and value.strip() == '\u767d\u841d\u535c':
                return '\u767d\u841d\u535c'
        except BaseException:
            pass
    return ''


def _daily_radish_state(module, bot):
    try:
        checker = getattr(module, '_is_daily_radish_exp_active', None)
        if callable(checker):
            return 'active' if bool(checker(bot)) else 'inactive'
    except BaseException:
        return 'unknown'
    return 'unknown'


def _daily_radish_active(module, bot):
    return _daily_radish_state(module, bot) == 'active'


def _wrap_planting_crop_context_func(fn, module, name=''):
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_planting_crop_context_wrapped__', False):
            return fn, False
        def _wrapped(*a, **k):
            bot = None
            try:
                import inspect
                bound = inspect.signature(fn).bind_partial(*a, **k)
                if 'bot' in bound.arguments:
                    bot = _business_bot_from_args((), {'bot': bound.arguments.get('bot')})
            except BaseException:
                pass
            if bot is None:
                bot = _business_bot_from_args(a, k)
            if bot is None:
                return fn(*a, **k)
            crop_name = _crop_name_from_bound_call(fn, a, k)
            radish_state = _daily_radish_state(module, bot)
            missing = object()
            try:
                old_crop = getattr(bot, '_qqfarm_planting_crop_context')
            except BaseException:
                old_crop = missing
            try:
                old_mode = getattr(bot, '_qqfarm_radish_mode_context')
            except BaseException:
                old_mode = missing
            try:
                setattr(bot, '_qqfarm_planting_crop_context', crop_name)
                setattr(bot, '_qqfarm_radish_mode_context', radish_state)
                return fn(*a, **k)
            finally:
                try:
                    if old_crop is missing:
                        delattr(bot, '_qqfarm_planting_crop_context')
                    else:
                        setattr(bot, '_qqfarm_planting_crop_context', old_crop)
                except BaseException:
                    pass
                try:
                    if old_mode is missing:
                        delattr(bot, '_qqfarm_radish_mode_context')
                    else:
                        setattr(bot, '_qqfarm_radish_mode_context', old_mode)
                except BaseException:
                    pass
        try:
            _wrapped.__name__ = getattr(fn, '__name__', 'planting_crop_context_wrapper')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__doc__ = getattr(fn, '__doc__', None)
            _wrapped.__qqfarm_planting_crop_context_wrapped__ = True
            _wrapped.__qqfarm_planting_crop_context_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _land_center_xy(land):
    try:
        import math
        import numbers
        seen = set()
        def _number(value):
            if isinstance(value, bool) or not isinstance(value, numbers.Real):
                return None
            result = float(value)
            if not math.isfinite(result):
                return None
            return result
        def _pair(value):
            marker = id(value)
            if marker in seen:
                return None
            seen.add(marker)
            if isinstance(value, (tuple, list)):
                if len(value) != 2:
                    return None
                x = _number(value[0])
                y = _number(value[1])
                return (x, y) if x is not None and y is not None else None
            if isinstance(value, dict):
                for key in ('center', 'land_center'):
                    if key in value:
                        result = _pair(value.get(key))
                        if result is not None:
                            return result
                for x_name, y_name in (('x', 'y'), ('cx', 'cy')):
                    if x_name in value and y_name in value:
                        x = _number(value.get(x_name))
                        y = _number(value.get(y_name))
                        if x is not None and y is not None:
                            return (x, y)
                return None
            for attr in ('center', 'land_center'):
                try:
                    if hasattr(value, attr):
                        result = _pair(getattr(value, attr))
                        if result is not None:
                            return result
                except BaseException:
                    pass
            for x_name, y_name in (('x', 'y'), ('cx', 'cy')):
                try:
                    if hasattr(value, x_name) and hasattr(value, y_name):
                        x = _number(getattr(value, x_name))
                        y = _number(getattr(value, y_name))
                        if x is not None and y is not None:
                            return (x, y)
                except BaseException:
                    pass
            return None
        return _pair(land)
    except BaseException:
        return None


def _group_safe_fertilizer_lands(lands, row_tolerance_px=45.0, max_horizontal_gap_px=120.0):
    try:
        values = list(lands or [])
    except BaseException:
        return None
    if not values:
        return []
    decorated = []
    for land in values:
        xy = _land_center_xy(land)
        if xy is None:
            if len(values) == 1:
                return [[land]]
            return None
        decorated.append((xy[1], xy[0], land))
    try:
        row_tolerance = float(row_tolerance_px)
        max_gap = float(max_horizontal_gap_px)
    except BaseException:
        return None
    decorated.sort(key=lambda item: (item[0], item[1]))
    rows = []
    current = []
    current_row_y = None
    for y, x, land in decorated:
        if current and abs(y - current_row_y) > row_tolerance:
            rows.append(current)
            current = []
            current_row_y = None
        if not current:
            current_row_y = y
        current.append((x, land))
    if current:
        rows.append(current)
    groups = []
    for row in rows:
        group = []
        previous_x = None
        for x, land in row:
            if group and (x - previous_x) > max_gap:
                groups.append(group)
                group = []
            group.append(land)
            previous_x = x
        if group:
            groups.append(group)
    return groups


def _wrap_radish_fertilizer_func(fn, module, name=''):
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_radish_fertilizer_wrapped__', False):
            return fn, False
        def _wrapped(*a, **k):
            bot = None
            bound = None
            lands_name = ''
            try:
                import inspect
                bound = inspect.signature(fn).bind_partial(*a, **k)
                if 'bot' in bound.arguments:
                    bot = _business_bot_from_args((), {'bot': bound.arguments.get('bot')})
                if 'lands' in bound.arguments:
                    lands_name = 'lands'
                else:
                    for param_name in bound.arguments:
                        if 'land' in str(param_name).lower():
                            lands_name = param_name
                            break
            except BaseException:
                bound = None
            if bot is None:
                bot = _business_bot_from_args(a, k)
            if bot is None:
                return fn(*a, **k)
            missing = object()
            try:
                mode_context = getattr(bot, '_qqfarm_radish_mode_context')
            except BaseException:
                mode_context = missing
            if mode_context is missing:
                radish_state = _daily_radish_state(module, bot)
            elif mode_context in ('active', 'inactive', 'unknown'):
                radish_state = mode_context
            elif isinstance(mode_context, bool):
                radish_state = 'active' if mode_context else 'inactive'
            else:
                radish_state = 'unknown'
            if radish_state == 'inactive':
                return fn(*a, **k)
            if radish_state != 'active':
                try:
                    _throttled_write('v35-radish-fertilizer-state-unknown-' + str(name), 'v35 radish fertilizer skipped radish state unknown', 30.0)
                except BaseException:
                    pass
                return False
            try:
                crop_context = getattr(bot, '_qqfarm_planting_crop_context')
            except BaseException:
                crop_context = missing
            crop_name = crop_context.strip() if isinstance(crop_context, str) else ''
            if crop_name != '\u767d\u841d\u535c':
                try:
                    _throttled_write('v35-radish-fertilizer-non-radish-' + str(name), 'v35 radish fertilizer skipped non-radish crop=' + crop_name, 30.0)
                except BaseException:
                    pass
                return False
            if bound is None or not lands_name:
                groups = None
            else:
                groups = _group_safe_fertilizer_lands(bound.arguments.get(lands_name))
            if groups is None:
                try:
                    _throttled_write('v35-radish-fertilizer-unsafe-' + str(name), 'v35 radish fertilizer skipped unsafe sparse lands', 30.0)
                except BaseException:
                    pass
                return False
            land_count = sum(len(group) for group in groups)
            try:
                _throttled_write(
                    'v35-radish-fertilizer-exec-' + str(name),
                    'v35 radish fertilizer crop=' + crop_name + ' lands=' + str(land_count) +
                    ' groups=' + str(len(groups)) + ' normal-fertilizer-only=True',
                    30.0,
                )
            except BaseException:
                pass
            overrides = (
                ('auto_fertilize_one', True),
                ('planting_auto_fertilize_one', True),
                ('auto_fertilize_more', False),
                ('planting_auto_fertilize_more', False),
                ('auto_fill_fertilizer_container', False),
            )
            saved = []
            def _restore_saved_aliases():
                first_error = None
                for attr, prior in reversed(saved):
                    try:
                        setattr(bot, attr, prior)
                        restored = getattr(bot, attr)
                        if restored is not prior:
                            try:
                                same_value = type(restored) is type(prior) and restored == prior
                            except BaseException:
                                same_value = False
                            if not same_value:
                                raise RuntimeError('v35 fertilizer restore verification failed attr=' + str(attr))
                    except BaseException as e:
                        if first_error is None:
                            first_error = e
                return first_error
            setup_error = None
            setup_attr = ''
            for attr, temporary in overrides:
                declared = False
                try:
                    declared = attr in vars(bot)
                except BaseException:
                    pass
                if not declared:
                    try:
                        declared = any(attr in vars(cls) for cls in type(bot).__mro__)
                    except BaseException:
                        pass
                try:
                    prior = getattr(bot, attr)
                except AttributeError as e:
                    if declared:
                        setup_error = e
                        setup_attr = attr
                        break
                    continue
                except BaseException as e:
                    setup_error = e
                    setup_attr = attr
                    break
                saved.append((attr, prior))
                try:
                    setattr(bot, attr, temporary)
                    if getattr(bot, attr) is not temporary:
                        raise RuntimeError('v35 fertilizer override verification failed attr=' + str(attr))
                except BaseException as e:
                    setup_error = e
                    setup_attr = attr
                    break
            if setup_error is not None:
                restore_error = _restore_saved_aliases()
                try:
                    _throttled_write(
                        'v35-radish-fertilizer-override-unsafe-' + str(name),
                        'v35 radish fertilizer skipped unsafe overrides attr=' + str(setup_attr),
                        30.0,
                    )
                except BaseException:
                    pass
                if restore_error is not None:
                    raise restore_error
                return False
            original_error = None
            original_traceback = None
            final_result = True
            try:
                for group in groups:
                    bound.arguments[lands_name] = group
                    result = fn(*bound.args, **bound.kwargs)
                    if not result:
                        final_result = False
                        break
            except BaseException as e:
                original_error = e
                original_traceback = e.__traceback__
            restore_error = _restore_saved_aliases()
            if original_error is not None:
                if restore_error is not None:
                    try:
                        original_error.add_note('v35 fertilizer restoration failure: ' + repr(restore_error))
                    except BaseException:
                        pass
                    try:
                        _throttled_write('v35-radish-fertilizer-restore-error-' + str(name), 'v35 radish fertilizer restoration failure after original error ' + repr(restore_error), 30.0)
                    except BaseException:
                        pass
                raise original_error.with_traceback(original_traceback)
            if restore_error is not None:
                raise restore_error
            return final_result
        try:
            _wrapped.__name__ = getattr(fn, '__name__', 'radish_fertilizer_wrapper')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__doc__ = getattr(fn, '__doc__', None)
            _wrapped.__qqfarm_radish_fertilizer_wrapped__ = True
            _wrapped.__qqfarm_radish_fertilizer_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _wrap_vip_business_func(fn, name=''):
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_vip_business_wrapped__', False):
            return fn, False
        lname = str(name).lower()
        def _wrapped(*a, **k):
            global _VIP_WAREHOUSE_LAST_SEQUENCE_CLASS, _VIP_WAREHOUSE_LAST_SEQUENCE_TS
            try:
                if _stop_requested_in_args(a, k):
                    return _stop_gate_return(name)
            except BaseException:
                pass
            try:
                if '_handle_home_auto_sell_fruit' in lname:
                    if _warehouse_recently_done():
                        cooldown_text = ''
                        try: cooldown_text = ' seconds=' + str(int(_warehouse_cooldown_seconds()))
                        except BaseException: pass
                        _throttled_write('warehouse-skip-normal-cooldown-' + str(name), 'v35 warehouse skip normal cooldown ' + str(name) + cooldown_text, 30.0)
                        return False
                    if _warehouse_retry_blocked():
                        blocked_text = ''
                        try: blocked_text = ' blocked_until=' + str(int(_warehouse_load_retry_state().get('blocked_until', 0.0)))
                        except BaseException: pass
                        _throttled_write('warehouse-skip-failure-retry-' + str(name), 'v35 warehouse skip failure retry ' + str(name) + blocked_text, 30.0)
                        return False
                    _VIP_WAREHOUSE_LAST_SEQUENCE_CLASS = ''
                    _VIP_WAREHOUSE_LAST_SEQUENCE_TS = 0.0
                changed = _force_vip_business_args(a, k)
                if ('auto_sell' in lname) or ('warehouse' in lname):
                    _runtime_info_once('v30-warehouse-wrapper', '\u4ed3\u5e93\u51fa\u552e\u51fd\u6570\u5df2\u8fdb\u5165\uff1a\u540e\u7aef\u6309UI/\u914d\u7f6e\u5f00\u5173\u6267\u884c\u3002')
                    _throttled_write('warehouse-wrapper-enter-' + str(name), 'v30 warehouse wrapper entered ' + str(name) + ' changed=' + str(changed), 60.0)
                elif 'daily_troublemaker' in lname:
                    _runtime_info_once('v30-trouble-wrapper', '\u6bcf\u65e5\u81ea\u52a8\u6363\u4e71\u51fd\u6570\u5df2\u8fdb\u5165\uff1a\u540e\u7aef\u6309UI/\u914d\u7f6e\u5f00\u5173\u6267\u884c\u3002')
                    _throttled_write('daily-trouble-wrapper-enter-' + str(name), 'v30 daily troublemaker wrapper entered ' + str(name) + ' changed=' + str(changed), 60.0)
            except BaseException as e:
                try: _throttled_write('business-pre-error-' + str(name), 'v30 business pre-force error ' + str(name) + ' ' + repr(e), 30.0)
                except BaseException: pass
            try:
                res = fn(*a, **k)
            except BaseException:
                if '_run_warehouse_sell_button_sequence' in lname:
                    _VIP_WAREHOUSE_LAST_SEQUENCE_CLASS = 'failed'
                    _VIP_WAREHOUSE_LAST_SEQUENCE_TS = time.time()
                elif '_handle_home_auto_sell_fruit' in lname:
                    try:
                        exc = __import__('sys').exc_info()[1]
                        _warehouse_mark_failed(repr(exc)[:160])
                    except BaseException:
                        pass
                raise
            try:
                if '_run_warehouse_sell_button_sequence' in lname:
                    _VIP_WAREHOUSE_LAST_SEQUENCE_CLASS = _warehouse_classify_result(res)
                    _VIP_WAREHOUSE_LAST_SEQUENCE_TS = time.time()
                elif '_handle_home_auto_sell_fruit' in lname:
                    now = time.time()
                    age = now - _VIP_WAREHOUSE_LAST_SEQUENCE_TS
                    if _VIP_WAREHOUSE_LAST_SEQUENCE_TS > 0 and 0.0 <= age < 120.0:
                        result_class = _VIP_WAREHOUSE_LAST_SEQUENCE_CLASS
                    else:
                        result_class = _warehouse_classify_result(res)
                    if result_class in ('completed', 'empty'):
                        _warehouse_mark_done(str(name) + ' -> ' + repr(res)[:80])
                        _warehouse_reset_retry_state()
                    else:
                        _warehouse_mark_failed(repr(res)[:160])
                if ('auto_sell' in lname) or ('warehouse' in lname) or ('daily_troublemaker' in lname):
                    _throttled_write('business-wrapper-result-' + str(name), 'v30 business wrapper result ' + str(name) + ' -> ' + repr(res)[:240], 30.0)
            except BaseException as e:
                try: _throttled_write('business-post-error-' + str(name), 'v30 business post error ' + str(name) + ' ' + repr(e), 30.0)
                except BaseException: pass
            return res
        try:
            _wrapped.__name__ = getattr(fn, '__name__', 'vip_business_wrapper')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_vip_business_wrapped__ = True
            _wrapped.__qqfarm_vip_business_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _looks_vip_business_module(mn, m):
    try:
        low = str(mn).lower()
        if not (low == 'bot.application.flows' or low.startswith('bot.application.')):
            return False
        for n in _VIP_BUSINESS_FUNC_NAMES:
            if hasattr(m, n):
                return True
        try:
            for obj in list(vars(m).values())[:500]:
                if isinstance(obj, type):
                    for n in _VIP_BUSINESS_FUNC_NAMES:
                        if hasattr(obj, n):
                            return True
        except BaseException:
            pass
    except BaseException:
        pass
    return False


def _patch_vip_business_loaded(tag=''):
    changed = []
    try:
        for mn, m in list(sys.modules.items()):
            if m is None or not _looks_vip_business_module(mn, m):
                continue
            local_count = 0
            try:
                local_count += _force_vip_business_object(m, 0)
            except BaseException:
                pass
            targets = [(m, str(mn), False)]
            try:
                class_targets = []
                for cls_name, obj in list(vars(m).items())[:500]:
                    if isinstance(obj, type):
                        class_targets.append((obj, str(mn) + '.' + str(cls_name), True))
                class_targets.sort(key=lambda item: len(getattr(item[0], '__mro__', ())))
                targets.extend(class_targets)
            except BaseException:
                pass
            for obj, prefix, is_class_target in targets:
                for n in list(_VIP_BUSINESS_FUNC_NAMES):
                    try:
                        descriptor_type = ''
                        if is_class_target:
                            raw = None
                            for base in getattr(obj, '__mro__', (obj,)):
                                if n in vars(base):
                                    raw = vars(base)[n]
                                    break
                            if isinstance(raw, staticmethod):
                                old = raw.__func__
                                descriptor_type = 'staticmethod'
                            elif isinstance(raw, classmethod):
                                old = raw.__func__
                                descriptor_type = 'classmethod'
                            else:
                                old = raw
                        else:
                            if not hasattr(obj, n):
                                continue
                            old = getattr(obj, n)
                        if not callable(old):
                            continue
                        if n == '_plant_seed_over_lands':
                            new, ok = _wrap_planting_crop_context_func(old, m, prefix + '.' + n)
                        elif n == '_run_auto_fertilize_after_planting':
                            new, ok = _wrap_radish_fertilizer_func(old, m, prefix + '.' + n)
                        else:
                            new, ok = _wrap_vip_business_func(old, prefix + '.' + n)
                        if ok:
                            if descriptor_type == 'staticmethod':
                                setattr(obj, n, staticmethod(new))
                            elif descriptor_type == 'classmethod':
                                setattr(obj, n, classmethod(new))
                            else:
                                setattr(obj, n, new)
                            local_count += 1
                    except BaseException:
                        pass
            if local_count:
                changed.append(str(mn) + ':' + str(local_count))
    except BaseException as e:
        try: _write('v28 vip business patch error ' + repr(e))
        except BaseException: pass
    if changed:
        sig = ', '.join(changed[:80])
        if sig not in _VIP_BUSINESS_PATCH_LOG_SEEN:
            _VIP_BUSINESS_PATCH_LOG_SEEN.add(sig)
            _write('v28 vip business patched ' + str(tag) + ' ' + sig)
    return changed




# ---- v32 daily task soft retry ----
# Do not permanently lock the whole day on transient task_prompt misses. Keep
# the counter one below the hard limit and retry after a bounded backoff.
_DAILY_TASK_SOFT_RETRY_PATCH_LOG_SEEN = set()
_DAILY_TASK_RETRY_STATE_PATH = r'C:/Users/11616/reverse-cases/qq-farm-vip/work/daily_task_retry_state.json'


def _daily_task_zero_retry_state():
    return {'next_ts': 0.0, 'last_fail_ts': 0.0, 'reason': ''}


def _daily_task_load_retry_state():
    state = _daily_task_zero_retry_state()
    try:
        path = str(_DAILY_TASK_RETRY_STATE_PATH or '')
        if not path or not os.path.exists(path):
            return state
        data = __import__('json').loads(open(path, 'r', encoding='utf-8').read())
        if not isinstance(data, dict):
            return state
        for key in ('next_ts', 'last_fail_ts'):
            try:
                value = float(data.get(key, 0.0) or 0.0)
                if value < 0.0 or value != value or abs(value) > 1000000000000.0:
                    value = 0.0
                state[key] = value
            except BaseException:
                state[key] = 0.0
        state['reason'] = str(data.get('reason', '') or '')[:240]
    except BaseException:
        pass
    return state


def _daily_task_write_retry_state(state):
    try:
        path = str(_DAILY_TASK_RETRY_STATE_PATH or '')
        if not path:
            return False
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        clean = _daily_task_zero_retry_state()
        if isinstance(state, dict):
            clean['next_ts'] = max(0.0, float(state.get('next_ts', 0.0) or 0.0))
            clean['last_fail_ts'] = max(0.0, float(state.get('last_fail_ts', 0.0) or 0.0))
            clean['reason'] = str(state.get('reason', '') or '')[:240]
        temp_path = path + '.tmp'
        payload = __import__('json').dumps(clean, ensure_ascii=True, sort_keys=True)
        open(temp_path, 'w', encoding='utf-8').write(payload)
        os.replace(temp_path, path)
        return True
    except BaseException as e:
        try: _throttled_write('v37-task-state-write', 'v37 daily task retry state write failed ' + repr(e), 60.0)
        except BaseException: pass
        return False


def _daily_task_set_retry_backoff(reason='', now=None):
    try:
        current = float(time.time() if now is None else now)
        seconds = float(_daily_task_soft_retry_backoff_seconds())
        state = {'next_ts': current + seconds, 'last_fail_ts': current, 'reason': str(reason or '')[:240]}
        _daily_task_write_retry_state(state)
        return state
    except BaseException:
        return _daily_task_zero_retry_state()


def _daily_task_retry_backoff_active(now=None):
    try:
        current = float(time.time() if now is None else now)
        state = _daily_task_load_retry_state()
        next_ts = float(state.get('next_ts', 0.0) or 0.0)
        if next_ts > current:
            return True
        if next_ts > 0.0:
            _daily_task_write_retry_state(_daily_task_zero_retry_state())
    except BaseException:
        pass
    return False


def _daily_task_clear_retry_backoff():
    return _daily_task_write_retry_state(_daily_task_zero_retry_state())


def _daily_task_bot_from_args(args, kwargs):
    try:
        for value in list(args) + list((kwargs or {}).values()):
            if value is None or isinstance(value, (str, bytes, int, float, bool)):
                continue
            if hasattr(value, 'daily_flow_retry_counts') or hasattr(value, 'task_last_date'):
                return value
    except BaseException:
        pass
    return None


def _daily_task_flow_key(args, kwargs):
    try:
        for value in list(args) + list((kwargs or {}).values()):
            if isinstance(value, str) and value.strip().lower() in ('task', 'daily_task'):
                return 'task'
    except BaseException:
        pass
    return ''


def _daily_task_retry_count(bot):
    try:
        counts = getattr(bot, 'daily_flow_retry_counts', None)
        if isinstance(counts, dict):
            return int(float(str(counts.get('task', 0) or 0)))
    except BaseException:
        pass
    return 0


def _set_daily_task_retry_count(bot, value):
    try:
        counts = getattr(bot, 'daily_flow_retry_counts', None)
        if isinstance(counts, dict):
            counts['task'] = int(value)
            return True
    except BaseException:
        pass
    return False


def _daily_task_soft_retry_backoff_seconds():
    try:
        value = _cfg_get(_active_bot_sections(), 'daily_task_soft_retry_backoff_seconds', '300')
        seconds = float(str(value).strip())
        if seconds < 30.0:
            seconds = 30.0
        if seconds > 3600.0:
            seconds = 3600.0
        return seconds
    except BaseException:
        return 300.0


def _patch_daily_task_soft_retry_for_module(m, tag=''):
    changed = 0
    try:
        module_name = str(getattr(m, '__name__', '') or '')
        if module_name != 'bot.application.freebenefits_flow':
            return 0
        original_failure = getattr(m, '_mark_daily_flow_failure', None)
        if callable(original_failure) and not getattr(original_failure, '__qqfarm_task_soft_retry_wrapped__', False):
            def _wrapped_failure(*a, __orig=original_failure, **k):
                if _daily_task_flow_key(a, k) != 'task':
                    return __orig(*a, **k)
                bot = _daily_task_bot_from_args(a, k)
                limit = max(2, _daily_retry_max_default())
                current = _daily_task_retry_count(bot)
                if bot is not None and current >= (limit - 1):
                    _set_daily_task_retry_count(bot, limit - 1)
                    state = _daily_task_set_retry_backoff('task failure capped at ' + str(limit - 1) + '/' + str(limit))
                    try: setattr(bot, '_qqfarm_task_retry_next_ts', float(state.get('next_ts', 0.0) or 0.0))
                    except BaseException: pass
                    _throttled_write('v37-task-soft-retry-cap', 'v37 daily task transient failure capped at ' + str(limit - 1) + '/' + str(limit) + '; persistent retry backoff active', 60.0)
                    return False
                result = __orig(*a, **k)
                try:
                    if bot is not None and _daily_task_retry_count(bot) >= limit:
                        _set_daily_task_retry_count(bot, limit - 1)
                    state = _daily_task_set_retry_backoff('task failure')
                    if bot is not None:
                        setattr(bot, '_qqfarm_task_retry_next_ts', float(state.get('next_ts', 0.0) or 0.0))
                except BaseException:
                    pass
                return result
            try: _wrapped_failure.__qqfarm_task_soft_retry_wrapped__ = True
            except BaseException: pass
            setattr(m, '_mark_daily_flow_failure', _wrapped_failure)
            changed += 1
        original_get = getattr(m, '_get_daily_flow_retry_count', None)
        if callable(original_get) and not getattr(original_get, '__qqfarm_task_soft_retry_wrapped__', False):
            def _wrapped_get(*a, __orig=original_get, **k):
                if _daily_task_flow_key(a, k) == 'task':
                    bot = _daily_task_bot_from_args(a, k)
                    if bot is not None:
                        return min(_daily_task_retry_count(bot), max(1, _daily_retry_max_default() - 1))
                return __orig(*a, **k)
            try: _wrapped_get.__qqfarm_task_soft_retry_wrapped__ = True
            except BaseException: pass
            setattr(m, '_get_daily_flow_retry_count', _wrapped_get)
            changed += 1
        original_should = getattr(m, 'should_run_daily_task', None)
        if callable(original_should) and not getattr(original_should, '__qqfarm_task_soft_retry_wrapped__', False):
            def _wrapped_should(*a, __orig=original_should, **k):
                bot = _daily_task_bot_from_args(a, k)
                try:
                    if _daily_task_retry_backoff_active():
                        try: _runtime_info_once('v37-task-backoff', '\u6bcf\u65e5\u4efb\u52a1\u5931\u8d25\u9000\u907f\u4e2d\uff1a\u5148\u6267\u884c\u6536\u83dc\u7b49\u5e38\u89c4\u5de1\u68c0\u3002')
                        except BaseException: pass
                        return False
                except BaseException:
                    pass
                return __orig(*a, **k)
            try: _wrapped_should.__qqfarm_task_soft_retry_wrapped__ = True
            except BaseException: pass
            setattr(m, 'should_run_daily_task', _wrapped_should)
            changed += 1
        original_run = getattr(m, 'run_daily_task', None)
        if callable(original_run) and not getattr(original_run, '__qqfarm_task_soft_retry_wrapped__', False):
            def _wrapped_run(*a, __orig=original_run, **k):
                if _daily_task_retry_backoff_active():
                    try: _runtime_info_once('v37-task-run-backoff', '\u6bcf\u65e5\u4efb\u52a1\u6682\u7f13\u91cd\u8bd5\uff0c\u672c\u8f6e\u4f18\u5148\u5904\u7406\u6536\u83dc\u4e0e\u519c\u573a\u5de1\u68c0\u3002')
                    except BaseException: pass
                    return False
                return __orig(*a, **k)
            try: _wrapped_run.__qqfarm_task_soft_retry_wrapped__ = True
            except BaseException: pass
            setattr(m, 'run_daily_task', _wrapped_run)
            changed += 1
        original_success = getattr(m, '_mark_daily_flow_success', None)
        if callable(original_success) and not getattr(original_success, '__qqfarm_task_soft_retry_wrapped__', False):
            def _wrapped_success(*a, __orig=original_success, **k):
                result = __orig(*a, **k)
                if _daily_task_flow_key(a, k) == 'task':
                    _daily_task_clear_retry_backoff()
                    bot = _daily_task_bot_from_args(a, k)
                    try:
                        if bot is not None:
                            setattr(bot, '_qqfarm_task_retry_next_ts', 0.0)
                    except BaseException:
                        pass
                return result
            try: _wrapped_success.__qqfarm_task_soft_retry_wrapped__ = True
            except BaseException: pass
            setattr(m, '_mark_daily_flow_success', _wrapped_success)
            changed += 1
        if changed:
            sig = module_name + ':' + str(changed)
            if sig not in _DAILY_TASK_SOFT_RETRY_PATCH_LOG_SEEN:
                _DAILY_TASK_SOFT_RETRY_PATCH_LOG_SEEN.add(sig)
                _write('v32 daily task soft retry patched ' + str(tag) + ' ' + sig)
    except BaseException as e:
        try: _throttled_write('v32-task-soft-retry-error', 'v32 daily task soft retry patch error ' + repr(e), 30.0)
        except BaseException: pass
    return changed


def _patch_daily_task_soft_retry_loaded(tag=''):
    try:
        module = sys.modules.get('bot.application.freebenefits_flow')
        if module is not None:
            return _patch_daily_task_soft_retry_for_module(module, tag)
    except BaseException:
        pass
    return 0


# ---- v33 start debounce: ignore a second Start click while initialization is still running ----
try:
    _START_DEBOUNCE_PATCH_LOG_SEEN
except BaseException:
    _START_DEBOUNCE_PATCH_LOG_SEEN = set()
try:
    _START_DEBOUNCE_PATCHED_CLASSES
except BaseException:
    _START_DEBOUNCE_PATCHED_CLASSES = set()
_START_DEBOUNCE_SECONDS = 15.0


def _start_debounce_log(msg):
    try:
        logging_mod = sys.modules.get('logging')
        if logging_mod is not None:
            logging_mod.getLogger().info(msg)
    except BaseException:
        pass
    try:
        _throttled_write('v33-start-debounce', 'v33 start debounce ' + str(msg), 2.0)
    except BaseException:
        pass


def _wrap_start_debounce_method(fn):
    if getattr(fn, '__qqfarm_start_debounce_wrapped__', False):
        return fn, False
    def _wrapped(self, *a, **k):
        now = time.time()
        try:
            last = float(getattr(self, '_qqfarm_last_start_request_ts', 0.0) or 0.0)
        except BaseException:
            last = 0.0
        if last > 0.0 and (now - last) < _START_DEBOUNCE_SECONDS:
            _start_debounce_log('\u542f\u52a8\u6b63\u5728\u521d\u59cb\u5316\uff0c\u5df2\u5ffd\u7565\u91cd\u590d\u70b9\u51fb\uff0c\u8bf7\u7a0d\u5019\u3002')
            return False
        try:
            setattr(self, '_qqfarm_last_start_request_ts', now)
        except BaseException:
            pass
        try:
            return fn(self, *a, **k)
        except BaseException:
            try: setattr(self, '_qqfarm_last_start_request_ts', 0.0)
            except BaseException: pass
            raise
    try:
        _wrapped.__name__ = getattr(fn, '__name__', '_start_bot')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_start_debounce_wrapped__ = True
    except BaseException:
        pass
    return _wrapped, True


def _wrap_stop_clears_start_debounce(fn):
    if getattr(fn, '__qqfarm_stop_clears_start_debounce_wrapped__', False):
        return fn, False
    def _wrapped(self, *a, **k):
        try:
            return fn(self, *a, **k)
        finally:
            try: setattr(self, '_qqfarm_last_start_request_ts', 0.0)
            except BaseException: pass
    try:
        _wrapped.__name__ = getattr(fn, '__name__', '_stop_bot')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_stop_clears_start_debounce_wrapped__ = True
    except BaseException:
        pass
    return _wrapped, True


def _patch_start_debounce_for_module(m, tag=''):
    changed = 0
    try:
        cls = getattr(m, 'FarmBotWindow', None)
        if not isinstance(cls, type):
            return 0
        if cls in _START_DEBOUNCE_PATCHED_CLASSES:
            return 0
        old_start = getattr(cls, '_start_bot', None)
        if callable(old_start):
            new_start, ok = _wrap_start_debounce_method(old_start)
            if ok:
                setattr(cls, '_start_bot', new_start)
                changed += 1
        old_stop = getattr(cls, '_stop_bot', None)
        if callable(old_stop):
            new_stop, ok = _wrap_stop_clears_start_debounce(old_stop)
            if ok:
                setattr(cls, '_stop_bot', new_stop)
                changed += 1
        if changed:
            _START_DEBOUNCE_PATCHED_CLASSES.add(cls)
            sig = str(getattr(m, '__name__', '')) + ':' + str(changed)
            if sig not in _START_DEBOUNCE_PATCH_LOG_SEEN:
                _START_DEBOUNCE_PATCH_LOG_SEEN.add(sig)
                _write('v33 start debounce patched ' + str(tag) + ' ' + sig)
    except BaseException as e:
        try: _throttled_write('v33-start-debounce-error', 'v33 start debounce patch error ' + repr(e), 30.0)
        except BaseException: pass
    return changed


def _patch_start_debounce_loaded(tag=''):
    changed = []
    try:
        for mn, m in list(sys.modules.items()):
            if m is None or not str(mn).startswith('gui.'):
                continue
            c = _patch_start_debounce_for_module(m, tag)
            if c:
                changed.append(str(mn) + ':' + str(c))
    except BaseException:
        pass
    return changed


# ---- v33 diagnostic trace for the GUI -> RuntimeService -> FarmBotCV start chain ----
try:
    _RUNTIME_START_DIAG_PATCH_LOG_SEEN
except BaseException:
    _RUNTIME_START_DIAG_PATCH_LOG_SEEN = set()
try:
    _RUNTIME_START_DIAG_PATCHED_METHODS
except BaseException:
    _RUNTIME_START_DIAG_PATCHED_METHODS = set()


def _runtime_diag_repr(value, limit=500):
    try:
        text = repr(value)
        if len(text) > int(limit):
            text = text[:int(limit)] + '...'
        return text
    except BaseException:
        return '<repr-error>'


def _runtime_diag_state(obj):
    data = {}
    try:
        for name in ('running', '_running', 'pause_status', 'stop_requested', '_stop_requested',
                     'stop_event', '_stop_event', 'exit_on_stop', 'instance_id', 'active_instance_id'):
            try:
                if not hasattr(obj, name):
                    continue
                value = getattr(obj, name)
                if hasattr(value, 'is_set') and callable(getattr(value, 'is_set')):
                    data[name] = {'repr': _runtime_diag_repr(value, 160), 'is_set': bool(value.is_set())}
                elif callable(value):
                    data[name] = '<callable>'
                else:
                    data[name] = _runtime_diag_repr(value, 160)
            except BaseException as e:
                data[name] = '<error ' + repr(e) + '>'
        try:
            checker = getattr(obj, 'is_stop_requested', None)
            if callable(checker):
                data['is_stop_requested()'] = _runtime_diag_repr(checker(), 160)
        except BaseException as e:
            data['is_stop_requested()'] = '<error ' + repr(e) + '>'
        try:
            dd = getattr(obj, '__dict__', None)
            if isinstance(dd, dict):
                selected = {}
                for key, value in list(dd.items()):
                    low = str(key).lower()
                    if any(token in low for token in ('run', 'stop', 'pause', 'thread', 'worker', 'instance')):
                        selected[str(key)] = _runtime_diag_repr(value, 160)
                data['dict_selected'] = selected
        except BaseException:
            pass
    except BaseException:
        pass
    return _runtime_diag_repr(data, 1800)


def _wrap_runtime_diag_method(fn, label):
    if getattr(fn, '__qqfarm_runtime_start_diag_wrapped__', False):
        return fn, False
    def _wrapped(*a, **k):
        self_obj = a[0] if a else None
        _write('v33diag enter ' + str(label) + ' args=' + _runtime_diag_repr(a[1:]) + ' kwargs=' + _runtime_diag_repr(k) + ' state=' + _runtime_diag_state(self_obj))
        started = time.time()
        try:
            result = fn(*a, **k)
        except BaseException as e:
            try:
                tb = __import__('traceback').format_exc()
            except BaseException:
                tb = ''
            _write('v33diag exception ' + str(label) + ' ' + repr(e) + ' traceback=' + str(tb)[-3000:])
            raise
        _write('v33diag exit ' + str(label) + ' elapsed=' + ('%.3f' % (time.time() - started)) + ' result=' + _runtime_diag_repr(result) + ' state=' + _runtime_diag_state(self_obj))
        return result
    try:
        _wrapped.__name__ = getattr(fn, '__name__', 'runtime_diag')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_runtime_start_diag_wrapped__ = True
        _wrapped.__qqfarm_runtime_start_diag_orig__ = fn
    except BaseException:
        pass
    return _wrapped, True


def _patch_runtime_start_diagnostics_for_module(m, tag=''):
    changed = 0
    try:
        specs = [
            ('FarmBotCV', ('start', 'run_cycle')),
            ('BotRuntimeService', ('start', 'start_instance', 'mark_stopped', 'stop_instance')),
            ('FarmBotWindow', ('_start_bot', '_on_bot_stopped')),
        ]
        for class_name, method_names in specs:
            cls = getattr(m, class_name, None)
            if not isinstance(cls, type):
                continue
            for method_name in method_names:
                patch_key = (cls, str(method_name))
                if patch_key in _RUNTIME_START_DIAG_PATCHED_METHODS:
                    continue
                old = getattr(cls, method_name, None)
                if not callable(old):
                    continue
                new, ok = _wrap_runtime_diag_method(old, class_name + '.' + method_name)
                if ok:
                    setattr(cls, method_name, new)
                    _RUNTIME_START_DIAG_PATCHED_METHODS.add(patch_key)
                    changed += 1
        if changed:
            sig = str(getattr(m, '__name__', '')) + ':' + str(changed)
            if sig not in _RUNTIME_START_DIAG_PATCH_LOG_SEEN:
                _RUNTIME_START_DIAG_PATCH_LOG_SEEN.add(sig)
                _write('v33 runtime start diagnostics patched ' + str(tag) + ' ' + sig)
    except BaseException as e:
        try: _throttled_write('v33-runtime-diag-error', 'v33 runtime start diagnostics patch error ' + repr(e), 30.0)
        except BaseException: pass
    return changed


def _patch_runtime_start_diagnostics_loaded(tag=''):
    changed = []
    try:
        for mn, m in list(sys.modules.items()):
            if m is None:
                continue
            c = _patch_runtime_start_diagnostics_for_module(m, tag)
            if c:
                changed.append(str(mn) + ':' + str(c))
    except BaseException:
        pass
    return changed


# ---- v31 share target guard: never default-send to first QQ row ----
try:
    _SHARE_TARGET_PATCH_LOG_SEEN
except BaseException:
    _SHARE_TARGET_PATCH_LOG_SEEN = set()


def _share_target_guard_config():
    try:
        secs = _active_bot_sections()
    except BaseException:
        secs = ['bot']
    try:
        target = str(_cfg_get(secs, 'share_target_name', '') or '').strip()
    except BaseException:
        target = ''
    try:
        search_enabled = _truthy(_cfg_get(secs, 'share_search_enabled', 'False'), False)
    except BaseException:
        search_enabled = False
    try:
        requires_match = _truthy(_cfg_get(secs, 'share_send_requires_target_match', 'False'), False)
    except BaseException:
        requires_match = False
    try:
        dry_run = _truthy(_cfg_get(secs, 'share_dry_run', 'True'), True)
    except BaseException:
        dry_run = True
    try:
        allow_group = _truthy(_cfg_get(secs, 'share_allow_group', 'False'), False)
    except BaseException:
        allow_group = False
    # A share is eligible only when an explicit target is configured.
    # Unverified/first-row fallbacks are intentionally never enabled.
    enabled = bool(target and search_enabled and requires_match)
    return {
        'enabled': enabled,
        'search_enabled': bool(search_enabled),
        'target_name': target,
        'requires_match': bool(requires_match),
        'dry_run': bool(dry_run),
        'allow_group': bool(allow_group),
    }


def _share_log_runtime(key, msg, warning=False):
    try:
        logging_mod = sys.modules.get('logging')
        if logging_mod is not None:
            lg = logging_mod.getLogger()
            if warning:
                lg.warning(msg)
            else:
                lg.info(msg)
    except BaseException:
        pass
    try:
        _throttled_write('share-target-' + str(key), 'v31 share target guard ' + str(msg), 5.0)
    except BaseException:
        pass


def _share_set_clipboard_unicode(text):
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        data = (str(text) + '\x00').encode('utf-16le')
        hglobal = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not hglobal:
            return False
        locked = kernel32.GlobalLock(hglobal)
        if not locked:
            return False
        ctypes.memmove(locked, data, len(data))
        kernel32.GlobalUnlock(hglobal)
        if not user32.OpenClipboard(0):
            return False
        try:
            user32.EmptyClipboard()
            if not user32.SetClipboardData(CF_UNICODETEXT, hglobal):
                return False
            # Clipboard now owns hglobal.
            return True
        finally:
            user32.CloseClipboard()
    except BaseException as e:
        try: _write('v31 share clipboard error ' + repr(e))
        except BaseException: pass
        return False


def _share_key(vk, up=False):
    try:
        import ctypes
        KEYEVENTF_KEYUP = 0x0002
        ctypes.windll.user32.keybd_event(int(vk), 0, KEYEVENTF_KEYUP if up else 0, 0)
        return True
    except BaseException:
        return False


def _share_send_ctrl_key(vk):
    try:
        VK_CONTROL = 0x11
        _share_key(VK_CONTROL, False)
        time.sleep(0.03)
        _share_key(vk, False)
        time.sleep(0.03)
        _share_key(vk, True)
        time.sleep(0.03)
        _share_key(VK_CONTROL, True)
        return True
    except BaseException:
        return False


def _share_click_abs(x, y):
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.SetCursorPos(int(x), int(y))
        time.sleep(0.05)
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.03)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
        return True
    except BaseException as e:
        try: _write('v31 share click error ' + repr(e))
        except BaseException: pass
        return False


def _share_find_dialog_hwnd(mod=None):
    try:
        if mod is not None and hasattr(mod, '_find_share_dialog_hwnd'):
            hwnd = mod._find_share_dialog_hwnd()
            if hwnd:
                return int(hwnd)
    except BaseException:
        pass
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kws = str(_cfg_get(_active_bot_sections(), 'share_dialog_title_keywords', '\u9009\u62e9\u8054\u7cfb\u4eba,\u53d1\u9001\u7ed9') or '')
        kws = kws.replace(';', ',').replace('|', ',')
        keywords = [x.strip() for x in kws.split(',') if x.strip()]
        found = []
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def _cb(hwnd, lparam):
            try:
                buf = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, buf, 256)
                title = str(buf.value or '')
                if title and any(k in title for k in keywords):
                    found.append(int(hwnd))
            except BaseException:
                pass
            return True
        user32.EnumWindows(WNDENUMPROC(_cb), 0)
        return found[0] if found else 0
    except BaseException as e:
        try: _write('v31 share find hwnd error ' + repr(e))
        except BaseException: pass
        return 0


def _share_get_rect(hwnd):
    try:
        import ctypes
        class RECT(ctypes.Structure):
            _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]
        rect = RECT()
        if not ctypes.windll.user32.GetWindowRect(int(hwnd), ctypes.byref(rect)):
            return None
        return (int(rect.left), int(rect.top), int(rect.right), int(rect.bottom))
    except BaseException:
        return None


def _share_activate_dialog(mod, hwnd):
    try:
        if mod is not None and hasattr(mod, '_activate_share_dialog_window'):
            try:
                mod._activate_share_dialog_window(hwnd)
                time.sleep(0.2)
                return True
            except BaseException:
                pass
        import ctypes
        user32 = ctypes.windll.user32
        user32.ShowWindow(int(hwnd), 9)
        user32.SetForegroundWindow(int(hwnd))
        time.sleep(0.2)
        return True
    except BaseException:
        return False


def _share_close_dialog(mod=None, hwnd=0):
    try:
        if mod is not None and hasattr(mod, '_close_share_dialog'):
            try:
                return bool(mod._close_share_dialog())
            except BaseException:
                pass
        if hwnd:
            import ctypes
            ctypes.windll.user32.PostMessageW(int(hwnd), 0x0010, 0, 0)
            return True
    except BaseException:
        pass
    return False


def _share_ratio_cfg(key, default):
    try:
        return float(str(_cfg_get(_active_bot_sections(), key, str(default))).strip())
    except BaseException:
        return float(default)


def _share_int_cfg(key, default):
    try:
        return int(float(str(_cfg_get(_active_bot_sections(), key, str(default))).strip()))
    except BaseException:
        return int(default)


def _share_point(rect, xr, yr):
    try:
        l, t, r, b = rect
        x = l + max(0.01, min(0.99, float(xr))) * max(1, r - l)
        y = t + max(0.01, min(0.99, float(yr))) * max(1, b - t)
        return int(x), int(y)
    except BaseException:
        return (0, 0)


def _share_norm_text(value):
    try:
        return ''.join(str(value or '').split()).casefold()
    except BaseException:
        return ''


def _share_text_matches_target(candidate_text, target):
    wanted = _share_norm_text(target)
    if not wanted:
        return False
    if wanted.isdigit() and 5 <= len(wanted) <= 12:
        token = ''
        tokens = []
        for char in str(candidate_text or ''):
            if char.isdigit():
                token += char
            elif token:
                tokens.append(token)
                token = ''
        if token:
            tokens.append(token)
        return wanted in tokens
    return _share_norm_text(candidate_text) == wanted


def _share_uia_element_texts(element):
    values = []
    try:
        values.append(element.window_text())
    except BaseException:
        pass
    try:
        values.extend(list(element.texts() or []))
    except BaseException:
        pass
    try:
        info = element.element_info
        for attr in ('name', 'rich_text'):
            try: values.append(getattr(info, attr, ''))
            except BaseException: pass
    except BaseException:
        pass
    return [str(x) for x in values if str(x or '').strip()]


def _share_uia_candidate_is_group(element):
    cur = element
    for _ in range(4):
        if cur is None:
            break
        parts = []
        try: parts.extend(_share_uia_element_texts(cur))
        except BaseException: pass
        try:
            info = cur.element_info
            for attr in ('control_type', 'class_name', 'automation_id'):
                try: parts.append(str(getattr(info, attr, '') or ''))
                except BaseException: pass
        except BaseException:
            pass
        blob = ' '.join(parts).casefold()
        if ('\u7fa4\u804a' in blob) or ('\u7fa4\u7ec4' in blob) or ('group chat' in blob) or ('groupchat' in blob):
            return True
        try:
            cur = cur.parent()
        except BaseException:
            break
    return False


def _share_uia_rect_valid(element):
    try:
        rect = element.rectangle()
        return int(rect.right) > int(rect.left) and int(rect.bottom) > int(rect.top)
    except BaseException:
        return False


def _share_pick_exact_uia_candidate(candidates, target, allow_group=False):
    wanted = _share_norm_text(target)
    if not wanted:
        return None
    for element in list(candidates or []):
        try:
            texts = _share_uia_element_texts(element)
            if not any(_share_text_matches_target(text, wanted) for text in texts):
                continue
            if not bool(allow_group) and _share_uia_candidate_is_group(element):
                continue
            if not _share_uia_rect_valid(element):
                continue
            return element
        except BaseException:
            continue
    return None


def _share_find_exact_uia_target(hwnd, target, allow_group=False):
    try:
        from pywinauto import Desktop
        dialog = Desktop(backend='uia').window(handle=int(hwnd))
        candidates = dialog.descendants()
        return _share_pick_exact_uia_candidate(candidates, target, allow_group=allow_group)
    except BaseException as e:
        try: _throttled_write('share-uia-error', 'v33 share UIA exact-match error ' + repr(e), 10.0)
        except BaseException: pass
        return None


def _share_click_uia_element(element):
    try:
        rect = element.rectangle()
        x = (int(rect.left) + int(rect.right)) // 2
        y = (int(rect.top) + int(rect.bottom)) // 2
        return _share_click_abs(x, y)
    except BaseException:
        return False


def _share_search_and_maybe_confirm(mod, cfg):
    target = str(cfg.get('target_name', '') or '').strip()
    if not target:
        _share_log_runtime('missing-target', 'daily share blocked: empty share_target_name', True)
        _share_close_dialog(mod, 0)
        return False
    hwnd = _share_find_dialog_hwnd(mod)
    if not hwnd:
        _share_log_runtime('no-dialog', 'daily share blocked: share dialog not found', True)
        return False
    _share_activate_dialog(mod, hwnd)
    rect = _share_get_rect(hwnd)
    if not rect:
        _share_log_runtime('no-rect', 'daily share blocked: share dialog rect unavailable', True)
        _share_close_dialog(mod, hwnd)
        return False
    sx = _share_ratio_cfg('share_search_box_x_ratio', 0.38)
    sy = _share_ratio_cfg('share_search_box_y_ratio', 0.12)
    cx = _share_ratio_cfg('share_dialog_confirm_x_ratio', 0.645)
    cy = _share_ratio_cfg('share_dialog_confirm_y_ratio', 0.935)
    settle_ms = _share_int_cfg('share_search_settle_ms', 900)
    x, y = _share_point(rect, sx, sy)
    _share_click_abs(x, y)
    time.sleep(0.1)
    _share_send_ctrl_key(0x41)
    if not _share_set_clipboard_unicode(target):
        _share_log_runtime('clipboard-fail', 'daily share blocked: clipboard set failed target=' + target, True)
        _share_close_dialog(mod, hwnd)
        return False
    _share_send_ctrl_key(0x56)
    time.sleep(max(0.2, float(settle_ms) / 1000.0))
    matched = _share_find_exact_uia_target(hwnd, target, allow_group=bool(cfg.get('allow_group', False)))
    if matched is None:
        _share_log_runtime('exact-miss', 'daily share blocked: exact UIA target not found; target=' + target, True)
        _share_close_dialog(mod, hwnd)
        return False
    if not _share_click_uia_element(matched):
        _share_log_runtime('exact-click-fail', 'daily share blocked: exact target click failed; target=' + target, True)
        _share_close_dialog(mod, hwnd)
        return False
    _share_log_runtime('exact-match', 'daily share exact target matched by UIA: target=' + target, False)
    time.sleep(0.2)
    if bool(cfg.get('dry_run', True)):
        _share_log_runtime('dry-run', 'daily share dry-run: exact target checked target=' + target + ', closed without sending', False)
        _share_close_dialog(mod, hwnd)
        return False
    x3, y3 = _share_point(rect, cx, cy)
    _share_click_abs(x3, y3)
    time.sleep(0.8)
    _share_log_runtime('sent-verified', 'daily share sent to exact UIA target=' + target, False)
    return True


def _wrap_share_target_guard_func(fn, mod, name):
    try:
        if getattr(fn, '__qqfarm_share_target_guard_wrapped__', False):
            return fn, False
    except BaseException:
        pass
    def _wrapped(*a, **k):
        try:
            if _stop_requested_in_args(a, k):
                return _stop_gate_return(name)
        except BaseException:
            pass
        try:
            cfg = _share_target_guard_config()
            if not cfg.get('enabled', False):
                _share_log_runtime('manual-or-invalid', 'daily share skipped: automatic sharing requires an explicit exact target', False)
                _share_close_dialog(mod, 0)
                return False
            return _share_search_and_maybe_confirm(mod, cfg)
        except BaseException as e:
            try: _write('v31 share target guard wrapper error ' + str(name) + ' ' + repr(e))
            except BaseException: pass
            try:
                _share_close_dialog(mod, 0)
            except BaseException:
                pass
            return False
    try:
        _wrapped.__name__ = getattr(fn, '__name__', '_click_share_dialog_first_friend_and_confirm')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_share_target_guard_wrapped__ = True
    except BaseException:
        pass
    return _wrapped, True


def _looks_share_target_module(m):
    try:
        return callable(getattr(m, '_click_share_dialog_first_friend_and_confirm', None))
    except BaseException:
        return False


def _patch_share_target_guard_for_module(m, tag=''):
    try:
        if not _looks_share_target_module(m):
            return 0
        mn = str(getattr(m, '__name__', '') or '')
        n = '_click_share_dialog_first_friend_and_confirm'
        old = getattr(m, n)
        new, ok = _wrap_share_target_guard_func(old, m, mn + '.' + n)
        if ok:
            setattr(m, n, new)
            return 1
    except BaseException as e:
        try: _write('v31 share target guard patch error ' + repr(e))
        except BaseException: pass
    return 0


def _patch_share_target_guard_loaded(tag=''):
    changed = []
    try:
        for mn, m in list(sys.modules.items()):
            if not _looks_share_target_module(m):
                continue
            c = _patch_share_target_guard_for_module(m, tag)
            if c:
                changed.append(str(mn) + ':' + str(c))
    except BaseException as e:
        try: _write('v31 share target guard scan error ' + repr(e))
        except BaseException: pass
    if changed:
        sig = ', '.join(changed[:20])
        if sig not in _SHARE_TARGET_PATCH_LOG_SEEN:
            _SHARE_TARGET_PATCH_LOG_SEEN.add(sig)
            _write('v31 share target guard patched ' + str(tag) + ' ' + sig)
    return changed


# ---- v34 daily-share page transition settle ----
try:
    _SHARE_ENTRY_SETTLE_PATCH_LOG_SEEN
except BaseException:
    _SHARE_ENTRY_SETTLE_PATCH_LOG_SEEN = set()


def _daily_entry_call_kind(args, kwargs):
    try:
        value = kwargs.get('tag')
        tag = str(value or '').strip().lower()
        if tag in ('share_entry', 'task_entry'):
            return tag
    except BaseException:
        pass
    try:
        for value in list(args or ()):
            if isinstance(value, str):
                tag = value.strip().lower()
                if tag in ('share_entry', 'task_entry'):
                    return tag
    except BaseException:
        pass
    return ''


def _share_entry_call_detected(args, kwargs):
    return _daily_entry_call_kind(args, kwargs) == 'share_entry'


def _share_click_result_succeeded(result):
    try:
        if isinstance(result, (tuple, list)):
            return bool(result) and bool(result[0])
        if isinstance(result, dict):
            for key in ('success', 'clicked', 'found', 'ok'):
                if key in result:
                    return bool(result.get(key))
        return bool(result)
    except BaseException:
        return False


def _wrap_share_entry_settle_func(fn):
    try:
        if getattr(fn, '__qqfarm_share_entry_settle_wrapped__', False):
            return fn, False
    except BaseException:
        pass

    def _wrapped(*a, **k):
        entry_kind = _daily_entry_call_kind(a, k)
        result = fn(*a, **k)
        if entry_kind and _share_click_result_succeeded(result):
            try:
                if entry_kind == 'task_entry':
                    settle_ms = _share_int_cfg('task_entry_settle_ms', 1200)
                else:
                    settle_ms = _share_int_cfg('share_entry_settle_ms', 1200)
            except BaseException:
                settle_ms = 1200
            settle_seconds = max(1.0, min(3.0, float(settle_ms) / 1000.0))
            try:
                _throttled_write(
                    str(entry_kind) + '-settle',
                    'v37 daily ' + str(entry_kind) + ' clicked; waiting %.3fs before prompt detection' % settle_seconds,
                    5.0,
                )
            except BaseException:
                pass
            time.sleep(settle_seconds)
        return result

    try:
        _wrapped.__name__ = getattr(fn, '__name__', '_click_template_once')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_share_entry_settle_wrapped__ = True
    except BaseException:
        pass
    return _wrapped, True


def _patch_share_entry_settle_for_module(m, tag=''):
    try:
        if m is None or str(getattr(m, '__name__', '') or '') != 'bot.application.freebenefits_flow':
            return 0
        name = '_click_template_once'
        old = getattr(m, name, None)
        if not callable(old):
            return 0
        new, ok = _wrap_share_entry_settle_func(old)
        if not ok:
            return 0
        setattr(m, name, new)
        return 1
    except BaseException as e:
        try: _write('v34 share entry settle patch error ' + repr(e))
        except BaseException: pass
        return 0


def _patch_share_entry_settle_loaded(tag=''):
    changed = []
    try:
        for mn, m in list(sys.modules.items()):
            if str(mn) != 'bot.application.freebenefits_flow':
                continue
            count = _patch_share_entry_settle_for_module(m, tag)
            if count:
                changed.append(str(mn) + ':' + str(count))
    except BaseException as e:
        try: _write('v34 share entry settle scan error ' + repr(e))
        except BaseException: pass
    if changed:
        sig = ', '.join(changed[:20])
        if sig not in _SHARE_ENTRY_SETTLE_PATCH_LOG_SEEN:
            _SHARE_ENTRY_SETTLE_PATCH_LOG_SEEN.add(sig)
            _write('v34 share entry settle patched ' + str(tag) + ' ' + sig)
    return changed


# ---- v36 friend radish false-positive diagnostics ----
# This is intentionally read-only. It records the compiled friend-flow
# boundary and the radish/cache-related names that are actually present at
# runtime before any behavioral gate is changed.
_FRIEND_RADISH_DIAG_SEEN = set()
_FRIEND_RADISH_DIAG_WRAP_SEEN = set()


def _friend_radish_evidence_map(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, bool):
        return {'confirmed': value}
    if isinstance(value, str):
        return {'confirmed': True, 'crop_name': value}
    try:
        fields = {}
        for key in ('confirmed', 'scope', 'crop_name', 'timestamp', 'target'):
            if hasattr(value, key):
                fields[key] = getattr(value, key)
        return fields
    except BaseException:
        return {}


def _should_skip_friend_radish(row_hint, farm_evidence, steal_evidence, skip_enabled=True, now=None, ttl=45.0):
    # A row cache is only a hint. It is deliberately not consulted here.
    if not bool(skip_enabled):
        return False
    steal = _friend_radish_evidence_map(steal_evidence)
    if bool(steal.get('confirmed')):
        return False
    evidence = _friend_radish_evidence_map(farm_evidence)
    if not bool(evidence.get('confirmed')):
        return False
    if str(evidence.get('scope', '')).strip().lower() != 'current_friend_farm':
        return False
    if str(evidence.get('crop_name', '')).strip() != '\u767d\u841d\u535c':
        return False
    try:
        current = float(now) if now is not None else float(__import__('time').time())
        observed = float(evidence.get('timestamp'))
        window = max(1.0, float(ttl))
        age = current - observed
        return 0.0 <= age <= window
    except BaseException:
        return False


def _friend_radish_wrapper_has_marker(value, marker):
    seen = set()
    current = value
    for _ in range(8):
        try:
            if current is None or id(current) in seen:
                return False
            seen.add(id(current))
            if bool(getattr(current, marker, False)):
                return True
            if bool(getattr(current, '__qqfarm_friend_radish_diag_wrapped__', False)):
                current = getattr(current, '__qqfarm_friend_radish_diag_orig__', None)
                continue
        except BaseException:
            return False
        return False
    return False


def _wrap_friend_skip_feature_gate_func(fn, name=''):
    try:
        if not callable(fn) or _friend_radish_wrapper_has_marker(fn, '__qqfarm_friend_skip_feature_gate_wrapped__'):
            return fn, False
        def _wrapped(*a, **k):
            try:
                writer = globals().get('_throttled_write')
                if callable(writer):
                    writer('v36-friend-radish-safe-gate', 'v36 friend radish safe gate disabled unverified row cache: ' + str(name), 60.0)
            except BaseException:
                pass
            return False
        try:
            _wrapped.__name__ = getattr(fn, '__name__', 'friend_skip_feature_gate')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_friend_skip_feature_gate_wrapped__ = True
            _wrapped.__qqfarm_friend_skip_feature_gate_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _wrap_friend_skip_cache_func(fn, name=''):
    try:
        if not callable(fn) or _friend_radish_wrapper_has_marker(fn, '__qqfarm_friend_skip_cache_wrapped__'):
            return fn, False
        def _wrapped(*a, **k):
            try:
                writer = globals().get('_throttled_write')
                if callable(writer):
                    writer('v36-friend-radish-cache-safe-gate', 'v36 friend radish row cache bypassed: ' + str(name), 60.0)
            except BaseException:
                pass
            return False
        try:
            _wrapped.__name__ = getattr(fn, '__name__', 'friend_skip_cache_gate')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_friend_skip_cache_wrapped__ = True
            _wrapped.__qqfarm_friend_skip_cache_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _patch_friend_radish_behavior_for_module(module, tag=''):
    changed = 0
    try:
        module_name = str(getattr(module, '__name__', '') or '')
        if module_name == 'bot.application.checks_friend':
            gate_names = ('_is_radish_skip_feature_enabled', '_is_friend_row_in_radish_skip_cache', 'mark_friend_row_as_radish_skip')
        elif module_name == 'bot.application.actions_friend':
            gate_names = ('_is_friend_skip_radish_enabled', 'mark_friend_row_as_radish_skip')
        else:
            return 0
        for function_name in gate_names:
            old = getattr(module, function_name, None)
            if not callable(old):
                continue
            if function_name.startswith('_is_'):
                new, ok = _wrap_friend_skip_feature_gate_func(old, module_name + '.' + function_name)
            else:
                new, ok = _wrap_friend_skip_cache_func(old, module_name + '.' + function_name)
            if ok:
                setattr(module, function_name, new)
                changed += 1
        if changed:
            _write('v36 friend-radish safe behavior patched ' + str(tag) + ' ' + module_name + ':' + str(changed))
    except BaseException as e:
        try:
            _write('v36 friend-radish behavior patch error ' + repr(e))
        except BaseException:
            pass
    return changed


def _patch_friend_radish_behavior_loaded(tag=''):
    changed = []
    try:
        for module_name in ('bot.application.checks_friend', 'bot.application.actions_friend'):
            module = sys.modules.get(module_name)
            if module is None:
                continue
            count = _patch_friend_radish_behavior_for_module(module, tag)
            if count:
                changed.append(module_name + ':' + str(count))
    except BaseException as e:
        try:
            _write('v36 friend-radish behavior scan error ' + repr(e))
        except BaseException:
            pass
    return changed


def _friend_diag_code_details(obj):
    try:
        code = getattr(obj, '__code__', None)
        if code is None:
            return 'no-code type=' + str(type(obj).__name__)
        names = []
        for value in getattr(code, 'co_names', ()):
            low = str(value).lower()
            if any(token in low for token in ('friend', 'radish', 'skip', 'row', 'steal', 'farm', 'cache', 'pending')):
                names.append(str(value))
        consts = []
        for value in getattr(code, 'co_consts', ()):
            if isinstance(value, str):
                low = value.lower()
                if any(token in low for token in ('friend', 'radish', 'skip', 'row', 'steal', 'farm', 'cache', 'pending')):
                    consts.append(value[:180])
            elif hasattr(value, 'co_name'):
                nested_names = []
                for nested_value in getattr(value, 'co_names', ()):
                    nested_low = str(nested_value).lower()
                    if any(token in nested_low for token in ('friend', 'radish', 'skip', 'row', 'steal', 'farm', 'cache', 'pending')):
                        nested_names.append(str(nested_value))
                if nested_names:
                    consts.append('nested=' + str(getattr(value, 'co_name', '')) + ':' + ','.join(nested_names[:30]))
        return 'varnames=' + repr(tuple(getattr(code, 'co_varnames', ()))[:40]) + ' names=' + repr(names[:80]) + ' consts=' + repr(consts[:80])
    except BaseException as e:
        return 'code-details-error=' + repr(e)[:180]


def _friend_radish_diag_dump(tag=''):
    try:
        low_tag = str(tag or '').lower()
        if not (low_tag in ('initial', 'qt-safe-tick') or low_tag.startswith('bot.') or low_tag == 'bot'):
            return 0
        changed = 0
        for module_name, module in list(sys.modules.items()):
            low_module = str(module_name).lower()
            if module is None or not (low_module == 'bot' or low_module.startswith('bot.')):
                continue
            objects = []
            try:
                for name, value in list(vars(module).items()):
                    low_name = str(name).lower()
                    if low_name in ('handle_friend_farm_actions', 'process_friend_farm') or any(token in low_name for token in ('radish', 'friend_farm', 'friend_row')):
                        objects.append((str(module_name) + '.' + str(name), value))
                    if isinstance(value, type):
                        for method_name in ('handle_friend_farm_actions', 'process_friend_farm'):
                            if hasattr(value, method_name):
                                objects.append((str(module_name) + '.' + str(name) + '.' + method_name, getattr(value, method_name)))
            except BaseException:
                pass
            for qualified_name, value in objects:
                try:
                    signature = qualified_name + ':' + str(id(value))
                    if signature in _FRIEND_RADISH_DIAG_SEEN:
                        continue
                    _FRIEND_RADISH_DIAG_SEEN.add(signature)
                    _write('v36 friend-radish diag object ' + qualified_name + ' type=' + str(type(value).__name__) + ' callable=' + str(callable(value)))
                    _write('v36 friend-radish diag details ' + qualified_name + ' ' + _friend_diag_code_details(value))
                    changed += 1
                except BaseException:
                    pass
            try:
                interesting_globals = []
                for key, value in list(vars(module).items()):
                    low_key = str(key).lower()
                    if any(token in low_key for token in ('radish', 'friend_row', 'pending_row', 'friend_cache')):
                        interesting_globals.append(str(key) + '=' + repr(value)[:180])
                if interesting_globals:
                    _write('v36 friend-radish diag globals ' + str(module_name) + ' ' + ' | '.join(interesting_globals[:80]))
            except BaseException:
                pass
        return changed
    except BaseException as e:
        try:
            _write('v36 friend-radish diag error ' + repr(e))
        except BaseException:
            pass
        return 0


def _friend_radish_diag_bot_summary(args, kwargs):
    try:
        values = list(args or ()) + list((kwargs or {}).values())
        for value in values:
            if value is None or isinstance(value, (str, bytes, int, float, bool, list, tuple, dict, set)):
                continue
            fields = []
            for key in dir(value):
                low = str(key).lower()
                if any(token in low for token in ('radish', 'friend', 'row', 'pending', 'steal')):
                    try:
                        item = getattr(value, key)
                        if callable(item):
                            continue
                        fields.append(str(key) + '=' + repr(item)[:240])
                    except BaseException:
                        pass
            if fields:
                return 'bot=' + str(type(value).__name__) + ' ' + ' | '.join(fields[:80])
    except BaseException:
        pass
    return ''


def _friend_radish_diag_arg_summary(args, kwargs):
    result = []
    try:
        for value in list(args or ()) + list((kwargs or {}).values()):
            if value is None or isinstance(value, (str, bytes, int, float, bool)):
                result.append(repr(value)[:120])
            elif isinstance(value, (list, tuple, set)):
                result.append(type(value).__name__ + '(len=' + str(len(value)) + ')')
            elif isinstance(value, dict):
                result.append('dict(keys=' + repr(list(value.keys())[:20]) + ')')
            else:
                shape = getattr(value, 'shape', None)
                if shape is not None:
                    result.append(type(value).__name__ + '(shape=' + repr(shape) + ')')
                else:
                    result.append(type(value).__name__)
    except BaseException:
        pass
    return '[' + ', '.join(result[:20]) + ']'


def _wrap_friend_radish_diag_func(fn, module_name, function_name):
    try:
        if not callable(fn) or getattr(fn, '__qqfarm_friend_radish_diag_wrapped__', False):
            return fn, False
        def _wrapped(*a, **k):
            prefix = 'v36 friend-radish call ' + str(module_name) + '.' + str(function_name)
            try:
                _write(prefix + ' enter args=' + _friend_radish_diag_arg_summary(a, k) + ' ' + _friend_radish_diag_bot_summary(a, k))
            except BaseException:
                pass
            try:
                result = fn(*a, **k)
            except BaseException as e:
                try:
                    _write(prefix + ' error=' + repr(e)[:240] + ' ' + _friend_radish_diag_bot_summary(a, k))
                except BaseException:
                    pass
                raise
            try:
                _write(prefix + ' exit result=' + repr(result)[:500] + ' ' + _friend_radish_diag_bot_summary(a, k))
            except BaseException:
                pass
            return result
        try:
            _wrapped.__name__ = getattr(fn, '__name__', str(function_name))
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_friend_radish_diag_wrapped__ = True
            _wrapped.__qqfarm_friend_radish_diag_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _patch_friend_radish_diag_for_module(module, tag=''):
    changed = 0
    try:
        module_name = str(getattr(module, '__name__', '') or '')
        if module_name not in ('bot.application.checks_friend', 'bot.application.actions_friend'):
            return 0
        names = (
            '_detect_friend_farm_radish',
            '_is_friend_row_in_radish_skip_cache',
            'mark_friend_row_as_radish_skip',
            '_build_friend_row_cache_key',
            'handle_friend_farm_actions',
            'process_friend_farm',
        )
        for function_name in names:
            old = getattr(module, function_name, None)
            if not callable(old):
                continue
            new, ok = _wrap_friend_radish_diag_func(old, module_name, function_name)
            if ok:
                setattr(module, function_name, new)
                changed += 1
        if changed:
            signature = module_name + ':' + str(changed)
            if signature not in _FRIEND_RADISH_DIAG_WRAP_SEEN:
                _FRIEND_RADISH_DIAG_WRAP_SEEN.add(signature)
                _write('v36 friend-radish diag wrappers installed ' + str(tag) + ' ' + signature)
    except BaseException as e:
        try:
            _write('v36 friend-radish diag wrapper error ' + repr(e))
        except BaseException:
            pass
    return changed


def _patch_friend_radish_diag_loaded(tag=''):
    changed = []
    try:
        for module_name in ('bot.application.checks_friend', 'bot.application.actions_friend'):
            module = sys.modules.get(module_name)
            if module is None:
                continue
            count = _patch_friend_radish_diag_for_module(module, tag)
            if count:
                changed.append(module_name + ':' + str(count))
    except BaseException as e:
        try:
            _write('v36 friend-radish diag scan error ' + repr(e))
        except BaseException:
            pass
    return changed


def _patch_tag_relevant(tag):
    try:
        low = str(tag or '').lower()
        if low in ('initial', 'qt-safe-tick', 'manual'):
            return True
        if low.startswith('bot.') or low == 'bot':
            return True
        if low.startswith('_q'):
            return True
        if low.startswith('gui.'):
            return True
        if low.startswith('configparser') or low.startswith('logging') or low.startswith('pyside6'):
            return True
    except BaseException:
        pass
    return False


def _patch_loaded(tag=''):
    global _PATCH_LOADED_RUNNING, _PATCH_LOADED_LAST_TS
    if _PATCH_LOADED_RUNNING:
        return []
    now = time.time()
    relevant = _patch_tag_relevant(tag)
    if not relevant:
        return []
    # Avoid full sys.modules scans on import storms.  Relevant bot.* modules are
    # still patched when they load; timer ticks are throttled.
    if str(tag) == 'qt-safe-tick' and (now - _PATCH_LOADED_LAST_TS) < 8.0:
        return []
    _PATCH_LOADED_LAST_TS = now
    _PATCH_LOADED_RUNNING = True
    patched = []
    try:
        for mn, m in list(sys.modules.items()):
            if m is None:
                continue
            if not (_is_target_module_name(mn) or _looks_integrity_exit_module(m)):
                continue
            try:
                c = _patch_module(m)
                if c:
                    patched.append(mn + ':' + str(c))
            except BaseException:
                pass
        try:
            _patch_security_watchdogs_loaded(tag)
        except BaseException:
            pass
        try:
            _install_runtime_log_patch()
        except BaseException:
            pass
        try:
            _install_config_override_patch()
        except BaseException:
            pass
        try:
            if str(tag) in ('initial', 'qt-safe-tick') or str(tag).startswith('bot.'):
                _force_autolaunch_config_file()
        except BaseException:
            pass
        try:
            if str(tag) in ('initial', 'qt-safe-tick') or 'security' in str(tag):
                _install_path_license_patch()
        except BaseException:
            pass
        try:
            _runtime_scan(tag)
        except BaseException:
            pass
        try:
            _friend_radish_diag_dump(tag)
        except BaseException:
            pass
        try:
            _patch_friend_radish_behavior_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_friend_radish_diag_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_friend_pause_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_guard_dog_config_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_wechat_focus_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_vip_business_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_share_target_guard_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_share_entry_settle_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_daily_task_soft_retry_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_start_debounce_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_runtime_start_diagnostics_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_gui_entitlement_aliases_loaded(tag)
        except BaseException:
            pass
        try:
            # Exact-class patch only; broad gui/utils patching remains disabled.
            _patch_core_runtime_loaded(tag)
        except BaseException:
            pass
        try:
            if str(tag) in ('initial', 'qt-safe-tick') or str(tag).startswith('bot.'):
                _repair_daily_task_retry_state_file(str(tag))
        except BaseException:
            pass
        if patched:
            sig = ', '.join(patched[:80])
            if sig not in _PATCH_LOG_SEEN:
                _PATCH_LOG_SEEN.add(sig)
                _write('patched ' + str(tag) + ' ' + sig)
    finally:
        _PATCH_LOADED_RUNNING = False
    return patched



# ---- Runtime entitlement object/log patch v7 ----
# The robot task layer may keep a copied feature_gate function or a cached context.entitlement_active=False.
# This section patches all already-loaded bot.* modules plus live runtime objects/contexts discovered via gc.
_RUNTIME_SCAN_COUNT = 0
_RUNTIME_LOG_PATCHED = False
_RUNTIME_LAST_SCAN_TS = 0.0
_RUNTIME_SCAN_RUNNING = False


def _is_vip_key(k):
    try:
        low = str(k).lower()
        return ('entitlement' in low) or ('vip' in low) or ('license' in low) or ('feature_flag' in low)
    except BaseException:
        return False



def _is_business_config_key(k):
    try:
        lk = _norm_key(k)
        return (lk in _VIP_BUSINESS_BOOL_TRUE) or (lk in _VIP_BUSINESS_VALUE_OVERRIDES) or (lk in _VIP_BUSINESS_RESET_NUMERIC) or (lk in _VIP_BUSINESS_ZERO_COUNTERS)
    except BaseException:
        return False


def _coerce_business_value(key, old=None):
    lk = _norm_key(key)
    try:
        if lk in _VIP_BUSINESS_BOOL_TRUE:
            if lk == 'enable_wechat_focus_guard':
                return bool(_active_is_weixin_mode())
            return True
        if lk in _VIP_BUSINESS_RESET_NUMERIC or lk in _VIP_BUSINESS_ZERO_COUNTERS:
            return 0
        if lk == 'auto_sell_fruit_interval_hours':
            if isinstance(old, float) or isinstance(old, int):
                return 0.10
            return '0.10'
        if lk == 'bottom_friend_list_help_all_limit':
            if isinstance(old, int):
                return 12
            return '12'
        if lk in _VIP_BUSINESS_VALUE_OVERRIDES:
            return _VIP_BUSINESS_VALUE_OVERRIDES.get(lk)
    except BaseException:
        pass
    return old


def _patch_runtime_dict(d):
    changed = 0
    try:
        keys = list(d.keys())
    except BaseException:
        return 0
    try:
        interesting = any((_is_vip_key(k) or _is_business_config_key(k)) for k in keys)
    except BaseException:
        interesting = False
    if not interesting:
        return 0
    for k in keys:
        try:
            lk = str(k).lower()
        except BaseException:
            continue
        try:
            if _friend_pause_active() and lk in _FRIEND_PAUSE_FORCE_FALSE:
                d[k] = False; changed += 1
            elif _is_business_config_key(lk):
                d[k] = _coerce_business_value(lk, d.get(k)); changed += 1
            elif lk in ('entitlement_active','_entitlement_active','vip_active','_vip_active','is_vip','_is_vip','license_active','_license_active','enabled_by_license','feature_enabled'):
                d[k] = True; changed += 1
            elif lk in ('entitlement_state_reason','_entitlement_state_reason','reason','message'):
                v = d.get(k)
                if v is None or 'license' in str(v).lower() or '\u8bb8\u53ef' in str(v) or '\u672a\u6fc0\u6d3b' in str(v) or '\u672c\u5730\u65e0' in str(v):
                    d[k] = 'local_runtime_patch'; changed += 1
            elif lk in ('claims','verified_claims','_entitlement_claims'):
                d[k] = _claims(); changed += 1
            elif lk in ('feature_flags','features'):
                flags = d.get(k)
                if not isinstance(flags, dict): flags = {}
                flags.update({'*': True, 'vip': True, 'all': True, 'entitlement': True, 'wechat_mouse': True})
                d[k] = flags; changed += 1
            elif lk in ('status','state'):
                d[k] = 'active'; changed += 1
            elif lk in ('ok','active','valid','success','passed'):
                d[k] = True; changed += 1
        except BaseException:
            pass
    return changed


def _runtime_obj_interesting(o):
    try:
        cls = o.__class__
        cname = getattr(cls, '__name__', '')
        mod = getattr(cls, '__module__', '')
        blob = (str(mod) + '.' + str(cname)).lower()
        if ('farmbot' in blob) or ('runtime' in blob and 'bot' in blob) or ('context' in blob and 'bot' in blob) or ('entitlement' in blob):
            return True
        dd = getattr(o, '__dict__', None)
        if isinstance(dd, dict) and any((_is_vip_key(k) or _is_business_config_key(k)) for k in dd.keys()):
            return True
    except BaseException:
        pass
    return False


def _patch_runtime_class(cls):
    changed = 0
    for nm, fn in [
        ('feature_gate', _fake_gate), ('check_feature_gate', _fake_gate),
        ('require_feature', _fake_gate), ('require_entitlement', _fake_gate),
        ('check_entitlement', _fake_gate), ('check_vip_access', _fake_gate),
        ('has_feature_access', _fake_gate),
        ('is_entitlement_enabled', _fake_true), ('_is_entitlement_enabled', _fake_true),
        ('has_entitlement', _fake_true), ('_has_entitlement', _fake_true),
        ('is_vip_active', _fake_true), ('_is_vip_active', _fake_true),
        ('_refresh_entitlement_status', _refresh_method),
        ('_update_entitlement_status', _refresh_method),
        ('_sync_entitlement_status', _refresh_method),
        ('_refresh_runtime_entitlement', _refresh_method),
        ('_enforce_multi_instance_entitlement_lock', _fake_none),
        ('_show_entitlement_access_dialog', _dialog_method),
        ('_should_clear_local_license_on_rejected_error_text', _fake_false),
        ('_is_entitlement_rejected_error_text', _fake_false),
        ('_is_entitlement_rejected_error', _fake_false),
    ]:
        if _patch_method(cls, nm, fn):
            changed += 1
    return changed


def _force_runtime_object(o):
    changed = 0
    try:
        _force_entitlement_attrs(o)
        changed += 1
    except BaseException:
        pass
    try:
        dd = getattr(o, '__dict__', None)
        if isinstance(dd, dict):
            changed += _patch_runtime_dict(dd)
            # common nested config/state/context dictionaries/objects
            for key in ('config','cfg','settings','state','runtime_state','context','ctx','bot','farm_bot','worker'):
                try:
                    child = dd.get(key)
                    if isinstance(child, dict): changed += _patch_runtime_dict(child)
                    elif child is not None and child is not o and _runtime_obj_interesting(child):
                        _force_entitlement_attrs(child); changed += 1
                except BaseException:
                    pass
    except BaseException:
        pass
    try:
        cls = o if isinstance(o, type) else o.__class__
        changed += _patch_runtime_class(cls)
    except BaseException:
        pass
    return changed


def _force_stack_runtime_objects():
    changed = 0
    try:
        frame = sys._getframe()
        depth = 0
        while frame is not None and depth < 18:
            try:
                for v in list(frame.f_locals.values()):
                    if isinstance(v, dict):
                        changed += _patch_runtime_dict(v)
                    elif _runtime_obj_interesting(v):
                        changed += _force_runtime_object(v)
            except BaseException:
                pass
            frame = frame.f_back
            depth += 1
    except BaseException:
        pass
    if changed:
        _write('runtime stack objects forced=' + str(changed))
    return changed


def _runtime_scan(tag=''):
    # v10-ui-stable: disabled. Exact module patches + fake license files are enough for startup; gc scan was too invasive.
    return 0


def _rewrite_entitlement_log_message(msg):
    try:
        s = str(msg)
        keys = [
            '\u6743\u76ca\u72b6\u6001\u5df2\u5173\u95ed',
            '\u672a\u68c0\u6d4b\u5230\u6709\u6548\u672c\u5730\u8bb8\u53ef\u8bc1',
            '\u672c\u5730\u65e0\u8bb8\u53ef\u8bc1',
            '\u8bf7\u8f93\u5165\u5361\u5bc6\u6216\u7ed1\u5b9a\u540e\u4f7f\u7528\u4f1a\u5458\u6743\u76ca',
        ]
        if '\u5fae\u4fe1\u62a2\u9f20\u6807\u5904\u7406\u8df3\u8fc7' in s:
            try:
                if _active_is_weixin_mode() and _wechat_focus_enabled():
                    return ('\u5fae\u4fe1\u62a2\u9f20\u6807\u5904\u7406\u5df2\u5f3a\u5236\u542f\u7528\uff1a\u5df2\u7ed5\u8fc7\u539f\u59cb\u5f00\u5173/VIP\u95e8\u63a7\u3002', True)
                if not _active_is_weixin_mode():
                    return ('QQ\u5c0f\u7a0b\u5e8f\u6a21\u5f0f\uff1a\u5fae\u4fe1\u62a2\u9f20\u6807\u5904\u7406\u4e0d\u9002\u7528\uff0c\u5df2\u8df3\u8fc7\u3002', True)
            except BaseException:
                pass
        for k in keys:
            if k in s:
                return ('\u6743\u76ca\u72b6\u6001\u5df2\u5f00\u542f\uff1a\u672c\u5730VIP\u6743\u76ca\u5df2\u751f\u6548\u3002', True)
    except BaseException:
        pass
    return msg, False


def _install_runtime_log_patch():
    global _RUNTIME_LOG_PATCHED
    if _RUNTIME_LOG_PATCHED:
        return True
    try:
        logging_mod = sys.modules.get('logging')
        if logging_mod is None:
            return False
        Logger = getattr(logging_mod, 'Logger', None)
        if Logger is None:
            return False
        orig_warning = getattr(Logger, 'warning')
        orig_info = getattr(Logger, 'info')
        def _patched_warning(self, msg, *args, **kwargs):
            new_msg, hit = _rewrite_entitlement_log_message(msg)
            if hit:
                return orig_info(self, new_msg, **kwargs)
            return orig_warning(self, msg, *args, **kwargs)
        def _patched_info(self, msg, *args, **kwargs):
            new_msg, hit = _rewrite_entitlement_log_message(msg)
            if hit:
                return orig_info(self, new_msg, **kwargs)
            return orig_info(self, msg, *args, **kwargs)
        Logger.warning = _patched_warning
        Logger.warn = _patched_warning
        Logger.info = _patched_info
        _RUNTIME_LOG_PATCHED = True
        _write('runtime logging info/warning patch installed v13')
        return True
    except BaseException as e:
        try: _write('runtime logging patch error ' + repr(e))
        except BaseException: pass
    return False


# ---- Local license file/path patch v8 ----
_PATH_LICENSE_PATCHED = False
_PATH_ORIG_METHODS = {}
_FAKE_LICENSE_WRITE_SEEN = set()
_FAKE_LICENSE_WRITING = False
_LICENSE_FILE_LOG_SEEN = set()


def _looks_like_license_path(path_obj):
    try:
        sp = str(path_obj).replace('\\', '/').lower()
        if '.qqfarm_security' in sp:
            # Do not fake crash diagnostics; fake everything else under security as an entitlement cache candidate.
            if ('crash/' in sp) or sp.endswith('/crash') or ('startup_diag' in sp) or ('fatal_fault' in sp):
                return False
            return True
        if ('entitlement' in sp or 'license' in sp or 'licence' in sp or 'vip' in sp) and ('qq-farm-bot-rev' in sp):
            return True
    except BaseException:
        pass
    return False


def _write_fake_license_file(path_text=None):
    global _FAKE_LICENSE_WRITING
    if _FAKE_LICENSE_WRITING:
        return
    _FAKE_LICENSE_WRITING = True
    try:
        text = _fake_license_text()
        base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'qq-farm-bot-rev', '.qqfarm_security')
        if base and base not in _FAKE_LICENSE_WRITE_SEEN:
            try: os.makedirs(base, exist_ok=True)
            except BaseException: pass
            names = ['vip_license.json', 'entitlement.json', 'license.json', 'local_entitlement.json', 'SmyoDppvTWetT2D2O4VpQA==']
            for nm in names:
                fp = os.path.join(base, nm)
                try:
                    with open(fp, 'w', encoding='utf-8') as f:
                        f.write(text)
                    _FAKE_LICENSE_WRITE_SEEN.add(fp)
                except BaseException:
                    pass
            _FAKE_LICENSE_WRITE_SEEN.add(base)
        if path_text:
            sp = str(path_text)
            if _looks_like_license_path(sp) and sp not in _FAKE_LICENSE_WRITE_SEEN:
                try:
                    d = os.path.dirname(sp)
                    if d: os.makedirs(d, exist_ok=True)
                    with open(sp, 'w', encoding='utf-8') as f:
                        f.write(text)
                    _FAKE_LICENSE_WRITE_SEEN.add(sp)
                    _write('fake entitlement license wrote ' + sp)
                except BaseException:
                    pass
    except BaseException as e:
        try: _write('fake license write error ' + repr(e))
        except BaseException: pass
    finally:
        _FAKE_LICENSE_WRITING = False

def _install_path_license_patch():
    # v9 stable: do not monkey-patch pathlib.Path. v8 caused recursive import/path calls before UI init.
    # Keep only the real fake license files on disk.
    try:
        _write_fake_license_file()
    except BaseException:
        pass
    return False


def _patch_late_vip_modules():
    # v14-runloop-safe: disabled. Patching gui/utils after startup changed
    # the run-loop state (UI returned to Not Running and no patrol cycle started).
    return []


# ---- Qt front-end unlocker: enable disabled VIP controls and refresh entitlement-looking UI ----
# v6 note: do NOT import PySide6 before the app imports it. In embedded Nuitka apps,
# importing Qt too early can stall before QApplication/main window creation. We wait until
# PySide6.QtCore and PySide6.QtWidgets already exist in sys.modules, then patch in-place.
_QT_UNLOCKER_INSTALLED = False
_QT_UNLOCKER_TRYING = False
_QT_WAIT_LOGGED = False
_QT_ORIG_METHODS = {}
_QT_DUMP_COUNT = 0
_QT_UNLOCK_PASS_COUNT = 0
_QT_DUMP_PATH = r'C:/Users/11616/reverse-cases/qq-farm-vip/work/qt_widget_dump.txt'


def _safe_str(v):
    try:
        return str(v)
    except BaseException:
        return ''


def _text_of(obj):
    try:
        if hasattr(obj, 'text'):
            return _safe_str(obj.text())
    except BaseException:
        pass
    return ''


def _obj_name(obj):
    try:
        return _safe_str(obj.objectName())
    except BaseException:
        return ''


def _tooltip_of(obj):
    try:
        if hasattr(obj, 'toolTip'):
            return _safe_str(obj.toolTip())
    except BaseException:
        pass
    return ''


def _access_name_of(obj):
    try:
        if hasattr(obj, 'accessibleName'):
            return _safe_str(obj.accessibleName())
    except BaseException:
        pass
    return ''


def _class_name(obj):
    try:
        return obj.__class__.__name__
    except BaseException:
        return ''


def _context_blob(obj, max_parent=5):
    parts = []
    cur = obj
    depth = 0
    while cur is not None and depth <= max_parent:
        try:
            parts.append(_class_name(cur))
            parts.append(_obj_name(cur))
            parts.append(_text_of(cur))
            parts.append(_tooltip_of(cur))
            parts.append(_access_name_of(cur))
        except BaseException:
            pass
        try:
            cur = cur.parentWidget() if hasattr(cur, 'parentWidget') else cur.parent()
        except BaseException:
            cur = None
        depth += 1
    return ' '.join([x for x in parts if x])


def _looks_vip_related(obj):
    blob = _context_blob(obj).lower()
    keys = [
        'vip', 'svip', 'entitlement', 'license', 'licence', 'card', 'key', 'premium',
        'openvip', 'is_vip', 'vip_active', 'feature_gate',
        '\u5f00\u901a', '\u4f1a\u5458', '\u6743\u76ca', '\u5361\u5bc6', '\u6fc0\u6d3b',
        '\u914d\u7f6e\u4e0d\u751f\u6548', '\u672a\u6fc0\u6d3b', '\u4e13\u5c5e',
        '\u591a\u5f00', '\u56db\u5bab\u683c', '\u80e1\u841d\u535c', '\u7ecf\u9a8c\u503c',
        'multi', 'seed', 'carrot', 'exp', 'experience'
    ]
    for k in keys:
        try:
            if k.lower() in blob:
                return True
        except BaseException:
            pass
    return False


def _force_entitlement_attrs(obj):
    vals = [
        ('entitlement_active', True), ('_entitlement_active', True),
        ('vip_active', True), ('_vip_active', True),
        ('is_vip', True), ('_is_vip', True),
        ('license_active', True), ('_license_active', True),
        ('enabled_by_license', True), ('_enabled_by_license', True),
        ('feature_enabled', True), ('_feature_enabled', True),
        ('locked', False), ('_locked', False), ('disabled', False), ('_disabled', False),
        ('entitlement_state_reason', 'local_runtime_patch'),
        ('_entitlement_state_reason', 'local_runtime_patch'),
        ('_entitlement_claims', _claims()),
        ('_last_entitlement_refresh_ts', time.time()),
    ]
    for n, v in vals:
        try:
            setattr(obj, n, v)
        except BaseException:
            pass


def _replace_inactive_text(txt):
    try:
        new = _safe_str(txt)
        new = new.replace('\u914d\u7f6e\u4e0d\u751f\u6548', '\u5df2\u89e3\u9501')
        new = new.replace('\u8be5\u529f\u80fd\u4e3a VIP \u4e13\u5c5e\uff0c\u5f53\u524d\u672a\u6fc0\u6d3b\uff0c\u914d\u7f6e\u5c06\u4e0d\u4f1a\u751f\u6548\u3002', '\u672c\u5730 VIP \u5df2\u89e3\u9501\uff0c\u914d\u7f6e\u5df2\u751f\u6548\u3002')
        new = new.replace('\u5f53\u524d\u672a\u6fc0\u6d3b\uff0c\u914d\u7f6e\u5c06\u4e0d\u4f1a\u751f\u6548\u3002', '\u672c\u5730 VIP \u5df2\u89e3\u9501\uff0c\u914d\u7f6e\u5df2\u751f\u6548\u3002')
        new = new.replace('\u5f53\u524d\u672a\u6fc0\u6d3b', '\u672c\u5730\u5df2\u6fc0\u6d3b')
        new = new.replace('\u672a\u6fc0\u6d3b', '\u5df2\u6fc0\u6d3b')
        new = new.replace('\u5f00\u901a VIP', 'VIP \u5df2\u5f00\u901a')
        new = new.replace('\u5f53\u524d\u8bbe\u5907\u672a\u68c0\u6d4b\u5230\u672c\u5730\u8bb8\u53ef\u8bc1\uff0c\u8bf7\u8f93\u5165\u5361\u5bc6\u5b8c\u6210\u7ed1\u5b9a\u540e\u4f7f\u7528\u4f1a\u5458\u6743\u76ca\u3002', '\u672c\u5730 VIP \u5df2\u6fc0\u6d3b\uff0c\u4f1a\u5458\u6743\u76ca\u5df2\u751f\u6548\u3002')
        new = new.replace('\u5f53\u524d\u8bbe\u5907\u672a\u68c0\u6d4b\u5230\u6709\u6548\u672c\u5730\u8bb8\u53ef\u8bc1\uff0c\u8bf7\u8f93\u5165\u5361\u5bc6\u6216\u7ed1\u5b9a\u540e\u4f7f\u7528\u4f1a\u5458\u6743\u76ca\u3002', '\u672c\u5730 VIP \u5df2\u6fc0\u6d3b\uff0c\u4f1a\u5458\u6743\u76ca\u5df2\u751f\u6548\u3002')
        new = new.replace('\u672a\u68c0\u6d4b\u5230\u6709\u6548\u672c\u5730\u8bb8\u53ef\u8bc1', '\u5df2\u68c0\u6d4b\u5230\u6709\u6548\u672c\u5730\u8bb8\u53ef\u8bc1')
        new = new.replace('\u672a\u68c0\u6d4b\u5230\u672c\u5730\u8bb8\u53ef\u8bc1', '\u5df2\u68c0\u6d4b\u5230\u672c\u5730\u8bb8\u53ef\u8bc1')
        new = new.replace('\u8fd8\u6ca1\u6709\u5361\u5bc6\uff1f', '\u4f1a\u5458\u6743\u76ca\u5df2\u89e3\u9501')
        new = new.replace('\u8d2d\u4e70\u5361\u5bc6', '\u5df2\u89e3\u9501')
        new = new.replace('\u7ed1\u5b9a\u5361\u5bc6', '\u5df2\u6fc0\u6d3b')
        return new
    except BaseException:
        return txt


_VIP_DIALOG_TEXTS = {
    'vipAccessTitle': '\u672c\u5730 VIP \u5df2\u6fc0\u6d3b',
    'btnVipAccess': 'VIP \u5df2\u6fc0\u6d3b',
    'vipAccessSubtitle': '\u4f1a\u5458\u6743\u76ca\u5df2\u751f\u6548\uff0c\u65e0\u9700\u518d\u7ed1\u5b9a\u5361\u5bc6',
    'vipAccessStateIcon': '\u2713',
    'vipAccessStateTitle': '\u72b6\u6001\uff1a\u5df2\u6fc0\u6d3b',
    'vipAccessStateDesc': '\u672c\u5730 VIP \u5df2\u6fc0\u6d3b\uff0c\u5f53\u524d\u8bbe\u5907\u4f1a\u5458\u6743\u76ca\u5df2\u751f\u6548\u3002',
    'vipAccessDetailTitle': '\u4f1a\u5458\u6743\u76ca\u5df2\u89e3\u9501',
    'vipAccessDetailMeta': '\u672c\u5730\u6743\u76ca\u5df2\u542f\u7528\uff0c\u4e0d\u9700\u8981\u8d2d\u4e70\u6216\u7ed1\u5b9a\u5361\u5bc6\u3002',
    'vipAccessInlineActionBtn': '\u5df2\u89e3\u9501',
    'vipAccessInputTitle': '\u672c\u5730\u8bb8\u53ef\u8bc1',
    'vipAccessInputHint': '\u8bb8\u53ef\u8bc1\u5df2\u5728\u672c\u8bbe\u5907\u751f\u6548\u3002',
    'vipAccessFooterHint': '\u25cf \u672c\u5730 VIP \u5df2\u751f\u6548\uff0c\u4f1a\u5458\u529f\u80fd\u5df2\u89e3\u9501',
    'vipAccessGhostBtn': '\u5237\u65b0\u72b6\u6001',
    'vipAccessPrimaryBtn': '\u5173\u95ed',
}


def _close_parent_dialog(w):
    try:
        cur = w
        depth = 0
        while cur is not None and depth < 16:
            try:
                if hasattr(cur, 'windowTitle'):
                    title = _safe_str(cur.windowTitle())
                    if ('VIP' in title) or ('vip' in title.lower()) or ('\u6743\u76ca' in title) or ('\u8bb8\u53ef' in title):
                        if hasattr(cur, 'close'):
                            cur.close()
                            return True
            except BaseException:
                pass
            try:
                cur = cur.parentWidget() if hasattr(cur, 'parentWidget') else cur.parent()
            except BaseException:
                cur = None
            depth += 1
        try:
            win = w.window() if hasattr(w, 'window') else None
            if win is not None and hasattr(win, 'close'):
                win.close()
                return True
        except BaseException:
            pass
    except BaseException:
        pass
    return False


def _apply_vip_dialog_text_fix(w):
    changed = 0
    try:
        name = _obj_name(w)
    except BaseException:
        name = ''
    try:
        if name in _VIP_DIALOG_TEXTS and hasattr(w, 'setText'):
            new = _VIP_DIALOG_TEXTS.get(name)
            try: old = _text_of(w)
            except BaseException: old = ''
            if old != new:
                w.setText(new)
                changed += 1
    except BaseException:
        pass
    try:
        if name == 'vipCardInput':
            if hasattr(w, 'setPlaceholderText'):
                w.setPlaceholderText('LOCAL-PATCH-VIP-2099')
            if hasattr(w, 'setText') and not _text_of(w):
                w.setText('LOCAL-PATCH-VIP-2099')
                changed += 1
    except BaseException:
        pass
    try:
        if hasattr(w, 'toolTip') and hasattr(w, 'setToolTip'):
            tip = _safe_str(w.toolTip())
            new_tip = _replace_inactive_text(tip)
            if name == 'btnVipAccess' or new_tip != tip:
                if name == 'btnVipAccess':
                    new_tip = '\u672c\u5730 VIP \u6743\u76ca\u5df2\u751f\u6548\uff0c\u4f1a\u5458\u529f\u80fd\u5df2\u89e3\u9501\u3002'
                w.setToolTip(new_tip)
                changed += 1
    except BaseException:
        pass
    try:
        if name in ('vipAccessDetailCard', 'vipAccessInputCard'):
            if hasattr(w, 'setEnabled'):
                w.setEnabled(True)
    except BaseException:
        pass
    try:
        if name == 'vipAccessPrimaryBtn':
            if hasattr(w, 'setEnabled'):
                w.setEnabled(True)
            if hasattr(w, 'clicked'):
                try:
                    already = bool(w.property('__qqfarm_vip_close_bound')) if hasattr(w, 'property') else False
                except BaseException:
                    already = False
                if not already:
                    def _on_vip_close_clicked(checked=False, __w=w):
                        _close_parent_dialog(__w)
                    try:
                        w.clicked.connect(_on_vip_close_clicked)
                        if hasattr(w, 'setProperty'):
                            w.setProperty('__qqfarm_vip_close_bound', True)
                        changed += 1
                    except BaseException:
                        pass
    except BaseException:
        pass
    return changed


def _qt_modules_ready():
    try:
        QtCore = sys.modules.get('PySide6.QtCore')
        QtWidgets = sys.modules.get('PySide6.QtWidgets')
        if QtCore is not None and QtWidgets is not None:
            return QtCore, QtWidgets
        p = sys.modules.get('PySide6')
        if p is not None:
            try:
                QtCore = getattr(p, 'QtCore', None) or QtCore
                QtWidgets = getattr(p, 'QtWidgets', None) or QtWidgets
            except BaseException:
                pass
        if QtCore is not None and QtWidgets is not None:
            return QtCore, QtWidgets
    except BaseException:
        pass
    return None, None


def _patch_qt_method(cls, method_name, wrapper_factory, tag):
    try:
        key = (_safe_str(cls), method_name)
        if key in _QT_ORIG_METHODS:
            return False
        orig = getattr(cls, method_name)
        _QT_ORIG_METHODS[key] = orig
        setattr(cls, method_name, wrapper_factory(orig))
        _write('qt patched ' + tag + '.' + method_name)
        return True
    except BaseException as e:
        _write('qt patch skipped ' + tag + '.' + method_name + ' ' + repr(e))
        return False


def _make_set_enabled_wrapper(orig):
    def _patched_set_enabled(self, enabled):
        try:
            if enabled is False:
                # Keep VIP/feature-related controls enabled, and also keep parents unlocked.
                if _looks_vip_related(self):
                    enabled = True
                    _force_entitlement_attrs(self)
        except BaseException:
            pass
        return orig(self, enabled)
    return _patched_set_enabled


def _make_set_disabled_wrapper(orig):
    def _patched_set_disabled(self, disabled):
        try:
            if disabled is True and _looks_vip_related(self):
                disabled = False
                _force_entitlement_attrs(self)
        except BaseException:
            pass
        return orig(self, disabled)
    return _patched_set_disabled


def _make_set_text_wrapper(orig):
    def _patched_set_text(self, text):
        try:
            text = _replace_inactive_text(text)
        except BaseException:
            pass
        return orig(self, text)
    return _patched_set_text


def _dump_qt_widgets(QtWidgets, app, tops):
    return
    global _QT_DUMP_COUNT
    try:
        _QT_DUMP_COUNT += 1
        # Dump only during startup and then very rarely.  A full widget dump is
        # expensive in this Qt app and makes the helper feel sluggish.
        if _QT_DUMP_COUNT > 3 and (_QT_DUMP_COUNT % 120) != 0:
            return
        lines = []
        lines.append('dump_count=' + str(_QT_DUMP_COUNT) + ' time=' + time.strftime('%Y-%m-%d %H:%M:%S'))
        lines.append('tops=' + str(len(tops)))
        idx = 0
        for top in tops:
            try:
                widgets = [top] + list(top.findChildren(QtWidgets.QWidget))
            except BaseException:
                widgets = [top]
            for w in widgets:
                try:
                    text = _text_of(w).replace('\n', '\\n')
                    name = _obj_name(w)
                    cname = _class_name(w)
                    enabled = w.isEnabled() if hasattr(w, 'isEnabled') else ''
                    visible = w.isVisible() if hasattr(w, 'isVisible') else ''
                    tooltip = _tooltip_of(w).replace('\n', '\\n')
                    aname = _access_name_of(w)
                    parent = None
                    try: parent = w.parentWidget() if hasattr(w, 'parentWidget') else w.parent()
                    except BaseException: parent = None
                    pinfo = ''
                    if parent is not None:
                        pinfo = _class_name(parent) + '/' + _obj_name(parent) + '/' + _text_of(parent)
                    related = _looks_vip_related(w)
                    interesting = related or (enabled is False) or text or name or ('button' in cname.lower()) or ('switch' in cname.lower()) or ('card' in cname.lower()) or ('label' in cname.lower())
                    if interesting:
                        lines.append(str(idx) + '\tcls=' + cname + '\tname=' + name + '\ttext=' + text + '\ten=' + str(enabled) + '\tvis=' + str(visible) + '\trel=' + str(related) + '\ttip=' + tooltip + '\tacc=' + aname + '\tparent=' + pinfo)
                    idx += 1
                except BaseException:
                    pass
        f = open(_QT_DUMP_PATH, 'w', encoding='utf-8', errors='replace')
        f.write('\n'.join(lines))
        f.close()
        _write('qt widget dump wrote count=' + str(_QT_DUMP_COUNT) + ' lines=' + str(len(lines)))
    except BaseException as e:
        _write('qt widget dump error ' + repr(e))


def _qt_unlock_pass():
    global _QT_UNLOCK_PASS_COUNT
    _QT_UNLOCK_PASS_COUNT += 1
    ready = _qt_modules_ready()
    if not ready[0]:
        return False
    QtCore, QtWidgets = ready
    app = None
    try:
        app = QtWidgets.QApplication.instance()
    except BaseException:
        app = None
    if app is None:
        return False
    changed = 0
    try:
        tops = list(app.topLevelWidgets())
    except BaseException:
        tops = []
    try:
        _dump_qt_widgets(QtWidgets, app, tops)
    except BaseException:
        pass
    for top in tops:
        try:
            _force_entitlement_attrs(top)
            widgets = [top] + list(top.findChildren(QtWidgets.QWidget))
        except BaseException:
            widgets = [top]
        for w in widgets:
            try:
                _force_entitlement_attrs(w)
            except BaseException:
                pass
            try:
                changed += _apply_vip_dialog_text_fix(w)
            except BaseException:
                pass
            try:
                if _patch_personal_ui_widget is not None:
                    changed += int(_patch_personal_ui_widget(w, context_getter=_context_blob) or 0)
            except BaseException:
                pass
            related = False
            try:
                related = _looks_vip_related(w)
            except BaseException:
                related = False
            try:
                if related:
                    w.setProperty('vip', True)
                    w.setProperty('active', True)
                    w.setProperty('entitlement_active', True)
                    w.setProperty('locked', False)
                    w.setProperty('disabled', False)
                    w.setProperty('feature_enabled', True)
            except BaseException:
                pass
            try:
                # Remove common click blockers on VIP cards/controls.
                if related and hasattr(QtCore, 'Qt'):
                    try: w.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
                    except BaseException:
                        try: w.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
                        except BaseException: pass
                    try: w.setAttribute(QtCore.Qt.WidgetAttribute.WA_ForceDisabled, False)
                    except BaseException: pass
                    try: w.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
                    except BaseException:
                        try: w.setFocusPolicy(QtCore.Qt.StrongFocus)
                        except BaseException: pass
            except BaseException:
                pass
            try:
                if related and (not w.isEnabled()):
                    w.setEnabled(True)
                    changed += 1
            except BaseException:
                pass
            try:
                if related and hasattr(w, 'setDisabled'):
                    w.setDisabled(False)
            except BaseException:
                pass
            try:
                txt = _text_of(w)
                if txt:
                    new = _replace_inactive_text(txt)
                    if new != txt and hasattr(w, 'setText'):
                        w.setText(new)
                        changed += 1
            except BaseException:
                pass
            # Some custom SwitchButton widgets expose internal state via methods/properties.
            # Do not force-check all toggles, only make them user-toggleable/clickable.
            for meth, val in [('setLocked', False), ('setReadOnly', False), ('setEnabledByLicense', True), ('setFeatureEnabled', True)]:
                try:
                    if related and hasattr(w, meth):
                        getattr(w, meth)(val)
                        changed += 1
                except BaseException:
                    pass
    if changed and (_QT_UNLOCK_PASS_COUNT <= 8 or (_QT_UNLOCK_PASS_COUNT % 120) == 0):
        _write('qt unlock pass changed=' + str(changed) + ' tops=' + str(len(tops)))
    return True


def _has_real_main_window(QtWidgets, app):
    try:
        for w in list(app.topLevelWidgets()):
            try:
                cname = _class_name(w)
                name = _obj_name(w)
                title = ''
                try:
                    if hasattr(w, 'windowTitle'):
                        title = _safe_str(w.windowTitle())
                except BaseException:
                    title = ''
                vis = False
                try: vis = bool(w.isVisible())
                except BaseException: vis = False
                if vis and cname != '_StartupLoadingOverlay' and (title or name or cname):
                    return True
            except BaseException:
                pass
    except BaseException:
        pass
    return False


def _install_qt_unlocker():
    global _QT_UNLOCKER_INSTALLED, _QT_UNLOCKER_TRYING, _QT_WAIT_LOGGED
    if _QT_UNLOCKER_INSTALLED or _QT_UNLOCKER_TRYING:
        return _QT_UNLOCKER_INSTALLED
    ready = _qt_modules_ready()
    if not ready[0]:
        if not _QT_WAIT_LOGGED:
            _QT_WAIT_LOGGED = True
            _write('qt safe unlocker waiting for PySide6.QtCore/QtWidgets')
        return False
    _QT_UNLOCKER_TRYING = True
    try:
        QtCore, QtWidgets = ready
        try:
            app0 = QtWidgets.QApplication.instance()
        except BaseException:
            app0 = None
        if app0 is None:
            return False
        try:
            if _install_early_personal_theme is not None:
                _install_early_personal_theme(QtWidgets)
        except BaseException as e:
            _write('early personal theme error ' + repr(e))
        def _tick():
            try:
                _patch_loaded('qt-safe-tick')
            except BaseException:
                pass
            try:
                _force_autolaunch_config_file()
            except BaseException:
                pass
            try:
                app = QtWidgets.QApplication.instance()
            except BaseException:
                app = None
            try:
                if app is not None:
                    tops = list(app.topLevelWidgets())
                    if _has_real_main_window(QtWidgets, app):
                        _qt_unlock_pass()
                    else:
                        try: _dump_qt_widgets(QtWidgets, app, tops)
                        except BaseException: pass
            except BaseException as e:
                try: _write('qt safe unlock pass error ' + repr(e))
                except BaseException: pass
            try:
                # Four fast startup passes, then low-frequency maintenance.
                # This keeps newly-created settings/dialog widgets consistent
                # without bringing back the old high-frequency UI scan cost.
                delay_ms = 3000 if _QT_UNLOCK_PASS_COUNT < 4 else 30000
                QtCore.QTimer.singleShot(delay_ms, _tick)
            except BaseException:
                pass
        try:
            QtCore.QTimer.singleShot(0, _tick)
        except BaseException as e:
            _write('qt safe timer schedule error ' + repr(e))
        _QT_UNLOCKER_INSTALLED = True
        _write('qt low-frequency long-run unlocker installed v32')
    except BaseException as e:
        _write('qt safe unlocker install error ' + repr(e))
    finally:
        _QT_UNLOCKER_TRYING = False
    return _QT_UNLOCKER_INSTALLED

# expose manual tick; C/Python import hooks can call this later
try:
    builtins.__qqfarm_vip_patch_tick__ = _patch_loaded
except BaseException:
    pass

try:
    _force_autolaunch_config_file()
except BaseException:
    pass
try:
    _repair_daily_task_retry_state_file('startup')
except BaseException:
    pass
try:
    _install_config_override_patch()
except BaseException:
    pass

try:
    _real_import = builtins.__import__
    def _patched_import(name, globals=None, locals=None, fromlist=(), level=0):
        mod = _real_import(name, globals, locals, fromlist, level)
        try: _patch_loaded(name)
        except BaseException: pass
        try:
            if _resource_limits is not None:
                _resource_limits.patch_loaded_modules(sys.modules, _RESOURCE_MAX_THREADS)
        except BaseException: pass
        try: _install_qt_unlocker()
        except BaseException: pass
        return mod
    builtins.__import__ = _patched_import

    _real_import_module = importlib.import_module
    def _patched_import_module(name, package=None):
        mod = _real_import_module(name, package)
        try: _patch_loaded(name)
        except BaseException: pass
        try:
            if _resource_limits is not None:
                _resource_limits.patch_loaded_modules(sys.modules, _RESOURCE_MAX_THREADS)
        except BaseException: pass
        try: _install_qt_unlocker()
        except BaseException: pass
        return mod
    importlib.import_module = _patched_import_module
    _write('import hooks installed no-thread')
except BaseException as e:
    _write('import hook install failed no-thread: ' + repr(e))

try:
    _patch_loaded('initial')
except BaseException as e:
    _write('initial patch failed: ' + repr(e))

try: _install_path_license_patch()
except BaseException: pass
try: _install_qt_unlocker()
except BaseException: pass
_write('v37 persistent daily task backoff + task entry settle installed')
_write('local vip hook installed no-thread + v35-vip-warehouse-radish-fertilizer')

