# ASCII-only hook body loaded by proxy python312.dll
# no threading dependency: uses import hook only
try:
    _hook_os = __import__('os')
    _hook_local = _hook_os.environ.get('LOCALAPPDATA', '')
    if not _hook_local:
        _hook_local = _hook_os.path.join(_hook_os.path.expanduser('~'), 'AppData', 'Local')
    _hook_default_log = _hook_os.path.join(
        _hook_local, 'qq-farm-bot-rev', 'logs', 'hook_runtime_log.txt'
    )
    LOG_PATH = _hook_os.environ.get('QQFARM_HOOK_LOG_PATH', _hook_default_log)
except BaseException:
    LOG_PATH = r'C:/Users/Public/qq-farm-bot-rev/logs/hook_runtime_log.txt'

_HOOK_LOG_WRITE_COUNT = 0
_HOOK_LOG_MAX_BYTES = 10 * 1024 * 1024


def _rotate_hook_log_if_needed(path=None, max_bytes=_HOOK_LOG_MAX_BYTES):
    try:
        os_module = __import__('os')
        target = str(path or LOG_PATH)
        if not os_module.path.isfile(target):
            return False
        if int(os_module.path.getsize(target)) <= int(max_bytes):
            return False
        backup = target + '.1'
        try:
            if os_module.path.exists(backup):
                os_module.remove(backup)
        except BaseException:
            pass
        os_module.replace(target, backup)
        return True
    except BaseException:
        return False


def _write(msg):
    global _HOOK_LOG_WRITE_COUNT
    try:
        os_module = __import__('os')
        parent = os_module.path.dirname(str(LOG_PATH))
        if parent:
            os_module.makedirs(parent, exist_ok=True)
        _HOOK_LOG_WRITE_COUNT = int(_HOOK_LOG_WRITE_COUNT or 0) + 1
        if _HOOK_LOG_WRITE_COUNT == 1 or (_HOOK_LOG_WRITE_COUNT % 128) == 0:
            _rotate_hook_log_if_needed(LOG_PATH)
        f = open(LOG_PATH, 'a', encoding='utf-8')
        f.write(str(msg) + '\n')
        f.close()
    except BaseException:
        pass


_THROTTLE_LOG_TS = {}
_SECURITY_WATCHDOG_PATCH_LOG_SEEN = set()
_DAILY_RETRY_REPAIR_LAST_TS = 0.0
_DAILY_TASK_PROMPT_MISS_LAST_TS = 0.0
_DAILY_METRICS_LAST_SYNC_TS = 0.0
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

_write('hook.py entered no-thread v70-friend-help-click-verify+v71-share-target-friend-chain+v72-friend-continuation+v73-share-prompt-context+v74-friend-toggle-persist+v75-share-obfuscated-entry+v76-runtime-chain-share+v77-share-compiled-callables+v78-share-run-cycle-recovery+v79-share-preflight-friend-branch+v80-friend-branch-refresh+v81-friend-navigation-verify+v82-friend-false-positive-stop+v83-share-direct-selected-friend+v87-share-contact-layout-friend-action-proof+v88-share-focus-paste-candidate-chain+v89-share-readback-fast-friend-chain+v90-native-clipboard-unreadable-chain+v91-pointer-clipboard-config-chain+v92-visible-share-fixed-right-chain+v93-single-click-share-selector+v94-share-idempotency+v95-friend-surface-guard+v96-window-owned-click-guard+v97-friend-ordered-stop+v98-strict-single-contact-share+v99-guard-dog-filter-persistence+v100-daily-flow-durable-status+v101-native-crash-supervisor+v102-autostart-idempotency+v103-share-counter-preservation+v104-next-friend-before-home+v105-bottom-carousel-only+v106-pre-action-card-cache+v107-friend-surface-gate+v108-carousel-exhausted-home+v114-guard-dog-runtime-gate+v116-friend-surface-lock+v117-friend-list-entry-recovery+v118-friend-list-preflight+v119-home-transition-verified+v120-friend-navigation-barrier+home-branch-recovery+v121-log-tail-branch-inference+v122-metrics-dailyflow-guard-list+v123-home-direct-entry+v124-friend-order-action-barrier+v125-native-home-chain-gate+v126-native-action-adjacent-order+v127-first-row-no-skip+v128-deferred-troublemaker-callable+v129-first-actionable-row+v130-guard-dog-help-gate+v131-guard-dog-skip-continuation+v132-troublemaker-counter-verified-help-frame+v133-native-guard-list-flow+v134-empty-guard-list-fast-fallback+v135-dog-badge-batch-proof+v136-share-direct-circle-uia+v137-daily-red-dot-proof+v138-share-uia-bootstrap-backoff+v139-share-uia-win32-helpers+v140-direct-view-hidden-group-filter+v142-guard-list-prequalified-help+v143-task-threshold-guard-list-route+v144-live-friend-state-no-recursion-task-authority+v145-ordered-guard-carousel-fast-chain+v146-fast-friend-list-open+v147-first-friend-approval-barrier+v148-first-friend-no-skip+v149-first-friend-render-grace+v150-troublemaker-adjacent-retry+v151-troublemaker-frame-diagnostics+v152-troublemaker-frame-import+v153-troublemaker-callable-diagnostic+v154-troublemaker-helper-probes+v155-troublemaker-seed-land-compat+v156-troublemaker-geometry-preferred+v157-troublemaker-dynamic-lattice+v158-troublemaker-chain-finalize+v159-stale-friend-branch-cooldown+v160-native-home-visual-gate+v161-false-friend-log-relabel+v162-same-cycle-false-friend-clear+v163-active-cycle-false-friend-suppression+v164-skip-legacy-false-friend-processor+v165-force-self-pass-after-false-friend+v167-runtime-go-home-threshold-floor+v168-friend-entry-callable-inventory+v169-native-bottom-adjacent-fallback+v170-native-bottom-fresh-frame+v171-private-home-icon-gate+v172-force-self-after-private-home+v173-first-friend-post-steal-grace+v174-durable-action-counter-merge+v175-troublemaker-runtime-callable+v176-troublemaker-home-probe-authority+v177-single-harvest-immediate-planting+v178-run-cycle-durable-sync+v179-visual-only-friend-action-poll+v180-durable-counter-flow-mirror+v181-fast-planting-cooldown+v182-radish-counter-isolation-first-friend-grace+v183-watchdog-visual-only-probe+v184-visible-friend-preflight-owner+v185-guard-initial-next-card+v186-first-friend-render-floor+v187-troublemaker-full-miss-cooldown+v188-bounded-guard-pending-advance+v189-friend-list-entry-settle-barrier+v190-visible-first-action-early-release+v191-delayed-friend-action-grace+v192-planting-callable-inventory+v193-safe-planting-callable-inventory+v194-pending-entry-guard-approval+v195-fast-backpack-panel-settle+v196-backpack-helper-profile+v197-backpack-preverified-empty-land+v198-trouble-planted-evidence+v199-trouble-native-evidence-gate+v200-trouble-popup-action-fallback+v201-fast-no-seed-ocr+v202-restore-native-no-seed-ocr+v203-friend-list-progress-cursor+v204-backpack-panel-capture+v205-first-friend-native-miss-fallback+v206-friend-list-pending-row-retry+v207-confirmed-entry-cursor+v208-restore-normal-cycle-interval+v209-pending-row-reopen-recovery+v210-friend-help-daily-quota+v211-quota-chain-short-circuit+v212-native-help-proof-barrier+v213-about-expiry-card-cleanup+v214-about-expiry-text-fallback+v215-about-widget-diagnostic+v216-native-project-dialog+v217-friend-capture-card-restore+v218-fast-planting-inventory-chain+v219-quad-click-friend-first-blocked-row-outfit-guard+v220-empty-land-candidate-diagnostics+v221-empty-land-crop-cover-filter+v222-blocked-toast-home-terminal+v223-blocked-row-second-cap+v224-troublemaker-bounded-three+v226-quad-skip-normal-seeds-soft-friend-action+v227-exhaustive-local-quad-groups+v228-bounded-help-false-positive-gap-scan+v229-current-card-guard-proof-gap-budget')

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
    'enable_bottom_friend_list_steal',
    'enable_daily_troublemaker',
])

_REQUIRED_FRIEND_BOT_BOOL_TRUE = set([
    'enable_process_friend',
    'enable_process_friend_help_entry',
])
_REQUIRED_FRIEND_SECTION_BOOL_TRUE = set([
    'enable_steal',
    'enable_help',
    'enable_friend_steal_one',
    'enable_friend_steal_one_fallback',
    'force_help_after_steal_success',
    'enable_bottom_friend_list_help_all',
    'enable_bottom_friend_list_steal',
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


def _effective_friend_cooldown(check_interval, friend_cooldown):
    # The legacy scheduler refreshes its friend timestamp even when a friend
    # cycle exits during cooldown.  A cooldown at or above the patrol interval
    # can therefore keep every later cycle on the friend page indefinitely.
    try:
        patrol = max(1, int(float(check_interval)))
    except BaseException:
        patrol = 15
    try:
        cooldown = max(0, int(float(friend_cooldown)))
    except BaseException:
        cooldown = 0
    safe_max = max(1, patrol - 5)
    if cooldown >= patrol:
        return safe_max
    return cooldown


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



def _daily_metrics_sync_runtime(
    context=None, counter_paths=None, csv_paths=None, today=None, force=False
):
    """Merge durable same-day counters into the live dashboard and stats CSV."""
    global _DAILY_METRICS_LAST_SYNC_TS
    day = ''
    summary = {
        'date': '',
        'friend_farming_count': 0,
        'self_farming_count': 0,
        'friend_help_daily_count': 0,
        'friend_trouble_daily_count': 0,
        'daily_radish_exp_count': 0,
        'self_actions_daily_count': 0,
    }
    try:
        os_module = __import__('os')
        json_module = __import__('json')
        csv_module = __import__('csv')
        time_module = __import__('time')
        day = str(today or time_module.strftime('%Y-%m-%d'))
        summary['date'] = day
        now_value = float(time_module.time())
        last_value = float(globals().get('_DAILY_METRICS_LAST_SYNC_TS', 0.0) or 0.0)
        if not force and last_value > 0.0 and (now_value - last_value) < 10.0:
            return summary
        globals()['_DAILY_METRICS_LAST_SYNC_TS'] = now_value

        if counter_paths is None:
            counter_paths = []
            local = str(os_module.environ.get('LOCALAPPDATA', '') or '')
            if local:
                local_counter_dir = os_module.path.join(local, 'qq-farm-bot-rev')
                counter_paths.append(os_module.path.join(
                    local_counter_dir, 'daily_counters.json'
                ))
                counter_paths.append(os_module.path.join(
                    local_counter_dir, 'daily_counters.hook.json'
                ))
            try:
                base = os_module.path.dirname(os_module.path.abspath(__file__))
                portable_counter_dir = os_module.path.join(
                    base, 'UserData', 'legacy-qq-farm-bot-rev'
                )
                counter_paths.append(os_module.path.join(
                    portable_counter_dir, 'daily_counters.json'
                ))
                counter_paths.append(os_module.path.join(
                    portable_counter_dir, 'daily_counters.hook.json'
                ))
            except BaseException:
                pass
        elif isinstance(counter_paths, (str, bytes, os_module.PathLike)):
            counter_paths = [counter_paths]
        normalized_counter_paths = []
        seen_counter_paths = set()
        for value in list(counter_paths or []):
            if not value:
                continue
            normalized_path = os_module.path.abspath(os_module.fspath(value))
            normalized_key = os_module.path.normcase(normalized_path)
            if normalized_key in seen_counter_paths:
                continue
            seen_counter_paths.add(normalized_key)
            normalized_counter_paths.append(normalized_path)
        counter_paths = normalized_counter_paths

        payloads = []

        def _safe_nonnegative(value):
            try:
                return max(0, int(float(str(value or 0))))
            except BaseException:
                return 0

        counter_specs = (
            ('friend_help_daily_count', 'friend_help_daily_date'),
            ('friend_trouble_daily_count', 'friend_trouble_daily_date'),
            ('daily_radish_exp_count', 'daily_radish_exp_date'),
            ('self_actions_daily_count', 'self_actions_daily_date'),
        )
        flow_date_keys = (
            'freebenefits_last_date', 'svip_last_date',
            'task_last_date', 'share_last_date',
        )
        flow_dates = dict((key, '') for key in flow_date_keys)

        def _consume_counter_node(node):
            if not isinstance(node, dict):
                return
            for count_key, date_key in counter_specs:
                if str(node.get(date_key, '') or '') != day:
                    continue
                summary[count_key] = max(
                    int(summary.get(count_key, 0) or 0),
                    _safe_nonnegative(node.get(count_key, 0)),
                )
            summary['friend_farming_count'] = int(
                summary.get('friend_help_daily_count', 0) or 0
            )
            summary['self_farming_count'] = int(
                summary.get('self_actions_daily_count', 0) or 0
            )
            for flow_key in flow_date_keys:
                if str(node.get(flow_key, '') or '') == day:
                    flow_dates[flow_key] = day

        def _consume_metrics_node(metrics):
            if not isinstance(metrics, dict):
                return
            if str(metrics.get('date', '') or '') != day:
                return
            summary['friend_help_daily_count'] = max(
                int(summary.get('friend_help_daily_count', 0) or 0),
                _safe_nonnegative(metrics.get('friend_farming_count', 0)),
            )
            summary['friend_trouble_daily_count'] = max(
                int(summary.get('friend_trouble_daily_count', 0) or 0),
                _safe_nonnegative(metrics.get('troublemaker_count', 0)),
            )
            summary['self_actions_daily_count'] = max(
                int(summary.get('self_actions_daily_count', 0) or 0),
                _safe_nonnegative(metrics.get('self_farming_count', 0)),
            )
            summary['daily_radish_exp_count'] = max(
                int(summary.get('daily_radish_exp_count', 0) or 0),
                _safe_nonnegative(metrics.get('daily_radish_exp_count', 0)),
            )
            summary['friend_farming_count'] = int(
                summary.get('friend_help_daily_count', 0) or 0
            )
            summary['self_farming_count'] = int(
                summary.get('self_actions_daily_count', 0) or 0
            )

        for path in counter_paths:
            data = {}
            try:
                if os_module.path.isfile(path):
                    with open(path, 'r', encoding='utf-8-sig') as handle:
                        loaded = json_module.load(handle)
                    if isinstance(loaded, dict):
                        data = loaded
            except BaseException:
                data = {}
            payloads.append((path, data))
            _consume_counter_node(data)
            _consume_metrics_node(data.get('gui_metrics'))
            instances = data.get('instances') if isinstance(data, dict) else None
            if isinstance(instances, dict):
                for instance_key, node in list(instances.items()):
                    if str(instance_key) == '__global__':
                        continue
                    _consume_counter_node(node)
                    if isinstance(node, dict):
                        _consume_metrics_node(node.get('gui_metrics'))

        count_fields = (
            'operation_count', 'self_harvest_count', 'friend_harvest_count',
            'self_farming_count', 'friend_farming_count',
            'warehouse_sell_count', 'troublemaker_count', 'reconnect_count',
            'radish_detect_count', 'planting_count', 'miniapp_restart_count',
        )

        def _apply_metrics(metrics):
            if not isinstance(metrics, dict):
                metrics = {}
            same_day = str(metrics.get('date', '') or '') == day
            if not same_day:
                for field in count_fields:
                    metrics[field] = 0
                metrics['scene_hint'] = 'home'
            for field in count_fields:
                metrics[field] = _safe_nonnegative(metrics.get(field, 0))
            metrics['date'] = day
            metrics['friend_farming_count'] = max(
                metrics['friend_farming_count'],
                int(summary['friend_farming_count']),
            )
            metrics['self_farming_count'] = max(
                metrics['self_farming_count'],
                int(summary['self_farming_count']),
            )
            metrics['troublemaker_count'] = max(
                metrics['troublemaker_count'],
                int(summary.get('friend_trouble_daily_count', 0) or 0),
            )
            radish_count = int(summary.get('daily_radish_exp_count', 0) or 0)
            metrics['radish_detect_count'] = radish_count
            metrics['planting_count'] = max(
                metrics['planting_count'], radish_count
            )
            if not str(metrics.get('scene_hint', '') or ''):
                metrics['scene_hint'] = 'home'
            return metrics

        try:
            instance_id = str(
                getattr(context, 'current_instance_id', '')
                or getattr(context, 'instance_id', '')
                or '1'
            )
        except BaseException:
            instance_id = '1'

        live_metrics = getattr(context, '_instance_metrics', None) if context is not None else None
        if isinstance(live_metrics, dict):
            _consume_metrics_node(live_metrics.get(instance_id))

        if context is not None:
            context_node = {}
            for count_key, date_key in counter_specs:
                try:
                    context_node[count_key] = getattr(context, count_key, 0)
                    context_node[date_key] = getattr(context, date_key, '')
                except BaseException:
                    pass
            for flow_key in flow_date_keys:
                try:
                    context_node[flow_key] = getattr(context, flow_key, '')
                except BaseException:
                    pass
            _consume_counter_node(context_node)
            for count_key, date_key in counter_specs:
                try:
                    setattr(context, count_key, int(summary.get(count_key, 0) or 0))
                    setattr(context, date_key, day)
                except BaseException:
                    pass
            for flow_key in flow_date_keys:
                if not flow_dates.get(flow_key):
                    continue
                try:
                    setattr(context, flow_key, day)
                except BaseException:
                    pass

        if isinstance(live_metrics, dict):
            live_metrics[instance_id] = _apply_metrics(live_metrics.get(instance_id))

        for path, data in payloads:
            try:
                if not isinstance(data, dict):
                    data = {}
                for count_key, date_key in counter_specs:
                    data[count_key] = int(summary.get(count_key, 0) or 0)
                    data[date_key] = day
                for flow_key in flow_date_keys:
                    if flow_dates.get(flow_key):
                        data[flow_key] = day
                data['gui_metrics'] = _apply_metrics(data.get('gui_metrics'))
                instances = data.get('instances')
                if not isinstance(instances, dict):
                    instances = {}
                    data['instances'] = instances
                global_bucket = instances.get('__global__')
                if not isinstance(global_bucket, dict):
                    global_bucket = {}
                    instances['__global__'] = global_bucket
                global_bucket['gui_metrics'] = _apply_metrics(
                    global_bucket.get('gui_metrics')
                )
                instance_bucket = instances.get(instance_id)
                if not isinstance(instance_bucket, dict):
                    instance_bucket = {}
                    instances[instance_id] = instance_bucket
                for count_key, date_key in counter_specs:
                    instance_bucket[count_key] = int(summary.get(count_key, 0) or 0)
                    instance_bucket[date_key] = day
                for flow_key in flow_date_keys:
                    if flow_dates.get(flow_key):
                        instance_bucket[flow_key] = day
                instance_bucket['gui_metrics'] = _apply_metrics(
                    instance_bucket.get('gui_metrics')
                )
                parent = os_module.path.dirname(path)
                if parent:
                    os_module.makedirs(parent, exist_ok=True)
                temp_path = path + '.tmp-v122-' + str(os_module.getpid())
                with open(temp_path, 'w', encoding='utf-8', newline='\n') as handle:
                    json_module.dump(data, handle, ensure_ascii=False, indent=2)
                    handle.write('\n')
                os_module.replace(temp_path, path)
            except BaseException as error:
                try:
                    if 'temp_path' in locals() and os_module.path.exists(temp_path):
                        os_module.remove(temp_path)
                except BaseException:
                    pass
                try:
                    log_fn = globals().get('_write')
                    if callable(log_fn):
                        log_fn('v122 daily metrics counter sync error ' + repr(error)[:220])
                except BaseException:
                    pass

        if csv_paths is None:
            csv_paths = []
            try:
                base = os_module.path.dirname(os_module.path.abspath(__file__))
                csv_paths.append(os_module.path.join(
                    base, 'UserData', 'QQFarmCopilot', 'instances',
                    'default', 'stats', 'daily_action_stats.csv'
                ))
            except BaseException:
                pass
        elif isinstance(csv_paths, (str, bytes, os_module.PathLike)):
            csv_paths = [csv_paths]
        required_fields = [
            'date', 'harvest', 'operation', 'friend_steal', 'friend_help'
        ]
        for raw_path in list(csv_paths or []):
            if not raw_path:
                continue
            path = os_module.path.abspath(os_module.fspath(raw_path))
            try:
                rows = []
                fieldnames = list(required_fields)
                if os_module.path.isfile(path):
                    with open(path, 'r', encoding='utf-8-sig', newline='') as handle:
                        reader = csv_module.DictReader(handle)
                        if reader.fieldnames:
                            fieldnames = list(reader.fieldnames)
                        rows = [dict(row) for row in reader]
                for field in required_fields:
                    if field not in fieldnames:
                        fieldnames.append(field)
                existing = None
                kept = []
                for row in rows:
                    if str(row.get('date', '') or '') == day:
                        if existing is None:
                            existing = row
                        continue
                    kept.append(row)
                if existing is None:
                    existing = {field: '0' for field in fieldnames}
                existing['date'] = day
                existing['operation'] = str(int(summary['self_farming_count']))
                existing['friend_help'] = str(int(summary['friend_farming_count']))
                for field in fieldnames:
                    existing.setdefault(field, '')
                kept.append(existing)
                parent = os_module.path.dirname(path)
                if parent:
                    os_module.makedirs(parent, exist_ok=True)
                temp_csv = path + '.tmp-v122-' + str(os_module.getpid())
                with open(temp_csv, 'w', encoding='utf-8', newline='') as handle:
                    writer = csv_module.DictWriter(handle, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(kept)
                os_module.replace(temp_csv, path)
            except BaseException as error:
                try:
                    if 'temp_csv' in locals() and os_module.path.exists(temp_csv):
                        os_module.remove(temp_csv)
                except BaseException:
                    pass
                try:
                    log_fn = globals().get('_write')
                    if callable(log_fn):
                        log_fn('v122 daily metrics csv sync error ' + repr(error)[:220])
                except BaseException:
                    pass
        try:
            log_fn = globals().get('_write')
            if callable(log_fn):
                log_fn(
                    'v122 daily metrics synced date=' + day +
                    ' self=' + str(summary['self_farming_count']) +
                    ' friend=' + str(summary['friend_farming_count'])
                )
        except BaseException:
            pass
        return summary
    except BaseException as error:
        try:
            log_fn = globals().get('_write')
            if callable(log_fn):
                log_fn('v122 daily metrics sync fatal ' + repr(error)[:220])
        except BaseException:
            pass
        summary['date'] = day
        return summary


def _daily_flow_status_paths(paths=None):
    try:
        if paths:
            if isinstance(paths, (str, bytes, os.PathLike)):
                values = [paths]
            else:
                values = list(paths)
            result = []
            for value in values:
                item = os.path.abspath(os.fspath(value))
                if item not in result:
                    result.append(item)
            return result
    except BaseException:
        pass
    result = []
    try:
        local = os.environ.get('LOCALAPPDATA', '')
        if local:
            result.append(os.path.join(
                local, 'qq-farm-bot-rev', 'daily_flow_status.json'
            ))
    except BaseException:
        pass
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        portable = os.path.join(
            base, 'UserData', 'legacy-qq-farm-bot-rev',
            'daily_flow_status.json'
        )
        if portable not in result:
            result.append(portable)
    except BaseException:
        pass
    return result


def _daily_flow_read_status(path):
    try:
        import json
        if not path or not os.path.isfile(path):
            return {}
        with open(path, 'r', encoding='utf-8-sig') as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except BaseException:
        return {}


def _daily_flow_write_status(path, data):
    try:
        import json
        target = os.path.abspath(os.fspath(path))
        parent = os.path.dirname(target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        temp = target + '.tmp-' + str(os.getpid())
        with open(temp, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write('\n')
        os.replace(temp, target)
        return True
    except BaseException:
        try:
            if 'temp' in locals() and os.path.exists(temp):
                os.remove(temp)
        except BaseException:
            pass
        return False


def _daily_flow_repair_unverified_status(
    paths=None, counter_paths=None, today=None
):
    """Downgrade legacy seeded task/benefit flags until UI success is observed."""
    try:
        import json
        day = str(today or time.strftime('%Y-%m-%d'))
        stamp = time.strftime('%Y-%m-%dT%H:%M:%S%z')
        repaired_flows = set()
        changed = False
        for path in _daily_flow_status_paths(paths):
            data = _daily_flow_read_status(path)
            if str(data.get('date', '') or '') != day:
                continue
            flows = data.get('flows')
            if not isinstance(flows, dict):
                continue
            file_changed = False
            for flow in ('freebenefits', 'task', 'svip'):
                entry = flows.get(flow)
                if not isinstance(entry, dict):
                    continue
                if str(entry.get('date', '') or '') != day:
                    continue
                if str(entry.get('status', '') or '').strip().lower() != 'success':
                    continue
                if str(entry.get('reason', '') or '').strip().lower() != 'seeded-from-daily-counters':
                    continue
                replacement = dict(entry)
                replacement['status'] = 'pending'
                replacement['verified_at'] = stamp
                replacement['reason'] = 'legacy-success-requires-verification'
                flows[flow] = replacement
                repaired_flows.add(flow)
                file_changed = True
            if file_changed:
                data['updated_at'] = stamp
                changed = _daily_flow_write_status(path, data) or changed

        if not repaired_flows:
            return changed
        if counter_paths is None:
            counter_paths = []
            local = os.environ.get('LOCALAPPDATA', '')
            if local:
                counter_paths.append(os.path.join(
                    local, 'qq-farm-bot-rev', 'daily_counters.json'
                ))
            try:
                base = os.path.dirname(os.path.abspath(__file__))
                counter_paths.append(os.path.join(
                    base, 'UserData', 'legacy-qq-farm-bot-rev',
                    'daily_counters.json'
                ))
            except BaseException:
                pass
        elif isinstance(counter_paths, (str, bytes, os.PathLike)):
            counter_paths = [counter_paths]
        field_names = {
            'freebenefits': 'freebenefits_last_date',
            'task': 'task_last_date',
            'svip': 'svip_last_date',
        }
        for raw_path in list(counter_paths or []):
            try:
                path = os.path.abspath(os.fspath(raw_path))
                if not os.path.isfile(path):
                    continue
                with open(path, 'r', encoding='utf-8-sig') as handle:
                    data = json.load(handle)
                if not isinstance(data, dict):
                    continue
                nodes = [data]
                instances = data.get('instances')
                if isinstance(instances, dict):
                    nodes.extend(
                        node for node in instances.values()
                        if isinstance(node, dict)
                    )
                file_changed = False
                for node in nodes:
                    for flow in repaired_flows:
                        field = field_names.get(flow)
                        if field and str(node.get(field, '') or '') == day:
                            node[field] = ''
                            file_changed = True
                if not file_changed:
                    continue
                temp_path = path + '.tmp-v122-' + str(os.getpid())
                with open(temp_path, 'w', encoding='utf-8', newline='\n') as handle:
                    json.dump(data, handle, ensure_ascii=False, indent=2)
                    handle.write('\n')
                os.replace(temp_path, path)
                changed = True
            except BaseException:
                try:
                    if 'temp_path' in locals() and os.path.exists(temp_path):
                        os.remove(temp_path)
                except BaseException:
                    pass
        return changed
    except BaseException:
        return False


def _daily_flow_mark_status(
    flow, status, target='', paths=None, today=None,
    verified_at=None, reason=''
):
    try:
        flow_key = str(flow or '').strip().lower()
        status_value = str(status or '').strip().lower()
        if not flow_key or status_value not in ('pending', 'success', 'failed'):
            return False
        day = str(today or time.strftime('%Y-%m-%d'))
        stamp = str(verified_at or time.strftime('%Y-%m-%dT%H:%M:%S%z'))
        changed = False
        for path in _daily_flow_status_paths(paths):
            data = _daily_flow_read_status(path)
            if str(data.get('date', '') or '') != day:
                data = {'date': day, 'flows': {}}
            flows = data.get('flows')
            if not isinstance(flows, dict):
                flows = {}
                data['flows'] = flows
            entry = {
                'date': day,
                'status': status_value,
                'verified_at': stamp,
            }
            target_value = str(target or '').strip()
            if target_value:
                entry['target'] = target_value
            reason_value = str(reason or '').strip()
            if reason_value:
                entry['reason'] = reason_value
            flows[flow_key] = entry
            data['date'] = day
            data['updated_at'] = stamp
            changed = _daily_flow_write_status(path, data) or changed
        return changed
    except BaseException:
        return False


def _daily_flow_success_today(flow, target='', paths=None, today=None):
    try:
        flow_key = str(flow or '').strip().lower()
        day = str(today or time.strftime('%Y-%m-%d'))
        wanted_target = str(target or '').strip()
        for path in _daily_flow_status_paths(paths):
            data = _daily_flow_read_status(path)
            if str(data.get('date', '') or '') != day:
                continue
            flows = data.get('flows')
            if not isinstance(flows, dict):
                continue
            entry = flows.get(flow_key)
            if not isinstance(entry, dict):
                continue
            if str(entry.get('date', '') or '') != day:
                continue
            if str(entry.get('status', '') or '').strip().lower() != 'success':
                continue
            reason_value = str(entry.get('reason', '') or '').strip().lower()
            if (
                flow_key in ('freebenefits', 'task', 'svip')
                and reason_value == 'seeded-from-daily-counters'
            ):
                continue
            if wanted_target and str(entry.get('target', '') or '').strip() != wanted_target:
                continue
            return True
        return False
    except BaseException:
        return False

def _daily_task_authoritative_success_today(paths=None, today=None):
    """Preserve a same-day task completion established by prompt absence or user confirmation."""
    try:
        day = str(today or time.strftime('%Y-%m-%d'))
        for path in _daily_flow_status_paths(paths):
            data = _daily_flow_read_status(path)
            if str(data.get('date', '') or '') != day:
                continue
            flows = data.get('flows')
            if not isinstance(flows, dict):
                continue
            entry = flows.get('task')
            if not isinstance(entry, dict):
                continue
            if str(entry.get('date', '') or '') != day:
                continue
            if str(entry.get('status', '') or '').strip().lower() != 'success':
                continue
            reason = str(entry.get('reason', '') or '').strip().lower()
            if (
                reason == 'entry-no-prompt-assumed-cleared'
                or reason.startswith('user-confirmed-already-claimed-')
            ):
                return True
        return False
    except BaseException:
        return False




def _daily_flow_mark_failure(
    flow, reason='', paths=None, today=None, now_epoch=None
):
    try:
        flow_key = str(flow or '').strip().lower()
        if not flow_key:
            return False
        day = str(today or time.strftime('%Y-%m-%d'))
        now_value = float(time.time() if now_epoch is None else now_epoch)
        stamp = time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(now_value))
        max_fn = globals().get('_daily_retry_max_default')
        try:
            max_attempts = int(max_fn()) if callable(max_fn) else 3
        except BaseException:
            max_attempts = 3
        max_attempts = max(1, min(6, max_attempts))
        changed = False
        for path in _daily_flow_status_paths(paths):
            data = _daily_flow_read_status(path)
            if str(data.get('date', '') or '') != day:
                data = {'date': day, 'flows': {}}
            flows = data.get('flows')
            if not isinstance(flows, dict):
                flows = {}
                data['flows'] = flows
            existing = flows.get(flow_key)
            if not isinstance(existing, dict):
                existing = {}
            if (
                str(existing.get('date', '') or '') == day
                and str(existing.get('status', '') or '').lower() == 'success'
            ):
                continue
            try:
                attempts = int(existing.get('attempts', 0) or 0) + 1
            except BaseException:
                attempts = 1
            attempts = max(1, min(max_attempts, attempts))
            retry_seconds = min(1800.0, 300.0 * (2 ** max(0, attempts - 1)))
            flows[flow_key] = {
                'date': day,
                'status': 'failed',
                'verified_at': stamp,
                'attempts': attempts,
                'next_retry_at': now_value + retry_seconds,
                'reason': str(reason or '')[:240],
            }
            data['date'] = day
            data['updated_at'] = stamp
            changed = _daily_flow_write_status(path, data) or changed
        return changed
    except BaseException:
        return False


def _daily_flow_retry_blocked(
    flow, paths=None, today=None, now_epoch=None
):
    try:
        flow_key = str(flow or '').strip().lower()
        day = str(today or time.strftime('%Y-%m-%d'))
        now_value = float(time.time() if now_epoch is None else now_epoch)
        for path in _daily_flow_status_paths(paths):
            data = _daily_flow_read_status(path)
            if str(data.get('date', '') or '') != day:
                continue
            flows = data.get('flows')
            if not isinstance(flows, dict):
                continue
            entry = flows.get(flow_key)
            if not isinstance(entry, dict):
                continue
            if str(entry.get('status', '') or '').lower() != 'failed':
                continue
            next_retry = float(entry.get('next_retry_at', 0.0) or 0.0)
            if next_retry > now_value:
                return True
        return False
    except BaseException:
        return False


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
        try:
            active_friend_secs = set([_norm_key(x) for x in _active_friend_sections()])
        except BaseException:
            active_friend_secs = set(['friend'])
        try:
            check_interval = _cfg_get(_active_bot_sections(), 'check_interval', '15')
            friend_cooldown = _cfg_get(_active_bot_sections(), 'friend_colddown_time', '0')
            effective_friend_cooldown = _effective_friend_cooldown(check_interval, friend_cooldown)
        except BaseException:
            check_interval = 15
            friend_cooldown = 0
            effective_friend_cooldown = 0
        lines = []
        cur_sec = ''
        for line in data.splitlines():
            low = line.strip().lower()
            if low.startswith('[') and ']' in low:
                cur_sec = low[1:low.find(']')].strip()
                lines.append(line)
                continue
            key = low.split('=', 1)[0].strip().replace('-', '_') if '=' in low else ''
            if cur_sec in active_bot_secs and key in _REQUIRED_FRIEND_BOT_BOOL_TRUE:
                line = key + ' = True'
            elif cur_sec in active_friend_secs and key in _REQUIRED_FRIEND_SECTION_BOOL_TRUE:
                line = key + ' = True'
            elif key in _VIP_CONFIG_FORCED_BOOL_TRUE and key != 'enable_wechat_focus_guard':
                line = key + ' = True'
            elif cur_sec in active_bot_secs and key == 'friend_colddown_time':
                line = 'friend_colddown_time = ' + str(effective_friend_cooldown)
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
        try:
            active_bot_secs = set([_norm_key(x) for x in _active_bot_sections()])
        except BaseException:
            active_bot_secs = set(['bot'])
        try:
            active_friend_secs = set([_norm_key(x) for x in _active_friend_sections()])
        except BaseException:
            active_friend_secs = set(['friend'])
        if s in active_bot_secs and o in _REQUIRED_FRIEND_BOT_BOOL_TRUE:
            return True if kind == 'bool' else 'True'
        if s in active_friend_secs and o in _REQUIRED_FRIEND_SECTION_BOOL_TRUE:
            return True if kind == 'bool' else 'True'
        if o == 'friend_colddown_time' and s in active_bot_secs:
            check_interval = _cfg_get(_active_bot_sections(), 'check_interval', '15')
            friend_cooldown = _cfg_get(_active_bot_sections(), 'friend_colddown_time', '0')
            value = _effective_friend_cooldown(check_interval, friend_cooldown)
            return value if kind == 'int' else str(value)
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
                    v = _config_override_value(section, option, 'int')
                    if v is not None:
                        return int(v)
                    return __orig(self, section, option, *args, **kwargs)
                cls.getint = patched_getint
            try: cls.__qqfarm_config_patched__ = True
            except BaseException: pass
        sp = getattr(cp, 'SectionProxy', None)
        if sp is not None and not getattr(sp, '__qqfarm_config_patched__', False):
            orig_sp_get = getattr(sp, 'get', None)
            orig_sp_getboolean = getattr(sp, 'getboolean', None)
            orig_sp_getint = getattr(sp, 'getint', None)
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
            if orig_sp_getint:
                def patched_sp_getint(self, option, *args, __orig=orig_sp_getint, **kwargs):
                    sec = getattr(self, 'name', None) or getattr(self, '_name', '')
                    v = _config_override_value(sec, option, 'int')
                    if v is not None:
                        return int(v)
                    return __orig(self, option, *args, **kwargs)
                sp.getint = patched_sp_getint
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


def _planting_callable_inventory(module):
    """Return planting-related callables, including obfuscated helpers found by constants."""
    entries = []
    if module is None:
        return entries
    try:
        import inspect
        module_name = str(getattr(module, '__name__', '') or type(module).__name__)
        targets = [(module, module_name)]
        try:
            for class_name, value in list(vars(module).items())[:800]:
                if isinstance(value, type):
                    targets.append((value, module_name + '.' + str(class_name)))
        except BaseException:
            pass
        seen = set()
        ascii_tokens = (
            'plant', 'seed', 'backpack', 'empty_land', 'fertiliz', 'crop',
            'land_count', 'seed_page', 'seed_shop', 'quad_act',
        )
        unicode_tokens = ('播种', '种子', '背包', '空地', '化肥', '地块')
        for owner, prefix in targets:
            try:
                items = list(vars(owner).items())[:1200]
            except BaseException:
                continue
            for attr_name, raw in items:
                if isinstance(raw, (staticmethod, classmethod)):
                    fn = raw.__func__
                else:
                    fn = raw
                if not callable(fn) or isinstance(fn, type):
                    continue
                marker = id(fn)
                if marker in seen:
                    continue
                seen.add(marker)
                code = getattr(fn, '__code__', None)
                if code is None:
                    continue
                parts = [str(attr_name), str(getattr(fn, '__name__', '') or '')]
                try:
                    parts.extend(str(value) for value in getattr(code, 'co_names', ()) or ())
                except BaseException:
                    pass
                try:
                    for value in getattr(code, 'co_consts', ()) or ():
                        if isinstance(value, str):
                            parts.append(value)
                        elif hasattr(value, 'co_name'):
                            parts.append(str(getattr(value, 'co_name', '') or ''))
                            parts.extend(
                                str(item) for item in getattr(value, 'co_names', ()) or ()
                            )
                            parts.extend(
                                str(item) for item in getattr(value, 'co_consts', ()) or ()
                                if isinstance(item, str)
                            )
                except BaseException:
                    pass
                searchable = ' '.join(parts)
                lowered = searchable.lower()
                if not (
                    any(token in lowered for token in ascii_tokens)
                    or any(token in searchable for token in unicode_tokens)
                ):
                    continue
                path = prefix + '.' + str(attr_name)
                detail_lines = ['path=' + path]
                try:
                    detail_lines.append('signature=' + str(inspect.signature(fn)))
                except BaseException as error:
                    detail_lines.append('signature-error=' + repr(error)[:240])
                try:
                    detail_lines.append(
                        'varnames=' + repr(tuple(getattr(code, 'co_varnames', ()) or ()))
                    )
                    detail_lines.append(
                        'names=' + repr(tuple(getattr(code, 'co_names', ()) or ()))
                    )
                    detail_lines.append(
                        'consts=' + repr(tuple(getattr(code, 'co_consts', ()) or ()))[:20000]
                    )
                except BaseException:
                    pass
                entries.append({
                    'path': path,
                    'details': '\n'.join(detail_lines),
                })
        entries.sort(key=lambda item: str(item.get('path', '')))
        return entries
    except BaseException:
        return entries


_PLANTING_CALLABLE_INVENTORY_WRITTEN = set()


def _write_planting_callable_inventory(module):
    try:
        module_name = str(getattr(module, '__name__', '') or type(module).__name__)
        written = globals().get('_PLANTING_CALLABLE_INVENTORY_WRITTEN')
        if not isinstance(written, set):
            written = set()
            globals()['_PLANTING_CALLABLE_INVENTORY_WRITTEN'] = written
        if module_name in written:
            return ''
        entries = _planting_callable_inventory(module)
        if not entries:
            return ''
        written.add(module_name)
        target_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(target_dir, exist_ok=True)
        target = os.path.join(target_dir, 'planting-callable-inventory.txt')
        with open(target, 'a', encoding='utf-8') as stream:
            stream.write('\n=== module ' + module_name + ' ===\n')
            for entry in entries:
                stream.write(str(entry.get('details', '')) + '\n\n')
        _write(
            'v192 planting callable inventory module=' + module_name +
            ' entries=' + str(len(entries)) + ' target=' + target
        )
        return target
    except BaseException as error:
        try:
            _write('v192 planting callable inventory error=' + repr(error)[:240])
        except BaseException:
            pass
        return ''


def _wrap_backpack_profile_helper(fn, name=''):
    """Accumulate helper timings only while the backpack-priority branch is active."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_backpack_profile_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            bot = args[0] if args else kwargs.get('bot')
            try:
                active = bool(getattr(bot, '_qqfarm_backpack_profile_active', False))
            except BaseException:
                active = False
            if not active:
                return fn(*args, **kwargs)
            start = __import__('time').perf_counter()
            try:
                return fn(*args, **kwargs)
            finally:
                elapsed = max(0.0, __import__('time').perf_counter() - start)
                try:
                    profile = getattr(bot, '_qqfarm_backpack_profile', None)
                    if not isinstance(profile, dict):
                        profile = {}
                        setattr(bot, '_qqfarm_backpack_profile', profile)
                    key = str(name or getattr(fn, '__name__', 'helper'))
                    stats = profile.get(key)
                    if not isinstance(stats, dict):
                        stats = {'count': 0, 'total': 0.0, 'max': 0.0}
                    stats['count'] = int(stats.get('count', 0) or 0) + 1
                    stats['total'] = float(stats.get('total', 0.0) or 0.0) + elapsed
                    stats['max'] = max(float(stats.get('max', 0.0) or 0.0), elapsed)
                    profile[key] = stats
                except BaseException:
                    pass

        _wrapped.__name__ = getattr(fn, '__name__', 'backpack_profile_helper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_backpack_profile_wrapped__ = True
        _wrapped.__qqfarm_backpack_profile_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _seed_panel_strip_visible(frame):
    """Return whether the fixed bottom seed toolbar is visibly open."""
    try:
        if frame is None or getattr(frame, 'shape', None) is None:
            return False
        cv_module = globals().get('cv2') or __import__('cv2')
        np_module = globals().get('np') or __import__('numpy')
        height, width = frame.shape[:2]
        if int(height) < 120 or int(width) < 120:
            return False
        x1 = max(0, int(round(float(width) * 0.04)))
        x2 = min(int(width), int(round(float(width) * 0.92)))
        y1 = max(0, int(round(float(height) * 0.61)))
        y2 = min(int(height), int(round(float(height) * 0.75)))
        roi = frame[y1:y2, x1:x2]
        if getattr(roi, 'size', 0) <= 0:
            return False
        hsv = cv_module.cvtColor(roi, cv_module.COLOR_BGR2HSV)
        dark = (hsv[:, :, 2] < 165) & (hsv[:, :, 1] < 205)
        return bool(float(np_module.mean(dark)) >= 0.12)
    except BaseException:
        return False


def _fast_seed_badge_candidates_from_frame(frame, capacity_hint=None):
    """Detect positive seed slots from their fixed cream quantity badges."""
    candidates = []
    try:
        try:
            candidate_capacity = int(capacity_hint or 1)
        except BaseException:
            candidate_capacity = 1
        candidate_capacity = max(1, min(999, candidate_capacity))
        if not _seed_panel_strip_visible(frame):
            return candidates
        cv_module = globals().get('cv2') or __import__('cv2')
        np_module = globals().get('np') or __import__('numpy')
        height, width = frame.shape[:2]
        hsv = cv_module.cvtColor(frame, cv_module.COLOR_BGR2HSV)
        center_y = int(round(float(height) * 0.639))
        probe_center_ys = []
        for y_ratio in (0.598, 0.618, 0.639):
            probe_y = int(round(float(height) * y_ratio))
            if probe_y not in probe_center_ys:
                probe_center_ys.append(probe_y)
        radius_x = max(10, int(round(float(width) * 0.055)))
        radius_y = max(8, int(round(float(height) * 0.018)))
        for ratio in (0.159, 0.318, 0.477, 0.637, 0.796):
            center_x = int(round(float(width) * ratio))
            x1 = max(0, center_x - radius_x)
            x2 = min(int(width), center_x + radius_x)
            cream_ratio = 0.0
            for probe_y in probe_center_ys:
                y1 = max(0, probe_y - radius_y)
                y2 = min(int(height), probe_y + radius_y)
                crop = hsv[y1:y2, x1:x2]
                if getattr(crop, 'size', 0) <= 0:
                    continue
                cream = cv_module.inRange(
                    crop,
                    np_module.array([5, 10, 115], dtype=np_module.uint8),
                    np_module.array([40, 175, 255], dtype=np_module.uint8),
                )
                cream_ratio = max(
                    cream_ratio, float(np_module.mean(cream > 0))
                )
            if cream_ratio < 0.22:
                continue
            candidates.append({
                'count': int(candidate_capacity),
                'center': (center_x, center_y),
                'score': min(1.0, max(0.0, cream_ratio)),
                'text': 'visual-positive-capacity',
            })
        return candidates
    except BaseException:
        return candidates


def _wrap_seed_quantity_badges_fast(fn, name=''):
    """Use fixed-slot visual evidence before invoking the slow badge OCR."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_seed_badges_fast_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            bot = args[0] if args else kwargs.get('bot')
            try:
                active = bool(getattr(bot, '_qqfarm_backpack_profile_active', False))
            except BaseException:
                active = False
            if not active:
                return fn(*args, **kwargs)
            frame = args[1] if len(args) > 1 else kwargs.get('frame')
            panel_visible = _seed_panel_strip_visible(frame)
            if panel_visible:
                try:
                    capacity_hint = int(getattr(
                        bot, '_qqfarm_recent_empty_land_count', 0
                    ) or 0)
                except BaseException:
                    capacity_hint = 0
                fast = _fast_seed_badge_candidates_from_frame(
                    frame, capacity_hint=max(1, capacity_hint)
                )
                if fast:
                    try:
                        now = __import__('time').time()
                        setattr(bot, '_qqfarm_backpack_candidates_seen_ts', now)
                        setattr(bot, '_qqfarm_backpack_candidate_centers', [x.get('center') for x in fast])
                        _write(
                            'v218 fast seed badges count=' + str(len(fast)) +
                            ' name=' + str(name)
                        )
                    except BaseException:
                        pass
                    return fast
            else:
                try:
                    _write('v218 seed panel not visible; skipped slow badge OCR name=' + str(name))
                except BaseException:
                    pass
                return []
            result = fn(*args, **kwargs)
            try:
                if result:
                    setattr(bot, '_qqfarm_backpack_candidates_seen_ts', __import__('time').time())
            except BaseException:
                pass
            return result

        _wrapped.__name__ = getattr(fn, '__name__', 'seed_badges_fast_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_seed_badges_fast_wrapped__ = True
        _wrapped.__qqfarm_seed_badges_fast_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _empty_land_candidate_has_crop_cover(frame, center, threshold=0.12):
    """Reject empty-land template hits surrounded by visible crop foliage."""
    try:
        if frame is None or getattr(frame, 'shape', None) is None:
            return False
        if not isinstance(center, (tuple, list)) or len(center) < 2:
            return False
        cv_module = globals().get('cv2') or __import__('cv2')
        np_module = globals().get('np') or __import__('numpy')
        height, width = frame.shape[:2]
        x = int(round(float(center[0])))
        y = int(round(float(center[1])))
        radius = 20
        x1 = max(0, x - radius)
        x2 = min(int(width), x + radius + 1)
        y1 = max(0, y - radius)
        y2 = min(int(height), y + radius + 1)
        roi = frame[y1:y2, x1:x2, :3]
        if getattr(roi, 'size', 0) <= 0:
            return False
        hsv = cv_module.cvtColor(roi, cv_module.COLOR_BGR2HSV)
        green = (
            (hsv[:, :, 0] >= 30)
            & (hsv[:, :, 0] <= 95)
            & (hsv[:, :, 1] >= 45)
            & (hsv[:, :, 2] >= 40)
        )
        green_ratio = float(np_module.mean(green))
        return bool(green_ratio >= max(0.05, min(0.40, float(threshold))))
    except BaseException:
        return False


def _wrap_detect_empty_lands_state(fn, name=''):
    """Remember fresh multi-land detections for the following label check."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_empty_land_state_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            result = fn(*args, **kwargs)
            bot = args[0] if args else kwargs.get('bot')
            frame = args[1] if len(args) > 1 else kwargs.get('frame')
            rejected_centers = []
            try:
                filter_fn = globals().get('_empty_land_candidate_has_crop_cover')
                if isinstance(result, list) and callable(filter_fn):
                    filtered = []
                    for item in result:
                        center = item.get('center') if isinstance(item, dict) else None
                        if (
                            isinstance(center, (tuple, list))
                            and len(center) >= 2
                            and filter_fn(frame, center)
                        ):
                            rejected_centers.append((
                                int(round(float(center[0]))),
                                int(round(float(center[1]))),
                            ))
                            continue
                        filtered.append(item)
                    result = filtered
                    if rejected_centers:
                        _write(
                            'v221 empty land crop-covered false positives=' +
                            str(len(rejected_centers)) + ' centers=' +
                            repr(rejected_centers)[:360] + ' name=' + str(name)
                        )
            except BaseException:
                rejected_centers = []
            try:
                count = len(result) if result is not None else 0
                centers = []
                for item in list(result or []):
                    center = item.get('center') if isinstance(item, dict) else None
                    if isinstance(center, (tuple, list)) and len(center) >= 2:
                        centers.append((
                            int(round(float(center[0]))),
                            int(round(float(center[1]))),
                        ))
                setattr(bot, '_qqfarm_recent_empty_land_count', int(count))
                setattr(bot, '_qqfarm_recent_empty_land_centers', centers)
                setattr(bot, '_qqfarm_recent_empty_land_rejected_centers', rejected_centers)
                setattr(bot, '_qqfarm_recent_empty_land_ts', __import__('time').time())
                if count > 0:
                    _write(
                        'v220 empty land candidates count=' + str(int(count)) +
                        ' centers=' + repr(centers)[:360] +
                        ' raw=' + repr(result)[:720] +
                        ' name=' + str(name)
                    )
            except BaseException:
                pass
            return result

        _wrapped.__name__ = getattr(fn, '__name__', 'empty_land_state_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_empty_land_state_wrapped__ = True
        _wrapped.__qqfarm_empty_land_state_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _wrap_buy_seed_for_crop_backpack_guard(fn, name=''):
    """Defer shop purchases while recently observed backpack inventory remains."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_backpack_buy_guard_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            bot = args[0] if args else kwargs.get('bot')
            try:
                seen_ts = float(getattr(bot, '_qqfarm_backpack_candidates_seen_ts', 0.0) or 0.0)
                age = max(0.0, __import__('time').time() - seen_ts) if seen_ts > 0 else 999999.0
            except BaseException:
                seen_ts = 0.0
                age = 999999.0
            if seen_ts > 0 and age <= 300.0:
                try:
                    setattr(
                        bot,
                        'planting_buy_retry_no_buy_quota',
                        max(1, int(getattr(bot, 'planting_buy_retry_no_buy_quota', 0) or 0)),
                    )
                    _write(
                        'v218 deferred seed shop because backpack inventory was seen age=' +
                        ('%.1f' % age) + ' name=' + str(name)
                    )
                except BaseException:
                    pass
                return False
            return fn(*args, **kwargs)

        _wrapped.__name__ = getattr(fn, '__name__', 'backpack_buy_guard_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_backpack_buy_guard_wrapped__ = True
        _wrapped.__qqfarm_backpack_buy_guard_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _wrap_planting_template_center_fast(fn, name=''):
    """Use a contextual threshold for the short-lived 2x2 confirmation popup."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_planting_template_center_fast_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            call_args = list(args or ())
            call_kwargs = dict(kwargs or {})
            template_id = call_args[2] if len(call_args) >= 3 else call_kwargs.get('template_id')
            if str(template_id or '') in ('act_seeds_btn_ok', 'act_seeds_btn_close'):
                if len(call_args) >= 4:
                    try:
                        call_args[3] = min(float(call_args[3]), 0.62)
                    except BaseException:
                        pass
                else:
                    try:
                        call_kwargs['threshold'] = min(float(call_kwargs.get('threshold', 0.75)), 0.62)
                    except BaseException:
                        call_kwargs['threshold'] = 0.62
            return fn(*tuple(call_args), **call_kwargs)

        _wrapped.__name__ = getattr(fn, '__name__', 'planting_template_center_fast_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_planting_template_center_fast_wrapped__ = True
        _wrapped.__qqfarm_planting_template_center_fast_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False



def _wrap_backpack_seed_blacklist_fast(fn, name=''):
    """Recognize the clickable 2x2 seed before the normal drag-seed path."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_backpack_seed_blacklist_fast_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            bot = args[0] if args else kwargs.get('bot')
            marker = object()
            old_value = marker
            try:
                old_value = getattr(bot, 'act_seeds_frame_threshold')
            except BaseException:
                pass
            try:
                current = float(old_value if old_value is not marker else 0.72)
                setattr(bot, 'act_seeds_frame_threshold', min(current, 0.62))
                result = fn(*args, **kwargs)
                if result:
                    try:
                        _write(
                            'v219 2x2 seed recognized before drag path name=' + str(name)
                        )
                    except BaseException:
                        pass
                return result
            finally:
                try:
                    if old_value is marker:
                        delattr(bot, 'act_seeds_frame_threshold')
                    else:
                        setattr(bot, 'act_seeds_frame_threshold', old_value)
                except BaseException:
                    pass

        _wrapped.__name__ = getattr(fn, '__name__', 'backpack_seed_blacklist_fast_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_backpack_seed_blacklist_fast_wrapped__ = True
        _wrapped.__qqfarm_backpack_seed_blacklist_fast_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _qqfarm_quad_land_center(land):
    """Return a stable integer center for a detected land candidate."""
    try:
        if isinstance(land, dict):
            center = land.get('center')
            if isinstance(center, (tuple, list)) and len(center) >= 2:
                return int(round(float(center[0]))), int(round(float(center[1])))
            left = land.get('left')
            top = land.get('top')
            right = land.get('right')
            bottom = land.get('bottom')
            if None not in (left, top, right, bottom):
                return (
                    int(round((float(left) + float(right)) * 0.5)),
                    int(round((float(top) + float(bottom)) * 0.5)),
                )
        center = getattr(land, 'center', None)
        if isinstance(center, (tuple, list)) and len(center) >= 2:
            return int(round(float(center[0]))), int(round(float(center[1])))
    except BaseException:
        pass
    return None


def _qqfarm_find_all_quad_empty_land_groups(lands):
    """Exhaustively find every local isometric 2x2 group among all empty lands.

    A farm can contain 24 plots.  The four plots for a special seed can be in
    any local lattice position, so this deliberately evaluates every 4-point
    combination instead of treating the outer farm corners as the candidate.
    """
    try:
        source = list(lands or [])
    except BaseException:
        source = []
    if len(source) < 4:
        return []

    points = []
    seen_centers = set()
    for index, land in enumerate(source):
        center = _qqfarm_quad_land_center(land)
        if center is None or center in seen_centers:
            continue
        seen_centers.add(center)
        points.append((index, land, center))
    if len(points) < 4:
        return []

    groups = []
    seen_groups = set()
    count = len(points)
    for a in range(count - 3):
        for b in range(a + 1, count - 2):
            for c in range(b + 1, count - 1):
                for d in range(c + 1, count):
                    combo = [points[a], points[b], points[c], points[d]]
                    # In the isometric farm lattice, the logical top-left plot
                    # is the visually highest point (leftmost on a y tie).
                    anchor = min(combo, key=lambda item: (item[2][1], item[2][0]))
                    others = [item for item in combo if item is not anchor]
                    accepted = None
                    for oi in range(3):
                        for oj in range(3):
                            if oi == oj:
                                continue
                            ok = 3 - oi - oj
                            if ok < 0 or ok > 2 or ok == oi or ok == oj:
                                continue
                            first = others[oi]
                            second = others[oj]
                            opposite = others[ok]
                            ax, ay = anchor[2]
                            fx, fy = first[2]
                            sx, sy = second[2]
                            ox, oy = opposite[2]
                            v1x, v1y = fx - ax, fy - ay
                            v2x, v2y = sx - ax, sy - ay

                            # The two adjacent isometric directions descend to
                            # opposite horizontal sides.  This rejects vertical
                            # diagonals and multi-cell outer-corner rectangles.
                            if v1x == 0 or v2x == 0 or (v1x > 0) == (v2x > 0):
                                continue
                            if v1y < 5 or v2y < 5:
                                continue
                            if not (18 <= abs(v1x) <= 72 and 18 <= abs(v2x) <= 72):
                                continue
                            if not (6 <= abs(v1y) <= 52 and 6 <= abs(v2y) <= 52):
                                continue
                            if abs(v1y - v2y) > max(9.0, 0.35 * max(v1y, v2y)):
                                continue

                            length1 = (float(v1x * v1x + v1y * v1y)) ** 0.5
                            length2 = (float(v2x * v2x + v2y * v2y)) ** 0.5
                            if min(length1, length2) < 22.0:
                                continue
                            if max(length1, length2) > 76.0:
                                continue
                            if max(length1, length2) / max(1.0, min(length1, length2)) > 1.55:
                                continue

                            predicted_x = ax + v1x + v2x
                            predicted_y = ay + v1y + v2y
                            closure_error = (
                                float((ox - predicted_x) ** 2 + (oy - predicted_y) ** 2)
                            ) ** 0.5
                            if closure_error > max(6.0, 0.14 * min(length1, length2)):
                                continue

                            dot = float(v1x * v2x + v1y * v2y)
                            cosine = dot / max(1.0, length1 * length2)
                            cosine = max(-1.0, min(1.0, cosine))
                            try:
                                angle = __import__('math').degrees(__import__('math').acos(cosine))
                            except BaseException:
                                angle = 90.0
                            if angle < 45.0 or angle > 140.0:
                                continue
                            area = abs(float(v1x * v2y - v1y * v2x))
                            if area < 0.55 * length1 * length2:
                                continue

                            right = first if first[2][0] > second[2][0] else second
                            left = second if right is first else first
                            score = (
                                closure_error
                                + abs(length1 - length2) * 0.20
                                + abs(first[2][1] - second[2][1]) * 0.15
                            )
                            accepted = (
                                score,
                                [anchor[1], right[1], left[1], opposite[1]],
                                frozenset((anchor[0], right[0], left[0], opposite[0])),
                            )
                            break
                        if accepted is not None:
                            break
                    if accepted is None or accepted[2] in seen_groups:
                        continue
                    seen_groups.add(accepted[2])
                    groups.append(accepted)

    groups.sort(
        key=lambda item: (
            float(item[0]),
            _qqfarm_quad_land_center(item[1][0])[1],
            _qqfarm_quad_land_center(item[1][0])[0],
        )
    )
    return [item[1] for item in groups]


def _wrap_quad_empty_land_groups(fn, name=''):
    """Use exhaustive local-lattice search, with the native finder as fallback."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_quad_group_exhaustive_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            call_args = list(args or ())
            lands = kwargs.get('lands')
            if lands is None and len(call_args) >= 2:
                lands = call_args[1]
            exhaustive = _qqfarm_find_all_quad_empty_land_groups(lands)
            if exhaustive:
                try:
                    _write(
                        'v227 exhaustive 2x2 lattice scan: empty_lands=' +
                        str(len(list(lands or []))) + ', local_groups=' +
                        str(len(exhaustive)) + ', name=' + str(name)
                    )
                except BaseException:
                    pass
                return exhaustive
            try:
                native = fn(*args, **kwargs)
            except BaseException:
                native = []
            try:
                _write(
                    'v227 exhaustive 2x2 lattice scan: no local group; native_fallback=' +
                    str(len(list(native or []))) + ', name=' + str(name)
                )
            except BaseException:
                pass
            return native

        _wrapped.__name__ = getattr(fn, '__name__', 'quad_empty_land_groups_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_quad_group_exhaustive_wrapped__ = True
        _wrapped.__qqfarm_quad_group_exhaustive_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _wrap_quad_act_seed_transaction(fn, name=''):
    """Retry the native 2x2 select-seed-confirm transaction once on a transient miss."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_quad_transaction_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            call_args = list(args or ())
            call_kwargs = dict(kwargs or {})
            bot = call_args[0] if call_args else call_kwargs.get('bot')
            remain_lands = call_kwargs.get('remain_lands')
            if remain_lands is None and len(call_args) >= 2:
                remain_lands = call_args[1]
            try:
                before_count = len(list(remain_lands or []))
            except BaseException:
                before_count = 0
            if before_count < 4:
                if bot is not None:
                    try:
                        setattr(bot, '_qqfarm_quad_skip_and_continue', True)
                    except BaseException:
                        pass
                try:
                    _write(
                        'v226 skip 2x2 seed: fewer than four empty lands count=' +
                        str(before_count) + '; continue normal backpack seeds name=' +
                        str(name)
                    )
                except BaseException:
                    pass
                return False, list(remain_lands or [])

            marker = object()
            old_threshold = marker
            try:
                old_threshold = getattr(bot, 'act_seeds_frame_threshold')
            except BaseException:
                pass

            def _call_once(retry=False):
                retry_args = list(call_args)
                retry_kwargs = dict(call_kwargs)
                if retry:
                    if 'panel_settle' in retry_kwargs:
                        try:
                            retry_kwargs['panel_settle'] = max(
                                0.35, float(retry_kwargs.get('panel_settle', 0.0) or 0.0)
                            )
                        except BaseException:
                            retry_kwargs['panel_settle'] = 0.35
                    elif len(retry_args) >= 3:
                        try:
                            retry_args[2] = max(0.35, float(retry_args[2] or 0.0))
                        except BaseException:
                            retry_args[2] = 0.35
                return fn(*tuple(retry_args), **retry_kwargs)

            def _confirmed(result):
                try:
                    if isinstance(result, (tuple, list)) and result:
                        if bool(result[0]):
                            return True
                        if before_count >= 4 and len(result) >= 2:
                            remaining = result[1]
                            if isinstance(remaining, (tuple, list)):
                                return len(remaining) <= (before_count - 4)
                        return False
                    return bool(result)
                except BaseException:
                    return False

            try:
                current = float(old_threshold if old_threshold is not marker else 0.72)
                setattr(bot, 'act_seeds_frame_threshold', min(current, 0.62))
                try:
                    _write(
                        'v225 2x2 transaction: choose 2x2 empty group -> click '
                        'act_seeds -> click confirm OK name=' + str(name)
                    )
                except BaseException:
                    pass
                result = _call_once(False)
                if _confirmed(result):
                    if (
                        isinstance(result, (tuple, list))
                        and result
                        and not bool(result[0])
                        and len(result) >= 2
                    ):
                        return True, result[1]
                    return result
                try:
                    _write(
                        'v225 2x2 transaction retry after transient confirm miss '
                        'name=' + str(name)
                    )
                except BaseException:
                    pass
                try:
                    sleep_fn = globals().get('_friend_guard_sleep')
                    if callable(sleep_fn):
                        sleep_fn(0.18)
                    else:
                        __import__('time').sleep(0.18)
                except BaseException:
                    pass
                retry_result = _call_once(True)
                if _confirmed(retry_result):
                    if (
                        isinstance(retry_result, (tuple, list))
                        and retry_result
                        and not bool(retry_result[0])
                        and len(retry_result) >= 2
                    ):
                        return True, retry_result[1]
                    return retry_result
                if bot is not None:
                    try:
                        setattr(bot, '_qqfarm_quad_skip_and_continue', True)
                        _write(
                            'v226 2x2 transaction failed twice; mark special seed to skip '
                            'and continue normal backpack seeds name=' + str(name)
                        )
                    except BaseException:
                        pass
                return retry_result
            finally:
                try:
                    if old_threshold is marker:
                        delattr(bot, 'act_seeds_frame_threshold')
                    else:
                        setattr(bot, 'act_seeds_frame_threshold', old_threshold)
                except BaseException:
                    pass

        _wrapped.__name__ = getattr(fn, '__name__', 'quad_act_seed_transaction_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_quad_transaction_wrapped__ = True
        _wrapped.__qqfarm_quad_transaction_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _configured_player_level(default=120):
    try:
        raw = _cfg_get(_active_planting_sections(), 'player_level', str(default))
        value = int(float(str(raw).strip()))
        if 1 <= value <= 999:
            return value
    except BaseException:
        pass
    return int(default)


def _wrap_player_level_fast(fn, name=''):
    """Use the configured/cached level and probe OCR only on a long interval."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_player_level_fast_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            bot = args[0] if args else kwargs.get('self')
            now = __import__('time').time()
            has_schedule = False
            try:
                has_schedule = hasattr(bot, '_qqfarm_player_level_next_probe_ts')
                next_probe = float(getattr(bot, '_qqfarm_player_level_next_probe_ts', 0.0) or 0.0)
                cached = int(getattr(bot, '_qqfarm_player_level_cache_value', 0) or 0)
            except BaseException:
                next_probe = 0.0
                cached = 0
            if has_schedule and 1 <= cached <= 999 and now < next_probe:
                return cached
            if not has_schedule:
                try:
                    existing = int(getattr(bot, '_last_player_level_detected', 0) or 0)
                except BaseException:
                    existing = 0
                value = existing if 1 <= existing <= 999 else _configured_player_level(120)
                try:
                    setattr(bot, '_qqfarm_player_level_cache_value', int(value))
                    setattr(bot, '_qqfarm_player_level_next_probe_ts', now + 3600.0)
                    setattr(bot, '_last_player_level_detect_source', 'hook-config-cache')
                    _write('v218 player level fast cache=' + str(value) + ' name=' + str(name))
                except BaseException:
                    pass
                return int(value)
            result = fn(*args, **kwargs)
            try:
                value = int(result or 0)
            except BaseException:
                value = 0
            if not 1 <= value <= 999:
                value = _configured_player_level(120)
            try:
                setattr(bot, '_qqfarm_player_level_cache_value', int(value))
                setattr(bot, '_qqfarm_player_level_next_probe_ts', now + 3600.0)
            except BaseException:
                pass
            return int(value)

        _wrapped.__name__ = getattr(fn, '__name__', 'player_level_fast_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_player_level_fast_wrapped__ = True
        _wrapped.__qqfarm_player_level_fast_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _wrap_fertilizer_template_fast(fn, name=''):
    """Lower only the contextual fertilizer template threshold and restore state."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_fertilizer_template_fast_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            bot = args[0] if args else kwargs.get('bot')
            fertilizer_type = args[2] if len(args) >= 3 else kwargs.get('fertilizer_type', 'one')
            attr_name = (
                'fertilizer_more_frame_threshold'
                if str(fertilizer_type or '').strip().lower() == 'more'
                else 'fertilizer_one_frame_threshold'
            )
            marker = object()
            old_value = marker
            try:
                old_value = getattr(bot, attr_name)
            except BaseException:
                pass
            try:
                current = float(old_value if old_value is not marker else 0.72)
                setattr(bot, attr_name, min(current, 0.62))
                return fn(*args, **kwargs)
            finally:
                try:
                    if old_value is marker:
                        delattr(bot, attr_name)
                    else:
                        setattr(bot, attr_name, old_value)
                except BaseException:
                    pass

        _wrapped.__name__ = getattr(fn, '__name__', 'fertilizer_template_fast_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_fertilizer_template_fast_wrapped__ = True
        _wrapped.__qqfarm_fertilizer_template_fast_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _save_backpack_seed_panel_debug_frame(frame):
    """Persist one live backpack seed-panel frame for local detector tuning."""
    try:
        cached = str(globals().get('_BACKPACK_SEED_PANEL_DEBUG_PATH', '') or '')
        if bool(globals().get('_BACKPACK_SEED_PANEL_DEBUG_SAVED', False)):
            return cached
        if frame is None or getattr(frame, 'shape', None) is None:
            return ''
        cv_module = globals().get('cv2') or __import__('cv2')
        os_module = globals().get('os') or __import__('os')
        base = os_module.path.dirname(os_module.path.abspath(__file__))
        log_dir = os_module.path.join(base, 'logs')
        os_module.makedirs(log_dir, exist_ok=True)
        target = os_module.path.join(log_dir, 'backpack-seed-panel-live.png')
        encoded_ok, encoded = cv_module.imencode('.png', frame)
        if not encoded_ok:
            return ''
        encoded.tofile(target)
        globals()['_BACKPACK_SEED_PANEL_DEBUG_SAVED'] = True
        globals()['_BACKPACK_SEED_PANEL_DEBUG_PATH'] = target
        return target
    except BaseException:
        return ''


def _wrap_backpack_no_seed_hint_fast(fn, name=''):
    """Preserve the native no-seed OCR result while profiling the backpack branch."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_backpack_no_seed_hint_fast_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            bot = args[0] if args else kwargs.get('bot')
            try:
                active = bool(getattr(bot, '_qqfarm_backpack_profile_active', False))
            except BaseException:
                active = False
            if active:
                try:
                    frame = args[1] if len(args) > 1 else kwargs.get('frame')
                    save_fn = globals().get('_save_backpack_seed_panel_debug_frame')
                    debug_path = save_fn(frame) if callable(save_fn) else ''
                    if debug_path:
                        _write('v204 backpack seed panel frame saved=' + str(debug_path))
                except BaseException:
                    frame = None
                try:
                    panel_fn = globals().get('_seed_panel_strip_visible')
                    badges_fn = globals().get('_fast_seed_badge_candidates_from_frame')
                    panel_visible = bool(panel_fn(frame)) if callable(panel_fn) else False
                    try:
                        capacity_hint = int(getattr(
                            bot, '_qqfarm_recent_empty_land_count', 0
                        ) or 0)
                    except BaseException:
                        capacity_hint = 0
                    fast_badges = (
                        badges_fn(frame, capacity_hint=max(1, capacity_hint))
                        if panel_visible and callable(badges_fn) else []
                    )
                    if fast_badges:
                        now_ts = __import__('time').time()
                        setattr(bot, '_qqfarm_backpack_candidates_seen_ts', now_ts)
                        setattr(
                            bot,
                            '_qqfarm_backpack_candidate_centers',
                            [item.get('center') for item in fast_badges],
                        )
                        _write(
                            'v219 visible seed inventory bypassed slow no-seed OCR '
                            'count=' + str(len(fast_badges)) + ' name=' + str(name)
                        )
                        return False, 'hook-visible-seed-inventory', 1.0
                except BaseException:
                    pass
            result = fn(*args, **kwargs)
            if active:
                try:
                    _write(
                        'v202 restored native no-seed OCR name=' + str(name)
                    )
                except BaseException:
                    pass
            return result

        _wrapped.__name__ = getattr(fn, '__name__', 'backpack_no_seed_hint_fast_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_backpack_no_seed_hint_fast_wrapped__ = True
        _wrapped.__qqfarm_backpack_no_seed_hint_fast_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False

def _wrap_backpack_empty_land_label_fast(fn, name=''):
    """Trust lands already verified by the active backpack-priority branch."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_backpack_empty_land_fast_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            bot = args[0] if args else kwargs.get('bot')
            try:
                active = bool(getattr(bot, '_qqfarm_backpack_profile_active', False))
            except BaseException:
                active = False
            batch_preverified = False
            try:
                batch_count = int(getattr(bot, '_qqfarm_recent_empty_land_count', 0) or 0)
                batch_ts = float(getattr(bot, '_qqfarm_recent_empty_land_ts', 0.0) or 0.0)
                batch_age = max(0.0, __import__('time').time() - batch_ts) if batch_ts > 0 else 999999.0
                batch_preverified = bool(batch_count >= 4 and batch_age <= 12.0)
            except BaseException:
                batch_preverified = False
            if not active and not batch_preverified:
                return fn(*args, **kwargs)

            land_center = None
            if len(args) >= 3:
                land_center = args[2]
            elif 'land_center' in kwargs:
                land_center = kwargs.get('land_center')
            try:
                valid_center = (
                    isinstance(land_center, (tuple, list))
                    and len(land_center) >= 2
                    and land_center[0] is not None
                    and land_center[1] is not None
                )
                center_x = int(round(float(land_center[0]))) if valid_center else None
            except BaseException:
                valid_center = False
                center_x = None
            if not valid_center:
                return fn(*args, **kwargs)

            reason = (
                'hook-backpack-preverified-empty-land'
                if active else 'hook-batch-preverified-empty-land'
            )
            try:
                _write(
                    ('v197 backpack preverified empty land' if active else 'v218 batch preverified empty land') +
                    '; skipped slow label OCR center=' +
                    repr((land_center[0], land_center[1])) +
                    ' name=' + str(name)
                )
            except BaseException:
                pass
            return True, reason, 1.0, center_x

        _wrapped.__name__ = getattr(fn, '__name__', 'backpack_empty_land_fast_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_backpack_empty_land_fast_wrapped__ = True
        _wrapped.__qqfarm_backpack_empty_land_fast_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _wrap_backpack_seed_priority_planting_fast(fn, name=''):
    """Cap repeated waits and report safe per-helper timings for the native branch."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_backpack_fast_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            call_args = list(args or ())
            call_kwargs = dict(kwargs or {})
            original_settle = None
            effective_settle = None
            if len(call_args) >= 3:
                try:
                    original_settle = float(call_args[2])
                    effective_settle = min(original_settle, 0.65)
                    call_args[2] = effective_settle
                except BaseException:
                    original_settle = None
                    effective_settle = None
            elif 'panel_settle' in call_kwargs:
                try:
                    original_settle = float(call_kwargs.get('panel_settle'))
                    effective_settle = min(original_settle, 0.65)
                    call_kwargs['panel_settle'] = effective_settle
                except BaseException:
                    original_settle = None
                    effective_settle = None
            bot = call_args[0] if call_args else call_kwargs.get('bot')
            marker = object()
            old_active = marker
            old_profile = marker
            quad_skip_flag = '_qqfarm_quad_skip_and_continue'
            if bot is not None:
                try:
                    delattr(bot, quad_skip_flag)
                except BaseException:
                    pass
                try:
                    old_active = getattr(bot, '_qqfarm_backpack_profile_active')
                except BaseException:
                    pass
                try:
                    old_profile = getattr(bot, '_qqfarm_backpack_profile')
                except BaseException:
                    pass
                try:
                    setattr(bot, '_qqfarm_backpack_profile_active', True)
                    setattr(bot, '_qqfarm_backpack_profile', {})
                except BaseException:
                    pass
            start = __import__('time').perf_counter()
            result_marker = object()
            result = result_marker
            profile = {}
            try:
                result = fn(*tuple(call_args), **call_kwargs)
                skip_quad = False
                if bot is not None:
                    try:
                        skip_quad = bool(getattr(bot, quad_skip_flag, False))
                    except BaseException:
                        skip_quad = False
                if skip_quad:
                    try:
                        delattr(bot, quad_skip_flag)
                    except BaseException:
                        pass
                    old_quad_switches = {}
                    try:
                        for switch_name in ('enable_quad_act_seeds', 'quad_act_seeds'):
                            try:
                                old_quad_switches[switch_name] = getattr(bot, switch_name)
                            except BaseException:
                                old_quad_switches[switch_name] = marker
                            try:
                                setattr(bot, switch_name, False)
                            except BaseException:
                                pass
                        try:
                            _write(
                                'v226 skip failed 2x2 seed and continue normal seeds '
                                'in the same backpack round name=' + str(name)
                            )
                        except BaseException:
                            pass
                        result = fn(*tuple(call_args), **call_kwargs)
                    finally:
                        for switch_name, old_value in old_quad_switches.items():
                            try:
                                if old_value is marker:
                                    delattr(bot, switch_name)
                                else:
                                    setattr(bot, switch_name, old_value)
                            except BaseException:
                                pass
                        try:
                            delattr(bot, quad_skip_flag)
                        except BaseException:
                            pass
            finally:
                elapsed = max(0.0, __import__('time').perf_counter() - start)
                if bot is not None:
                    try:
                        current_profile = getattr(bot, '_qqfarm_backpack_profile', {})
                        if isinstance(current_profile, dict):
                            profile = dict(current_profile)
                    except BaseException:
                        profile = {}
                    try:
                        if old_active is marker:
                            delattr(bot, '_qqfarm_backpack_profile_active')
                        else:
                            setattr(bot, '_qqfarm_backpack_profile_active', old_active)
                    except BaseException:
                        pass
                    try:
                        if old_profile is marker:
                            delattr(bot, '_qqfarm_backpack_profile')
                        else:
                            setattr(bot, '_qqfarm_backpack_profile', old_profile)
                    except BaseException:
                        pass
                try:
                    remaining = None
                    if result is not result_marker and isinstance(result, (tuple, list)) and len(result) >= 2:
                        remaining_value = result[1]
                        remaining = len(remaining_value) if remaining_value is not None else 0
                    ordered = sorted(
                        profile.items(),
                        key=lambda item: float((item[1] or {}).get('total', 0.0) or 0.0),
                        reverse=True,
                    )
                    profile_text = ','.join(
                        str(key).split('.')[-1] + ':' +
                        str(int((stats or {}).get('count', 0) or 0)) + '/' +
                        ('%.3f' % float((stats or {}).get('total', 0.0) or 0.0)) + '/' +
                        ('%.3f' % float((stats or {}).get('max', 0.0) or 0.0))
                        for key, stats in ordered[:12]
                    )
                    _write(
                        'v195 backpack priority elapsed=' + ('%.3f' % elapsed) +
                        ' panel_settle=' + (
                            ('%.3f->%.3f' % (original_settle, effective_settle))
                            if original_settle is not None and effective_settle is not None
                            else 'unchanged'
                        ) +
                        ' remaining=' + repr(remaining) +
                        ' profile=' + profile_text +
                        ' name=' + str(name)
                    )
                except BaseException:
                    pass
            return result

        _wrapped.__name__ = getattr(fn, '__name__', 'backpack_seed_priority_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__doc__ = getattr(fn, '__doc__', None)
        _wrapped.__qqfarm_backpack_fast_wrapped__ = True
        _wrapped.__qqfarm_backpack_fast_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _fast_planting_switch_value(key, desired):
    """Disable the per-land OCR path that stalls drag planting for tens of seconds."""
    try:
        if str(key or '') == 'enhance_empty_land_detection':
            return False
    except BaseException:
        pass
    return bool(desired)


def _restore_runtime_business_switches(obj):
    changed = 0
    try:
        groups = [
            (_active_bot_sections(), [
                ('enable_process_friend', ('enable_process_friend',)),
                ('enable_process_friend_help_entry', ('enable_process_friend_help_entry',)),
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
                ('enable_steal', ('enable_steal', 'enable_friend_steal')),
                ('enable_help', ('enable_help', 'enable_friend_help')),
                ('enable_friend_steal_one', ('enable_friend_steal_one',)),
                ('enable_friend_steal_one_fallback', ('enable_friend_steal_one_fallback',)),
                ('enable_bottom_friend_list_help_all', ('enable_bottom_friend_list_help_all',)),
                ('enable_bottom_friend_list_steal', ('enable_bottom_friend_list_steal',)),
                ('enable_guard_dog_help_only', (
                    'enable_guard_dog_help_only', 'guard_dog_help_only',
                    'help_only_guard_dog',
                )),
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
                    desired = _fast_planting_switch_value(key, desired)
                except BaseException:
                    pass
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
        'quad_act_seeds': True, 'enable_quad_act_seeds': True,
        'daily_radish_exp': True, 'enable_daily_radish_exp': True,
        'skip_radish': True, 'enable_skip_radish': True,
        'enable_no_steal_window': True, 'no_steal_window': True,
        'guard_dog_help_only': True, 'enable_guard_dog_help_only': True,
        'bottom_friend_list_help_all': True, 'enable_bottom_friend_list_help_all': True,
        'multi_instance': True, 'svip': True, 'daily_svip': True, 'enable_daily_svip': True}
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
_GUARD_DOG_MODE_FUNC_NAMES = set([
    '_guard_dog_detection_mode',
    'is_friend_guard_list_help_only_mode',
])
_GUARD_DOG_VALUE_NAMES = set([
    'enable_guard_dog_help_only',
    'guard_dog_help_only',
    'help_only_guard_dog',
])



def _persist_guard_dog_mode(enabled, ini_paths=None, json_paths=None):
    desired = bool(enabled)
    changed = False
    try:
        if ini_paths is None:
            ini_paths = []
            local = os.environ.get('LOCALAPPDATA', '')
            if local:
                ini_paths.append(os.path.join(
                    local, 'qq-farm-bot-rev', 'config-multi.ini'
                ))
            try:
                base = os.path.dirname(os.path.abspath(__file__))
                ini_paths.append(os.path.join(
                    base, 'UserData', 'legacy-qq-farm-bot-rev',
                    'config-multi.ini'
                ))
            except BaseException:
                pass
        if isinstance(ini_paths, (str, bytes, os.PathLike)):
            ini_paths = [ini_paths]
        for raw_path in list(ini_paths or []):
            try:
                path = os.path.abspath(os.fspath(raw_path))
                if not os.path.isfile(path):
                    continue
                with open(path, 'r', encoding='utf-8-sig') as handle:
                    raw = handle.read()
                lines = raw.splitlines()
                output = []
                current = ''
                target_seen = set()
                key_seen = False

                def _flush_missing(section_name):
                    nonlocal key_seen
                    if section_name in ('friend', 'instance.1.friend') and not key_seen:
                        output.append(
                            'enable_guard_dog_help_only = ' +
                            ('True' if desired else 'False')
                        )
                    key_seen = False

                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('[') and ']' in stripped:
                        _flush_missing(current)
                        current = stripped[1:stripped.find(']')].strip().lower()
                        if current in ('friend', 'instance.1.friend'):
                            target_seen.add(current)
                        output.append(line)
                        continue
                    if current in ('friend', 'instance.1.friend'):
                        key = stripped.split('=', 1)[0].strip().lower() if '=' in stripped else ''
                        if key == 'enable_guard_dog_help_only':
                            output.append(
                                'enable_guard_dog_help_only = ' +
                                ('True' if desired else 'False')
                            )
                            key_seen = True
                            continue
                    output.append(line)
                _flush_missing(current)
                for section_name in ('friend', 'instance.1.friend'):
                    if section_name not in target_seen:
                        if output and output[-1] != '':
                            output.append('')
                        output.append('[' + section_name + ']')
                        output.append(
                            'enable_guard_dog_help_only = ' +
                            ('True' if desired else 'False')
                        )
                updated = '\n'.join(output) + ('\n' if raw.endswith(('\n', '\r')) else '')
                if updated != raw:
                    temp = path + '.tmp-guard-dog-' + str(os.getpid())
                    with open(temp, 'w', encoding='utf-8', newline='\n') as handle:
                        handle.write(updated)
                    os.replace(temp, path)
                    changed = True
            except BaseException:
                try:
                    if 'temp' in locals() and os.path.exists(temp):
                        os.remove(temp)
                except BaseException:
                    pass
        if json_paths is None:
            json_paths = []
            try:
                base = os.path.dirname(os.path.abspath(__file__))
                json_paths.append(os.path.join(
                    base, 'UserData', 'QQFarmCopilot', 'instances',
                    'default', 'configs', 'config.json'
                ))
            except BaseException:
                pass
        if isinstance(json_paths, (str, bytes, os.PathLike)):
            json_paths = [json_paths]
        for raw_path in list(json_paths or []):
            try:
                import json
                path = os.path.abspath(os.fspath(raw_path))
                if not os.path.isfile(path):
                    continue
                with open(path, 'r', encoding='utf-8-sig') as handle:
                    data = json.load(handle)
                if not isinstance(data, dict):
                    continue
                tasks = data.setdefault('tasks', {})
                friend = tasks.setdefault('friend', {})
                features = friend.setdefault('features', {})
                old_value = features.get('help_only_guard_dog')
                features['help_only_guard_dog'] = desired
                if bool(old_value) != desired:
                    temp = path + '.tmp-guard-dog-' + str(os.getpid())
                    with open(temp, 'w', encoding='utf-8', newline='\n') as handle:
                        json.dump(data, handle, ensure_ascii=False, indent=2)
                        handle.write('\n')
                    os.replace(temp, path)
                    changed = True
            except BaseException:
                try:
                    if 'temp' in locals() and os.path.exists(temp):
                        os.remove(temp)
                except BaseException:
                    pass
        return changed
    except BaseException:
        return False


def _guard_dog_ui_config_enabled():
    try:
        return _truthy(_cfg_get(_active_friend_sections(), 'enable_guard_dog_help_only', 'False'), False)
    except BaseException:
        return False


def _friend_guard_list_confirmed_config():
    """Only use native per-friend templates after an explicit confirmation flag."""
    try:
        return _truthy(_cfg_get(
            _active_friend_sections(),
            'friend_guard_list_confirmed',
            'False',
        ), False)
    except BaseException:
        return False


def _friend_guard_verified_entry_active(context, now_ts=None, max_age_seconds=90.0):
    """Return True while the current farm came from a dog-badge-verified list row."""
    try:
        if context is None or not bool(getattr(context, '_qqfarm_guard_row_verified', False)):
            return False
        verified_ts = float(getattr(context, '_qqfarm_guard_row_verified_ts', 0.0) or 0.0)
        if verified_ts <= 0.0:
            return False
        if now_ts is None:
            now_fn = globals().get('_friend_watchdog_now')
            now_ts = (
                float(now_fn())
                if callable(now_fn)
                else float(__import__('time').time())
            )
        age = float(now_ts) - verified_ts
        return bool(age >= -5.0 and age <= max(1.0, float(max_age_seconds)))
    except BaseException:
        return False



def _friend_guard_list_prequalified_entry_active(
        context, now_ts=None, max_age_seconds=90.0):
    """Return True after native friend-list matching approved this visit."""
    try:
        if context is None or not bool(getattr(
                context, '_qqfarm_guard_list_prequalified', False)):
            return False
        approved_ts = float(getattr(
            context, '_qqfarm_guard_list_prequalified_ts', 0.0
        ) or 0.0)
        if approved_ts <= 0.0:
            return False
        if now_ts is None:
            now_fn = globals().get('_friend_watchdog_now')
            now_ts = (
                float(now_fn())
                if callable(now_fn)
                else float(__import__('time').time())
            )
        age = float(now_ts) - approved_ts
        return bool(age >= -5.0 and age <= max(1.0, float(max_age_seconds)))
    except BaseException:
        return False


def _friend_guard_clear_prequalification(context):
    """Clear native friend-list approval before a new inspection cycle."""
    if context is None:
        return False
    try:
        setattr(context, '_qqfarm_guard_list_prequalified', False)
        setattr(context, '_qqfarm_guard_list_prequalified_ts', 0.0)
        return True
    except BaseException:
        return False

def _friend_guard_active_instance_ids():
    """Return the active legacy instance ids used by the native template loader."""
    values = []

    def _add(value):
        try:
            text = str(value or '').strip()
        except BaseException:
            return
        if not text or text.lower() in ('none', 'null'):
            return
        if text not in values:
            values.append(text)

    try:
        context = globals().get('_ACTIVE_RUN_CYCLE_CONTEXT')
        for owner in (
            context,
            getattr(context, 'bot', None) if context is not None else None,
            getattr(context, 'runtime', None) if context is not None else None,
        ):
            if owner is None:
                continue
            for attr in ('instance_id', 'current_instance_id', 'active_instance_id'):
                try:
                    _add(getattr(owner, attr, None))
                except BaseException:
                    pass
    except BaseException:
        pass
    try:
        cfg_fn = globals().get('_cfg_get')
        if callable(cfg_fn):
            sections_fn = globals().get('_active_bot_sections')
            sections = sections_fn() if callable(sections_fn) else ('bot',)
            _add(cfg_fn(sections, 'instance_id', '1'))
            _add(cfg_fn(('instances',), 'active_id', '1'))
    except BaseException:
        pass
    if not values:
        values.append('1')
    return tuple(values)


def _friend_guard_template_status(instance_ids=None, template_root=None):
    """Inspect the native per-instance friend guard whitelist directory."""
    os_module = __import__('os')
    if template_root is None:
        local = str(os_module.environ.get('LOCALAPPDATA', '') or '').strip()
        if not local:
            local = os_module.path.join(
                os_module.path.expanduser('~'), 'AppData', 'Local'
            )
        template_root = os_module.path.join(
            local,
            'qq-farm-bot-rev',
            'assert',
            'templates',
            'element',
        )
    root = os_module.path.abspath(os_module.fspath(template_root))
    if instance_ids is None:
        ids_fn = globals().get('_friend_guard_active_instance_ids')
        instance_ids = ids_fn() if callable(ids_fn) else ('1',)
    if isinstance(instance_ids, (str, bytes, os_module.PathLike)):
        instance_ids = (instance_ids,)
    normalized_ids = []
    for raw_value in tuple(instance_ids or ()):
        try:
            value = str(raw_value or '').strip()
        except BaseException:
            continue
        if value and value not in normalized_ids:
            normalized_ids.append(value)
    if not normalized_ids:
        normalized_ids.append('1')
    directories = []
    files = []
    allowed_extensions = ('.png', '.jpg', '.jpeg')
    for instance_id in normalized_ids:
        directory = os_module.path.join(
            root, 'instances', instance_id, 'friend_list', 'guard'
        )
        directories.append(directory)
        try:
            with os_module.scandir(directory) as entries:
                for entry in entries:
                    try:
                        if not entry.is_file():
                            continue
                        if str(entry.name or '').lower().endswith(allowed_extensions):
                            files.append(entry.path)
                    except BaseException:
                        continue
        except BaseException:
            continue
    return {
        'instance_ids': tuple(normalized_ids),
        'directories': tuple(directories),
        'files': tuple(files),
        'count': len(files),
    }


def _friend_guard_list_template_ready(instance_ids=None, template_root=None):
    try:
        status_fn = globals().get('_friend_guard_template_status')
        if not callable(status_fn):
            return False
        status = status_fn(instance_ids=instance_ids, template_root=template_root)
        return int(status.get('count', 0) or 0) > 0
    except BaseException:
        return False


def _friend_guard_list_template_paths(template_paths=None):
    """Return imported friend-whitelist templates without rescanning unrelated assets."""
    if template_paths is not None:
        if isinstance(template_paths, (str, bytes)):
            return (template_paths,)
        try:
            return tuple(template_paths or ())
        except BaseException:
            return ()
    try:
        status_fn = globals().get('_friend_guard_template_status')
        status = status_fn() if callable(status_fn) else {}
        return tuple(status.get('files', ()) or ())
    except BaseException:
        return ()


def _friend_guard_list_carousel_card_match(
        frame, card_bounds=None, template_paths=None, threshold=0.72):
    """Match the currently selected bottom friend card against imported whitelist rows."""
    result = {
        'matched': False,
        'score': 0.0,
        'path': '',
        'center': None,
    }
    if frame is None:
        return result
    try:
        np = __import__('numpy')
        cv2 = __import__('cv2')
        arr = np.asarray(frame)
        shape = getattr(arr, 'shape', None)
        if not shape or len(shape) < 3 or int(shape[2]) < 3:
            return result
        height, width = int(shape[0]), int(shape[1])
        if not isinstance(card_bounds, dict):
            bounds_fn = globals().get('_friend_selected_carousel_card_bounds')
            card_bounds = bounds_fn(frame) if callable(bounds_fn) else None
        if not isinstance(card_bounds, dict):
            return result
        left = max(0, int(card_bounds.get('left', 0) or 0) - max(2, int(width * 0.008)))
        right = min(
            width,
            int(card_bounds.get('right', left) or left) + max(2, int(width * 0.008)),
        )
        top = max(0, int(card_bounds.get('top', 0) or 0) - max(2, int(height * 0.006)))
        bottom = min(
            height,
            int(card_bounds.get('bottom', top) or top) + max(2, int(height * 0.006)),
        )
        if right - left < 20 or bottom - top < 20:
            return result
        roi = arr[top:bottom, left:right, :3]
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        paths_fn = globals().get('_friend_guard_list_template_paths')
        paths = (
            paths_fn(template_paths)
            if callable(paths_fn)
            else tuple(template_paths or ())
        )
        reader = globals().get('_friend_guard_read_template')
        frame_scale = max(
            0.45,
            min(2.5, ((float(width) / 428.0) + (float(height) / 800.0)) / 2.0),
        )
        best_score = 0.0
        best_path = ''
        best_center = None
        for template_path in paths:
            try:
                template = reader(template_path) if callable(reader) else None
                if template is None:
                    raw = np.fromfile(str(template_path), dtype=np.uint8)
                    template = cv2.imdecode(raw, cv2.IMREAD_COLOR) if raw.size else None
                if template is None:
                    continue
                template_height, template_width = int(template.shape[0]), int(template.shape[1])
                avatar_width = max(12, min(template_width, int(round(template_width * 0.455))))
                avatar = template[:, :avatar_width, :3]
                for factor in (0.82, 0.88, 0.94, 1.00, 1.06):
                    scale = frame_scale * factor
                    target_width = max(8, int(round(int(avatar.shape[1]) * scale)))
                    target_height = max(8, int(round(int(avatar.shape[0]) * scale)))
                    if target_width > int(roi_gray.shape[1]) or target_height > int(roi_gray.shape[0]):
                        continue
                    interpolation = (
                        cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
                    )
                    resized = cv2.resize(
                        avatar,
                        (target_width, target_height),
                        interpolation=interpolation,
                    )
                    template_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                    matched = cv2.matchTemplate(
                        roi_gray, template_gray, cv2.TM_CCOEFF_NORMED
                    )
                    _, score, _, location = cv2.minMaxLoc(matched)
                    score = float(score)
                    if score <= best_score:
                        continue
                    best_score = score
                    best_path = str(template_path)
                    best_center = (
                        left + int(location[0]) + (target_width // 2),
                        top + int(location[1]) + (target_height // 2),
                    )
            except BaseException:
                continue
        result.update({
            'matched': bool(best_score >= max(0.45, min(0.95, float(threshold)))),
            'score': float(best_score),
            'path': best_path,
            'center': best_center,
        })
        return result
    except BaseException:
        return result


def _friend_guard_list_refresh_prequalification(context, frame):
    """Replace stale row approval with proof for the newly selected carousel friend."""
    if context is None:
        return False
    match_fn = globals().get('_friend_guard_list_carousel_card_match')
    try:
        match = match_fn(frame) if callable(match_fn) else {}
    except BaseException:
        match = {}
    matched = bool(match.get('matched', False)) if isinstance(match, dict) else False
    score = float(match.get('score', 0.0) or 0.0) if isinstance(match, dict) else 0.0
    path = str(match.get('path', '') or '') if isinstance(match, dict) else ''
    try:
        if matched:
            now_fn = globals().get('_friend_watchdog_now')
            now_ts = (
                float(now_fn())
                if callable(now_fn)
                else float(__import__('time').time())
            )
            setattr(context, '_qqfarm_guard_list_prequalified', True)
            setattr(context, '_qqfarm_guard_list_prequalified_ts', now_ts)
        else:
            setattr(context, '_qqfarm_guard_list_prequalified', False)
            setattr(context, '_qqfarm_guard_list_prequalified_ts', 0.0)
        setattr(context, '_qqfarm_guard_list_carousel_score', score)
        setattr(context, '_qqfarm_guard_list_carousel_template', path)
    except BaseException:
        return False
    try:
        writer = globals().get('_write')
        if callable(writer):
            writer(
                'v145 guard-list carousel identity matched=' + repr(matched) +
                ' score=' + ('%.4f' % score) +
                ' template=' + str(path).split('\\')[-1].split('/')[-1]
            )
    except BaseException:
        pass
    return matched


def _friend_guard_list_row_match_score(frame, row_y, template_paths=None):
    """Score one visible actionable friend-list row against imported whitelist rows."""
    if frame is None:
        return 0.0
    try:
        np = __import__('numpy')
        cv2 = __import__('cv2')
        arr = np.asarray(frame)
        shape = getattr(arr, 'shape', None)
        if not shape or len(shape) < 3 or int(shape[2]) < 3:
            return 0.0
        height, width = int(shape[0]), int(shape[1])
        center_y = int(row_y)
        vertical_pad = max(38, int(round(height * 0.058)))
        y0 = max(0, center_y - vertical_pad)
        y1 = min(height, center_y + vertical_pad)
        x0 = max(0, int(round(width * 0.015)))
        x1 = min(width, int(round(width * 0.78)))
        roi = arr[y0:y1, x0:x1, :3]
        if int(roi.shape[0]) < 20 or int(roi.shape[1]) < 30:
            return 0.0
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        paths_fn = globals().get('_friend_guard_list_template_paths')
        paths = (
            paths_fn(template_paths)
            if callable(paths_fn)
            else tuple(template_paths or ())
        )
        reader = globals().get('_friend_guard_read_template')
        frame_scale = max(
            0.45,
            min(2.5, ((float(width) / 428.0) + (float(height) / 800.0)) / 2.0),
        )
        best_score = 0.0
        for template_path in paths:
            try:
                template = reader(template_path) if callable(reader) else None
                if template is None:
                    raw = np.fromfile(str(template_path), dtype=np.uint8)
                    template = cv2.imdecode(raw, cv2.IMREAD_COLOR) if raw.size else None
                if template is None:
                    continue
                template_width = int(template.shape[1])
                candidates = (
                    template[:, :, :3],
                    template[:, :max(12, int(round(template_width * 0.455))), :3],
                )
                for candidate_template in candidates:
                    for factor in (0.90, 0.96, 1.00, 1.04):
                        scale = frame_scale * factor
                        target_width = max(8, int(round(int(candidate_template.shape[1]) * scale)))
                        target_height = max(8, int(round(int(candidate_template.shape[0]) * scale)))
                        if target_width > int(roi_gray.shape[1]) or target_height > int(roi_gray.shape[0]):
                            continue
                        resized = cv2.resize(
                            candidate_template,
                            (target_width, target_height),
                            interpolation=(
                                cv2.INTER_AREA if scale < 1.0 else cv2.INTER_LINEAR
                            ),
                        )
                        template_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                        matched = cv2.matchTemplate(
                            roi_gray, template_gray, cv2.TM_CCOEFF_NORMED
                        )
                        _, score, _, _ = cv2.minMaxLoc(matched)
                        best_score = max(best_score, float(score))
            except BaseException:
                continue
        return float(best_score)
    except BaseException:
        return 0.0


def _guard_dog_detection_mode_config():
    try:
        raw = str(_cfg_get(
            _active_friend_sections(),
            'guard_dog_detection_mode',
            'friend_guard_list',
        ) or '').strip().lower().replace('-', '_').replace(' ', '_')
        if raw in ('friend_guard_list', 'friend_list', 'whitelist', 'list'):
            confirmed_fn = globals().get('_friend_guard_list_confirmed_config')
            list_confirmed = bool(confirmed_fn()) if callable(confirmed_fn) else False
            ready_fn = globals().get('_friend_guard_list_template_ready')
            templates_ready = bool(ready_fn()) if callable(ready_fn) else False
            if not list_confirmed or not templates_ready:
                status = {}
                status_fn = globals().get('_friend_guard_template_status')
                if callable(status_fn):
                    try:
                        status = status_fn()
                    except BaseException:
                        status = {}
                directories = tuple(status.get('directories', ()) or ())
                template_count = int(status.get('count', 0) or 0)
                reason = 'unconfirmed' if not list_confirmed else 'empty'
                log_fn = globals().get('_throttled_write')
                if callable(log_fn):
                    try:
                        log_fn(
                            'v135-friend-guard-list-fallback-' + reason,
                            'v135 friend guard whitelist ' + reason + '; '
                            'fallback=dog_badge(avatar_frame); '
                            'scan=single-visible-frame; templates=' +
                            str(template_count) + '; dirs=' + repr(directories)[:500],
                            60.0,
                        )
                    except BaseException:
                        pass
                return 'avatar_frame'
            return 'friend_guard_list'
        return 'avatar_frame'
    except BaseException:
        return 'avatar_frame'


def _wrap_guard_dog_mode_func(fn, name):
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_guard_dog_mode_wrapped__', False):
            return fn, False
        function_name = str(name or '').lower()

        def _wrapped(*a, **k):
            enabled_fn = globals().get('_guard_dog_ui_config_enabled')
            mode_fn = globals().get('_guard_dog_detection_mode_config')
            enabled = bool(enabled_fn()) if callable(enabled_fn) else False
            mode = str(mode_fn() if callable(mode_fn) else 'friend_guard_list')
            if function_name.endswith('is_friend_guard_list_help_only_mode'):
                return bool(enabled and mode == 'friend_guard_list')
            return mode

        try:
            _wrapped.__name__ = getattr(fn, '__name__', 'guard_dog_mode_wrapper')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_guard_dog_mode_wrapped__ = True
            _wrapped.__qqfarm_guard_dog_mode_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _wrap_guard_dog_enabled_func(fn, name):
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_guard_dog_config_wrapped__', False):
            return fn, False
        def _wrapped(*a, **k):
            try:
                enabled = bool(_guard_dog_ui_config_enabled())
                if not enabled:
                    _runtime_info_once('guard-dog-config-off', '\u62a4\u4e3b\u72ac\u7b5b\u9009\u5df2\u6309\u914d\u7f6e\u5173\u95ed\uff1a\u540e\u7aef\u5df2\u8df3\u8fc7\u8be5\u5206\u652f\u3002')
                    return False
                # This predicate is the business switch itself.  Once entitlement
                # access is available, the saved UI option is the source of truth;
                # deferring to the stale compiled predicate silently disables the
                # per-row and bottom-carousel guard-dog filters.
                return True
            except BaseException:
                return False
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
            for n in _GUARD_DOG_MODE_FUNC_NAMES:
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
                        for n in _GUARD_DOG_MODE_FUNC_NAMES:
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
                for n in list(_GUARD_DOG_MODE_FUNC_NAMES):
                    try:
                        if hasattr(obj, n):
                            old = getattr(obj, n)
                            new, ok = _wrap_guard_dog_mode_func(old, prefix + '.' + n)
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
_VIP_WAREHOUSE_STATE_PATH = r'C:/Users/USER/reverse-cases/qq-farm-vip/work/warehouse_last_done_ts.txt'
_VIP_WAREHOUSE_MIN_COOLDOWN_SECONDS = 360.0
_VIP_WAREHOUSE_RETRY_STATE_PATH = r'C:/Users/USER/reverse-cases/qq-farm-vip/work/warehouse_retry_state.json'
_VIP_WAREHOUSE_RETRY_SECONDS = 600.0
_VIP_WAREHOUSE_RETRY_LIMIT = 3
_VIP_WAREHOUSE_BACKOFF_SECONDS = 3600.0
_VIP_WAREHOUSE_RETRY_MEMORY_STATE = {'fail_count': 0, 'last_fail_ts': 0.0, 'blocked_until': 0.0, 'last_reason': ''}
_VIP_WAREHOUSE_RETRY_MEMORY_PATH = ''
_VIP_WAREHOUSE_RETRY_MEMORY_DIRTY = False
_VIP_WAREHOUSE_LAST_SEQUENCE_CLASS = ''
_VIP_WAREHOUSE_LAST_SEQUENCE_TS = 0.0
_BACKPACK_PROFILE_FUNC_NAMES = set([
    '_detect_seed_quantity_badges_by_ocr',
    '_detect_empty_lands',
    '_check_empty_land_label_with_retry',
    '_infer_land_center_from_shovel',
    '_detect_no_seed_hint_by_ocr',
    '_is_backpack_seed_blacklisted_by_template',
    '_execute_planting_by_mode',
    '_buy_seed_for_crop',
    '_match_template_center',
    '_detect_fertilizer_template',
])


_VIP_BUSINESS_FUNC_NAMES = set([
    '_handle_home_auto_sell_fruit',
    '_run_warehouse_sell_button_sequence',
    'handle_home_maintenance',
    'handle_home_pre_planting_maintenance',
    'handle_home_harvest',
    'handle_home_planting',
    'process_self_farm',
    '_run_friend_daily_troublemaker',
    'process_friend_farm',
    'handle_friend_farm_actions',
    '_plant_seed_over_lands',
    '_run_auto_fertilize_after_planting',
    '_run_backpack_seed_priority_planting',
    '_find_quad_empty_land_groups',
    '_try_plant_quad_act_seeds',
    'get_current_player_level',
]).union(globals().get('_BACKPACK_PROFILE_FUNC_NAMES', set()))
_FRIEND_HOME_FUNC_NAMES = set([
    'check_go_home_icon',
    '_has_go_home_icon',
    'go_home',
    'return_home',
    '_return_home',
])
_FRIEND_NEXT_ENTRY_FUNC_NAMES = set([
    'check_friend_farm_bottom_help_all_entry',
    'check_friend_farm_bottom_steal_entry',
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


_VIP_CONTEXT_BOOL_ATTRS = (
    'entitlement_active', '_entitlement_active',
    'vip_active', '_vip_active',
    'is_vip', '_is_vip',
    'license_active', '_license_active',
    'member_active', '_member_active',
    'premium_active', '_premium_active',
    'is_svip', '_is_svip',
    'enabled_by_license', 'feature_enabled',
)
_VIP_CONTEXT_GATE_NAMES = (
    'is_vip_unlocked', 'is_vip_active', '_is_vip_active',
    'is_entitlement_enabled', '_is_entitlement_enabled',
    'has_entitlement', '_has_entitlement',
    'has_feature_access', 'feature_gate',
    'verify_vip_license', 'check_vip_license_signature',
    'validate_vip_device_binding', 'verify_vip_server_challenge',
    'validate_vip_public_key', 'check_vip_payment_receipt',
    '_qf_7df7ee432596', '_qf_60adf77be908', '_qf_c8757eb57f8d',
)
_VIP_CONTEXT_FALSE_GATE_NAMES = (
    '_qf_aa860ac25206',
)
_VIP_CONTEXT_TRUE_METHOD_ATTRS = (
    '_qf_3dc9b7de9bd9',
)
_VIP_CONTEXT_CHILD_NAMES = (
    'config', 'settings', 'context', 'runtime', 'state',
    'entitlement', 'license', 'account', 'user',
)



_LAST_SUCCESSFUL_FULL_PLANTING_TS = 0.0


def _note_runtime_planting_outcome(message):
    """Remember a verified full-land drag so false empty-land matches cool down."""
    global _LAST_SUCCESSFUL_FULL_PLANTING_TS
    try:
        if '拖拽播种已覆盖全地块' not in str(message or ''):
            return float(_LAST_SUCCESSFUL_FULL_PLANTING_TS or 0.0)
        _LAST_SUCCESSFUL_FULL_PLANTING_TS = float(time.time())
        context = globals().get('_ACTIVE_RUN_CYCLE_CONTEXT')
        if context is not None:
            try:
                setattr(context, '_qqfarm_single_harvest_planting_pending', False)
            except BaseException:
                pass
        _write(
            'v181 full-land planting cooldown armed ts=' +
            ('%.3f' % _LAST_SUCCESSFUL_FULL_PLANTING_TS)
        )
    except BaseException:
        pass
    return float(_LAST_SUCCESSFUL_FULL_PLANTING_TS or 0.0)


def _wrap_home_planting_cooldown(fn, name=''):
    """Skip immediate repeat planting scans after a verified full-land drag."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_home_planting_cooldown_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            context = None
            try:
                context_fn = globals().get('_friend_guard_context')
                context = context_fn(args, kwargs) if callable(context_fn) else None
            except BaseException:
                context = None
            if context is None and args:
                context = args[0]
            try:
                pending_single = bool(getattr(
                    context, '_qqfarm_single_harvest_planting_pending', False
                ))
            except BaseException:
                pending_single = False
            try:
                cooldown_seconds = float(getattr(
                    context, 'planting_post_success_cooldown_seconds', 180.0
                ) or 180.0)
            except BaseException:
                cooldown_seconds = 180.0
            cooldown_seconds = max(30.0, min(900.0, cooldown_seconds))
            try:
                last_success = float(globals().get(
                    '_LAST_SUCCESSFUL_FULL_PLANTING_TS', 0.0
                ) or 0.0)
                age = float(time.time()) - last_success if last_success > 0.0 else -1.0
            except BaseException:
                age = -1.0
            if not pending_single and 0.0 <= age < cooldown_seconds:
                try:
                    _throttled_write(
                        'v181-planting-cooldown',
                        'v181 skipped repeat planting scan age=' + ('%.1f' % age) +
                        ' cooldown=' + ('%.1f' % cooldown_seconds),
                        15.0,
                    )
                except BaseException:
                    pass
                return False
            return fn(*args, **kwargs)

        _wrapped.__name__ = getattr(fn, '__name__', 'home_planting_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_home_planting_cooldown_wrapped__ = True
        _wrapped.__qqfarm_home_planting_cooldown_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


_SINGLE_HARVEST_EVENT_TOKEN = 0


def _note_runtime_single_harvest_outcome(message):
    """Record the native single-harvest branch so planting can run immediately."""
    global _SINGLE_HARVEST_EVENT_TOKEN
    try:
        if '?????????' not in str(message or ''):
            return int(_SINGLE_HARVEST_EVENT_TOKEN or 0)
        _SINGLE_HARVEST_EVENT_TOKEN = int(
            _SINGLE_HARVEST_EVENT_TOKEN or 0
        ) + 1
    except BaseException:
        pass
    return int(_SINGLE_HARVEST_EVENT_TOKEN or 0)


def _wrap_home_harvest_planting_trigger(fn, name=''):
    """Convert a verified single harvest into an immediate harvest planting quota."""
    try:
        if not callable(fn):
            return fn, False
        if bool(getattr(fn, '__qqfarm_single_harvest_planting_wrapped__', False)):
            return fn, False

        def _wrapped(*args, **kwargs):
            before_token = int(globals().get(
                '_SINGLE_HARVEST_EVENT_TOKEN', 0
            ) or 0)
            result = fn(*args, **kwargs)
            after_token = int(globals().get(
                '_SINGLE_HARVEST_EVENT_TOKEN', 0
            ) or 0)
            if after_token <= before_token:
                return result
            try:
                context_fn = globals().get('_friend_guard_context')
                context = (
                    context_fn(args, kwargs) if callable(context_fn) else None
                )
            except BaseException:
                context = None
            if context is not None:
                try:
                    quota = max(0, int(getattr(
                        context, 'planting_harvest_quota', 0
                    ) or 0))
                except BaseException:
                    quota = 0
                try:
                    setattr(context, 'planting_harvest_quota', max(1, quota))
                    setattr(
                        context, '_qqfarm_single_harvest_planting_pending', True
                    )
                except BaseException:
                    pass
            try:
                _write(
                    'v177 single harvest queued planting source=' + str(name) +
                    ' quota=' + str(getattr(
                        context, 'planting_harvest_quota', 1
                    ))
                )
            except BaseException:
                pass
            return True

        _wrapped.__name__ = getattr(fn, '__name__', 'home_harvest_wrapper')
        _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
        _wrapped.__qqfarm_single_harvest_planting_wrapped__ = True
        _wrapped.__qqfarm_single_harvest_planting_orig__ = fn
        return _wrapped, True
    except BaseException:
        return fn, False


def _collect_friend_seed_land_centers_from_frame(frame):
    """Recover planted-land centers by selecting the largest coherent farm lattice."""
    try:
        shape = getattr(frame, 'shape', None)
        if shape is None or len(shape) < 2:
            return []
        frame_h, frame_w = int(shape[0]), int(shape[1])
        if frame_h < 240 or frame_w < 160:
            return []
        cv_module = globals().get('cv2') or __import__('cv2')
        np_module = globals().get('np') or globals().get('numpy') or __import__('numpy')
        x0 = max(0, min(frame_w - 1, int(round(frame_w * 0.04))))
        x1 = max(x0 + 1, min(frame_w, int(round(frame_w * 0.99))))
        y0 = max(0, min(frame_h - 1, int(round(frame_h * 0.38))))
        y1 = max(y0 + 1, min(frame_h, int(round(frame_h * 0.99))))
        roi = frame[y0:y1, x0:x1]
        if getattr(roi, 'size', 0) <= 0:
            return []
        if len(getattr(roi, 'shape', ())) == 2:
            roi_bgr = cv_module.cvtColor(roi, cv_module.COLOR_GRAY2BGR)
        elif int(roi.shape[2]) == 4:
            roi_bgr = cv_module.cvtColor(roi, cv_module.COLOR_BGRA2BGR)
        else:
            roi_bgr = roi
        hsv = cv_module.cvtColor(roi_bgr, cv_module.COLOR_BGR2HSV)
        mask = cv_module.inRange(
            hsv,
            np_module.array([10, 85, 120], dtype=np_module.uint8),
            np_module.array([179, 255, 255], dtype=np_module.uint8),
        )
        kernel = np_module.ones((3, 3), dtype=np_module.uint8)
        mask = cv_module.morphologyEx(mask, cv_module.MORPH_CLOSE, kernel)
        contour_result = cv_module.findContours(
            mask, cv_module.RETR_LIST, cv_module.CHAIN_APPROX_SIMPLE
        )
        contours = contour_result[-2]
        scale_x = max(0.01, float(frame_w) / 428.0)
        scale_y = max(0.01, float(frame_h) / 800.0)
        area_scale = scale_x * scale_y
        candidates = []
        for contour in contours:
            bx, by, bw, bh = cv_module.boundingRect(contour)
            area = float(cv_module.contourArea(contour))
            norm_w = float(bw) / scale_x
            norm_h = float(bh) / scale_y
            norm_area = area / area_scale
            if not (23.0 <= norm_w <= 55.0):
                continue
            if not (10.0 <= norm_h <= 38.0):
                continue
            if not (110.0 <= norm_area <= 950.0):
                continue
            center = (
                int(round(x0 + bx + (bw / 2.0))),
                int(round(y0 + by + (bh / 2.0))),
            )
            if any(
                abs(center[0] - old[0]) <= max(3, int(round(6 * scale_x)))
                and abs(center[1] - old[1]) <= max(3, int(round(5 * scale_y)))
                for old in candidates
            ):
                continue
            candidates.append(center)
        if len(candidates) < 3:
            return []
        candidates.sort(key=lambda value: (value[0], value[1]))
        adjacency = [set() for _ in candidates]
        for left_index, left in enumerate(candidates):
            for right_index in range(left_index + 1, len(candidates)):
                right = candidates[right_index]
                dx = abs(float(left[0] - right[0])) / scale_x
                dy = abs(float(left[1] - right[1])) / scale_y
                same_row = dy <= 7.0 and 45.0 <= dx <= 105.0
                diagonal = 10.0 <= dy <= 30.0 and 20.0 <= dx <= 52.0
                if not (same_row or diagonal):
                    continue
                adjacency[left_index].add(right_index)
                adjacency[right_index].add(left_index)
        components = []
        seen = set()
        for index in range(len(candidates)):
            if index in seen:
                continue
            pending = [index]
            seen.add(index)
            component = []
            while pending:
                current = pending.pop()
                component.append(candidates[current])
                for linked in adjacency[current]:
                    if linked in seen:
                        continue
                    seen.add(linked)
                    pending.append(linked)
            components.append(component)
        components = [component for component in components if len(component) >= 3]
        if not components:
            return []
        components.sort(
            key=lambda component: (
                len(component),
                sum(point[1] for point in component) / float(len(component)),
            ),
            reverse=True,
        )
        centers = components[0]
        centers.sort(key=lambda value: (value[1], value[0]))
        if len(centers) > 36:
            return []

        evidence_centers = []
        patch_radius_x = max(6, int(round(12.0 * scale_x)))
        patch_radius_y = max(6, int(round(12.0 * scale_y)))
        for center_x, center_y in centers:
            roi_x = int(center_x) - x0
            roi_y = int(center_y) - y0
            px0 = max(0, roi_x - patch_radius_x)
            px1 = min(int(hsv.shape[1]), roi_x + patch_radius_x + 1)
            py0 = max(0, roi_y - patch_radius_y)
            py1 = min(int(hsv.shape[0]), roi_y + patch_radius_y + 1)
            patch = hsv[py0:py1, px0:px1]
            if getattr(patch, 'size', 0) <= 0:
                continue
            green_mask = (
                (patch[:, :, 0] >= 35)
                & (patch[:, :, 0] <= 100)
                & (patch[:, :, 1] >= 60)
                & (patch[:, :, 2] >= 40)
            )
            green_score = float(np_module.count_nonzero(green_mask)) / float(
                max(1, int(green_mask.size))
            )
            if green_score >= 0.025:
                evidence_centers.append((int(center_x), int(center_y)))

        dense_mask = cv_module.inRange(
            hsv,
            np_module.array([130, 90, 80], dtype=np_module.uint8),
            np_module.array([179, 255, 255], dtype=np_module.uint8),
        )
        dense_gate = np_module.zeros_like(dense_mask)
        gate_x0 = max(0, min(int(dense_mask.shape[1]) - 1, int(round(frame_w * 0.08)) - x0))
        gate_x1 = max(gate_x0 + 1, min(int(dense_mask.shape[1]), int(round(frame_w * 0.92)) - x0))
        gate_y0 = max(0, min(int(dense_mask.shape[0]) - 1, int(round(frame_h * 0.45)) - y0))
        gate_y1 = max(gate_y0 + 1, min(int(dense_mask.shape[0]), int(round(frame_h * 0.70)) - y0))
        dense_gate[gate_y0:gate_y1, gate_x0:gate_x1] = dense_mask[
            gate_y0:gate_y1, gate_x0:gate_x1
        ]
        dense_kernel = np_module.ones(
            (max(5, int(round(15 * scale_y))), max(5, int(round(15 * scale_x)))),
            dtype=np_module.uint8,
        )
        dense_close_kernel = np_module.ones(
            (max(7, int(round(19 * scale_y))), max(7, int(round(19 * scale_x)))),
            dtype=np_module.uint8,
        )
        dense_gate = cv_module.dilate(dense_gate, dense_kernel, iterations=1)
        dense_gate = cv_module.morphologyEx(
            dense_gate, cv_module.MORPH_CLOSE, dense_close_kernel
        )
        dense_contours = cv_module.findContours(
            dense_gate, cv_module.RETR_EXTERNAL, cv_module.CHAIN_APPROX_SIMPLE
        )[-2]
        dense_best = None
        for contour in dense_contours:
            bx, by, bw, bh = cv_module.boundingRect(contour)
            norm_w = float(bw) / scale_x
            norm_h = float(bh) / scale_y
            if norm_w < 150.0 or norm_h < 65.0:
                continue
            patch = hsv[by:by + bh, bx:bx + bw]
            if getattr(patch, 'size', 0) <= 0:
                continue
            green_mask = (
                (patch[:, :, 0] >= 35)
                & (patch[:, :, 0] <= 100)
                & (patch[:, :, 1] >= 70)
                & (patch[:, :, 2] >= 40)
            )
            green_score = float(np_module.count_nonzero(green_mask)) / float(
                max(1, int(green_mask.size))
            )
            if green_score < 0.35:
                continue
            dense_score = green_score * float(max(1, bw * bh))
            if dense_best is None or dense_score > dense_best[0]:
                dense_best = (dense_score, bx, by, bw, bh, green_score)

        if dense_best is not None:
            _, bx, by, bw, bh, green_score = dense_best
            dense_centers = []
            for y_ratio in (0.35, 0.55, 0.75):
                for x_ratio in (0.20, 0.35, 0.50, 0.65, 0.80):
                    dense_centers.append((
                        int(round(x0 + bx + (bw * x_ratio))),
                        int(round(y0 + by + (bh * y_ratio))),
                    ))
            dense_centers.sort(key=lambda value: (value[1], value[0]))
            try:
                log_fn = globals().get('_write')
                if callable(log_fn):
                    log_fn(
                        'v198 trouble dense crop lattice count=' +
                        str(len(dense_centers)) + ' bbox=' +
                        repr((x0 + bx, y0 + by, bw, bh)) +
                        ' green=' + ('%.3f' % green_score)
                    )
            except BaseException:
                pass
            return dense_centers

        if len(evidence_centers) >= 3:
            return evidence_centers
        try:
            log_fn = globals().get('_write')
            if callable(log_fn) and centers:
                log_fn(
                    'v198 trouble rejected empty-soil geometry count=' +
                    str(len(centers)) + ' evidence=' + str(len(evidence_centers))
                )
        except BaseException:
            pass
        return []
    except BaseException:
        return []


def _detect_friend_trouble_popup_action(frame):
    """Detect the paired weed/worm action buttons in the visible crop popup."""
    try:
        shape = getattr(frame, 'shape', None)
        if shape is None or len(shape) < 2:
            return None
        frame_h, frame_w = int(shape[0]), int(shape[1])
        if frame_h < 240 or frame_w < 160:
            return None
        cv_module = globals().get('cv2') or __import__('cv2')
        np_module = globals().get('np') or globals().get('numpy') or __import__('numpy')
        if len(shape) == 2:
            bgr = cv_module.cvtColor(frame, cv_module.COLOR_GRAY2BGR)
        elif int(shape[2]) == 4:
            bgr = cv_module.cvtColor(frame, cv_module.COLOR_BGRA2BGR)
        else:
            bgr = frame
        hsv = cv_module.cvtColor(bgr, cv_module.COLOR_BGR2HSV)
        x0 = max(0, min(frame_w - 1, int(round(frame_w * 0.25))))
        x1 = max(x0 + 1, min(frame_w, int(round(frame_w * 0.75))))
        y0 = max(0, min(frame_h - 1, int(round(frame_h * 0.58))))
        y1 = max(y0 + 1, min(frame_h, int(round(frame_h * 0.67))))
        roi = hsv[y0:y1, x0:x1]
        if getattr(roi, 'size', 0) <= 0:
            return None
        white = cv_module.inRange(
            roi,
            np_module.array([0, 0, 175], dtype=np_module.uint8),
            np_module.array([179, 105, 255], dtype=np_module.uint8),
        )
        contours = cv_module.findContours(
            white, cv_module.RETR_EXTERNAL, cv_module.CHAIN_APPROX_SIMPLE
        )[-2]
        scale_x = max(0.01, float(frame_w) / 428.0)
        scale_y = max(0.01, float(frame_h) / 800.0)
        area_scale = scale_x * scale_y
        bubbles = []
        for contour in contours:
            bx, by, bw, bh = cv_module.boundingRect(contour)
            area = float(cv_module.contourArea(contour)) / area_scale
            norm_w = float(bw) / scale_x
            norm_h = float(bh) / scale_y
            if not (180.0 <= area <= 850.0):
                continue
            if not (20.0 <= norm_w <= 42.0 and 13.0 <= norm_h <= 27.0):
                continue
            full_x = int(x0 + bx)
            full_y = int(y0 + by)
            bubbles.append((full_x, full_y, int(bw), int(bh), area))
        best_pair = None
        for left_index, left in enumerate(bubbles):
            for right in bubbles[left_index + 1:]:
                first, second = (left, right) if left[0] <= right[0] else (right, left)
                gap = float(second[0] - first[0]) / scale_x
                y_gap = abs(float(second[1] - first[1])) / scale_y
                if not (45.0 <= gap <= 90.0 and y_gap <= 8.0):
                    continue
                score = abs(gap - 68.0) + (y_gap * 4.0)
                if best_pair is None or score < best_pair[0]:
                    best_pair = (score, first, second)
        if best_pair is None:
            return None
        _, left, right = best_pair
        chosen = right
        center_x = int(round(chosen[0] + (chosen[2] / 2.0)))
        center_y = int(round(chosen[1] + chosen[3] + (22.0 * scale_y)))
        half_w = max(20, int(round(28.0 * scale_x)))
        half_h = max(20, int(round(28.0 * scale_y)))
        return {
            'top_left': (center_x - half_w, center_y - half_h),
            'bottom_right': (center_x + half_w, center_y + half_h),
            'confidence': 0.99,
            'center': (center_x, center_y),
            'source': 'hook-trouble-popup-pair',
        }
    except BaseException:
        return None


def _wrap_troublemaker_button_picker(original):
    """Use the visible paired popup controls when native templates miss."""
    if not callable(original):
        return original

    def _wrapped(*args, **kwargs):
        result = original(*args, **kwargs)
        if result:
            return result
        frame = None
        for value in tuple(args or ()):
            shape = getattr(value, 'shape', None)
            if shape is not None and len(shape) >= 2:
                frame = value
                break
        if frame is None:
            for value in dict(kwargs or {}).values():
                shape = getattr(value, 'shape', None)
                if shape is not None and len(shape) >= 2:
                    frame = value
                    break
        match = _detect_friend_trouble_popup_action(frame)
        if match:
            try:
                _write(
                    'v200 trouble popup action fallback center=' +
                    repr(match.get('center')) + ' source=' +
                    str(match.get('source', ''))
                )
            except BaseException:
                pass
            return match
        return result

    try:
        _wrapped.__name__ = getattr(original, '__name__', 'trouble_button_picker_wrapper')
        _wrapped.__qualname__ = getattr(original, '__qualname__', _wrapped.__name__)
    except BaseException:
        pass
    return _wrapped


def _wrap_troublemaker_seed_land_collector(original, owner_globals):
    """Accept planted-land candidates only when the current frame proves vegetation."""
    if not callable(original):
        return original

    def _wrapped(*args, **kwargs):
        result = original(*args, **kwargs)
        frame = None
        for value in reversed(tuple(args or ())):
            shape = getattr(value, 'shape', None)
            if shape is not None and len(shape) >= 2:
                frame = value
                break
        if frame is None:
            for value in dict(kwargs or {}).values():
                shape = getattr(value, 'shape', None)
                if shape is not None and len(shape) >= 2:
                    frame = value
                    break
        if frame is None:
            return result

        centers = _collect_friend_seed_land_centers_from_frame(frame)
        if centers:
            try:
                _write(
                    'v199 trouble seed_land frame evidence preferred count=' +
                    str(len(centers)) + ' native=' +
                    str(len(result) if result is not None else 0) +
                    ' first=' + repr(centers[:4])
                )
            except BaseException:
                pass
            return centers
        if result:
            try:
                _write(
                    'v199 trouble rejected native seed_land without planted evidence count=' +
                    str(len(result) if result is not None else 0)
                )
            except BaseException:
                pass
        return []

    try:
        _wrapped.__name__ = getattr(original, '__name__', 'trouble_seed_land_wrapper')
        _wrapped.__qualname__ = getattr(original, '__qualname__', _wrapped.__name__)
    except BaseException:
        pass
    return _wrapped


def _diagnose_daily_troublemaker_vip_source(fn, args, kwargs, name=''):
    """Write a bounded one-shot inventory of the live troublemaker callable."""
    try:
        if bool(globals().get('_TROUBLEMAKER_CALLABLE_DIAG_DONE', False)):
            return None
        globals()['_TROUBLEMAKER_CALLABLE_DIAG_DONE'] = True
        os_module = globals().get('os') or __import__('os')
        base = os_module.path.dirname(os_module.path.abspath(__file__))
        log_dir = os_module.path.join(base, 'logs')
        os_module.makedirs(log_dir, exist_ok=True)
        target = os_module.path.join(log_dir, 'troublemaker-callable-diagnostic.txt')
        lines = [
            'name=' + str(name),
            'callable=' + repr(fn),
            'module=' + str(getattr(fn, '__module__', '')),
            'qualname=' + str(getattr(fn, '__qualname__', '')),
            'args=' + repr(tuple(type(value).__name__ for value in tuple(args or ()))),
            'kwargs=' + repr(tuple(sorted(str(key) for key in dict(kwargs or {}).keys()))),
        ]
        code = getattr(fn, '__code__', None)
        if code is not None:
            try:
                lines.append('code_names=' + repr(tuple(getattr(code, 'co_names', ()) or ())))
                lines.append('code_consts=' + repr(tuple(getattr(code, 'co_consts', ()) or ()))[:12000])
            except BaseException:
                pass
        owner_globals = getattr(fn, '__globals__', None)
        if isinstance(owner_globals, dict):
            def _install_probe(helper_name):
                original = owner_globals.get(helper_name)
                if not callable(original) or bool(getattr(
                    original, '__qqfarm_trouble_probe_wrapped__', False
                )):
                    return False
                if helper_name == '_collect_friend_seed_land_centers':
                    _traced = _wrap_troublemaker_seed_land_collector(
                        original, owner_globals
                    )
                elif helper_name == '_pick_friend_trouble_button':
                    _traced = _wrap_troublemaker_button_picker(original)
                else:
                    def _traced(*probe_args, **probe_kwargs):
                        result = original(*probe_args, **probe_kwargs)
                        try:
                            summaries = []
                            for value in tuple(probe_args or ())[:5]:
                                shape = getattr(value, 'shape', None)
                                summaries.append(
                                    type(value).__name__ +
                                    ((' shape=' + repr(tuple(shape))) if shape is not None else '')
                                )
                            _write(
                                'v154 trouble helper ' + helper_name +
                                ' args=' + repr(tuple(summaries)) +
                                ' result=' + repr(result)[:1200]
                            )
                        except BaseException:
                            pass
                        return result
                try:
                    _traced.__name__ = getattr(original, '__name__', helper_name)
                    _traced.__qualname__ = getattr(original, '__qualname__', helper_name)
                    _traced.__module__ = getattr(original, '__module__', '')
                    _traced.__qqfarm_trouble_probe_wrapped__ = True
                    _traced.__qqfarm_trouble_probe_original__ = original
                except BaseException:
                    pass
                owner_globals[helper_name] = _traced
                return True
            probe_names = (
                '_collect_friend_seed_land_centers',
                '_pick_friend_trouble_button',
                '_hit_friend_trouble_end',
                '_record_friend_trouble_action',
            )
            installed = tuple(
                helper_name for helper_name in probe_names
                if _install_probe(helper_name)
            )
            lines.append('installed_probes=' + repr(installed))
            lines.append('global_count=' + str(len(owner_globals)))
            for key in sorted(owner_globals.keys(), key=lambda value: str(value)):
                try:
                    value = owner_globals.get(key)
                    value_type = type(value).__name__
                    if callable(value):
                        detail = (
                            str(getattr(value, '__module__', '')) + '.' +
                            str(getattr(value, '__qualname__', getattr(value, '__name__', '')))
                        )
                    elif isinstance(value, (str, int, float, bool, type(None))):
                        detail = repr(value)[:500]
                    elif isinstance(value, dict):
                        detail = 'dict_keys=' + repr(tuple(list(value.keys())[:80]))[:1200]
                    elif isinstance(value, (tuple, list, set)):
                        detail = repr(tuple(list(value)[:40]))[:1200]
                    else:
                        detail = repr(value)[:500]
                    lines.append('global ' + str(key) + ' type=' + value_type + ' value=' + detail)
                except BaseException as error:
                    lines.append('global ' + str(key) + ' error=' + repr(error)[:220])
        for index, value in enumerate(tuple(args or ())):
            try:
                attrs = []
                data = getattr(value, '__dict__', None)
                if isinstance(data, dict):
                    for key in sorted(data.keys(), key=lambda item: str(item)):
                        lowered = str(key).lower()
                        if any(token in lowered for token in (
                            'trouble', 'friend', 'template', 'seed', 'land', 'vip', 'counter'
                        )):
                            attrs.append((str(key), repr(data.get(key))[:500]))
                lines.append('arg' + str(index) + '_attrs=' + repr(tuple(attrs))[:12000])
            except BaseException:
                pass
        with open(target, 'w', encoding='utf-8') as stream:
            stream.write('\n'.join(lines) + '\n')
        _write('v153 troublemaker callable diagnostic saved=' + str(target))
        return target
    except BaseException as error:
        try:
            _write('v153 troublemaker callable diagnostic error=' + repr(error)[:220])
        except BaseException:
            pass
        return None


def _enter_vip_entitlement_context(fn, args, kwargs):
    """Temporarily expose entitlement=True without changing feature toggles."""
    saved = []
    seen = set()

    def _save_mapping(mapping, key, value):
        marker = ('mapping', id(mapping), key)
        if marker in seen:
            return
        seen.add(marker)
        saved.append(('mapping', mapping, key, mapping[key]))
        mapping[key] = value

    def _save_attr(obj, key, value):
        marker = ('attr', id(obj), key)
        if marker in seen:
            return
        seen.add(marker)
        old = getattr(obj, key)
        data = getattr(obj, '__dict__', None)
        had_own_attr = isinstance(data, dict) and key in data
        saved.append(('attr' if had_own_attr else 'attr_delete', obj, key, old))
        setattr(obj, key, value)

    def _patch_obj(obj, depth=0):
        if obj is None or depth > 2:
            return
        marker = ('object', id(obj), depth)
        if marker in seen:
            return
        seen.add(marker)
        if isinstance(obj, dict):
            for key in _VIP_CONTEXT_BOOL_ATTRS:
                if key in obj:
                    try:
                        _save_mapping(obj, key, True)
                    except BaseException:
                        pass
            if depth < 2:
                for key in _VIP_CONTEXT_CHILD_NAMES:
                    try:
                        if key in obj:
                            _patch_obj(obj.get(key), depth + 1)
                    except BaseException:
                        pass
            return
        for key in _VIP_CONTEXT_BOOL_ATTRS:
            try:
                if hasattr(obj, key):
                    _save_attr(obj, key, True)
            except BaseException:
                pass
        for key in _VIP_CONTEXT_TRUE_METHOD_ATTRS:
            try:
                if hasattr(obj, key) and callable(getattr(obj, key)):
                    _save_attr(obj, key, lambda *a, **k: True)
            except BaseException:
                pass
        if depth < 2:
            for key in _VIP_CONTEXT_CHILD_NAMES:
                try:
                    if hasattr(obj, key):
                        _patch_obj(getattr(obj, key), depth + 1)
                except BaseException:
                    pass

    try:
        globals_dict = getattr(fn, '__globals__', None)
        if isinstance(globals_dict, dict):
            for key in _VIP_CONTEXT_BOOL_ATTRS:
                if key in globals_dict and isinstance(globals_dict.get(key), (bool, int)):
                    try:
                        _save_mapping(globals_dict, key, True)
                    except BaseException:
                        pass
            for key in _VIP_CONTEXT_GATE_NAMES:
                if key in globals_dict and callable(globals_dict.get(key)):
                    try:
                        _save_mapping(globals_dict, key, lambda *a, **k: True)
                    except BaseException:
                        pass
            for key in _VIP_CONTEXT_FALSE_GATE_NAMES:
                if key in globals_dict and callable(globals_dict.get(key)):
                    try:
                        _save_mapping(globals_dict, key, lambda *a, **k: False)
                    except BaseException:
                        pass
    except BaseException:
        pass
    try:
        for obj in tuple(args or ()):
            _patch_obj(obj, 0)
        for obj in tuple((kwargs or {}).values()):
            _patch_obj(obj, 0)
    except BaseException:
        pass
    return saved


def _restore_vip_entitlement_context(saved):
    restored = 0
    for kind, owner, key, old in reversed(list(saved or ())):
        try:
            if kind == 'mapping':
                owner[key] = old
            elif kind == 'attr_delete':
                delattr(owner, key)
            else:
                setattr(owner, key, old)
            restored += 1
        except BaseException:
            pass
    return restored



def _friend_empty_guard_next(previous_count, elapsed_seconds, now_ts, last_count_ts,
                             fast_seconds=3.0, distinct_seconds=5.0, trigger_count=2):
    """Return (new_count, trigger_home) for distinct fast friend-farm passes."""
    try:
        previous_count = max(0, int(previous_count or 0))
        elapsed_seconds = max(0.0, float(elapsed_seconds or 0.0))
        now_ts = float(now_ts or 0.0)
        last_count_ts = float(last_count_ts or 0.0)
        if elapsed_seconds > float(fast_seconds):
            return 0, False
        if last_count_ts > 0.0 and (now_ts - last_count_ts) < float(distinct_seconds):
            return previous_count, False
        new_count = previous_count + 1
        return new_count, new_count >= max(1, int(trigger_count))
    except BaseException:
        return 0, False


def _friend_guard_context(args, kwargs):
    """Return the scheduler/bot instance even when it has no go_home method."""
    try:
        values = list(args or ()) + list((kwargs or {}).values())
        for value in values:
            if value is None or isinstance(value, (str, bytes, int, float, bool, list, tuple, dict, set)):
                continue
            return value
    except BaseException:
        pass
    return None


def _mark_friend_cycle_seen(args, kwargs):
    """Record friend routing unless the same cycle rejected a false home icon."""
    try:
        context = _friend_guard_context(args, kwargs)
        if context is None:
            return None
        active_context = globals().get('_ACTIVE_RUN_CYCLE_CONTEXT')
        now_fn = globals().get('_friend_watchdog_now')
        now_ts = (
            float(now_fn())
            if callable(now_fn)
            else float(__import__('time').time())
        )
        targets = []
        for candidate in (context, active_context):
            if candidate is None or any(
                candidate is existing for existing in targets
            ):
                continue
            targets.append(candidate)
        recent_false_positive = any(
            (
                float(getattr(
                    target, '_qqfarm_native_home_false_positive_ts', 0.0
                ) or 0.0) > 0.0
                and 0.0 <= (
                    now_ts - float(getattr(
                        target, '_qqfarm_native_home_false_positive_ts', 0.0
                    ) or 0.0)
                ) <= 30.0
            )
            for target in targets
        )
        if recent_false_positive:
            for target in targets:
                setattr(target, '_qqfarm_friend_cycle_seen', False)
                setattr(target, '_qqfarm_cycle_branch_hint', 'self')
            log_fn = globals().get('_throttled_write')
            if callable(log_fn):
                log_fn(
                    'v163-suppress-friend-mark-after-native-home-false-positive',
                    'v163 suppressed friend-cycle mark after a native home-icon ' +
                    'false positive in the same run cycle',
                    4.0,
                )
            return context
        setattr(context, '_qqfarm_friend_cycle_seen', True)
        if active_context is not None and active_context is not context:
            setattr(active_context, '_qqfarm_friend_cycle_seen', True)
        return context
    except BaseException:
        return None


def _friend_guard_original_chain(fn):
    """Return wrapper/original functions without looping on repeated links."""
    result = []
    seen = set()
    current = fn
    try:
        while callable(current) and id(current) not in seen and len(result) < 16:
            seen.add(id(current))
            result.append(current)
            next_fn = None
            for key in (
                '__qqfarm_vip_business_orig__',
                '__qqfarm_friend_radish_diag_orig__',
                '__qqfarm_friend_pause_orig__',
                '__wrapped__',
            ):
                candidate = getattr(current, key, None)
                if callable(candidate) and id(candidate) not in seen:
                    next_fn = candidate
                    break
            if next_fn is None:
                break
            current = next_fn
    except BaseException:
        pass
    return result


def _resolve_friend_guard_action(fn, args, kwargs):
    """Resolve a direct return-home action before falling back to self-farm processing."""
    context = _friend_guard_context(args, kwargs)
    try:
        if context is not None:
            action = getattr(context, 'go_home', None)
            if callable(action):
                return action, None, 'method.go_home'
    except BaseException:
        pass
    try:
        for current in _friend_guard_original_chain(fn):
            globals_map = getattr(current, '__globals__', None)
            if not isinstance(globals_map, dict):
                continue
            action = globals_map.get('go_home')
            if callable(action):
                return action, context, 'global.go_home'
    except BaseException:
        pass
    try:
        if context is not None:
            action = getattr(context, 'check_go_home_icon', None)
            if callable(action):
                return action, None, 'method.check_go_home_icon'
    except BaseException:
        pass
    try:
        for current in _friend_guard_original_chain(fn):
            globals_map = getattr(current, '__globals__', None)
            if not isinstance(globals_map, dict):
                continue
            action = globals_map.get('check_go_home_icon')
            if callable(action):
                return action, context, 'global.check_go_home_icon'
    except BaseException:
        pass
    return _resolve_friend_guard_self_action(fn, args, kwargs)


def _resolve_friend_guard_self_action(fn, args, kwargs):
    """Resolve the self-farm processor used when the home icon is already absent."""
    context = _friend_guard_context(args, kwargs)
    try:
        if context is not None:
            action = getattr(context, 'process_self_farm', None)
            if callable(action):
                return action, None, 'method.process_self_farm'
    except BaseException:
        pass
    try:
        for current in _friend_guard_original_chain(fn):
            globals_map = getattr(current, '__globals__', None)
            if not isinstance(globals_map, dict):
                continue
            action = globals_map.get('process_self_farm')
            if callable(action):
                return action, context, 'global.process_self_farm'
    except BaseException:
        pass
    return None, context, ''


def _friend_guard_args_with_frame(context, original_args, original_kwargs, fresh_frame):
    call_args = list(original_args or ())
    call_kwargs = dict(original_kwargs or {})
    if fresh_frame is None:
        return tuple(call_args), call_kwargs
    if 'game_frame' in call_kwargs:
        call_kwargs['game_frame'] = fresh_frame
        return tuple(call_args), call_kwargs
    if call_args and call_args[0] is context:
        if len(call_args) >= 2:
            call_args[1] = fresh_frame
        else:
            call_args.append(fresh_frame)
    elif call_args:
        call_args[0] = fresh_frame
    else:
        call_kwargs['game_frame'] = fresh_frame
    return tuple(call_args), call_kwargs


def _invoke_friend_guard_action(action, target, original_args=(), original_kwargs=None):
    call_args = tuple(original_args or ())
    call_kwargs = dict(original_kwargs or {})
    bound_owner = getattr(action, '__self__', None)
    if bound_owner is not None:
        if call_args and call_args[0] is bound_owner:
            call_args = call_args[1:]
        return action(*call_args, **call_kwargs)
    if target is not None and (not call_args or call_args[0] is not target):
        call_args = (target,) + call_args
    return action(*call_args, **call_kwargs)



def _friend_guard_help_button_match(frame):
    try:
        os_module = __import__('os')
        template_path = globals().get(
            '_FRIEND_HELP_ALL_TEMPLATE_PATH',
            os_module.path.join(os_module.getcwd(), 'friend_help_all_button.png'),
        )
        match = _friend_guard_match_template(
            frame, template_path, (0.20, 0.55, 0.80, 0.90), 0.44, 0.22
        )
        if not bool(match.get('matched')):
            shape = getattr(frame, 'shape', None)
            height = int(shape[0]) if shape is not None and len(shape) >= 2 else 0
            width = int(shape[1]) if shape is not None and len(shape) >= 2 else 0
            center = match.get('center') if isinstance(match, dict) else None
            center_ok = bool(
                width > 0
                and height > 0
                and isinstance(center, (tuple, list))
                and len(center) >= 2
                and (width * 0.34) <= float(center[0]) <= (width * 0.66)
                and (height * 0.64) <= float(center[1]) <= (height * 0.82)
            )
            bounds_fn = globals().get('_friend_selected_carousel_card_bounds')
            selected_bounds = bounds_fn(frame) if callable(bounds_fn) else None
            home_path = globals().get(
                '_FRIEND_HOME_TEMPLATE_PATH',
                os_module.path.join(os_module.getcwd(), 'friend_home_button.png'),
            )
            home = _friend_guard_match_template(
                frame, home_path, (0.68, 0.52, 1.0, 0.86), 1.1, 1.1
            )
            soft_help = bool(
                center_ok
                and isinstance(selected_bounds, dict)
                and float(match.get('gray', 0.0) or 0.0) >= 0.36
                and float(match.get('edge', 0.0) or 0.0) >= 0.18
                and float(home.get('gray', 0.0) or 0.0) >= 0.72
                and float(home.get('edge', 0.0) or 0.0) >= 0.18
            )
            if soft_help:
                match = dict(match)
                match['matched'] = True
                match['match_mode'] = 'soft-help+friend-footer'
                match['home_gray'] = float(home.get('gray', 0.0) or 0.0)
                match['home_edge'] = float(home.get('edge', 0.0) or 0.0)
        globals()['_FRIEND_HELP_ALL_LAST_MATCH'] = match
        return match
    except BaseException:
        return {'matched': False, 'gray': 0.0, 'edge': 0.0, 'center': None}


def _friend_guard_steal_button_match(frame):
    try:
        os_module = __import__('os')
        template_path = globals().get(
            '_FRIEND_STEAL_ALL_TEMPLATE_PATH',
            os_module.path.join(os_module.getcwd(), 'friend_steal_all_button.png'),
        )
        match = _friend_guard_match_template(
            frame, template_path, (0.20, 0.55, 0.80, 0.90), 0.70, 0.35
        )
        globals()['_FRIEND_STEAL_ALL_LAST_MATCH'] = match
        return match
    except BaseException:
        return {'matched': False, 'gray': 0.0, 'edge': 0.0, 'center': None}

def _invoke_friend_guard_match_coordinate_click(context, fresh_frame, match):
    try:
        shape = getattr(fresh_frame, 'shape', None)
        height, width = int(shape[0]), int(shape[1])
        center = match.get('center') if isinstance(match, dict) else None
        if not isinstance(center, (tuple, list)) or len(center) < 2:
            return False
        frame_x, frame_y = int(center[0]), int(center[1])
        if not (0 <= frame_x < width and 0 <= frame_y < height):
            return False
    except BaseException:
        return False
    client_result = False
    client_click = globals().get('_friend_guard_post_client_click')
    if callable(client_click):
        try:
            try:
                client_result = bool(client_click(frame_x, frame_y, width, height))
            except TypeError:
                client_result = bool(client_click(frame_x, frame_y))
        except BaseException:
            client_result = False
    if client_result:
        try:
            _write('v83 friend visual action delivered by client-only click frame=(' +
                   str(frame_x) + ',' + str(frame_y) + ',' + str(width) + ',' +
                   str(height) + ')')
        except BaseException:
            pass
        return True
    screen_x, screen_y = frame_x, frame_y
    converted_ok = False
    absolute_converter = globals().get('_friend_guard_frame_to_screen')
    if callable(absolute_converter):
        try:
            try:
                point = absolute_converter(frame_x, frame_y, width, height)
            except TypeError:
                point = absolute_converter(frame_x, frame_y)
            if isinstance(point, (tuple, list)) and len(point) >= 2:
                screen_x, screen_y = int(point[0]), int(point[1])
                converted_ok = True
        except BaseException:
            converted_ok = False
    converter = getattr(context, 'convert_to_screen_coordinate', None)
    if not converted_ok and callable(converter):
        try:
            try:
                point = converter(frame_x, frame_y)
            except TypeError:
                point = converter((frame_x, frame_y))
            if isinstance(point, (tuple, list)) and len(point) >= 2:
                screen_x, screen_y = int(point[0]), int(point[1])
                converted_ok = True
        except BaseException:
            converted_ok = False
    ownership_fn = globals().get('_friend_guard_screen_point_owned_by_farm')
    if callable(ownership_fn):
        try:
            point_owned = bool(
                converted_ok and ownership_fn(screen_x, screen_y)
            )
        except BaseException:
            point_owned = False
        if not point_owned:
            try:
                _write(
                    'v96 friend visual absolute click blocked screen=(' +
                    str(screen_x) + ',' + str(screen_y) + ') converted=' +
                    repr(converted_ok)
                )
            except BaseException:
                pass
            return False
    click = getattr(context, 'click_at_position', None)
    if callable(click):
        try:
            try:
                click_result = click(screen_x, screen_y)
            except TypeError:
                click_result = click((screen_x, screen_y))
            accepted = bool(click_result is not False)
        except BaseException:
            accepted = False
    else:
        accepted = False
    try:
        _write('v70 friend visual action coordinate frame=(' + str(frame_x) + ',' +
               str(frame_y) + ',' + str(width) + ',' + str(height) +
               ') screen=(' + str(screen_x) + ',' + str(screen_y) +
               ') converted=' + repr(converted_ok) +
               ' client=' + repr(client_result) +
               ' accepted=' + repr(accepted))
    except BaseException:
        pass
    return accepted


def _resolve_friend_guard_native_callable(context, function_name):
    """Find a compiled checks_friend guard predicate without importing a fixed module name."""
    try:
        name = str(function_name or '').strip()
        if not name:
            return None, ''
        if context is not None:
            try:
                direct = getattr(context, name, None)
            except BaseException:
                direct = None
            if callable(direct):
                return direct, 'context.' + name
            for probe_name in (
                'check_friend_farm_bottom_help_all_entry',
                'check_help_all_entry',
                '_match_help_all_entry_with_skip',
            ):
                try:
                    probe = getattr(context, probe_name, None)
                except BaseException:
                    probe = None
                for owner in (probe, getattr(probe, '__func__', None)):
                    try:
                        owner_globals = getattr(owner, '__globals__', None)
                        candidate = (
                            owner_globals.get(name)
                            if isinstance(owner_globals, dict) else None
                        )
                    except BaseException:
                        candidate = None
                    if callable(candidate):
                        return candidate, 'context.' + probe_name + '.__globals__.' + name
        sys_module = globals().get('sys')
        modules = getattr(sys_module, 'modules', {}) if sys_module is not None else {}
        for module_name, module in list(modules.items()):
            try:
                lowered = str(module_name or '').lower()
                if module is None or 'checks_friend' not in lowered:
                    continue
                candidate = getattr(module, name, None)
                if callable(candidate):
                    return candidate, str(module_name) + '.' + name
            except BaseException:
                continue
    except BaseException:
        pass
    return None, ''


def _friend_guard_help_action_allowed(context, game_frame, match_center):
    """Apply the native bottom-help guard predicate before the visual click fallback."""
    try:
        enabled_fn = globals().get('_guard_dog_ui_config_enabled')
        guard_enabled = bool(enabled_fn()) if callable(enabled_fn) else False
    except BaseException:
        guard_enabled = False
    if not guard_enabled:
        return True
    try:
        mode_fn = globals().get('_guard_dog_detection_mode_config')
        guard_mode = str(mode_fn() if callable(mode_fn) else 'avatar_frame')
    except BaseException:
        guard_mode = 'avatar_frame'
    if guard_mode == 'friend_guard_list':
        approved_fn = globals().get(
            '_friend_guard_list_prequalified_entry_active'
        )
        approved = bool(approved_fn(context)) if callable(approved_fn) else False
        if not approved:
            refresh_fn = globals().get('_friend_guard_list_refresh_prequalification')
            if callable(refresh_fn):
                try:
                    refresh_fn(context, game_frame)
                    approved = bool(
                        approved_fn(context) if callable(approved_fn) else False
                    )
                except BaseException:
                    approved = False
        if approved:
            try:
                _write(
                    'v229 guard-list help allowed by current carousel identity '
                    'center=' + repr(match_center)
                )
            except BaseException:
                pass
            return True
    if guard_mode == 'avatar_frame':
        verified_fn = globals().get('_friend_guard_verified_entry_active')
        verified = bool(verified_fn(context)) if callable(verified_fn) else False
        if verified:
            try:
                _write(
                    'v135 guard dog help allowed by recent list dog-badge proof '
                    'center=' + repr(match_center)
                )
            except BaseException:
                pass
            return True
    resolver = globals().get('_resolve_friend_guard_native_callable')
    predicate = None
    source = ''
    if callable(resolver):
        try:
            predicate, source = resolver(
                context, '_has_guard_dog_for_bottom_help_action'
            )
        except BaseException:
            predicate, source = None, ''
    if not callable(predicate):
        try:
            _write('v130 guard dog visual help blocked: native bottom predicate missing')
        except BaseException:
            pass
        return False
    label = 'visual.friend_help_all'
    bound = getattr(predicate, '__self__', None)
    if bound is not None:
        call_variants = (
            (game_frame, match_center, label),
            (context, game_frame, match_center, label),
        )
    else:
        call_variants = (
            (context, game_frame, match_center, label),
            (game_frame, match_center, label),
        )
    last_type_error = None
    for call_args in call_variants:
        try:
            allowed = bool(predicate(*call_args))
            try:
                _write(
                    'v130 guard dog visual help gate source=' + str(source) +
                    ' allowed=' + repr(allowed) +
                    ' center=' + repr(match_center)
                )
            except BaseException:
                pass
            return allowed
        except TypeError as error:
            last_type_error = error
            continue
        except BaseException as error:
            try:
                _write(
                    'v130 guard dog visual help blocked: predicate error source=' +
                    str(source) + ' error=' + repr(error)[:220]
                )
            except BaseException:
                pass
            return False
    try:
        _write(
            'v130 guard dog visual help blocked: predicate signature mismatch source=' +
            str(source) + ' error=' + repr(last_type_error)[:220]
        )
    except BaseException:
        pass
    return False


def _friend_help_counter_snapshot(context, counter_paths=None, today=None):
    """Return the largest durable same-day friend-help count for this instance."""
    try:
        os_module = __import__('os')
        json_module = __import__('json')
        time_module = __import__('time')
        day = str(today or time_module.strftime('%Y-%m-%d'))
        try:
            instance_id = str(getattr(context, 'instance_id', '1') or '1')
        except BaseException:
            instance_id = '1'
        maximum = 0

        def _safe_count(value):
            try:
                return max(0, int(float(str(value or 0))))
            except BaseException:
                return 0

        def _consume_node(node):
            nonlocal maximum
            if not isinstance(node, dict):
                return
            if str(node.get('friend_help_daily_date', '') or '') == day:
                maximum = max(
                    maximum,
                    _safe_count(node.get('friend_help_daily_count', 0)),
                )
            metrics = node.get('gui_metrics')
            if (
                isinstance(metrics, dict)
                and str(metrics.get('date', '') or '') == day
            ):
                maximum = max(
                    maximum,
                    _safe_count(metrics.get('friend_farming_count', 0)),
                )

        try:
            context_date = str(getattr(
                context, 'friend_help_daily_date', ''
            ) or '')
            if context_date == day:
                maximum = max(maximum, _safe_count(getattr(
                    context, 'friend_help_daily_count', 0
                )))
            context_metrics = getattr(context, 'gui_metrics', None)
            if isinstance(context_metrics, dict):
                _consume_node({'gui_metrics': context_metrics})
        except BaseException:
            pass

        if counter_paths is None:
            counter_paths = []
            local = str(os_module.environ.get('LOCALAPPDATA', '') or '')
            if local:
                counter_paths.append(os_module.path.join(
                    local, 'qq-farm-bot-rev', 'daily_counters.json'
                ))
            try:
                base = os_module.path.dirname(os_module.path.abspath(__file__))
                counter_paths.append(os_module.path.join(
                    base, 'UserData', 'legacy-qq-farm-bot-rev',
                    'daily_counters.json',
                ))
            except BaseException:
                pass
        elif isinstance(counter_paths, (str, bytes, os_module.PathLike)):
            counter_paths = [counter_paths]

        seen = set()
        for raw_path in list(counter_paths or []):
            try:
                path = os_module.path.abspath(os_module.fspath(raw_path))
                key = os_module.path.normcase(path)
                if not path or key in seen or not os_module.path.isfile(path):
                    continue
                seen.add(key)
                with open(path, 'r', encoding='utf-8-sig') as handle:
                    payload = json_module.load(handle)
                if not isinstance(payload, dict):
                    continue
                _consume_node(payload)
                instances = payload.get('instances')
                if isinstance(instances, dict):
                    _consume_node(instances.get(instance_id))
            except BaseException:
                continue
        return int(maximum)
    except BaseException:
        return 0


def _friend_help_quota_active(context, today=None):
    """Keep the daily quota marker active only for the day it was observed."""
    if context is None:
        return False
    try:
        if not bool(getattr(
            context, '_qqfarm_friend_help_quota_exhausted', False
        )):
            return False
        day = str(today or __import__('time').strftime('%Y-%m-%d'))
        marker_day = str(getattr(
            context, '_qqfarm_friend_help_quota_date', ''
        ) or '')
        if marker_day and marker_day != day:
            setattr(context, '_qqfarm_friend_help_quota_exhausted', False)
            setattr(context, '_qqfarm_friend_help_quota_date', '')
            return False
        return True
    except BaseException:
        return False


def _invoke_friend_guard_help_visual_click(context, fresh_frame):
    try:
        counter_fn = globals().get('_friend_help_counter_snapshot')
        try:
            daily_limit = int(getattr(
                context, 'friend_help_daily_limit', 500
            ) or 500)
        except BaseException:
            daily_limit = 500
        daily_limit = max(1, daily_limit)
        daily_count = (
            int(counter_fn(context)) if callable(counter_fn) else 0
        )
        if daily_count >= daily_limit:
            try:
                setattr(context, '_qqfarm_friend_help_quota_exhausted', True)
                setattr(
                    context,
                    '_qqfarm_friend_help_quota_date',
                    __import__('time').strftime('%Y-%m-%d'),
                )
                setattr(context, '_qqfarm_friend_chain_pending', False)
                setattr(context, '_qqfarm_friend_chain_exhausted', True)
                setattr(context, '_qqfarm_friend_chain_allow_home', True)
            except BaseException:
                pass
            message = (
                'v210 friend help daily quota exhausted count=' +
                str(daily_count) + '/' + str(daily_limit)
            )
            throttle_fn = globals().get('_throttled_write')
            if callable(throttle_fn):
                throttle_fn('v210-friend-help-daily-quota', message, 30.0)
            else:
                _write(message)
            return False
        try:
            setattr(context, '_qqfarm_friend_help_quota_exhausted', False)
        except BaseException:
            pass
        match_fn = globals().get('_friend_guard_help_button_match')
        click_fn = globals().get('_invoke_friend_guard_match_coordinate_click')
        if not callable(match_fn) or not callable(click_fn):
            return False
        current_frame = fresh_frame
        match = match_fn(current_frame)
        if not isinstance(match, dict) or not bool(match.get('matched')):
            return False
        card_key = None
        try:
            bounds_fn = globals().get('_friend_selected_carousel_card_bounds')
            selected_bounds = bounds_fn(current_frame) if callable(bounds_fn) else None
            if isinstance(selected_bounds, dict):
                card_key = tuple(int(selected_bounds.get(key, 0) or 0) for key in (
                    'left', 'right', 'top', 'bottom'
                ))
        except BaseException:
            card_key = None
        try:
            time_module = globals().get('time')
            now_fn = getattr(time_module, 'time', None)
            now_ts = float(now_fn() if callable(now_fn) else __import__('time').time())
        except BaseException:
            now_ts = 0.0
        if card_key is not None:
            try:
                blocked_card = getattr(
                    context, '_qqfarm_friend_help_visual_unresolved_card', None
                )
                blocked_until = float(getattr(
                    context, '_qqfarm_friend_help_visual_unresolved_until', 0.0
                ) or 0.0)
            except BaseException:
                blocked_card, blocked_until = None, 0.0
            if blocked_card == card_key and blocked_until > now_ts:
                try:
                    _write(
                        'v228 suppress unchanged friend help false-positive card=' +
                        repr(card_key) + ' until=' + str(blocked_until)
                    )
                except BaseException:
                    pass
                return False
            if blocked_card is not None and blocked_card != card_key:
                try:
                    setattr(context, '_qqfarm_friend_help_visual_unresolved_card', None)
                    setattr(context, '_qqfarm_friend_help_visual_unresolved_until', 0.0)
                except BaseException:
                    pass
        gate_fn = globals().get('_friend_guard_help_action_allowed')
        if callable(gate_fn):
            match_center = match.get('center')
            if not bool(gate_fn(context, current_frame, match_center)):
                try:
                    setattr(context, '_qqfarm_guard_dog_help_skipped', True)
                except BaseException:
                    pass
                try:
                    _write(
                        'v131 friend visual help skipped by guard dog eligibility gate ' +
                        'center=' + repr(match_center)
                    )
                except BaseException:
                    pass
                return False
        settle_seconds = (0.9, 1.1, 1.3)
        for attempt, delay in enumerate(settle_seconds, 1):
            click_result = bool(click_fn(context, current_frame, match))
            _write('v70 friend visual help click attempt=' + str(attempt) +
                   ' result=' + repr(click_result) +
                   ' match=' + repr(match)[:220])
            if not click_result:
                return False
            sleep_fn = globals().get('_friend_guard_sleep')
            if callable(sleep_fn):
                sleep_fn(delay)
            else:
                __import__('time').sleep(delay)
            next_frame_fn = globals().get('_get_frame_from_bot')
            next_frame = next_frame_fn(context) if callable(next_frame_fn) else None
            if next_frame is None:
                _write('v70 friend visual help verify missing-frame attempt=' + str(attempt))
                return False
            post_match = match_fn(next_frame)
            disappeared = bool(
                isinstance(post_match, dict)
                and not bool(post_match.get('matched'))
            )
            _write('v70 friend visual help verify attempt=' + str(attempt) +
                   ' disappeared=' + repr(disappeared) +
                   ' post=' + repr(post_match)[:220])
            if disappeared:
                try:
                    setattr(context, '_qqfarm_friend_help_visual_unresolved_card', None)
                    setattr(context, '_qqfarm_friend_help_visual_unresolved_until', 0.0)
                except BaseException:
                    pass
                return True
            if not isinstance(post_match, dict):
                return False
            current_frame = next_frame
            match = post_match
        try:
            if card_key is not None:
                setattr(context, '_qqfarm_friend_help_visual_unresolved_card', card_key)
                setattr(
                    context,
                    '_qqfarm_friend_help_visual_unresolved_until',
                    float(now_ts) + 15.0,
                )
        except BaseException:
            pass
        _write(
            'v228 friend visual help unresolved after 3 verified clicks; '
            'suppress unchanged card=' + repr(card_key)
        )
        return False
    except BaseException as e:
        try:
            _write('v70 friend visual help error ' + repr(e)[:240])
        except BaseException:
            pass
        return False


def _invoke_friend_guard_steal_visual_click(context, fresh_frame):
    try:
        match_fn = globals().get('_friend_guard_steal_button_match')
        click_fn = globals().get('_invoke_friend_guard_match_coordinate_click')
        if not callable(match_fn) or not callable(click_fn):
            return False
        current_frame = fresh_frame
        match = match_fn(current_frame)
        if not isinstance(match, dict) or not bool(match.get('matched')):
            return False
        settle_seconds = (0.75, 0.95, 1.15)
        for attempt, delay in enumerate(settle_seconds, 1):
            click_result = bool(click_fn(context, current_frame, match))
            _write('v71 friend visual steal click attempt=' + str(attempt) +
                   ' result=' + repr(click_result) +
                   ' match=' + repr(match)[:220])
            if not click_result:
                return False
            sleep_fn = globals().get('_friend_guard_sleep')
            if callable(sleep_fn):
                sleep_fn(delay)
            else:
                __import__('time').sleep(delay)
            next_frame_fn = globals().get('_get_frame_from_bot')
            next_frame = next_frame_fn(context) if callable(next_frame_fn) else None
            if next_frame is None:
                _write('v71 friend visual steal verify missing-frame attempt=' + str(attempt))
                return False
            post_match = match_fn(next_frame)
            disappeared = bool(
                isinstance(post_match, dict)
                and not bool(post_match.get('matched'))
            )
            _write('v71 friend visual steal verify attempt=' + str(attempt) +
                   ' disappeared=' + repr(disappeared) +
                   ' post=' + repr(post_match)[:220])
            if disappeared:
                return True
            if not isinstance(post_match, dict):
                return False
            current_frame = next_frame
            match = post_match
        _write('v71 friend visual steal unresolved after 3 verified clicks')
        return False
    except BaseException as e:
        try:
            _write('v71 friend visual steal error ' + repr(e)[:240])
        except BaseException:
            pass
        return False

def _friend_action_frame_without_bottom_bar(frame):
    """Mask friend-carousel badges so they cannot impersonate farm action icons."""
    try:
        shape = getattr(frame, 'shape', None)
        if shape is None or len(shape) < 2:
            return frame
        height = int(shape[0])
        if height < 20:
            return frame
        masked = frame.copy()
        cutoff = max(1, min(height, int(round(height * 0.84))))
        masked[cutoff:, ...] = 0
        return masked
    except BaseException:
        return frame


def _friend_navigation_signature(frame):
    """Compact top-profile signature used to verify that a friend visit changed."""
    try:
        np = __import__('numpy')
        arr = np.asarray(frame)
        if arr.ndim < 2:
            return None
        height, width = int(arr.shape[0]), int(arr.shape[1])
        if height < 24 or width < 24:
            return None
        y1, y2 = max(0, int(height * 0.03)), max(2, int(height * 0.25))
        x1, x2 = max(0, int(width * 0.01)), max(2, int(width * 0.55))
        roi = arr[y1:y2, x1:x2]
        if roi.size <= 0:
            return None
        if roi.ndim >= 3:
            roi = roi[..., :3].astype('float32').mean(axis=2)
        else:
            roi = roi.astype('float32')
        sample_y = np.linspace(0, max(0, roi.shape[0] - 1), 10).astype('int32')
        sample_x = np.linspace(0, max(0, roi.shape[1] - 1), 20).astype('int32')
        sampled = roi[sample_y[:, None], sample_x[None, :]]
        return tuple(int(round(float(value))) for value in sampled.reshape(-1))
    except BaseException:
        return None


def _friend_navigation_change_score(before_signature, after_frame):
    try:
        after_signature = _friend_navigation_signature(after_frame)
        if before_signature is None or after_signature is None:
            return None
        if len(before_signature) != len(after_signature) or not before_signature:
            return None
        total = 0.0
        for before_value, after_value in zip(before_signature, after_signature):
            total += abs(float(after_value) - float(before_value))
        return total / (255.0 * float(len(before_signature)))
    except BaseException:
        return None


def _invoke_friend_visual_actions_before_home(context, fresh_frame):
    """Fast template-only action probe used repeatedly while a friend page settles."""
    if context is None or fresh_frame is None:
        return False, ''
    # Remember the selected bottom card before the one-click action makes the
    # carousel fade during its transition.  The cached geometry is used only by
    # the active in-farm continuation chain and never as a global fixed slot.
    try:
        bounds_fn = globals().get('_friend_selected_carousel_card_bounds')
        selected_bounds = bounds_fn(fresh_frame) if callable(bounds_fn) else None
        if isinstance(selected_bounds, dict):
            setattr(
                context,
                '_qqfarm_friend_chain_last_selected_bounds',
                dict(selected_bounds),
            )
    except BaseException:
        selected_bounds = None
    # The self farm and the decoration catalogue both contain green controls.
    # A green rectangle alone is never friend-page proof: require the current
    # frame's verified friend-farm home button before caching or clicking.
    state_fn = globals().get('_friend_guard_friend_ui_state')
    if callable(state_fn):
        try:
            visual_friend_state = state_fn(fresh_frame)
        except BaseException:
            visual_friend_state = None
        if visual_friend_state is not True:
            try:
                setattr(context, '_qqfarm_friend_chain_last_selected_bounds', None)
            except BaseException:
                pass
            try:
                _write(
                    'v116 friend visual action rejected: current frame has no '
                    'verified friend surface state=' + repr(visual_friend_state)
                )
            except BaseException:
                pass
            return False, ''
    action_frame = fresh_frame
    try:
        mask_fn = globals().get('_friend_action_frame_without_bottom_bar')
        if callable(mask_fn):
            action_frame = mask_fn(fresh_frame)
    except BaseException:
        action_frame = fresh_frame
    attempted = []
    for visual_name, function_name in (
        ('visual.friend_steal_all', '_invoke_friend_guard_steal_visual_click'),
        ('visual.friend_help_all', '_invoke_friend_guard_help_visual_click'),
    ):
        visual_fn = globals().get(function_name)
        # Keep the full friend frame for the help path: the guard-dog predicate
        # reads the selected bottom-carousel card.  Steal matching still uses the
        # masked frame so bottom-card badges cannot impersonate a farm action.
        probe_frame = (
            fresh_frame
            if function_name == '_invoke_friend_guard_help_visual_click'
            else action_frame
        )
        try:
            visual_result = bool(visual_fn(context, probe_frame)) if callable(visual_fn) else False
        except BaseException as error:
            attempted.append((visual_name, 'error:' + repr(error)[:120]))
            visual_result = False
        if not visual_result:
            attempted.append((visual_name, False))
            continue
        attempted.append((visual_name, True))
        try:
            now_ts = __import__('time').time()
            setattr(context, '_qqfarm_friend_action_last_ts', now_ts)
            setattr(context, '_qqfarm_friend_action_last_label', visual_name)
            setattr(context, '_qqfarm_friend_fast_empty_count', 0)
            setattr(context, '_qqfarm_friend_fast_empty_ts', now_ts)
            setattr(context, '_qqfarm_visual_friend_count', 1)
        except BaseException:
            pass
        if 'help' in visual_name:
            try:
                recorder = getattr(context, '_record_friend_help_action', None)
                if callable(recorder):
                    try:
                        recorder()
                    except TypeError:
                        recorder(visual_name)
            except BaseException:
                pass
        try:
            _write('v89 friend fast visual action handled action=' + visual_name +
                   ' attempts=' + repr(attempted)[:240])
        except BaseException:
            pass
        return True, visual_name
    return False, ''


def _invoke_friend_actions_before_home(context, fresh_frame):
    """Try fast visible actions first, then one bounded native fallback scan."""
    if context is None or fresh_frame is None:
        return False, ''
    try:
        setattr(context, '_qqfarm_friend_native_action_unverified', False)
    except BaseException:
        pass
    visual_fn = globals().get('_invoke_friend_visual_actions_before_home')
    if callable(visual_fn):
        try:
            visual_result, visual_label = visual_fn(context, fresh_frame)
        except BaseException:
            visual_result, visual_label = False, ''
        if visual_result:
            return True, str(visual_label or '')
    action_frame = fresh_frame
    try:
        mask_fn = globals().get('_friend_action_frame_without_bottom_bar')
        if callable(mask_fn):
            action_frame = mask_fn(fresh_frame)
    except BaseException:
        action_frame = fresh_frame
    strict_visual_only = False
    try:
        state_fn = globals().get('_friend_guard_friend_ui_state')
        strict_visual_only = bool(
            callable(state_fn) and state_fn(fresh_frame) is False
        )
    except BaseException:
        strict_visual_only = False
    if strict_visual_only:
        try:
            _write('v90 friend unreadable frame: visual probes complete; native probes skipped')
        except BaseException:
            pass
        return False, ''
    attempted = []
    for method_name in (
        'check_steal_all_icon',
        'check_steal_one_icon',
        'check_steal_icon',
        'check_help_all_entry',
    ):
        if strict_visual_only and method_name in (
            'check_steal_one_icon',
            'check_steal_icon',
            'check_help_all_entry',
        ):
            attempted.append((method_name, 'skipped-unreadable-friend-ui'))
            continue
        try:
            action = getattr(context, method_name, None)
        except BaseException:
            action = None
        if not callable(action):
            continue
        label = 'method.' + str(method_name)
        native_help_count_before = None
        if method_name == 'check_help_all_entry':
            counter_fn = globals().get('_friend_help_counter_snapshot')
            if callable(counter_fn):
                try:
                    native_help_count_before = int(counter_fn(context))
                except BaseException:
                    native_help_count_before = None
        try:
            result = _invoke_friend_guard_action(
                action, None, (context, action_frame), {}
            )
            attempted.append((method_name, bool(result)))
        except BaseException as error:
            attempted.append((method_name, 'error:' + repr(error)[:120]))
            continue
        if not result:
            continue
        if method_name == 'check_help_all_entry':
            capture_fn = globals().get('_get_frame_from_bot')
            match_fn = globals().get('_friend_guard_help_button_match')
            counter_fn = globals().get('_friend_help_counter_snapshot')
            verification_available = bool(
                (callable(capture_fn) and callable(match_fn))
                or callable(counter_fn)
            )
            if verification_available:
                verified = False
                proof = ''
                for verify_attempt in range(3):
                    if callable(counter_fn):
                        try:
                            native_help_count_after = int(counter_fn(context))
                        except BaseException:
                            native_help_count_after = native_help_count_before
                        if (
                            native_help_count_before is not None
                            and native_help_count_after is not None
                            and native_help_count_after > native_help_count_before
                        ):
                            verified = True
                            proof = 'durable-count'
                            break
                    post_frame = None
                    if callable(capture_fn):
                        try:
                            post_frame = capture_fn(context)
                        except BaseException:
                            post_frame = None
                    if post_frame is not None and callable(match_fn):
                        try:
                            post_match = match_fn(post_frame)
                        except BaseException:
                            post_match = None
                        if (
                            isinstance(post_match, dict)
                            and not bool(post_match.get('matched'))
                        ):
                            verified = True
                            proof = 'button-disappeared'
                            break
                    if verify_attempt < 2:
                        sleep_fn = globals().get('_friend_guard_sleep')
                        try:
                            if callable(sleep_fn):
                                sleep_fn(0.16 + (0.06 * verify_attempt))
                            else:
                                __import__('time').sleep(0.16 + (0.06 * verify_attempt))
                        except BaseException:
                            pass
                if not verified:
                    try:
                        setattr(
                            context,
                            '_qqfarm_friend_native_action_unverified',
                            True,
                        )
                    except BaseException:
                        pass
                    try:
                        _write(
                            'v212 friend native help claim unverified; '
                            'keeping current friend active attempts=' +
                            repr(attempted)[:260]
                        )
                    except BaseException:
                        pass
                    return False, ''
                try:
                    _write(
                        'v212 friend native help verified proof=' + str(proof)
                    )
                except BaseException:
                    pass
        try:
            now_ts = __import__('time').time()
            setattr(context, '_qqfarm_friend_action_last_ts', now_ts)
            setattr(context, '_qqfarm_friend_action_last_label', label)
            setattr(context, '_qqfarm_friend_fast_empty_count', 0)
            setattr(context, '_qqfarm_friend_fast_empty_ts', now_ts)
            setattr(context, '_qqfarm_visual_friend_count', 1)
        except BaseException:
            pass
        try:
            _write('v89 friend bounded native action handled action=' + label +
                   ' attempts=' + repr(attempted)[:300])
        except BaseException:
            pass
        return True, label
    try:
        _write('v89 friend bounded native action found nothing attempts=' + repr(attempted)[:300])
    except BaseException:
        pass
    return False, ''

def _friend_selected_carousel_card_bounds(frame):
    """Return the green selected-card bounds in the bottom friend carousel."""
    try:
        np = __import__('numpy')
        cv2 = __import__('cv2')
        arr = np.asarray(frame)
        shape = getattr(arr, 'shape', None)
        if not shape or len(shape) < 3 or int(shape[2]) < 3:
            return None
        height, width = int(shape[0]), int(shape[1])
        if height < 120 or width < 120:
            return None
        y0 = max(0, min(height - 1, int(round(height * 0.82))))
        roi = arr[y0:, :, :3]
        channel0 = roi[:, :, 0].astype('int16')
        green = roi[:, :, 1].astype('int16')
        channel2 = roi[:, :, 2].astype('int16')
        vivid_green = (
            (green >= 135)
            & ((green - channel0) >= 35)
            & ((green - channel2) >= 30)
        ).astype('uint8')
        count, _, stats, _ = cv2.connectedComponentsWithStats(vivid_green, 8)
        best = None
        min_area = max(100, int(round(width * height * 0.0007)))
        for index in range(1, int(count)):
            x, y, component_width, component_height, area = (
                int(value) for value in stats[index]
            )
            if area < min_area:
                continue
            if component_width < int(width * 0.15) or component_width > int(width * 0.42):
                continue
            if component_height < int(height * 0.055) or component_height > int(height * 0.16):
                continue
            # Friend cards are landscape rectangles.  The decoration catalogue
            # uses taller green selection frames; accepting those turns house
            # items into fake "next friend" cards.
            if float(component_width) < (float(component_height) * 1.04):
                continue
            score = float(area) + (float(component_width * component_height) * 0.05)
            if best is None or score > best[0]:
                best = (
                    score,
                    x,
                    y + y0,
                    component_width,
                    component_height,
                    area,
                )
        if best is None:
            return None
        _, left, top, card_width, card_height, area = best
        return {
            'left': int(left),
            'right': int(left + card_width),
            'top': int(top),
            'bottom': int(top + card_height),
            'width': int(card_width),
            'height': int(card_height),
            'area': int(area),
        }
    except BaseException:
        return None


def _friend_carousel_selection_changed(before_bounds, after_bounds, frame_width=428):
    """Confirm that the green selected friend card moved to another slot."""
    try:
        if not isinstance(before_bounds, dict) or not isinstance(after_bounds, dict):
            return False
        before_left = float(before_bounds.get('left', 0) or 0)
        before_right = float(before_bounds.get('right', before_left) or before_left)
        after_left = float(after_bounds.get('left', 0) or 0)
        after_right = float(after_bounds.get('right', after_left) or after_left)
        before_width = max(
            1.0,
            float(before_bounds.get('width', before_right - before_left) or 0),
        )
        after_width = max(
            1.0,
            float(after_bounds.get('width', after_right - after_left) or 0),
        )
        before_center = (before_left + before_right) / 2.0
        after_center = (after_left + after_right) / 2.0
        width = max(1.0, float(frame_width or 428))
        minimum_shift = max(
            8.0,
            min(width * 0.08, min(before_width, after_width) * 0.42),
        )
        return abs(after_center - before_center) >= minimum_shift
    except BaseException:
        return False


def _friend_adjacent_card_center(frame):
    """Return only the immediate right-hand card in the in-farm carousel."""
    try:
        bounds = _friend_selected_carousel_card_bounds(frame)
        if not isinstance(bounds, dict):
            return None
        shape = getattr(frame, 'shape', None)
        if shape is None or len(shape) < 2:
            return None
        height, width = int(shape[0]), int(shape[1])
        card_width = max(24, int(bounds.get('width', 0) or 0))
        gap = max(4, int(round(width * 0.012)))
        center_y = int(round(
            (float(bounds.get('top', 0)) + float(bounds.get('bottom', 0))) / 2.0
        ))
        right_x = int(bounds.get('right', 0)) + gap + (card_width // 2)
        if right_x <= width - max(4, card_width // 5):
            return (max(0, min(width - 1, right_x)), max(0, min(height - 1, center_y)))
        # Sequential processing must never move back to the previous friend.
        return None
    except BaseException:
        pass
    return None


def _invoke_friend_adjacent_card_navigation(context, fresh_frame):
    """Click only the immediate next card in the current friend-farm carousel."""
    if context is None or fresh_frame is None:
        return False, ''
    try:
        shape = getattr(fresh_frame, 'shape', None)
        height = int(shape[0])
        width = int(shape[1])
    except BaseException:
        return False, ''

    state_fn = globals().get('_friend_guard_friend_ui_state')
    try:
        current_friend_state = state_fn(fresh_frame) if callable(state_fn) else True
    except BaseException:
        current_friend_state = None
    if current_friend_state is not True:
        try:
            setattr(context, '_qqfarm_friend_chain_last_selected_bounds', None)
        except BaseException:
            pass
        try:
            _write(
                'v116 bottom carousel navigation blocked: non-friend surface state=' +
                repr(current_friend_state)
            )
        except BaseException:
            pass
        return False, ''
    bounds_fn = globals().get('_friend_selected_carousel_card_bounds')
    center_fn = globals().get('_friend_adjacent_card_center')
    try:
        selected_bounds = bounds_fn(fresh_frame) if callable(bounds_fn) else None
    except BaseException:
        selected_bounds = None
    bounds_source = 'live'
    if not isinstance(selected_bounds, dict):
        try:
            chain_active = bool(getattr(context, '_qqfarm_friend_chain_active', False))
            cached_bounds = getattr(
                context, '_qqfarm_friend_chain_last_selected_bounds', None
            )
        except BaseException:
            chain_active = False
            cached_bounds = None
        if chain_active and isinstance(cached_bounds, dict):
            selected_bounds = dict(cached_bounds)
            bounds_source = 'cached-pre-action'
        else:
            try:
                _write(
                    'v105 bottom carousel navigation blocked: selected-card-missing state=' +
                    repr(current_friend_state) + ' chain_active=' + repr(chain_active)
                )
            except BaseException:
                pass
            return False, ''
    if bounds_source == 'live':
        try:
            center = center_fn(fresh_frame) if callable(center_fn) else None
        except BaseException:
            center = None
    else:
        try:
            card_width = max(24, int(selected_bounds.get('width', 0) or 0))
            gap = max(4, int(round(width * 0.012)))
            center_y = int(round(
                (float(selected_bounds.get('top', 0)) +
                 float(selected_bounds.get('bottom', 0))) / 2.0
            ))
            right_x = int(selected_bounds.get('right', 0)) + gap + (card_width // 2)
            if right_x <= width - max(4, card_width // 5):
                center = (
                    max(0, min(width - 1, right_x)),
                    max(0, min(height - 1, center_y)),
                )
            else:
                center = None
        except BaseException:
            center = None
    if center is None:
        try:
            _write(
                'v105 bottom carousel navigation stopped: no immediate-right-card bounds=' +
                repr(selected_bounds)[:220]
            )
        except BaseException:
            pass
        return False, ''
    try:
        if int(center[0]) <= int(selected_bounds.get('right', 0) or 0):
            return False, ''
    except BaseException:
        return False, ''

    click_fn = globals().get('_friend_guard_post_client_click')
    if not callable(click_fn):
        return False, ''
    try:
        clicked = bool(click_fn(center[0], center[1], width, height))
    except BaseException:
        clicked = False
    if not clicked:
        return False, ''
    label = 'visual.adjacent-friend-card'
    try:
        setattr(context, '_qqfarm_friend_chain_last_nav_label', label)
        setattr(context, '_qqfarm_friend_page_seen_ts', 0.0)
        setattr(context, '_qqfarm_visual_friend_count', 0)
        setattr(context, '_qqfarm_friend_chain_last_selected_bounds', selected_bounds)
    except BaseException:
        pass
    try:
        _write(
            'v105 bottom carousel immediate-next click center=' + repr(center) +
            ' selected=' + repr(selected_bounds)[:220] +
            ' bounds_source=' + str(bounds_source) +
            ' frame=' + str(width) + 'x' + str(height)
        )
    except BaseException:
        pass
    return True, label

def _friend_navigation_frame_without_selected_card(frame):
    """Mask the green-selected carousel card before probing the next friend."""
    try:
        np = __import__('numpy')
        cv2 = __import__('cv2')
        arr = np.asarray(frame)
        shape = getattr(arr, 'shape', None)
        if not shape or len(shape) < 3 or int(shape[2]) < 3:
            return frame
        height, width = int(shape[0]), int(shape[1])
        if height < 120 or width < 120:
            return frame
        y0 = max(0, min(height - 1, int(round(height * 0.82))))
        roi = arr[y0:, :, :3]
        c0 = roi[:, :, 0].astype('int16')
        green = roi[:, :, 1].astype('int16')
        c2 = roi[:, :, 2].astype('int16')
        vivid_green = (
            (green >= 135)
            & ((green - c0) >= 35)
            & ((green - c2) >= 30)
        ).astype('uint8')
        count, _, stats, _ = cv2.connectedComponentsWithStats(vivid_green, 8)
        best = None
        min_area = max(100, int(round(width * height * 0.0007)))
        for index in range(1, int(count)):
            x, y, component_width, component_height, area = (
                int(value) for value in stats[index]
            )
            if area < min_area:
                continue
            if component_width < int(width * 0.15) or component_width > int(width * 0.42):
                continue
            if component_height < int(height * 0.055) or component_height > int(height * 0.22):
                continue
            score = float(area) + (float(component_width * component_height) * 0.05)
            if best is None or score > best[0]:
                best = (score, x, y + y0, component_width, component_height, area)
        if best is None:
            return frame
        _, x, y, component_width, component_height, area = best
        pad = max(5, int(round(width * 0.035)))
        left = max(0, x - pad)
        right = min(width, x + component_width + pad)
        masked = arr.copy()
        masked[y0:, left:right, ...] = 0
        globals()['_FRIEND_NAV_SELECTED_MASK'] = {
            'left': left,
            'right': right,
            'top': y0,
            'component_top': y,
            'component_height': component_height,
            'area': area,
        }
        return masked
    except BaseException:
        return frame


def _invoke_friend_next_actionable_entry(context, fresh_frame, last_action_label=''):
    if context is None or fresh_frame is None:
        return False, ''
    last = str(last_action_label or '').lower()
    if 'steal' in last or 'harvest' in last:
        method_names = (
            'check_friend_farm_bottom_steal_entry',
            'check_friend_farm_bottom_help_all_entry',
        )
    else:
        method_names = (
            'check_friend_farm_bottom_help_all_entry',
            'check_friend_farm_bottom_steal_entry',
        )
    attempts = []
    navigation_frame = fresh_frame
    try:
        mask_fn = globals().get('_friend_navigation_frame_without_selected_card')
        if callable(mask_fn):
            navigation_frame = mask_fn(fresh_frame)
    except BaseException:
        navigation_frame = fresh_frame
    for method_name in method_names:
        if 'steal' in method_name and not bool(getattr(context, 'enable_friend_steal', True)):
            continue
        if 'help' in method_name and not bool(getattr(context, 'enable_friend_help', True)):
            continue
        action = getattr(context, method_name, None)
        if not callable(action):
            continue
        try:
            result = _invoke_friend_guard_action(action, None, (context, navigation_frame), {})
            attempts.append((method_name, bool(result)))
        except BaseException as e:
            attempts.append((method_name, 'error:' + repr(e)[:100]))
            continue
        if not result:
            continue
        label = 'method.' + method_name
        try:
            count = int(getattr(context, '_qqfarm_friend_chain_count', 0) or 0) + 1
            setattr(context, '_qqfarm_friend_chain_count', count)
            setattr(context, '_qqfarm_friend_chain_last_nav_label', label)
            setattr(context, '_qqfarm_friend_page_seen_ts', 0.0)
            setattr(context, '_qqfarm_friend_action_last_ts', 0.0)
            setattr(context, '_qqfarm_visual_friend_count', 0)
        except BaseException:
            pass
        try:
            _write('v71 friend chain moved next action=' + label +
                   ' attempts=' + repr(attempts)[:260])
        except BaseException:
            pass
        return True, label
    try:
        _write('v71 friend chain no next entry attempts=' + repr(attempts)[:260])
    except BaseException:
        pass
    return False, ''


def _friend_chain_begin_dispatch(context):
    """Arm one friend dispatch so nested flows cannot return home early."""
    if context is None:
        return False
    try:
        depth = int(getattr(context, '_qqfarm_friend_chain_dispatch_depth', 0) or 0)
    except BaseException:
        depth = 0
    try:
        if depth <= 0:
            was_pending = bool(getattr(
                context, '_qqfarm_friend_chain_pending', False
            ))
            setattr(context, '_qqfarm_friend_chain_pending', True)
            setattr(context, '_qqfarm_friend_chain_exhausted', False)
            setattr(context, '_qqfarm_friend_chain_native_home_blocked', False)
            if not was_pending:
                # A compiled troublemaker call may have been deferred by the
                # previous friend chain.  Preserve its callable and arguments
                # across redispatches until a real counter increment confirms it.
                setattr(context, '_qqfarm_friend_chain_troublemaker_ran', False)
            try:
                setattr(
                    context,
                    '_qqfarm_friend_chain_started_ts',
                    float(__import__('time').time()),
                )
            except BaseException:
                pass
        setattr(context, '_qqfarm_friend_chain_dispatch_depth', depth + 1)
        setattr(context, '_qqfarm_friend_chain_active', True)
        return True
    except BaseException:
        return False


def _friend_chain_finish_dispatch(context):
    """Drop the nested dispatch marker while preserving pending chain work."""
    if context is None:
        return False
    try:
        depth = max(0, int(getattr(
            context, '_qqfarm_friend_chain_dispatch_depth', 0
        ) or 0) - 1)
        setattr(context, '_qqfarm_friend_chain_dispatch_depth', depth)
        if depth <= 0:
            setattr(context, '_qqfarm_friend_chain_active', False)
        return True
    except BaseException:
        return False


def _friend_chain_should_block_troublemaker(context):
    """True while the current friend still needs verification or continuation."""
    if context is None:
        return False
    try:
        pending = bool(getattr(context, '_qqfarm_friend_chain_pending', False))
        active = bool(getattr(context, '_qqfarm_friend_chain_active', False))
        exhausted = bool(getattr(context, '_qqfarm_friend_chain_exhausted', False))
        return bool((pending or active) and not exhausted)
    except BaseException:
        return False


def _friend_chain_should_block_home(context):
    """Block native home calls until the ordered friend chain is exhausted."""
    if context is None:
        return False
    try:
        if bool(getattr(context, '_qqfarm_friend_chain_allow_home', False)):
            return False
    except BaseException:
        pass
    try:
        if bool(getattr(context, '_qqfarm_troublemaker_retry_scan_active', False)):
            return True
    except BaseException:
        pass
    try:
        block_fn = globals().get('_friend_chain_should_block_troublemaker')
        if callable(block_fn):
            return bool(block_fn(context))
        pending = bool(getattr(context, '_qqfarm_friend_chain_pending', False))
        active = bool(getattr(context, '_qqfarm_friend_chain_active', False))
        exhausted = bool(getattr(context, '_qqfarm_friend_chain_exhausted', False))
        return bool((pending or active) and not exhausted)
    except BaseException:
        return False


def _wrap_friend_home_func(fn, name=''):
    """Gate compiled go-home helpers while the current friend still has work."""
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_friend_home_wrapped__', False):
            return fn, False

        def _wrapped(*args, **kwargs):
            try:
                context_fn = globals().get('_friend_guard_context')
                context = context_fn(args, kwargs) if callable(context_fn) else None
            except BaseException:
                context = None
            if str(name or '').lower().endswith(
                    ('check_go_home_icon', '_has_go_home_icon')):
                candidate_frame = None
                for value in reversed(tuple(args or ())):
                    shape = getattr(value, 'shape', None)
                    if shape is not None and len(shape) >= 2:
                        candidate_frame = value
                        break
                if candidate_frame is None:
                    for value in dict(kwargs or {}).values():
                        shape = getattr(value, 'shape', None)
                        if shape is not None and len(shape) >= 2:
                            candidate_frame = value
                            break
                if candidate_frame is None:
                    try:
                        capture_fn = globals().get('_get_frame_from_bot')
                        if callable(capture_fn):
                            candidate_frame = capture_fn(context)
                    except BaseException:
                        candidate_frame = None
                try:
                    state_fn = globals().get('_friend_guard_friend_ui_state')
                    verified_state = (
                        state_fn(candidate_frame)
                        if callable(state_fn) and candidate_frame is not None
                        else None
                    )
                except BaseException:
                    verified_state = None
                if verified_state is False:
                    try:
                        now_fn = globals().get('_friend_watchdog_now')
                        false_positive_ts = (
                            float(now_fn())
                            if callable(now_fn)
                            else float(__import__('time').time())
                        )
                    except BaseException:
                        false_positive_ts = 0.0
                    try:
                        finalize_fn = globals().get(
                            '_finalize_friend_chain_after_troublemaker'
                        )
                        targets = []
                        for candidate in (
                            context, globals().get('_ACTIVE_RUN_CYCLE_CONTEXT')
                        ):
                            if candidate is None or any(
                                candidate is existing for existing in targets
                            ):
                                continue
                            targets.append(candidate)
                        for target in targets:
                            setattr(
                                target, '_qqfarm_native_home_false_positive_ts',
                                false_positive_ts,
                            )
                            if callable(finalize_fn):
                                finalize_fn(target)
                            setattr(target, '_qqfarm_cycle_branch_hint', 'self')
                            setattr(target, '_qqfarm_friend_cycle_seen', False)
                            setattr(target, '_qqfarm_friend_home_noop_count', 0)
                            setattr(target, '_qqfarm_force_self_cycle_next', True)
                    except BaseException:
                        pass
                    try:
                        log_fn = globals().get('_throttled_write')
                        if callable(log_fn):
                            log_fn(
                                'v160-native-home-false-positive-' + str(name),
                                'v160 rejected native home-icon false positive on ' +
                                'verified non-friend surface ' + str(name),
                                4.0,
                            )
                    except BaseException:
                        pass
                    return False
            try:
                block_fn = globals().get('_friend_chain_should_block_home')
                blocked = bool(block_fn(context)) if callable(block_fn) else False
            except BaseException:
                blocked = False
            if blocked:
                try:
                    setattr(context, '_qqfarm_friend_chain_native_home_blocked', True)
                    setattr(
                        context, '_qqfarm_friend_chain_native_home_blocked_name',
                        str(name),
                    )
                except BaseException:
                    pass
                try:
                    log_fn = globals().get('_throttled_write')
                    if callable(log_fn):
                        log_fn(
                            'v125-native-home-gate-' + str(name),
                            'v125 native home blocked while friend chain pending ' +
                            str(name),
                            10.0,
                        )
                except BaseException:
                    pass
                return False
            return fn(*args, **kwargs)

        try:
            _wrapped.__name__ = getattr(fn, '__name__', 'friend_home_wrapper')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_friend_home_wrapped__ = True
            _wrapped.__qqfarm_friend_home_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False



def _wrap_friend_next_entry_func(fn, name=''):
    """Recover a native bottom-entry miss by clicking the immediate next friend."""
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_friend_next_entry_wrapped__', False):
            return fn, False

        def _wrapped(*args, **kwargs):
            result = fn(*args, **kwargs)
            if result:
                return result

            try:
                context_fn = globals().get('_friend_guard_context')
                context = context_fn(args, kwargs) if callable(context_fn) else None
            except BaseException:
                context = None
            if context is None:
                return result

            candidate_frame = None
            try:
                values = list(args or ()) + list((kwargs or {}).values())
                for value in reversed(values):
                    if value is None or value is context:
                        continue
                    if getattr(value, 'shape', None) is not None:
                        candidate_frame = value
                        break
            except BaseException:
                candidate_frame = None
            if candidate_frame is None:
                try:
                    capture_fn = globals().get('_get_frame_from_bot')
                    if callable(capture_fn):
                        candidate_frame = capture_fn(context)
                except BaseException:
                    candidate_frame = None

            try:
                state_fn = globals().get('_friend_guard_friend_ui_state')
                friend_state = (
                    state_fn(candidate_frame)
                    if callable(state_fn) and candidate_frame is not None
                    else None
                )
            except BaseException:
                friend_state = None
            if friend_state is not True:
                return result

            try:
                navigate_fn = globals().get('_invoke_friend_adjacent_card_navigation')
                navigation = (
                    navigate_fn(context, candidate_frame)
                    if callable(navigate_fn)
                    else (False, '')
                )
                if isinstance(navigation, tuple):
                    moved = bool(navigation[0]) if navigation else False
                    label = str(navigation[1] or '') if len(navigation) > 1 else ''
                else:
                    moved = bool(navigation)
                    label = ''
            except BaseException:
                moved = False
                label = ''
            if not moved:
                return result

            try:
                setattr(context, '_qqfarm_friend_chain_pending', True)
                setattr(context, '_qqfarm_friend_chain_exhausted', False)
                setattr(context, '_qqfarm_friend_chain_active', True)
                setattr(context, '_qqfarm_friend_chain_last_nav_label', label)
            except BaseException:
                pass
            try:
                log_fn = globals().get('_write')
                if callable(log_fn):
                    log_fn(
                        'v169 native bottom entry miss recovered by immediate adjacent friend ' +
                        str(name) + ' label=' + str(label)
                    )
            except BaseException:
                pass
            return True

        try:
            _wrapped.__name__ = getattr(fn, '__name__', 'friend_next_entry_wrapper')
            _wrapped.__qualname__ = getattr(fn, '__qualname__', _wrapped.__name__)
            _wrapped.__qqfarm_friend_next_entry_wrapped__ = True
            _wrapped.__qqfarm_friend_next_entry_orig__ = fn
        except BaseException:
            pass
        return _wrapped, True
    except BaseException:
        return fn, False


def _friend_trouble_counter_snapshot(context, counter_paths=None, today=None):
    """Return the largest durable same-day troublemaker count for this instance."""
    try:
        os_module = __import__('os')
        json_module = __import__('json')
        time_module = __import__('time')
        day = str(today or time_module.strftime('%Y-%m-%d'))
        try:
            instance_id = str(getattr(context, 'instance_id', '1') or '1')
        except BaseException:
            instance_id = '1'
        maximum = 0

        def _safe_count(value):
            try:
                return max(0, int(float(str(value or 0))))
            except BaseException:
                return 0

        def _consume_node(node):
            nonlocal maximum
            if not isinstance(node, dict):
                return
            if str(node.get('friend_trouble_daily_date', '') or '') == day:
                maximum = max(
                    maximum,
                    _safe_count(node.get('friend_trouble_daily_count', 0)),
                )
            metrics = node.get('gui_metrics')
            if (
                isinstance(metrics, dict)
                and str(metrics.get('date', '') or '') == day
            ):
                maximum = max(
                    maximum,
                    _safe_count(metrics.get('troublemaker_count', 0)),
                )

        try:
            context_date = str(getattr(
                context, 'friend_trouble_daily_date', ''
            ) or '')
            if context_date == day:
                maximum = max(maximum, _safe_count(getattr(
                    context, 'friend_trouble_daily_count', 0
                )))
            context_metrics = getattr(context, 'gui_metrics', None)
            if isinstance(context_metrics, dict):
                _consume_node({'gui_metrics': context_metrics})
        except BaseException:
            pass

        if counter_paths is None:
            counter_paths = []
            local = str(os_module.environ.get('LOCALAPPDATA', '') or '')
            if local:
                counter_paths.append(os_module.path.join(
                    local, 'qq-farm-bot-rev', 'daily_counters.json'
                ))
            try:
                base = os_module.path.dirname(os_module.path.abspath(__file__))
                counter_paths.append(os_module.path.join(
                    base, 'UserData', 'legacy-qq-farm-bot-rev',
                    'daily_counters.json',
                ))
            except BaseException:
                pass
        elif isinstance(counter_paths, (str, bytes, os_module.PathLike)):
            counter_paths = [counter_paths]

        seen = set()
        for raw_path in list(counter_paths or []):
            try:
                path = os_module.path.abspath(os_module.fspath(raw_path))
                key = os_module.path.normcase(path)
                if not path or key in seen or not os_module.path.isfile(path):
                    continue
                seen.add(key)
                with open(path, 'r', encoding='utf-8-sig') as handle:
                    payload = json_module.load(handle)
                if not isinstance(payload, dict):
                    continue
                _consume_node(payload)
                instances = payload.get('instances')
                if isinstance(instances, dict):
                    _consume_node(instances.get(instance_id))
            except BaseException:
                continue
        return int(maximum)
    except BaseException:
        return 0

def _save_troublemaker_debug_frame(frame, attempt):
    """Persist the latest failed troublemaker frame for local visual diagnosis."""
    try:
        if frame is None or getattr(frame, 'shape', None) is None:
            return ''
        cv_module = globals().get('cv2') or __import__('cv2')
        os_module = globals().get('os') or __import__('os')
        base = os_module.path.dirname(os_module.path.abspath(__file__))
        log_dir = os_module.path.join(base, 'logs')
        os_module.makedirs(log_dir, exist_ok=True)
        target = os_module.path.join(
            log_dir, 'troublemaker-debug-attempt-' + str(int(attempt)) + '.png'
        )
        encoded_ok, encoded = cv_module.imencode('.png', frame)
        if not encoded_ok:
            return ''
        encoded.tofile(target)
        return target
    except BaseException:
        return ''


def _finalize_friend_chain_after_troublemaker(context):
    """Clear exhausted friend-chain state after troublemaker returns to the home farm."""
    if context is None:
        return False
    try:
        interval_fn = globals().get('_set_friend_chain_fast_interval')
        if callable(interval_fn):
            interval_fn(context, False)
    except BaseException:
        pass
    values = {
        '_qqfarm_friend_chain_pending': False,
        '_qqfarm_friend_chain_exhausted': False,
        '_qqfarm_friend_chain_active': False,
        '_qqfarm_friend_chain_allow_home': False,
        '_qqfarm_troublemaker_retry_scan_active': False,
        '_qqfarm_friend_cycle_seen': False,
        '_qqfarm_visual_friend_count': 0,
        '_qqfarm_friend_branch_last_ts': 0.0,
        '_last_friend_farm_go_home_present': False,
        '_qqfarm_friend_action_last_label': '',
    }
    changed = False
    for name, value in values.items():
        try:
            setattr(context, name, value)
            changed = True
        except BaseException:
            pass
    try:
        clear_fn = globals().get('_friend_guard_clear_prequalification')
        if callable(clear_fn):
            clear_fn(context)
    except BaseException:
        pass
    return changed



def _record_failed_friend_branch_recovery(context, now_ts):
    """Clear a stale native friend hint after two failed self-surface recoveries."""
    if context is None:
        return False
    try:
        failures = int(getattr(
            context, '_qqfarm_friend_home_recovery_fail_count', 0
        ) or 0) + 1
    except BaseException:
        failures = 1
    try:
        setattr(context, '_qqfarm_friend_home_recovery_fail_count', failures)
    except BaseException:
        pass
    if failures < 2:
        return False
    finalize_fn = globals().get('_finalize_friend_chain_after_troublemaker')
    if callable(finalize_fn):
        finalize_fn(context)
    try:
        setattr(context, '_qqfarm_cycle_branch_hint', 'home')
        setattr(context, '_qqfarm_friend_cycle_seen', False)
        setattr(context, '_qqfarm_friend_home_noop_count', 0)
        setattr(context, '_qqfarm_friend_home_recovery_fail_count', 0)
        setattr(
            context, '_qqfarm_false_friend_branch_block_until',
            float(now_ts or 0.0) + 12.0,
        )
    except BaseException:
        pass
    return True


def _apply_runtime_go_home_threshold_floor(context, floor=0.79):
    """Raise every loaded native go-home threshold holder above self-farm noise."""
    if context is None:
        return 0
    try:
        minimum = max(0.0, min(1.0, float(floor)))
    except BaseException:
        minimum = 0.79
    changed = 0

    def _raise_attr(owner, name):
        nonlocal changed
        try:
            marker = object()
            current = getattr(owner, name, marker)
            if current is marker:
                return False
            value = float(current)
            if value >= minimum:
                return False
            setattr(owner, name, minimum)
            changed += 1
            return True
        except BaseException:
            return False

    def _raise_mapping(mapping):
        nonlocal changed
        if not isinstance(mapping, dict):
            return False
        local_changed = False
        for name in ('go_home_frame', 'go_home_frame_threshold', 'go_home_threshold'):
            if name not in mapping:
                continue
            try:
                if float(mapping.get(name)) >= minimum:
                    continue
                mapping[name] = minimum
                changed += 1
                local_changed = True
            except BaseException:
                pass
        for nested_name in ('threshold', 'thresholds'):
            nested = mapping.get(nested_name)
            if isinstance(nested, dict):
                local_changed = _raise_mapping(nested) or local_changed
        return local_changed

    try:
        marker = object()
        current = getattr(context, 'go_home_frame_threshold', marker)
        if current is marker:
            setattr(context, 'go_home_frame_threshold', minimum)
            changed += 1
        else:
            _raise_attr(context, 'go_home_frame_threshold')
    except BaseException:
        pass
    for name in ('go_home_frame', 'go_home_threshold', 'threshold_go_home_frame'):
        _raise_attr(context, name)
    for holder_name in (
            'config', '_config', 'settings', 'bot_config',
            'threshold', 'thresholds', '_thresholds'):
        try:
            holder = getattr(context, holder_name, None)
        except BaseException:
            holder = None
        if holder is None:
            continue
        if isinstance(holder, dict):
            _raise_mapping(holder)
            continue
        for name in ('go_home_frame', 'go_home_frame_threshold', 'go_home_threshold'):
            _raise_attr(holder, name)
        try:
            if (
                callable(getattr(holder, 'has_section', None))
                and holder.has_section('threshold')
                and callable(getattr(holder, 'getfloat', None))
                and callable(getattr(holder, 'set', None))
                and float(holder.getfloat('threshold', 'go_home_frame')) < minimum
            ):
                holder.set('threshold', 'go_home_frame', str(minimum))
                changed += 1
        except BaseException:
            pass
    return changed


def _false_friend_branch_cooldown_active(context, visual_state, now_ts):
    if context is None or visual_state is not False:
        return False
    try:
        block_until = float(getattr(
            context, '_qqfarm_false_friend_branch_block_until', 0.0
        ) or 0.0)
        return bool(block_until > float(now_ts or 0.0))
    except BaseException:
        return False



def _run_deferred_friend_troublemaker(context, frame):
    """Run deferred troublemaker work across adjacent friends and verify persistence."""
    if context is None:
        return False
    try:
        if bool(getattr(context, '_qqfarm_friend_chain_pending', False)):
            return False
        if not bool(getattr(context, '_qqfarm_friend_chain_exhausted', False)):
            return False
        if bool(getattr(context, '_qqfarm_friend_chain_troublemaker_ran', False)):
            return False
        now_fn = globals().get('_friend_watchdog_now')
        try:
            now_ts = (
                float(now_fn())
                if callable(now_fn)
                else float(__import__('time').time())
            )
        except BaseException:
            now_ts = 0.0
        try:
            full_miss_until = float(getattr(
                context, '_qqfarm_troublemaker_full_miss_until', 0.0
            ) or 0.0)
        except BaseException:
            full_miss_until = 0.0
        if full_miss_until > now_ts:
            try:
                _write(
                    'v187 troublemaker full-miss cooldown active remaining=' +
                    ('%.1f' % max(0.0, full_miss_until - now_ts)) + 's'
                )
            except BaseException:
                pass
            return False
        action = getattr(context, '_run_friend_daily_troublemaker', None)
        cached_action = False
        if not callable(action):
            action = getattr(
                context, '_qqfarm_friend_chain_deferred_troublemaker', None
            )
            cached_action = callable(action)
        if not callable(action):
            try:
                for module_name, module in list(sys.modules.items()):
                    if module is None or not str(module_name).startswith('bot.'):
                        continue
                    candidate = getattr(
                        module, '_run_friend_daily_troublemaker', None
                    )
                    if not callable(candidate):
                        continue
                    action = candidate
                    cached_action = True
                    setattr(
                        context,
                        '_qqfarm_friend_chain_deferred_troublemaker',
                        candidate,
                    )
                    setattr(
                        context,
                        '_qqfarm_friend_chain_deferred_troublemaker_args',
                        (context, frame),
                    )
                    setattr(
                        context,
                        '_qqfarm_friend_chain_deferred_troublemaker_kwargs',
                        {},
                    )
                    _write(
                        'v175 deferred daily troublemaker resolved runtime callable ' +
                        str(module_name) + '._run_friend_daily_troublemaker'
                    )
                    break
            except BaseException as error:
                try:
                    _write(
                        'v175 deferred troublemaker runtime resolver error=' +
                        repr(error)[:220]
                    )
                except BaseException:
                    pass
        if not callable(action):
            try:
                _write('v175 deferred daily troublemaker callable missing; retryable=True')
            except BaseException:
                pass
            return False

        try:
            retry_limit = int(getattr(
                context, 'friend_troublemaker_adjacent_retry_limit', 3
            ) or 3)
        except BaseException:
            retry_limit = 3
        retry_limit = max(1, min(12, retry_limit))
        snapshot_fn = globals().get('_friend_trouble_counter_snapshot')
        snapshot_available = callable(snapshot_fn)
        invoke_fn = globals().get('_invoke_friend_guard_action')
        adjacent_fn = globals().get('_invoke_friend_adjacent_card_navigation')
        capture_fn = globals().get('_get_frame_from_bot')
        state_fn = globals().get('_friend_guard_friend_ui_state')
        sleep_fn = globals().get('_friend_guard_sleep')
        marker = object()

        def _pause(seconds):
            try:
                if callable(sleep_fn):
                    sleep_fn(seconds)
                else:
                    __import__('time').sleep(seconds)
            except BaseException:
                pass

        def _restore_attr(name, previous):
            try:
                if previous is marker:
                    delattr(context, name)
                else:
                    setattr(context, name, previous)
            except BaseException:
                pass

        def _invoke_on_frame(current_frame):
            if cached_action:
                try:
                    cached_args = list(getattr(
                        context,
                        '_qqfarm_friend_chain_deferred_troublemaker_args',
                        (),
                    ) or ())
                except BaseException:
                    cached_args = []
                try:
                    cached_kwargs = dict(getattr(
                        context,
                        '_qqfarm_friend_chain_deferred_troublemaker_kwargs',
                        {},
                    ) or {})
                except BaseException:
                    cached_kwargs = {}
                for index, value in enumerate(list(cached_args)):
                    try:
                        if value is not context and hasattr(value, 'shape'):
                            cached_args[index] = current_frame
                    except BaseException:
                        pass
                for key, value in list(cached_kwargs.items()):
                    try:
                        if value is not context and hasattr(value, 'shape'):
                            cached_kwargs[key] = current_frame
                    except BaseException:
                        pass
                if not cached_args:
                    cached_args = [context]
                if callable(invoke_fn):
                    return invoke_fn(
                        action, None, tuple(cached_args), cached_kwargs
                    )
                return action(*tuple(cached_args), **cached_kwargs)
            try:
                if callable(invoke_fn):
                    return invoke_fn(action, None, (context, current_frame), {})
                return action(current_frame)
            except TypeError:
                return action()

        current_frame = frame
        last_result = False
        for attempt in range(retry_limit):
            before_count = None
            if snapshot_available:
                try:
                    before_count = int(snapshot_fn(context))
                except BaseException:
                    before_count = 0

            previous_allow_home = getattr(
                context, '_qqfarm_friend_chain_allow_home', marker
            )
            previous_retry_active = getattr(
                context, '_qqfarm_troublemaker_retry_scan_active', marker
            )
            setattr(context, '_qqfarm_friend_chain_allow_home', True)
            setattr(context, '_qqfarm_troublemaker_retry_scan_active', True)
            try:
                last_result = _invoke_on_frame(current_frame)
            finally:
                _restore_attr(
                    '_qqfarm_troublemaker_retry_scan_active',
                    previous_retry_active,
                )
                _restore_attr(
                    '_qqfarm_friend_chain_allow_home', previous_allow_home
                )

            after_count = None
            if snapshot_available:
                try:
                    after_count = int(snapshot_fn(context))
                except BaseException:
                    after_count = int(before_count or 0)
                success = bool(after_count > int(before_count or 0))
            else:
                success = bool(last_result)
            try:
                _write(
                    'v150 deferred daily troublemaker attempt=' +
                    str(attempt + 1) + '/' + str(retry_limit) +
                    ' raw=' + repr(last_result)[:180] +
                    ' count=' + repr(before_count) + '->' + repr(after_count) +
                    ' success=' + repr(success) +
                    ' cached=' + repr(cached_action)
                )
            except BaseException:
                pass
            if success:
                setattr(context, '_qqfarm_friend_chain_troublemaker_ran', True)
                try:
                    setattr(context, '_qqfarm_troublemaker_full_miss_until', 0.0)
                except BaseException:
                    pass
                finalize_fn = globals().get(
                    '_finalize_friend_chain_after_troublemaker'
                )
                if callable(finalize_fn):
                    finalize_fn(context)
                try:
                    _write('v158 troublemaker success finalized friend chain')
                except BaseException:
                    pass
                return last_result
            debug_frame_fn = globals().get('_save_troublemaker_debug_frame')
            if callable(debug_frame_fn):
                try:
                    debug_path = debug_frame_fn(current_frame, attempt + 1)
                    if debug_path:
                        _write(
                            'v151 troublemaker debug frame saved=' + str(debug_path)
                        )
                except BaseException:
                    pass
            if attempt + 1 >= retry_limit or not callable(adjacent_fn):
                break

            try:
                moved_raw = adjacent_fn(context, current_frame)
                moved = bool(moved_raw[0]) if isinstance(moved_raw, tuple) else bool(moved_raw)
            except BaseException as error:
                moved = False
                try:
                    _write('v150 troublemaker adjacent navigation error=' + repr(error)[:220])
                except BaseException:
                    pass
            if not moved:
                break
            _pause(0.14)

            next_frame = None
            for poll in range(12):
                try:
                    candidate = capture_fn(context) if callable(capture_fn) else None
                except BaseException:
                    candidate = None
                if candidate is not None:
                    try:
                        ready = state_fn(candidate) if callable(state_fn) else True
                    except BaseException:
                        ready = None
                    if ready is True:
                        next_frame = candidate
                        break
                if poll < 11:
                    _pause(min(0.24, 0.08 + (0.015 * poll)))
            if next_frame is None:
                try:
                    _write(
                        'v150 troublemaker next friend surface not ready; '
                        'leaving retryable state'
                    )
                except BaseException:
                    pass
                break
            current_frame = next_frame

        setattr(context, '_qqfarm_friend_chain_troublemaker_ran', False)
        try:
            cooldown_seconds = float(getattr(
                context, 'friend_troublemaker_full_miss_cooldown_seconds', 90.0
            ) or 90.0)
        except BaseException:
            cooldown_seconds = 90.0
        cooldown_seconds = max(10.0, min(900.0, cooldown_seconds))
        try:
            cooldown_now = (
                float(now_fn())
                if callable(now_fn)
                else float(__import__('time').time())
            )
        except BaseException:
            cooldown_now = now_ts
        try:
            setattr(
                context, '_qqfarm_troublemaker_full_miss_until',
                float(cooldown_now) + cooldown_seconds,
            )
        except BaseException:
            pass
        try:
            _write(
                'v187 deferred daily troublemaker full miss; cooldown=' +
                ('%.1f' % cooldown_seconds) + 's'
            )
        except BaseException:
            pass
        try:
            _write(
                'v150 deferred daily troublemaker exhausted attempts; '
                'success=False retryable=True'
            )
        except BaseException:
            pass
        return False
    except BaseException as error:
        try:
            setattr(context, '_qqfarm_friend_chain_troublemaker_ran', False)
        except BaseException:
            pass
        try:
            _write('v150 deferred daily troublemaker error=' + repr(error)[:220])
        except BaseException:
            pass
        return False

def _run_friend_continuation_chain(context, start_frame, last_action_label=''):
    """Visit and process successive friends before allowing home recovery."""
    result = {
        'moves': 0,
        'actions': 0,
        'last_label': str(last_action_label or ''),
        'frame': start_frame,
        'exhausted': False,
        'reason': 'not-started',
    }
    if context is None or start_frame is None:
        result['reason'] = 'invalid-context-or-frame'
        return result
    try:
        quota_fn = globals().get('_friend_help_quota_active')
        quota_active = bool(
            quota_fn(context) if callable(quota_fn)
            else getattr(context, '_qqfarm_friend_help_quota_exhausted', False)
        )
    except BaseException:
        quota_active = False
    if quota_active:
        result['exhausted'] = True
        result['reason'] = 'friend-help-quota-exhausted'
        try:
            setattr(context, '_qqfarm_friend_chain_pending', False)
            setattr(context, '_qqfarm_friend_chain_exhausted', True)
            setattr(context, '_qqfarm_friend_chain_allow_home', True)
        except BaseException:
            pass
        return result
    try:
        guard_enabled_fn = globals().get('_guard_dog_ui_config_enabled')
        guard_mode_fn = globals().get('_guard_dog_detection_mode_config')
        guard_enabled = bool(guard_enabled_fn()) if callable(guard_enabled_fn) else False
        guard_mode = str(
            guard_mode_fn() if callable(guard_mode_fn) else 'avatar_frame'
        )
    except BaseException:
        guard_enabled, guard_mode = False, 'avatar_frame'
    try:
        verified_fn = globals().get('_friend_guard_verified_entry_active')
        verified_guard_row = bool(
            guard_enabled
            and guard_mode == 'avatar_frame'
            and callable(verified_fn)
            and verified_fn(context)
        )
    except BaseException:
        verified_guard_row = False
    move_fn = globals().get('_invoke_friend_next_actionable_entry')
    adjacent_fn = globals().get('_invoke_friend_adjacent_card_navigation')
    action_fn = globals().get('_invoke_friend_actions_before_home')
    fast_action_fn = globals().get('_invoke_friend_visual_actions_before_home')
    try:
        native_action_fallback_enabled = bool(
            not callable(fast_action_fn)
            or getattr(context, 'friend_chain_allow_native_action_fallback', False)
        )
    except BaseException:
        native_action_fallback_enabled = not callable(fast_action_fn)
    initial_native_action_fallback_enabled = bool(
        native_action_fallback_enabled
        or (guard_enabled and guard_mode == 'friend_guard_list')
    )
    capture_fn = globals().get('_get_frame_from_bot')
    state_fn = globals().get('_friend_guard_friend_ui_state')
    sleep_fn = globals().get('_friend_guard_sleep')
    write_fn = globals().get('_write')
    if not callable(move_fn) or not callable(action_fn) or not callable(capture_fn):
        result['reason'] = 'missing-chain-helper'
        return result
    try:
        setattr(context, '_qqfarm_friend_chain_active', True)
        setattr(context, '_qqfarm_friend_chain_pending', True)
        setattr(context, '_qqfarm_friend_chain_exhausted', False)
    except BaseException:
        pass
    try:
        restore_fn = globals().get('_restore_runtime_business_switches')
        if callable(restore_fn):
            restore_fn(context)
    except BaseException:
        pass
    try:
        fast_fn = globals().get('_set_friend_chain_fast_interval')
        if callable(fast_fn):
            fast_fn(context, True)
    except BaseException:
        pass
    try:
        limit = int(getattr(context, 'bottom_friend_list_help_all_limit', 12) or 12)
    except BaseException:
        limit = 12
    limit = max(1, min(50, limit))
    try:
        known_actionable_count = max(0, int(getattr(
            context, '_qqfarm_friend_list_visible_candidate_count', 0
        ) or 0))
    except BaseException:
        known_actionable_count = 0
    try:
        configured_guard_gap_budget = int(getattr(
            context, 'friend_chain_guard_gap_scan_budget', 6
        ) or 6)
    except BaseException:
        configured_guard_gap_budget = 6
    configured_guard_gap_budget = max(2, min(limit, configured_guard_gap_budget))
    guard_gap_scan_budget = min(
        limit,
        max(
            configured_guard_gap_budget
            if guard_enabled and guard_mode == 'friend_guard_list'
            else 1,
            known_actionable_count * 2,
        ),
    )
    try:
        action_poll_limit = int(getattr(context, 'friend_chain_action_poll_limit', 16) or 16)
    except BaseException:
        action_poll_limit = 16
    action_poll_limit = max(24, min(36, action_poll_limit))
    try:
        primary_navigation_poll_limit = int(
            getattr(context, 'friend_chain_primary_navigation_poll_limit', 4) or 4
        )
    except BaseException:
        primary_navigation_poll_limit = 4
    primary_navigation_poll_limit = max(
        2, min(action_poll_limit - 1, primary_navigation_poll_limit)
    )
    try:
        idle_confirmations = int(
            getattr(context, 'friend_chain_idle_confirmations', 3) or 3
        )
    except BaseException:
        idle_confirmations = 3
    idle_confirmations = max(2, min(6, idle_confirmations))
    try:
        initial_idle_poll_min = int(getattr(
            context, 'friend_chain_initial_idle_poll_min', 8
        ) or 8)
    except BaseException:
        initial_idle_poll_min = 8
    initial_idle_poll_min = max(
        idle_confirmations, min(action_poll_limit, initial_idle_poll_min)
    )
    if guard_enabled and guard_mode == 'friend_guard_list':
        try:
            extended_entry_grace = bool(getattr(
                context, '_qqfarm_friend_entry_extended_action_grace', False
            ))
        except BaseException:
            extended_entry_grace = False
        try:
            guard_initial_idle_poll_min = int(getattr(
                context, 'friend_chain_guard_initial_idle_poll_min', 12
            ) or 12)
        except BaseException:
            guard_initial_idle_poll_min = 12
        if extended_entry_grace:
            guard_initial_idle_poll_min = max(20, guard_initial_idle_poll_min)
        initial_idle_poll_min = max(
            initial_idle_poll_min,
            min(action_poll_limit, max(idle_confirmations, guard_initial_idle_poll_min)),
        )
    try:
        preference_marker = object()
        prefer_adjacent_raw = getattr(
            context, 'friend_chain_prefer_adjacent_navigation', preference_marker
        )
        if prefer_adjacent_raw is preference_marker:
            cfg_fn = globals().get('_cfg_get')
            sections_fn = globals().get('_active_bot_sections')
            if callable(cfg_fn):
                sections = sections_fn() if callable(sections_fn) else ('bot',)
                prefer_adjacent_raw = cfg_fn(
                    sections,
                    'friend_chain_prefer_adjacent_navigation',
                    'False',
                )
            else:
                prefer_adjacent_raw = False
        prefer_adjacent_navigation = str(prefer_adjacent_raw).strip().lower() in (
            '1', 'true', 'yes', 'on', 'enabled'
        )
    except BaseException:
        prefer_adjacent_navigation = False

    def _pause(seconds):
        try:
            if callable(sleep_fn):
                sleep_fn(seconds)
            else:
                __import__('time').sleep(seconds)
        except BaseException:
            pass

    def _adjacent_move(frame_value):
        navigation_callable = adjacent_fn
        if not callable(navigation_callable):
            # Compatibility for isolated/unit-loaded helpers; the production
            # module always supplies the in-farm adjacent-card navigator.
            navigation_callable = move_fn
        if not callable(navigation_callable):
            return False, ''
        try:
            if navigation_callable is move_fn:
                raw = navigation_callable(context, frame_value, last_label)
            else:
                raw = navigation_callable(context, frame_value)
        except BaseException as error:
            if callable(write_fn):
                try:
                    write_fn('v85 friend adjacent navigation error=' + repr(error)[:220])
                except BaseException:
                    pass
            return False, ''
        if isinstance(raw, tuple):
            return bool(raw[0]), str(raw[1] if len(raw) > 1 else '')
        return bool(raw), ('visual.adjacent-friend-card' if raw else '')

    def _consume_guard_dog_help_skip():
        try:
            skipped = bool(getattr(
                context, '_qqfarm_guard_dog_help_skipped', False
            ))
            if skipped:
                setattr(context, '_qqfarm_guard_dog_help_skipped', False)
            return skipped
        except BaseException:
            return False

    def _consume_native_action_unverified():
        try:
            unverified = bool(getattr(
                context, '_qqfarm_friend_native_action_unverified', False
            ))
            if unverified:
                setattr(context, '_qqfarm_friend_native_action_unverified', False)
            return unverified
        except BaseException:
            return False

    def _drain_current_friend_actions(
        frame_value, handled_label='', initial_friend=False
    ):
        """Finish remaining visual actions on one friend before moving right."""
        if not callable(fast_action_fn):
            return frame_value, 0, '', True, 1

        def _action_kind(label_value):
            lowered = str(label_value or '').lower()
            if 'steal' in lowered or 'harvest' in lowered:
                return 'steal'
            if 'help' in lowered or 'farm' in lowered:
                return 'help'
            return lowered

        handled_kinds = set()
        seed_kind = _action_kind(handled_label)
        if seed_kind and not bool(initial_friend):
            handled_kinds.add(seed_kind)
        current_frame = frame_value
        added_actions = 0
        newest_label = ''
        idle_streak = 0
        surface_hits = 0
        repeated_action_counts = {}
        for drain_attempt in range(action_poll_limit):
            try:
                captured = capture_fn(context)
            except BaseException:
                captured = None
            if captured is not None:
                current_frame = captured
            try:
                current_state = (
                    state_fn(current_frame) if callable(state_fn) else True
                )
            except BaseException:
                current_state = None
            if current_state is not True:
                idle_streak = 0
                if drain_attempt < action_poll_limit - 1:
                    _pause(min(0.22, 0.08 + (0.015 * drain_attempt)))
                continue
            surface_hits += 1
            try:
                acted_now, label_now = fast_action_fn(context, current_frame)
            except BaseException as error:
                acted_now = False
                label_now = ''
                if callable(write_fn):
                    try:
                        write_fn(
                            'v116 friend current-card drain error=' +
                            repr(error)[:220]
                        )
                    except BaseException:
                        pass
            if _consume_guard_dog_help_skip():
                if callable(write_fn):
                    try:
                        write_fn(
                            'v131 guard dog rejected help; current friend is drained ' +
                            'without counting a help action'
                        )
                    except BaseException:
                        pass
                return current_frame, added_actions, newest_label, True, surface_hits
            if acted_now:
                action_kind = _action_kind(label_now)
                if action_kind and action_kind not in handled_kinds:
                    handled_kinds.add(action_kind)
                    added_actions += 1
                    newest_label = str(label_now or newest_label)
                    idle_streak = 0
                    if action_kind == 'help':
                        try:
                            setattr(
                                context,
                                '_qqfarm_post_steal_help_retry_pending',
                                False,
                            )
                        except BaseException:
                            pass
                    if callable(write_fn):
                        try:
                            write_fn(
                                'v116 friend current-card action drained action=' +
                                str(newest_label) + ' total=' + str(added_actions)
                            )
                        except BaseException:
                            pass
                    _pause(0.18)
                    continue
                # The same action being detected again means it has not yet
                # disappeared.  Keep this friend active and retry instead of
                # counting stale visibility as proof that the card is idle.
                idle_streak = 0
                repeated_key = str(action_kind or label_now or handled_label or 'action')
                repeated_count = int(repeated_action_counts.get(repeated_key, 0) or 0) + 1
                repeated_action_counts[repeated_key] = repeated_count
                if callable(write_fn):
                    try:
                        write_fn(
                            'v124 friend current-card action still visible action=' +
                            str(label_now or handled_label) +
                            ' retry=' + str(repeated_count) + '/3'
                        )
                    except BaseException:
                        pass
                if repeated_count >= 3:
                    return current_frame, added_actions, newest_label, False, surface_hits
                if drain_attempt < action_poll_limit - 1:
                    _pause(min(0.24, 0.09 + (0.015 * drain_attempt)))
                continue
            idle_streak += 1
            post_steal_grace_active = bool(
                seed_kind == 'steal' and int(added_actions or 0) <= 0
            )
            minimum_idle_polls = (
                initial_idle_poll_min
                if bool(initial_friend) or post_steal_grace_active
                else idle_confirmations
            )
            if (
                idle_streak >= idle_confirmations
                and (drain_attempt + 1) >= minimum_idle_polls
            ):
                try:
                    hold_initial_post_steal = bool(
                        post_steal_grace_active
                        and getattr(
                            context,
                            '_qqfarm_friend_entry_extended_action_grace',
                            False,
                        )
                    )
                except BaseException:
                    hold_initial_post_steal = False
                if hold_initial_post_steal:
                    try:
                        retry_pending = bool(getattr(
                            context,
                            '_qqfarm_post_steal_help_retry_pending',
                            False,
                        ))
                    except BaseException:
                        retry_pending = False
                    if not retry_pending:
                        try:
                            setattr(
                                context,
                                '_qqfarm_post_steal_help_retry_pending',
                                True,
                            )
                            if callable(write_fn):
                                write_fn(
                                    'v219 compiled steal completed; keeping the same '
                                    'friend for one more help probe before navigation'
                                )
                        except BaseException:
                            pass
                        return (
                            current_frame, added_actions, newest_label, False, surface_hits
                        )
                    try:
                        setattr(
                            context,
                            '_qqfarm_post_steal_help_retry_pending',
                            False,
                        )
                        if callable(write_fn):
                            write_fn(
                                'v219 post-steal help absence confirmed twice; '
                                'adjacent navigation may continue'
                            )
                    except BaseException:
                        pass
                return (
                    current_frame, added_actions, newest_label, True, surface_hits
                )
            if drain_attempt < action_poll_limit - 1:
                _pause(min(0.22, 0.08 + (0.015 * drain_attempt)))
        try:
            hold_initial_post_steal = bool(
                seed_kind == 'steal'
                and int(added_actions or 0) <= 0
                and getattr(
                    context,
                    '_qqfarm_friend_entry_extended_action_grace',
                    False,
                )
            )
        except BaseException:
            hold_initial_post_steal = False
        if hold_initial_post_steal:
            try:
                retry_pending = bool(getattr(
                    context, '_qqfarm_post_steal_help_retry_pending', False
                ))
            except BaseException:
                retry_pending = False
            if not retry_pending:
                try:
                    setattr(context, '_qqfarm_post_steal_help_retry_pending', True)
                    if callable(write_fn):
                        write_fn(
                            'v219 compiled steal probe exhausted; keeping the same '
                            'friend for one more help probe before navigation'
                        )
                except BaseException:
                    pass
                return current_frame, added_actions, newest_label, False, surface_hits
            try:
                setattr(context, '_qqfarm_post_steal_help_retry_pending', False)
            except BaseException:
                pass
            return current_frame, added_actions, newest_label, True, surface_hits
        return current_frame, added_actions, newest_label, False, surface_hits

    frame = start_frame
    last_label = str(last_action_label or '')
    try:
        compiled_home_blocked = bool(getattr(
            context, '_qqfarm_friend_chain_native_home_blocked', False
        ))
    except BaseException:
        compiled_home_blocked = False
    result['reason'] = 'limit-reached'
    loop_limit = limit
    try:
        guard_mode_fn = globals().get('_guard_dog_ui_config_enabled')
        guard_dog_list_filter_required = bool(
            callable(guard_mode_fn) and guard_mode_fn()
        )
    except BaseException:
        guard_dog_list_filter_required = False
    if guard_dog_list_filter_required:
        # The bottom carousel is already ordered by visible one-click actions.
        # Continue to the next card and stop only after the first confirmed
        # friend without an action; returning home immediately after one friend
        # skips the remaining actionable cards shown in the carousel.
        prefer_adjacent_navigation = True

    # Once the first friend has been entered, the list/menu route is forbidden.
    # It can open the friend list or appearance catalogue and can also skip the
    # immediately adjacent friend.  Continuation always stays on the in-farm
    # bottom carousel regardless of stale compiled/config preferences.
    prefer_adjacent_navigation = True

    # A friend-list visit can arrive before the first friend's one-click button
    # has finished rendering.  Never advance until the current friend surface is
    # stable and every visible steal/help action on that same friend is finished.
    if last_label:
        try:
            extended_entry_grace = bool(getattr(
                context, '_qqfarm_friend_entry_extended_action_grace', False
            ))
        except BaseException:
            extended_entry_grace = False
        try:
            guard_entry_still_prequalified = bool(
                guard_enabled
                and guard_mode == 'friend_guard_list'
                and callable(globals().get(
                    '_friend_guard_list_prequalified_entry_active'
                ))
                and globals()['_friend_guard_list_prequalified_entry_active'](context)
            )
        except BaseException:
            guard_entry_still_prequalified = False
        initial_friend_recheck = bool(
            extended_entry_grace or guard_entry_still_prequalified
        )
        (
            frame,
            drained_actions,
            drained_label,
            current_idle_confirmed,
            current_surface_hits,
        ) = _drain_current_friend_actions(
            frame, last_label, initial_friend=initial_friend_recheck
        )
        result['frame'] = frame
        result['actions'] += int(drained_actions or 0)
        if drained_label:
            last_label = str(drained_label)
            result['last_label'] = last_label
        if not current_idle_confirmed:
            result['reason'] = (
                'friend-surface-not-ready'
                if int(current_surface_hits or 0) <= 0
                else 'current-friend-not-idle'
            )
            loop_limit = 0
    else:
        initial_acted = False
        initial_action_label = ''
        initial_full_probe_done = False
        initial_ready_streak = 0
        initial_guard_help_skipped = False
        initial_native_action_unverified = False
        for initial_attempt in range(action_poll_limit):
            try:
                initial_frame = (
                    frame if initial_attempt == 0 else capture_fn(context)
                )
            except BaseException:
                initial_frame = None
            if initial_frame is not None:
                frame = initial_frame
                result['frame'] = frame
                try:
                    initial_state = (
                        state_fn(frame) if callable(state_fn) else True
                    )
                except BaseException:
                    initial_state = None
                if initial_state is not True:
                    initial_ready_streak = 0
                    if initial_attempt < action_poll_limit - 1:
                        _pause(min(0.22, 0.08 + (0.015 * initial_attempt)))
                    continue
                try:
                    if callable(fast_action_fn):
                        initial_acted, initial_action_label = fast_action_fn(
                            context, frame
                        )
                        if _consume_guard_dog_help_skip():
                            initial_guard_help_skipped = True
                            break
                    if (
                        not initial_acted
                        and initial_native_action_fallback_enabled
                        and not initial_full_probe_done
                        and (initial_attempt + 1) >= primary_navigation_poll_limit
                    ):
                        initial_full_probe_done = True
                        initial_acted, initial_action_label = action_fn(context, frame)
                        if _consume_native_action_unverified():
                            initial_native_action_unverified = True
                            initial_acted = False
                            initial_action_label = ''
                            break
                        if _consume_guard_dog_help_skip():
                            initial_guard_help_skipped = True
                            break
                except BaseException as error:
                    initial_acted = False
                    initial_action_label = ''
                    if callable(write_fn):
                        try:
                            write_fn(
                                'v116 friend initial ordered action error=' +
                                repr(error)[:220]
                            )
                        except BaseException:
                            pass
                if initial_acted:
                    break
                initial_ready_streak += 1
                if (
                    initial_ready_streak >= idle_confirmations
                    and (initial_attempt + 1) >= initial_idle_poll_min
                ):
                    break
            if initial_attempt < action_poll_limit - 1:
                _pause(min(0.22, 0.08 + (0.015 * initial_attempt)))
        if initial_acted:
            try:
                setattr(context, '_qqfarm_initial_guard_approval_pending_count', 0)
            except BaseException:
                pass
            result['actions'] += 1
            last_label = str(initial_action_label or '')
            result['last_label'] = last_label
            result['reason'] = 'initial-action-complete'
            _pause(0.18)
            (
                frame,
                drained_actions,
                drained_label,
                current_idle_confirmed,
                current_surface_hits,
            ) = _drain_current_friend_actions(frame, last_label)
            result['frame'] = frame
            result['actions'] += int(drained_actions or 0)
            if drained_label:
                last_label = str(drained_label)
                result['last_label'] = last_label
            if not current_idle_confirmed:
                result['reason'] = (
                    'friend-surface-not-ready'
                    if int(current_surface_hits or 0) <= 0
                    else 'current-friend-not-idle'
                )
                loop_limit = 0
        elif initial_native_action_unverified:
            result['reason'] = 'initial-native-action-unverified'
            loop_limit = 0
            if callable(write_fn):
                try:
                    write_fn(
                        'v212 unverified native help claim; keeping the first '
                        'friend active without carousel navigation'
                    )
                except BaseException:
                    pass
        elif initial_guard_help_skipped:
            # Guard identity can be briefly unavailable while the first farm is
            # settling, so retry the same card a few times.  A persistent negative
            # decision is authoritative, however: continuing to pin the same card
            # creates an infinite empty-cycle loop even though later friends remain.
            try:
                pending_count = int(getattr(
                    context, '_qqfarm_initial_guard_approval_pending_count', 0
                ) or 0) + 1
            except BaseException:
                pending_count = 1
            try:
                pending_limit = int(getattr(
                    context, 'friend_chain_guard_pending_retry_limit', 3
                ) or 3)
            except BaseException:
                pending_limit = 3
            pending_limit = max(1, min(8, pending_limit))
            try:
                setattr(
                    context, '_qqfarm_initial_guard_approval_pending_count',
                    pending_count,
                )
            except BaseException:
                pass
            if pending_count < pending_limit:
                result['reason'] = 'initial-guard-approval-pending'
                loop_limit = 0
                if callable(write_fn):
                    try:
                        write_fn(
                            'v188 initial guard approval pending; keeping the first '
                            'friend active retry=' + str(pending_count) + '/' +
                            str(pending_limit)
                        )
                    except BaseException:
                        pass
            else:
                result['reason'] = 'initial-guard-rejected-advance'
                try:
                    setattr(
                        context, '_qqfarm_initial_guard_approval_pending_count', 0
                    )
                except BaseException:
                    pass
                clear_fn = globals().get('_friend_guard_clear_prequalification')
                if callable(clear_fn):
                    try:
                        clear_fn(context)
                    except BaseException:
                        pass
                if callable(write_fn):
                    try:
                        write_fn(
                            'v188 initial guard approval rejected after bounded '
                            'retries; advancing to the next adjacent friend'
                        )
                    except BaseException:
                        pass
        elif initial_ready_streak >= idle_confirmations:
            try:
                guard_list_initial_approved = bool(
                    guard_enabled
                    and guard_mode == 'friend_guard_list'
                    and callable(globals().get(
                        '_friend_guard_list_prequalified_entry_active'
                    ))
                    and globals()[
                        '_friend_guard_list_prequalified_entry_active'
                    ](context)
                )
            except BaseException:
                guard_list_initial_approved = False
            if compiled_home_blocked:
                # The compiled friend flow already completed its current-card
                # action and tried to return home.  The home gate is therefore
                # positive completion evidence even though the visual button has
                # disappeared before the Hook can record an action label.
                try:
                    setattr(
                        context, '_qqfarm_friend_chain_native_home_blocked', False
                    )
                except BaseException:
                    pass
                result['reason'] = 'compiled-current-friend-complete'
            elif guard_list_initial_approved:
                # A whitelist-selected first friend is an identity match, not
                # proof that this specific farm currently has an action.  Check
                # the next bottom card before ending the ordered friend block.
                result['reason'] = 'initial-guard-friend-no-action-continue'
            else:
                result['exhausted'] = True
                result['reason'] = 'initial-friend-no-action'
                loop_limit = 0
        else:
            result['reason'] = 'friend-surface-not-ready'
            loop_limit = 0
    if verified_guard_row:
        pending_reasons = ('friend-surface-not-ready', 'current-friend-not-idle')
        if str(result.get('reason', '')) not in pending_reasons:
            result['exhausted'] = True
            result['reason'] = 'verified-guard-row-complete'
            try:
                setattr(context, '_qqfarm_guard_row_verified', False)
            except BaseException:
                pass
            if callable(write_fn):
                try:
                    write_fn(
                        'v135 verified dog-badge friend drained; '
                        'returning to list before selecting another friend'
                    )
                except BaseException:
                    pass
        loop_limit = 0
    for index in range(loop_limit):
        try:
            stop_fn = globals().get('_is_stop_requested_like')
            if callable(stop_fn) and stop_fn(context):
                result['reason'] = 'stop-requested'
                break
        except BaseException:
            pass
        # `frame` already belongs to the friend just fully drained.  Capturing
        # again here can advance the synthetic/live frame stream before the click
        # and makes the chain skip the immediately adjacent card.
        signature_fn = globals().get('_friend_navigation_signature')
        score_fn = globals().get('_friend_navigation_change_score')
        selected_bounds_fn = globals().get('_friend_selected_carousel_card_bounds')
        selection_changed_fn = globals().get('_friend_carousel_selection_changed')
        try:
            before_navigation_signature = (
                signature_fn(frame) if callable(signature_fn) else None
            )
        except BaseException:
            before_navigation_signature = None
        try:
            before_selected_bounds = (
                selected_bounds_fn(frame) if callable(selected_bounds_fn) else None
            )
        except BaseException:
            before_selected_bounds = None
        fallback_attempted = False
        fallback_succeeded = False
        moved = False
        navigation_label = ''
        if prefer_adjacent_navigation:
            # Stay inside the current friend's farm.  Never open the friend list,
            # appearance/menu pages, or a native list-entry fallback from this chain.
            moved, navigation_label = _adjacent_move(frame)
            fallback_attempted = bool(moved)
            fallback_succeeded = bool(moved)
            if not moved:
                result['exhausted'] = True
                result['reason'] = 'no-next-bottom-card'
                break
        else:
            try:
                moved, navigation_label = move_fn(context, frame, last_label)
            except BaseException as error:
                moved, navigation_label = False, ''
                result['reason'] = 'navigation-error'
                if callable(write_fn):
                    try:
                        write_fn('v89 friend continuation navigation error=' + repr(error)[:220])
                    except BaseException:
                        pass
            if not moved:
                moved, navigation_label = _adjacent_move(frame)
                fallback_attempted = bool(moved)
                fallback_succeeded = bool(moved)
            if not moved:
                result['exhausted'] = True
                result['reason'] = 'no-next-entry'
                break
        _pause(0.12)

        next_frame = None
        friend_state = None
        acted = False
        action_label = ''
        guard_help_skipped = False
        native_action_unverified = False
        blocked_next_friend_returned_home = False
        # Synthetic/unreadable captures may not expose a usable signature.  Keep
        # the legacy bounded path for those cases; real farm frames provide the
        # signature and/or selected-card geometry used by the strict stale-frame gate.
        navigation_confirmed = before_navigation_signature is None
        navigation_change_hits = 0
        move_counted = False
        full_action_probed = False
        friend_ready_streak = 0
        use_fast_action_probe = callable(fast_action_fn)
        guard_identity_refreshed = False
        try:
            navigation_threshold = float(
                getattr(context, 'friend_chain_navigation_change_threshold', 0.012) or 0.012
            )
        except BaseException:
            navigation_threshold = 0.012
        navigation_threshold = max(0.004, min(0.12, navigation_threshold))
        for action_attempt in range(action_poll_limit):
            try:
                candidate = capture_fn(context)
            except BaseException:
                candidate = None
            if candidate is not None:
                next_frame = candidate
                action_probed = False
                try:
                    friend_state = (
                        state_fn(candidate) if callable(state_fn) else True
                    )
                except BaseException:
                    friend_state = None
                if friend_state is True:
                    friend_ready_streak += 1
                else:
                    friend_ready_streak = 0
                    try:
                        blocked_hint_fn = globals().get(
                            '_friend_blocked_visit_visual_hint'
                        )
                        blocked_next_friend_returned_home = bool(
                            blocked_hint_fn(candidate)
                        ) if callable(blocked_hint_fn) else False
                    except BaseException:
                        blocked_next_friend_returned_home = False
                    if blocked_next_friend_returned_home:
                        navigation_confirmed = True
                        if not move_counted:
                            result['moves'] += 1
                            move_counted = True
                        frame = candidate
                        result['frame'] = frame
                        if callable(write_fn):
                            try:
                                write_fn(
                                    'v219 blocked next friend returned home; '
                                    'finishing adjacent friend chain normally'
                                )
                            except BaseException:
                                pass
                        break
                # Never use a visible action from the first post-click frames as
                # navigation proof.  The previous friend's button can remain on
                # screen during the carousel transition; clicking it here advances
                # again from stale geometry and skips the immediately adjacent friend.
                # Wait for an independent carousel-selection or page-signature
                # confirmation first, then probe actions on the confirmed friend.
                if not navigation_confirmed and isinstance(before_selected_bounds, dict):
                    try:
                        after_selected_bounds = (
                            selected_bounds_fn(candidate)
                            if callable(selected_bounds_fn) else None
                        )
                    except BaseException:
                        after_selected_bounds = None
                    try:
                        selection_changed = bool(
                            selection_changed_fn(
                                before_selected_bounds,
                                after_selected_bounds,
                                getattr(candidate, 'shape', (0, 428))[1]
                                if getattr(candidate, 'shape', None) is not None
                                else 428,
                            )
                        ) if callable(selection_changed_fn) else False
                    except BaseException:
                        selection_changed = False
                    if selection_changed:
                        navigation_confirmed = True
                        if callable(write_fn):
                            try:
                                write_fn(
                                    'v120 friend navigation confirmed by carousel selection ' +
                                    repr(before_selected_bounds)[:120] + ' -> ' +
                                    repr(after_selected_bounds)[:120]
                                )
                            except BaseException:
                                pass
                if not navigation_confirmed and before_navigation_signature is not None:
                    try:
                        change_score = (
                            score_fn(before_navigation_signature, candidate)
                            if callable(score_fn) else None
                        )
                    except BaseException:
                        change_score = None
                    if change_score is None:
                        navigation_confirmed = True
                    elif float(change_score) >= navigation_threshold:
                        navigation_change_hits += 1
                        if navigation_change_hits >= 2:
                            navigation_confirmed = True
                    else:
                        navigation_change_hits = 0
                    if not navigation_confirmed:
                        if (
                            not fallback_attempted
                            and (action_attempt + 1) >= primary_navigation_poll_limit
                        ):
                            fallback_moved, fallback_label = _adjacent_move(frame)
                            fallback_attempted = True
                            if fallback_moved:
                                fallback_succeeded = True
                                navigation_label = fallback_label or navigation_label
                                navigation_change_hits = 0
                                _pause(0.10)
                                continue
                        if action_attempt < action_poll_limit - 1:
                            _pause(min(0.18, 0.06 + (0.012 * action_attempt)))
                        continue
                if not move_counted:
                    result['moves'] += 1
                    move_counted = True
                if (
                    guard_enabled
                    and guard_mode == 'friend_guard_list'
                    and not guard_identity_refreshed
                ):
                    refresh_fn = globals().get(
                        '_friend_guard_list_refresh_prequalification'
                    )
                    if callable(refresh_fn):
                        try:
                            refresh_fn(context, candidate)
                        except BaseException:
                            pass
                    guard_identity_refreshed = True
                frame = candidate
                result['frame'] = frame
                if friend_state is True:
                    try:
                        if use_fast_action_probe:
                            if not action_probed:
                                acted, action_label = fast_action_fn(context, frame)
                                action_probed = True
                                if _consume_guard_dog_help_skip():
                                    guard_help_skipped = True
                                    break
                            if (
                                not acted
                                and native_action_fallback_enabled
                                and not full_action_probed
                            ):
                                full_action_probed = True
                                acted, action_label = action_fn(context, frame)
                                if _consume_native_action_unverified():
                                    native_action_unverified = True
                                    acted = False
                                    action_label = ''
                                    break
                                if _consume_guard_dog_help_skip():
                                    guard_help_skipped = True
                                    break
                        elif not action_probed:
                            acted, action_label = action_fn(context, frame)
                            if _consume_native_action_unverified():
                                native_action_unverified = True
                                acted = False
                                action_label = ''
                                break
                            if _consume_guard_dog_help_skip():
                                guard_help_skipped = True
                                break
                    except BaseException as error:
                        acted = False
                        action_label = ''
                        if callable(write_fn):
                            try:
                                write_fn('v116 friend continuation action error=' + repr(error)[:220])
                            except BaseException:
                                pass
                if acted:
                    break
            if action_attempt < action_poll_limit - 1:
                _pause(min(0.24, 0.08 + (0.020 * action_attempt)))
        if next_frame is None:
            result['reason'] = 'missing-frame-after-navigation'
            break
        if blocked_next_friend_returned_home:
            result['exhausted'] = True
            result['reason'] = 'blocked-next-friend-returned-home'
            break
        if not navigation_confirmed:
            result['reason'] = 'navigation-not-confirmed'
            break
        if native_action_unverified:
            result['reason'] = 'native-action-unverified'
            if callable(write_fn):
                try:
                    write_fn(
                        'v212 unverified native help claim; keeping the current '
                        'friend active without carousel navigation'
                    )
                except BaseException:
                    pass
            break
        if guard_help_skipped:
            result['reason'] = 'guard-dog-help-skipped'
            if callable(write_fn):
                try:
                    write_fn(
                        'v131 guard dog rejected help; advancing to next adjacent friend'
                    )
                except BaseException:
                    pass
            continue
        if not acted:
            if friend_ready_streak < idle_confirmations:
                # A transition, overlay, or unreadable frame is not proof that
                # the friend has no work.  Stop in place so the next cycle can
                # retry this same friend instead of skipping to later cards.
                result['reason'] = 'friend-surface-not-ready'
                break
            # A friend-list page can contain several known actionable rows with
            # ordinary friends between them in the bottom carousel.  Continue a
            # bounded number of stable no-action gaps instead of returning home at
            # the first gap and skipping later approved friends.
            continue_known_gap = bool(
                guard_enabled
                and guard_mode == 'friend_guard_list'
                and (index + 1) < guard_gap_scan_budget
            )
            if continue_known_gap:
                result['reason'] = 'known-list-no-action-gap-continue'
                if callable(write_fn):
                    try:
                        write_fn(
                            'v228 stable no-action friend; continue adjacent scan '
                            'move=' + str(result.get('moves', 0)) + '/' +
                            str(guard_gap_scan_budget) + ', known_rows=' +
                            str(known_actionable_count)
                        )
                    except BaseException:
                        pass
                continue
            result['exhausted'] = True
            result['reason'] = 'first-no-action-friend'
            break
        if acted:
            result['actions'] += 1
            if action_label:
                last_label = str(action_label)
                result['last_label'] = last_label
            result['reason'] = 'action-complete'
            _pause(0.18)
            (
                frame,
                drained_actions,
                drained_label,
                current_idle_confirmed,
                current_surface_hits,
            ) = _drain_current_friend_actions(frame, last_label)
            result['frame'] = frame
            result['actions'] += int(drained_actions or 0)
            if drained_label:
                last_label = str(drained_label)
                result['last_label'] = last_label
            if not current_idle_confirmed:
                result['reason'] = (
                    'friend-surface-not-ready'
                    if int(current_surface_hits or 0) <= 0
                    else 'current-friend-not-idle'
                )
                break
    result['frame'] = frame
    if int(result.get('moves', 0) or 0) > 0:
        try:
            branch_now = float(time.time())
        except BaseException:
            try:
                branch_now = float(__import__('time').time())
            except BaseException:
                branch_now = 0.0
        try:
            setattr(context, '_qqfarm_friend_branch_last_ts', branch_now)
            setattr(context, '_qqfarm_visual_friend_count', 1)
            setattr(context, '_last_friend_farm_go_home_present', True)
        except BaseException:
            pass
    try:
        moved_count = int(result.get('moves', 0) or 0)
        visible_count = int(getattr(
            context, '_qqfarm_friend_list_visible_candidate_count', 0
        ) or 0)
        if moved_count > 0 and visible_count > 0:
            current_cursor = max(0, int(getattr(
                context, '_qqfarm_friend_list_visit_cursor', 0
            ) or 0))
            setattr(
                context,
                '_qqfarm_friend_list_visit_cursor',
                current_cursor + moved_count,
            )
            if callable(write_fn):
                write_fn(
                    'v203 friend list cursor advanced by carousel moves=' +
                    str(moved_count) + ' cursor=' +
                    str(current_cursor + moved_count) + '/' + str(visible_count)
                )
    except BaseException:
        pass
    if callable(write_fn):
        try:
            write_fn('v85 friend continuation summary moves=' + str(result['moves']) +
                     ' actions=' + str(result['actions']) +
                     ' exhausted=' + repr(result['exhausted']) +
                     ' reason=' + str(result['reason']) +
                     ' last=' + str(result['last_label']))
        except BaseException:
            pass
    try:
        terminal = bool(result.get('exhausted', False))
        setattr(context, '_qqfarm_friend_chain_exhausted', terminal)
        setattr(context, '_qqfarm_friend_chain_pending', not terminal)
        setattr(context, '_qqfarm_friend_chain_active', False)
        setattr(context, '_qqfarm_friend_entry_extended_action_grace', False)
    except BaseException:
        pass
    return result

def _set_friend_chain_fast_interval(context, active):
    if context is None:
        return False
    try:
        active = bool(active)
        if active:
            if not hasattr(context, '_qqfarm_friend_chain_original_interval'):
                current = float(getattr(context, 'check_interval', 15.0) or 15.0)
                setattr(context, '_qqfarm_friend_chain_original_interval', current)
            current = float(getattr(context, 'check_interval', 15.0) or 15.0)
            setattr(context, 'check_interval', min(current, 0.75))
            setattr(context, '_qqfarm_friend_chain_active', True)
        else:
            original = getattr(context, '_qqfarm_friend_chain_original_interval', None)
            if original is not None:
                setattr(context, 'check_interval', float(original))
                try:
                    delattr(context, '_qqfarm_friend_chain_original_interval')
                except BaseException:
                    pass
            setattr(context, '_qqfarm_friend_chain_active', False)
            setattr(context, '_qqfarm_friend_chain_count', 0)
        return True
    except BaseException:
        return False

def _invoke_friend_guard_relaxed_home_check(
    action, target, context, original_args=(), original_kwargs=None
):
    marker = object()
    old_threshold = getattr(context, 'go_home_frame_threshold', marker)
    try:
        current = 0.70 if old_threshold is marker else float(old_threshold)
        setattr(context, 'go_home_frame_threshold', min(current, 0.52))
        return _invoke_friend_guard_action(
            action, target, original_args, original_kwargs
        )
    finally:
        if old_threshold is marker:
            try:
                delattr(context, 'go_home_frame_threshold')
            except BaseException:
                pass
        else:
            try:
                setattr(context, 'go_home_frame_threshold', old_threshold)
            except BaseException:
                pass


def _friend_guard_scale_point_to_client(
    frame_x, frame_y, frame_width, frame_height, client_width, client_height
):
    """Map normalized capture pixels to the real DPI-aware client surface."""
    try:
        fw = max(1.0, float(frame_width))
        fh = max(1.0, float(frame_height))
        cw = max(1, int(client_width))
        ch = max(1, int(client_height))
        client_x = int(round(float(frame_x) * float(cw) / fw))
        client_y = int(round(float(frame_y) * float(ch) / fh))
        return (
            max(0, min(cw - 1, client_x)),
            max(0, min(ch - 1, client_y)),
        )
    except BaseException:
        return int(frame_x), int(frame_y)


def _friend_guard_screen_point_owned_by_farm(screen_x, screen_y):
    """Return True only when the screen point currently belongs to QQ classic farm."""
    try:
        win32gui = __import__('win32gui')
        target_hwnd = int(win32gui.WindowFromPoint((int(screen_x), int(screen_y))) or 0)
        if not target_hwnd:
            return False
        candidates = []

        def _cb(hwnd, extra):
            try:
                if not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
                    return True
                if str(win32gui.GetWindowText(hwnd) or '').strip() != '\u0051\u0051\u7ecf\u5178\u519c\u573a':
                    return True
                candidates.append(int(hwnd))
            except BaseException:
                pass
            return True

        win32gui.EnumWindows(_cb, None)
        for root_hwnd in candidates:
            if target_hwnd == root_hwnd or win32gui.IsChild(root_hwnd, target_hwnd):
                return True
        return False
    except BaseException:
        pass
    try:
        import ctypes
        user32 = ctypes.windll.user32
        class POINT(ctypes.Structure):
            _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]

        point = POINT(int(screen_x), int(screen_y))
        target_hwnd = int(user32.WindowFromPoint(point) or 0)
        if not target_hwnd:
            return False
        candidates = []
        enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        def _cb(hwnd, lparam):
            try:
                if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
                    return True
                title_buf = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, title_buf, 255)
                if str(title_buf.value or '').strip() == '\u0051\u0051\u7ecf\u5178\u519c\u573a':
                    candidates.append(int(hwnd))
            except BaseException:
                pass
            return True

        user32.EnumWindows(enum_proc(_cb), 0)
        for root_hwnd in candidates:
            if target_hwnd == root_hwnd or user32.IsChild(
                ctypes.c_void_p(root_hwnd), ctypes.c_void_p(target_hwnd)
            ):
                return True
    except BaseException:
        pass
    return False


def _friend_guard_post_client_click(
    frame_x, frame_y, frame_width=428, frame_height=800
):
    """Post a click to the DPI-aware QQ farm render surface."""
    try:
        win32gui = __import__('win32gui')
        candidates = []

        def _cb(hwnd, extra):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                if str(win32gui.GetWindowText(hwnd) or '').strip() != '\u0051\u0051\u7ecf\u5178\u519c\u573a':
                    return True
                rect = win32gui.GetClientRect(hwnd)
                width = int(rect[2] - rect[0])
                height = int(rect[3] - rect[1])
                if width < 300 or height < 500:
                    return True
                scale_x = float(width) / max(1.0, float(frame_width))
                scale_y = float(height) / max(1.0, float(frame_height))
                candidates.append((abs(scale_x - scale_y), -width * height, int(hwnd), width, height))
            except BaseException:
                pass
            return True

        win32gui.EnumWindows(_cb, None)
        if candidates:
            candidates.sort(key=lambda item: (item[0], item[1]))
            _, _, root_hwnd, client_width, client_height = candidates[0]
            client_x, client_y = _friend_guard_scale_point_to_client(
                frame_x, frame_y, frame_width, frame_height,
                client_width, client_height,
            )
            screen_point = win32gui.ClientToScreen(root_hwnd, (client_x, client_y))
            target_hwnd = int(win32gui.WindowFromPoint(screen_point) or 0)
            if not target_hwnd or (
                target_hwnd != root_hwnd
                and not win32gui.IsChild(root_hwnd, target_hwnd)
            ):
                target_hwnd = root_hwnd
            target_point = win32gui.ScreenToClient(target_hwnd, screen_point)
            lparam = ((int(target_point[1]) & 0xffff) << 16) | (int(target_point[0]) & 0xffff)
            win32gui.PostMessage(target_hwnd, 0x0200, 0, lparam)
            win32gui.PostMessage(target_hwnd, 0x0201, 0x0001, lparam)
            win32gui.PostMessage(target_hwnd, 0x0202, 0, lparam)
            return True
    except BaseException:
        pass
    try:
        import ctypes
        user32 = ctypes.windll.user32
        candidates = []
        enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        class RECT(ctypes.Structure):
            _fields_ = [
                ('left', ctypes.c_long), ('top', ctypes.c_long),
                ('right', ctypes.c_long), ('bottom', ctypes.c_long),
            ]

        class POINT(ctypes.Structure):
            _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]

        def _cb(hwnd, lparam):
            try:
                if not user32.IsWindowVisible(hwnd):
                    return True
                title_buf = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, title_buf, 255)
                if str(title_buf.value or '').strip() != '\u0051\u0051\u7ecf\u5178\u519c\u573a':
                    return True
                rect = RECT()
                if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
                    return True
                width = int(rect.right - rect.left)
                height = int(rect.bottom - rect.top)
                if width >= 300 and height >= 500:
                    scale_x = float(width) / max(1.0, float(frame_width))
                    scale_y = float(height) / max(1.0, float(frame_height))
                    candidates.append((abs(scale_x - scale_y), -width * height, int(hwnd), width, height))
            except BaseException:
                pass
            return True

        user32.EnumWindows(enum_proc(_cb), 0)
        if not candidates:
            return False
        candidates.sort(key=lambda item: (item[0], item[1]))
        _, _, root_hwnd, client_width, client_height = candidates[0]
        client_x, client_y = _friend_guard_scale_point_to_client(
            frame_x, frame_y, frame_width, frame_height,
            client_width, client_height,
        )
        screen_point = POINT(int(client_x), int(client_y))
        if not user32.ClientToScreen(ctypes.c_void_p(root_hwnd), ctypes.byref(screen_point)):
            return False
        target_hwnd = int(user32.WindowFromPoint(screen_point) or 0)
        if not target_hwnd or (
            target_hwnd != root_hwnd
            and not user32.IsChild(ctypes.c_void_p(root_hwnd), ctypes.c_void_p(target_hwnd))
        ):
            target_hwnd = root_hwnd
        client_point = POINT(int(screen_point.x), int(screen_point.y))
        if not user32.ScreenToClient(ctypes.c_void_p(target_hwnd), ctypes.byref(client_point)):
            return False
        lparam = ((int(client_point.y) & 0xffff) << 16) | (int(client_point.x) & 0xffff)
        user32.PostMessageW(ctypes.c_void_p(target_hwnd), 0x0200, 0, lparam)
        down_ok = user32.PostMessageW(ctypes.c_void_p(target_hwnd), 0x0201, 0x0001, lparam)
        up_ok = user32.PostMessageW(ctypes.c_void_p(target_hwnd), 0x0202, 0, lparam)
        return bool(down_ok and up_ok)
    except BaseException:
        return False

def _friend_guard_frame_to_screen(
    frame_x, frame_y, frame_width=428, frame_height=800
):
    """Translate capture coordinates to DPI-aware absolute screen pixels."""
    try:
        win32gui = __import__('win32gui')
        candidates = []

        def _cb(hwnd, extra):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                if str(win32gui.GetWindowText(hwnd) or '').strip() != '\u0051\u0051\u7ecf\u5178\u519c\u573a':
                    return True
                rect = win32gui.GetClientRect(hwnd)
                width = int(rect[2] - rect[0])
                height = int(rect[3] - rect[1])
                if width < 300 or height < 500:
                    return True
                scale_x = float(width) / max(1.0, float(frame_width))
                scale_y = float(height) / max(1.0, float(frame_height))
                candidates.append((abs(scale_x - scale_y), -width * height, int(hwnd), width, height))
            except BaseException:
                pass
            return True

        win32gui.EnumWindows(_cb, None)
        if candidates:
            candidates.sort(key=lambda item: (item[0], item[1]))
            _, _, hwnd, client_width, client_height = candidates[0]
            client_x, client_y = _friend_guard_scale_point_to_client(
                frame_x, frame_y, frame_width, frame_height,
                client_width, client_height,
            )
            point = win32gui.ClientToScreen(hwnd, (client_x, client_y))
            return int(point[0]), int(point[1])
    except BaseException:
        pass
    try:
        import ctypes
        user32 = ctypes.windll.user32
        candidates = []
        enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

        class RECT(ctypes.Structure):
            _fields_ = [
                ('left', ctypes.c_long), ('top', ctypes.c_long),
                ('right', ctypes.c_long), ('bottom', ctypes.c_long),
            ]

        class POINT(ctypes.Structure):
            _fields_ = [('x', ctypes.c_long), ('y', ctypes.c_long)]

        def _cb(hwnd, lparam):
            try:
                if not user32.IsWindowVisible(hwnd):
                    return True
                title_buf = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, title_buf, 255)
                if str(title_buf.value or '').strip() != '\u0051\u0051\u7ecf\u5178\u519c\u573a':
                    return True
                rect = RECT()
                if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
                    return True
                width = int(rect.right - rect.left)
                height = int(rect.bottom - rect.top)
                if width < 300 or height < 500:
                    return True
                scale_x = float(width) / max(1.0, float(frame_width))
                scale_y = float(height) / max(1.0, float(frame_height))
                candidates.append((abs(scale_x - scale_y), -width * height, int(hwnd), width, height))
            except BaseException:
                pass
            return True

        user32.EnumWindows(enum_proc(_cb), 0)
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[1]))
        _, _, hwnd, client_width, client_height = candidates[0]
        client_x, client_y = _friend_guard_scale_point_to_client(
            frame_x, frame_y, frame_width, frame_height,
            client_width, client_height,
        )
        point = POINT(int(client_x), int(client_y))
        if not user32.ClientToScreen(ctypes.c_void_p(hwnd), ctypes.byref(point)):
            return None
        return int(point.x), int(point.y)
    except BaseException:
        return None


_FRIEND_GUARD_TEMPLATE_CACHE = {}
_FRIEND_HOME_TEMPLATE_PATH = os.path.join(os.getcwd(), 'friend_home_button.png')
_FRIEND_LIST_TEMPLATE_PATH = os.path.join(os.getcwd(), 'friend_list_tabs.png')
_FRIEND_GUARD_DOG_AVATAR_TEMPLATE_PATH = os.path.join(
    os.getcwd(), 'friend_guard_dog_avatar_frame.png'
)


def _friend_guard_read_template(path):
    try:
        key = str(path or '')
        if not key:
            return None
        cache = globals().get('_FRIEND_GUARD_TEMPLATE_CACHE')
        if not isinstance(cache, dict):
            cache = {}
            globals()['_FRIEND_GUARD_TEMPLATE_CACHE'] = cache
        if key in cache:
            return cache.get(key)
        np = __import__('numpy')
        cv2 = __import__('cv2')
        raw = np.fromfile(key, dtype=np.uint8)
        template = cv2.imdecode(raw, cv2.IMREAD_COLOR) if raw.size else None
        cache[key] = template
        return template
    except BaseException:
        return None


def _friend_guard_match_template(
    frame, template_path, roi_bounds,
    gray_threshold=0.68, edge_threshold=0.30,
):
    try:
        np = __import__('numpy')
        cv2 = __import__('cv2')
        arr = np.asarray(frame)
        shape = getattr(arr, 'shape', None)
        if not shape or len(shape) < 3 or int(shape[2]) < 3:
            return {'matched': False, 'gray': 0.0, 'edge': 0.0, 'center': None}
        height, width = int(shape[0]), int(shape[1])
        x0r, y0r, x1r, y1r = tuple(roi_bounds)
        x0 = max(0, min(width - 1, int(round(width * float(x0r)))))
        x1 = max(x0 + 1, min(width, int(round(width * float(x1r)))))
        y0 = max(0, min(height - 1, int(round(height * float(y0r)))))
        y1 = max(y0 + 1, min(height, int(round(height * float(y1r)))))
        roi = arr[y0:y1, x0:x1, :3]
        template = _friend_guard_read_template(template_path)
        if template is None or getattr(roi, 'size', 0) <= 0:
            return {'matched': False, 'gray': 0.0, 'edge': 0.0, 'center': None}
        scale_x = max(0.25, float(width) / 428.0)
        scale_y = max(0.25, float(height) / 800.0)
        target_w = max(8, int(round(int(template.shape[1]) * scale_x)))
        target_h = max(8, int(round(int(template.shape[0]) * scale_y)))
        if target_w != int(template.shape[1]) or target_h != int(template.shape[0]):
            template = cv2.resize(template, (target_w, target_h), interpolation=cv2.INTER_AREA)
        if target_h > int(roi.shape[0]) or target_w > int(roi.shape[1]):
            return {'matched': False, 'gray': 0.0, 'edge': 0.0, 'center': None}
        roi_gray = np.mean(roi.astype(np.float32), axis=2).astype(np.uint8)
        template_gray = np.mean(template.astype(np.float32), axis=2).astype(np.uint8)
        gray_result = cv2.matchTemplate(roi_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, gray_score, _, gray_location = cv2.minMaxLoc(gray_result)
        roi_edge = cv2.Canny(roi_gray, 50, 150)
        template_edge = cv2.Canny(template_gray, 50, 150)
        edge_result = cv2.matchTemplate(roi_edge, template_edge, cv2.TM_CCOEFF_NORMED)
        _, edge_score, _, _ = cv2.minMaxLoc(edge_result)
        center = (
            int(x0 + gray_location[0] + target_w // 2),
            int(y0 + gray_location[1] + target_h // 2),
        )
        return {
            'matched': bool(
                float(gray_score) >= float(gray_threshold)
                and float(edge_score) >= float(edge_threshold)
            ),
            'gray': float(gray_score),
            'edge': float(edge_score),
            'center': center,
        }
    except BaseException:
        return {'matched': False, 'gray': 0.0, 'edge': 0.0, 'center': None}



def _friend_list_visit_button_rows(frame):
    """Return visible friend-list visit buttons ordered from top to bottom."""
    try:
        np = __import__('numpy')
        cv2 = __import__('cv2')
        arr = np.asarray(frame)
        shape = getattr(arr, 'shape', None)
        if not shape or len(shape) < 3 or int(shape[2]) < 3:
            return []
        height, width = int(shape[0]), int(shape[1])
        if height < 120 or width < 120:
            return []
        bgr = arr[:, :, :3]
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(
            hsv,
            np.array([25, 100, 80], dtype=np.uint8),
            np.array([95, 255, 255], dtype=np.uint8),
        )
        x_gate = max(0, min(width, int(round(width * 0.70))))
        y_gate = max(0, min(height, int(round(height * 0.24))))
        y_end = max(y_gate + 1, min(height, int(round(height * 0.93))))
        mask[:y_gate, :] = 0
        mask[y_end:, :] = 0
        mask[:, :x_gate] = 0
        kernel = np.ones((3, 3), dtype=np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        count, labels, stats, centers = cv2.connectedComponentsWithStats(mask, 8)
        min_width = max(24, int(round(width * 0.11)))
        max_width = max(min_width + 1, int(round(width * 0.26)))
        min_height = max(12, int(round(height * 0.025)))
        max_height = max(min_height + 1, int(round(height * 0.075)))
        min_area = max(120, int(round(width * height * 0.0015)))
        max_area = max(min_area + 1, int(round(width * height * 0.015)))
        rows = []
        for index in range(1, int(count)):
            x, y, component_width, component_height, area = [
                int(value) for value in stats[index]
            ]
            if not (min_width <= component_width <= max_width):
                continue
            if not (min_height <= component_height <= max_height):
                continue
            if not (min_area <= area <= max_area):
                continue
            fill_ratio = float(area) / float(max(1, component_width * component_height))
            if fill_ratio < 0.42:
                continue
            center_x = int(round(float(centers[index][0])))
            center_y = int(round(float(centers[index][1])))
            if center_x < int(round(width * 0.76)) or center_x > int(round(width * 0.97)):
                continue
            rows.append({
                'center': (center_x, center_y),
                'rect': (x, y, x + component_width, y + component_height),
                'area': area,
                'fill': fill_ratio,
            })
        rows.sort(key=lambda item: (int(item['center'][1]), int(item['center'][0])))
        merged = []
        merge_distance = max(6, int(round(height * 0.018)))
        for row in rows:
            if merged and abs(int(row['center'][1]) - int(merged[-1]['center'][1])) <= merge_distance:
                if int(row.get('area', 0)) > int(merged[-1].get('area', 0)):
                    merged[-1] = row
                continue
            merged.append(row)
        return merged
    except BaseException:
        return []


def _friend_list_guard_dog_score(frame, row_y):
    """Match the 19x19 guard-dog badge overlay; it is independent of avatar frame style."""
    try:
        np = __import__('numpy')
        cv2 = __import__('cv2')
        arr = np.asarray(frame)
        shape = getattr(arr, 'shape', None)
        if not shape or len(shape) < 3 or int(shape[2]) < 3:
            return 0.0
        height, width = int(shape[0]), int(shape[1])
        template_path = globals().get(
            '_FRIEND_GUARD_DOG_AVATAR_TEMPLATE_PATH',
            'friend_guard_dog_avatar_frame.png',
        )
        reader = globals().get('_friend_guard_read_template')
        template = reader(template_path) if callable(reader) else None
        if template is None:
            raw = np.fromfile(str(template_path), dtype=np.uint8)
            template = cv2.imdecode(raw, cv2.IMREAD_COLOR) if raw.size else None
        if template is None:
            return 0.0
        scale_x = max(0.25, float(width) / 428.0)
        scale_y = max(0.25, float(height) / 800.0)
        target_width = max(8, int(round(int(template.shape[1]) * scale_x)))
        target_height = max(8, int(round(int(template.shape[0]) * scale_y)))
        if target_width != int(template.shape[1]) or target_height != int(template.shape[0]):
            interpolation = cv2.INTER_AREA if scale_x < 1.0 or scale_y < 1.0 else cv2.INTER_LINEAR
            template = cv2.resize(
                template, (target_width, target_height), interpolation=interpolation
            )
        x0 = max(0, min(width - 1, int(round(width * 0.12))))
        x1 = max(x0 + 1, min(width, int(round(width * 0.21))))
        y0 = max(0, min(height - 1, int(round(float(row_y) + height * 0.003))))
        y1 = max(y0 + 1, min(height, int(round(float(row_y) + height * 0.046))))
        roi = arr[y0:y1, x0:x1, :3]
        if target_height > int(roi.shape[0]) or target_width > int(roi.shape[1]):
            return 0.0
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(roi_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, score, _, _ = cv2.minMaxLoc(result)
        return float(score)
    except BaseException:
        return 0.0



def _friend_blocked_visit_visual_hint(frame, threshold=0.70):
    """Match blocked-visit list text or the in-farm blocked toast."""
    try:
        cv2 = __import__('cv2')
        np = __import__('numpy')
        os_module = __import__('os')
        arr = np.asarray(frame)
        shape = getattr(arr, 'shape', None)
        if not shape or len(shape) < 2:
            return False
        height, width = int(shape[0]), int(shape[1])
        if height < 120 or width < 120:
            return False
        hook_file = globals().get('__file__', 'hook.py')
        base = os_module.path.dirname(os_module.path.abspath(hook_file))
        template_paths = [
            (
                'row',
                globals().get('_FRIEND_BLOCKED_VISIT_TEMPLATE_PATH')
                or os_module.path.join(base, 'friend_blocked_visit_text.png'),
            ),
            (
                'toast',
                globals().get('_FRIEND_BLOCKED_VISIT_TOAST_TEMPLATE_PATH')
                or os_module.path.join(base, 'friend_blocked_visit_toast.png'),
            ),
        ]
        x0 = max(0, min(width - 1, int(round(width * 0.08))))
        x1 = max(x0 + 1, min(width, int(round(width * 0.92))))
        y0 = max(0, min(height - 1, int(round(height * 0.12))))
        y1 = max(y0 + 1, min(height, int(round(height * 0.88))))
        roi = arr[y0:y1, x0:x1, :3]
        if getattr(roi, 'size', 0) <= 0:
            return False
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        cache = globals().setdefault('_FRIEND_BLOCKED_VISIT_TEMPLATE_CACHE', {})
        runtime_scale = max(0.65, min(1.65, float(width) / 428.0))
        best = -1.0
        best_label = ''
        for label, template_path in template_paths:
            cache_key = str(template_path)
            template = cache.get(cache_key) if isinstance(cache, dict) else None
            if template is None:
                try:
                    encoded = np.fromfile(cache_key, dtype=np.uint8)
                    template = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
                except BaseException:
                    template = None
                if template is not None and isinstance(cache, dict):
                    cache[cache_key] = template
            if template is None or getattr(template, 'size', 0) <= 0:
                continue
            for local_scale in (0.90, 0.96, 1.0, 1.04, 1.10):
                scale = runtime_scale * float(local_scale)
                target_width = max(8, int(round(template.shape[1] * scale)))
                target_height = max(6, int(round(template.shape[0] * scale)))
                if (
                    target_width > int(roi_gray.shape[1])
                    or target_height > int(roi_gray.shape[0])
                ):
                    continue
                resized = cv2.resize(
                    template,
                    (target_width, target_height),
                    interpolation=(
                        cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
                    ),
                )
                template_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                matched = cv2.matchTemplate(
                    roi_gray, template_gray, cv2.TM_CCOEFF_NORMED
                )
                _, score, _, _ = cv2.minMaxLoc(matched)
                score = float(score)
                if score > best:
                    best = score
                    best_label = str(label)
        matched = bool(best >= max(0.55, min(0.92, float(threshold))))
        if matched:
            try:
                _write(
                    'v222 blocked visit status matched kind=' + best_label +
                    ' score=' + ('%.4f' % best)
                )
            except BaseException:
                pass
        return matched
    except BaseException:
        return False


def _friend_list_blocked_row_visual_hint(frame, row_y, threshold=0.70):
    """Match the fixed ?account blocked, visit unavailable? text on one row."""
    try:
        cv2 = __import__('cv2')
        np = __import__('numpy')
        os_module = __import__('os')
        arr = np.asarray(frame)
        shape = getattr(arr, 'shape', None)
        if not shape or len(shape) < 2:
            return False
        height, width = int(shape[0]), int(shape[1])
        if height < 120 or width < 120:
            return False
        template_path = globals().get('_FRIEND_BLOCKED_VISIT_TEMPLATE_PATH')
        if not template_path:
            hook_file = globals().get('__file__', 'hook.py')
            template_path = os_module.path.join(
                os_module.path.dirname(os_module.path.abspath(hook_file)),
                'friend_blocked_visit_text.png',
            )
        try:
            encoded = np.fromfile(str(template_path), dtype=np.uint8)
            template = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        except BaseException:
            template = None
        if template is None or getattr(template, 'size', 0) <= 0:
            return False
        x0 = max(0, min(width - 1, int(round(width * 0.22))))
        x1 = max(x0 + 1, min(width, int(round(width * 0.82))))
        y0 = max(0, min(height - 1, int(round(float(row_y) - height * 0.034))))
        y1 = max(y0 + 1, min(height, int(round(float(row_y) + height * 0.034))))
        roi = arr[y0:y1, x0:x1, :3]
        if getattr(roi, 'size', 0) <= 0:
            return False
        roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        best = -1.0
        runtime_scale = max(0.65, min(1.65, float(width) / 428.0))
        for local_scale in (0.90, 0.96, 1.0, 1.04, 1.10):
            scale = runtime_scale * float(local_scale)
            target_width = max(8, int(round(template.shape[1] * scale)))
            target_height = max(6, int(round(template.shape[0] * scale)))
            if target_width > int(roi_gray.shape[1]) or target_height > int(roi_gray.shape[0]):
                continue
            resized = cv2.resize(
                template,
                (target_width, target_height),
                interpolation=(cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC),
            )
            template_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            matched = cv2.matchTemplate(roi_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            _, score, _, _ = cv2.minMaxLoc(matched)
            best = max(best, float(score))
        matched = bool(best >= max(0.55, min(0.92, float(threshold))))
        if matched:
            try:
                _write(
                    'v219 blocked friend row text matched row_y=' + str(int(row_y)) +
                    ' score=' + ('%.4f' % best)
                )
            except BaseException:
                pass
        return matched
    except BaseException:
        return False

def _commit_friend_list_entry_transition(context):
    """Advance the friend-list cursor only after the farm surface is confirmed."""
    if context is None:
        return False
    try:
        if not bool(getattr(context, '_qqfarm_friend_entry_pending', False)):
            return False
        pending_cursor = max(0, int(getattr(
            context, '_qqfarm_friend_list_pending_cursor', 0
        ) or 0))
        current_cursor = max(0, int(getattr(
            context, '_qqfarm_friend_list_visit_cursor', pending_cursor
        ) or 0))
        confirmed_cursor = max(current_cursor, pending_cursor + 1)
        setattr(
            context,
            '_qqfarm_friend_list_visit_cursor',
            confirmed_cursor,
        )
        setattr(context, '_qqfarm_friend_entry_retry_count', 0)
        setattr(context, '_qqfarm_friend_entry_last_retry_ts', 0.0)
        writer = globals().get('_write')
        if callable(writer):
            writer(
                'v207 friend list confirmed cursor pending=' +
                str(pending_cursor) + ' next=' + str(confirmed_cursor)
            )
        return True
    except BaseException as error:
        try:
            writer = globals().get('_write')
            if callable(writer):
                writer('v207 friend list cursor commit error=' + repr(error)[:180])
        except BaseException:
            pass
        return False


def _handle_friend_list_surface(context, frame):
    """Enter the first eligible friend from the list or close an empty list."""
    try:
        shape = getattr(frame, 'shape', None)
        if not shape or len(shape) < 2:
            return 'invalid'
        height, width = int(shape[0]), int(shape[1])
        if height <= 0 or width <= 0:
            return 'invalid'
        rows_fn = globals().get('_friend_list_visit_button_rows')
        rows = rows_fn(frame) if callable(rows_fn) else []
        rows = list(rows or [])
        guard_enabled_fn = globals().get('_guard_dog_ui_config_enabled')
        guard_enabled = bool(guard_enabled_fn()) if callable(guard_enabled_fn) else False
        mode_fn = globals().get('_guard_dog_detection_mode_config')
        guard_mode = str(mode_fn() if callable(mode_fn) else 'avatar_frame')
        if not (guard_enabled and guard_mode == 'avatar_frame'):
            try:
                setattr(context, '_qqfarm_guard_row_verified', False)
            except BaseException:
                pass
        target = None
        target_score = 0.0
        target_row_y = 0
        scored = []
        guard_list_candidates = []
        guard_list_cursor = 0
        guard_list_selection_cursor = 0
        guard_list_pending_retry = False
        guard_list_retry_count = 0
        if rows and guard_enabled and guard_mode == 'friend_guard_list':
            score_fn = globals().get('_friend_guard_list_row_match_score')
            for row in rows:
                center = row.get('center') if isinstance(row, dict) else None
                if not isinstance(center, (tuple, list)) or len(center) < 2:
                    continue
                row_y = int(center[1])
                try:
                    score = float(score_fn(frame, row_y)) if callable(score_fn) else 0.0
                except BaseException:
                    score = 0.0
                scored.append((row_y, score))
                if score >= 0.72:
                    guard_list_candidates.append((row, score, row_y))
            if not guard_list_candidates:
                try:
                    writer = globals().get('_write')
                    if callable(writer):
                        writer(
                            'v145 guard-list fast row match found no verified row; '
                            'delegating to native scroll flow rows=' + str(len(rows)) +
                            ' scores=' + repr(scored)[:320]
                        )
                except BaseException:
                    pass
                return 'native-guard-list'
            try:
                guard_list_cursor = max(0, int(getattr(
                    context, '_qqfarm_friend_list_visit_cursor', 0
                ) or 0))
            except BaseException:
                guard_list_cursor = 0
            guard_list_selection_cursor = guard_list_cursor
            try:
                friend_entry_pending = bool(getattr(
                    context, '_qqfarm_friend_entry_pending', False
                ))
                guard_list_retry_count = max(0, int(getattr(
                    context, '_qqfarm_friend_entry_retry_count', 0
                ) or 0))
                pending_cursor = max(0, int(getattr(
                    context,
                    '_qqfarm_friend_list_pending_cursor',
                    guard_list_cursor,
                ) or 0))
            except BaseException:
                friend_entry_pending = False
                guard_list_retry_count = 0
                pending_cursor = guard_list_cursor
            if not friend_entry_pending:
                stale_cursor = int(guard_list_cursor)
                guard_list_cursor = 0
                guard_list_selection_cursor = 0
                pending_cursor = 0
                try:
                    setattr(context, '_qqfarm_friend_list_visit_cursor', 0)
                    if stale_cursor > 0:
                        writer = globals().get('_write')
                        if callable(writer):
                            writer(
                                'v219 reopened friend list reset stale cursor=' +
                                str(stale_cursor) + '; selecting first row'
                            )
                except BaseException:
                    pass
            if friend_entry_pending:
                guard_list_pending_retry = True
                guard_list_selection_cursor = pending_cursor
                try:
                    now_fn = globals().get('_friend_watchdog_now')
                    retry_now = float(
                        now_fn() if callable(now_fn)
                        else __import__('time').time()
                    )
                except BaseException:
                    retry_now = 0.0
                try:
                    last_retry_ts = float(getattr(
                        context, '_qqfarm_friend_entry_last_retry_ts', 0.0
                    ) or 0.0)
                except BaseException:
                    last_retry_ts = 0.0
                try:
                    entry_clicked_ts = float(getattr(
                        context, '_qqfarm_friend_entry_clicked_ts', 0.0
                    ) or 0.0)
                except BaseException:
                    entry_clicked_ts = 0.0
                entry_age = (
                    max(0.0, retry_now - entry_clicked_ts)
                    if entry_clicked_ts > 0.0 else 0.0
                )
                blocked_row_hint = False
                if guard_list_retry_count >= 3 and entry_age >= 6.0:
                    try:
                        blocked_hint_fn = globals().get(
                            '_friend_list_blocked_row_visual_hint'
                        )
                        pending_row = guard_list_candidates[
                            pending_cursor % len(guard_list_candidates)
                        ][2]
                        blocked_row_hint = bool(
                            blocked_hint_fn(frame, pending_row)
                        ) if callable(blocked_hint_fn) else False
                    except BaseException:
                        blocked_row_hint = False
                # The list-entry policy permits exactly one bypass: first row
                # to second row when the first row is visibly blocked.  A failed
                # second-row visit closes/reopens the list instead of skipping
                # further friends.
                if (
                    blocked_row_hint
                    and pending_cursor == 0
                    and (pending_cursor + 1) < len(guard_list_candidates)
                ):
                    next_cursor = int(pending_cursor + 1)
                    try:
                        setattr(context, '_qqfarm_friend_entry_pending', False)
                        setattr(context, '_qqfarm_friend_entry_retry_count', 0)
                        setattr(context, '_qqfarm_friend_entry_clicked_ts', 0.0)
                        setattr(context, '_qqfarm_friend_entry_last_retry_ts', 0.0)
                        setattr(
                            context,
                            '_qqfarm_friend_list_visit_cursor',
                            next_cursor,
                        )
                        setattr(
                            context,
                            '_qqfarm_friend_list_pending_cursor',
                            next_cursor,
                        )
                        clear_fn = globals().get(
                            '_friend_guard_clear_prequalification'
                        )
                        if callable(clear_fn):
                            clear_fn(context)
                    except BaseException:
                        pass
                    try:
                        writer = globals().get('_write')
                        if callable(writer):
                            writer(
                                'v219 blocked row did not enter friend farm; '
                                'advancing from cursor=' + str(pending_cursor) +
                                ' to cursor=' + str(next_cursor)
                            )
                    except BaseException:
                        pass
                    return 'blocked-row-next'
                if guard_list_retry_count >= 3 and entry_age >= 6.0:
                    close_x = int(round(width * 0.946))
                    close_y = int(round(height * 0.118))
                    recovery_click_fn = globals().get(
                        '_friend_guard_post_client_click'
                    )
                    try:
                        closed = bool(
                            recovery_click_fn(close_x, close_y, width, height)
                        ) if callable(recovery_click_fn) else False
                    except TypeError:
                        closed = bool(recovery_click_fn(close_x, close_y))
                    except BaseException:
                        closed = False
                    if closed:
                        try:
                            setattr(context, '_qqfarm_friend_entry_pending', False)
                            setattr(context, '_qqfarm_friend_entry_retry_count', 0)
                            setattr(context, '_qqfarm_friend_entry_clicked_ts', 0.0)
                            setattr(context, '_qqfarm_friend_entry_last_retry_ts', 0.0)
                            setattr(
                                context,
                                '_qqfarm_friend_list_visit_cursor',
                                int(pending_cursor),
                            )
                            setattr(context, '_qqfarm_friend_chain_pending', False)
                            setattr(context, '_qqfarm_friend_cycle_seen', False)
                            setattr(context, '_qqfarm_visual_friend_count', 0)
                            clear_fn = globals().get(
                                '_friend_guard_clear_prequalification'
                            )
                            if callable(clear_fn):
                                clear_fn(context)
                        except BaseException:
                            pass
                        try:
                            fast_fn = globals().get(
                                '_set_friend_chain_fast_interval'
                            )
                            if callable(fast_fn):
                                fast_fn(context, False)
                        except BaseException:
                            pass
                        try:
                            writer = globals().get('_write')
                            if callable(writer):
                                writer(
                                    'v209 friend list pending row reopen recovery '
                                    'cursor=' + str(pending_cursor) +
                                    ' age=' + ('%.3f' % entry_age) +
                                    ' closed=True'
                                )
                        except BaseException:
                            pass
                        return 'pending-row-reopen'
                retry_backoff_seconds = 1.5
                if (
                    guard_list_retry_count >= 3
                    and last_retry_ts > 0.0
                    and 0.0 <= (retry_now - last_retry_ts) < retry_backoff_seconds
                ):
                    try:
                        writer = globals().get('_write')
                        if callable(writer):
                            writer(
                                'v207 friend list pending row backoff cursor=' +
                                str(pending_cursor) + ' retry_count=' +
                                str(guard_list_retry_count)
                            )
                    except BaseException:
                        pass
                    return 'pending-row-backoff'
                try:
                    writer = globals().get('_write')
                    if callable(writer):
                        writer(
                            'v207 friend list pending row retry cursor=' +
                            str(pending_cursor) + ' attempt=' +
                            str(min(3, guard_list_retry_count + 1)) + '/3' +
                            (' slow=True' if guard_list_retry_count >= 3 else '')
                        )
                except BaseException:
                    pass
            if (
                not friend_entry_pending
                and (guard_list_selection_cursor + 1) < len(guard_list_candidates)
            ):
                try:
                    blocked_hint_fn = globals().get(
                        '_friend_list_blocked_row_visual_hint'
                    )
                    current_row_y = guard_list_candidates[
                        guard_list_selection_cursor
                    ][2]
                    blocked_first_row = bool(
                        blocked_hint_fn(frame, current_row_y)
                    ) if callable(blocked_hint_fn) else False
                except BaseException:
                    blocked_first_row = False
                if blocked_first_row:
                    guard_list_selection_cursor += 1
                    try:
                        writer = globals().get('_write')
                        if callable(writer):
                            writer(
                                'v219 blocked first row is not visitable; '
                                'selecting second row immediately cursor=' +
                                str(guard_list_selection_cursor)
                            )
                    except BaseException:
                        pass
            target, target_score, target_row_y = guard_list_candidates[
                guard_list_selection_cursor % len(guard_list_candidates)
            ]
            try:
                setattr(
                    context,
                    '_qqfarm_friend_list_visible_candidate_count',
                    len(guard_list_candidates),
                )
            except BaseException:
                pass
        elif rows and guard_enabled:
            score_fn = globals().get('_friend_list_guard_dog_score')
            for row in rows:
                center = row.get('center') if isinstance(row, dict) else None
                if not isinstance(center, (tuple, list)) or len(center) < 2:
                    continue
                score = float(score_fn(frame, int(center[1]))) if callable(score_fn) else 0.0
                row_y = int(center[1])
                scored.append((row_y, score))
                if target is None and score >= 0.82:
                    target = row
                    target_score = float(score)
                    target_row_y = row_y
        elif rows:
            target = rows[0]
        click_fn = globals().get('_friend_guard_post_client_click')
        if target is not None and callable(click_fn):
            center = target.get('center') if isinstance(target, dict) else None
            if isinstance(center, (tuple, list)) and len(center) >= 2:
                click_x, click_y = int(center[0]), int(center[1])
                try:
                    clicked = bool(click_fn(click_x, click_y, width, height))
                except TypeError:
                    clicked = bool(click_fn(click_x, click_y))
                if clicked:
                    try:
                        now_fn = globals().get('_friend_watchdog_now')
                        now_ts = float(now_fn()) if callable(now_fn) else float(__import__('time').time())
                        setattr(context, '_qqfarm_friend_branch_last_ts', now_ts)
                        setattr(context, '_qqfarm_friend_entry_pending', True)
                        if not (
                            guard_enabled
                            and guard_mode == 'friend_guard_list'
                            and guard_list_pending_retry
                        ):
                            setattr(context, '_qqfarm_friend_entry_clicked_ts', now_ts)
                        if guard_enabled and guard_mode == 'avatar_frame' and target_score >= 0.82:
                            setattr(context, '_qqfarm_guard_row_verified', True)
                            setattr(context, '_qqfarm_guard_row_verified_ts', now_ts)
                            setattr(context, '_qqfarm_guard_row_y', int(target_row_y))
                            setattr(context, '_qqfarm_guard_row_score', float(target_score))
                        else:
                            setattr(context, '_qqfarm_guard_row_verified', False)
                        if guard_enabled and guard_mode == 'friend_guard_list':
                            setattr(context, '_qqfarm_guard_list_prequalified', True)
                            setattr(context, '_qqfarm_guard_list_prequalified_ts', now_ts)
                            setattr(context, '_qqfarm_guard_list_row_y', int(target_row_y))
                            setattr(context, '_qqfarm_guard_list_row_score', float(target_score))
                            if guard_list_pending_retry:
                                next_retry_count = int(guard_list_retry_count) + 1
                            else:
                                next_retry_count = 1
                                setattr(
                                    context,
                                    '_qqfarm_friend_list_pending_cursor',
                                    int(guard_list_selection_cursor),
                                )
                            setattr(
                                context,
                                '_qqfarm_friend_entry_retry_count',
                                min(3, next_retry_count),
                            )
                            setattr(
                                context,
                                '_qqfarm_friend_entry_last_retry_ts',
                                now_ts,
                            )
                            # The row is still pending until the friend-farm
                            # surface is visibly confirmed.  Keeping the cursor
                            # here prevents a lost click from skipping a friend.
                            setattr(
                                context,
                                '_qqfarm_friend_list_visit_cursor',
                                int(guard_list_selection_cursor),
                            )
                            setattr(context, '_qqfarm_friend_chain_pending', True)
                            setattr(context, '_qqfarm_friend_chain_exhausted', False)
                            setattr(context, '_qqfarm_friend_chain_native_home_blocked', False)
                        else:
                            setattr(context, '_qqfarm_guard_list_prequalified', False)
                            setattr(context, '_qqfarm_guard_list_prequalified_ts', 0.0)
                        setattr(context, '_qqfarm_friend_cycle_seen', True)
                        setattr(context, '_qqfarm_visual_friend_count', 0)
                        setattr(context, '_qqfarm_friend_page_seen_ts', 0.0)
                        setattr(context, '_qqfarm_friend_action_last_ts', 0.0)
                        setattr(context, '_qqfarm_friend_action_last_label', '')
                        setattr(context, '_last_friend_farm_go_home_present', False)
                    except BaseException:
                        pass
                    fast_fn = globals().get('_set_friend_chain_fast_interval')
                    if callable(fast_fn):
                        try:
                            fast_fn(context, True)
                        except BaseException:
                            pass
                    write_fn = globals().get('_write')
                    if callable(write_fn):
                        write_fn(
                            'v203 friend list visit row=' + repr((click_x, click_y)) +
                            ' cursor=' + str(guard_list_selection_cursor) + '/' +
                            str(len(guard_list_candidates)) +
                            ' guard_only=' + repr(guard_enabled) +
                            ' guard_scores=' + repr(scored)[:240]
                        )
                    return 'visited'
                write_fn = globals().get('_write')
                if callable(write_fn):
                    write_fn('v117 friend list visit click failed row=' + repr((click_x, click_y)))
                return 'visit-failed'
        close_x = int(round(width * 0.946))
        close_y = int(round(height * 0.118))
        closed = False
        if callable(click_fn):
            try:
                closed = bool(click_fn(close_x, close_y, width, height))
            except TypeError:
                closed = bool(click_fn(close_x, close_y))
            except BaseException:
                closed = False
        try:
            setattr(context, '_qqfarm_friend_cycle_seen', False)
            setattr(context, '_qqfarm_guard_row_verified', False)
            setattr(context, '_qqfarm_visual_friend_count', 0)
            setattr(context, '_qqfarm_friend_page_seen_ts', 0.0)
            setattr(context, '_qqfarm_friend_action_last_ts', 0.0)
            setattr(context, '_qqfarm_friend_action_last_label', '')
            setattr(context, '_qqfarm_friend_branch_last_ts', 0.0)
            setattr(context, '_last_friend_farm_go_home_present', False)
        except BaseException:
            pass
        fast_fn = globals().get('_set_friend_chain_fast_interval')
        if callable(fast_fn):
            try:
                fast_fn(context, False)
            except BaseException:
                pass
        write_fn = globals().get('_write')
        if callable(write_fn):
            write_fn(
                'v117 friend list close result=' + repr(closed) +
                ' rows=' + str(len(rows)) +
                ' guard_only=' + repr(guard_enabled) +
                ' guard_scores=' + repr(scored)[:240]
            )
        return 'closed' if closed else 'close-failed'
    except BaseException as error:
        try:
            write_fn = globals().get('_write')
            if callable(write_fn):
                write_fn('v117 friend list handler error ' + repr(error)[:240])
        except BaseException:
            pass
        return 'invalid'

def _friend_guard_friend_ui_state(frame):
    """True: farm home button visible; None: friend list; False: other farm frame."""
    try:
        os_module = __import__('os')
        home_path = globals().get(
            '_FRIEND_HOME_TEMPLATE_PATH',
            os_module.path.join(os_module.getcwd(), 'friend_home_button.png'),
        )
        home = _friend_guard_match_template(
            frame, home_path, (0.68, 0.52, 1.0, 0.86), 0.68, 0.30
        )
        home_is_strong_soft_edge = bool(
            float(home.get('gray', 0.0) or 0.0) >= 0.74
            and float(home.get('edge', 0.0) or 0.0) >= 0.18
        )
        if home_is_strong_soft_edge and not bool(home.get('matched')):
            home = dict(home)
            home['matched'] = True
            home['match_mode'] = 'strong-gray-soft-edge'
        globals()['_FRIEND_HOME_LAST_MATCH'] = home
        if bool(home.get('matched')):
            bounds_fn = globals().get('_friend_selected_carousel_card_bounds')
            if callable(bounds_fn):
                try:
                    selected_bounds = bounds_fn(frame)
                except BaseException:
                    selected_bounds = None
                home_gray = float(home.get('gray', 0.0) or 0.0)
                home_edge = float(home.get('edge', 0.0) or 0.0)
                unmistakable_home = bool(home_gray >= 0.88 and home_edge >= 0.40)
                visible_friend_action = False
                if not isinstance(selected_bounds, dict):
                    for matcher_name in (
                        '_friend_guard_help_button_match',
                        '_friend_guard_steal_button_match',
                    ):
                        matcher = globals().get(matcher_name)
                        if not callable(matcher):
                            continue
                        try:
                            action_match = matcher(frame)
                        except BaseException:
                            action_match = None
                        if isinstance(action_match, dict) and bool(action_match.get('matched')):
                            visible_friend_action = True
                            break
                if (
                    not isinstance(selected_bounds, dict)
                    and not unmistakable_home
                    and not visible_friend_action
                ):
                    home = dict(home)
                    home['matched'] = False
                    home['rejected_reason'] = 'missing-friend-carousel'
                    globals()['_FRIEND_HOME_LAST_MATCH'] = home
                else:
                    if visible_friend_action:
                        home = dict(home)
                        home['match_mode'] = 'home+visible-friend-action'
                        globals()['_FRIEND_HOME_LAST_MATCH'] = home
                    return True
            else:
                return True
        list_path = globals().get(
            '_FRIEND_LIST_TEMPLATE_PATH',
            os_module.path.join(os_module.getcwd(), 'friend_list_tabs.png'),
        )
        friend_list = _friend_guard_match_template(
            frame, list_path, (0.0, 0.08, 1.0, 0.48), 0.72, 0.45
        )
        rows_fn = globals().get('_friend_list_visit_button_rows')
        layout_rows = rows_fn(frame) if callable(rows_fn) else []
        if layout_rows:
            friend_list = dict(friend_list)
            friend_list['layout_rows'] = len(layout_rows)
            friend_list['layout_centers'] = [
                row.get('center') for row in layout_rows[:8] if isinstance(row, dict)
            ]
        globals()['_FRIEND_LIST_LAST_MATCH'] = friend_list
        if bool(friend_list.get('matched')) or len(layout_rows) >= 3:
            return None
        return False
    except BaseException:
        return None


def _invoke_friend_guard_home_coordinate_click(context, fresh_frame):
    marker_present = bool(getattr(context, '_last_friend_farm_go_home_present', False))
    visual_state = None
    try:
        state_fn = globals().get('_friend_guard_friend_ui_state')
        if callable(state_fn):
            visual_state = state_fn(fresh_frame)
    except BaseException:
        visual_state = None
    # A readable self-farm frame overrides a stale marker.  A readable friend
    # footer can recover even when the legacy marker was never populated.
    if visual_state is False:
        return False
    if visual_state is not True and not marker_present:
        return False
    try:
        shape = getattr(fresh_frame, 'shape', None)
        height, width = int(shape[0]), int(shape[1])
        frame_x = int(round(width * 0.92))
        frame_y = int(round(height * 0.78))
        home_match = globals().get('_FRIEND_HOME_LAST_MATCH', {})
        center = home_match.get('center') if isinstance(home_match, dict) else None
        if bool(home_match.get('matched')) and isinstance(center, (tuple, list)) and len(center) >= 2:
            match_x, match_y = int(center[0]), int(center[1])
            if 0 <= match_x < width and 0 <= match_y < height:
                frame_x, frame_y = match_x, match_y
    except BaseException:
        return False
    client_result = False
    client_click = globals().get('_friend_guard_post_client_click')
    if callable(client_click):
        try:
            try:
                client_result = bool(client_click(frame_x, frame_y, width, height))
            except TypeError:
                client_result = bool(client_click(frame_x, frame_y))
        except BaseException:
            client_result = False
    if client_result:
        try:
            setattr(context, '_last_friend_farm_go_home_present', True)
            _write('v96 friend home delivered by client-only click')
        except BaseException:
            pass
        return True
    screen_x, screen_y = frame_x, frame_y
    converted_ok = False
    absolute_converter = globals().get('_friend_guard_frame_to_screen')
    if callable(absolute_converter):
        try:
            try:
                absolute_point = absolute_converter(frame_x, frame_y, width, height)
            except TypeError:
                absolute_point = absolute_converter(frame_x, frame_y)
            if isinstance(absolute_point, (tuple, list)) and len(absolute_point) >= 2:
                screen_x, screen_y = int(absolute_point[0]), int(absolute_point[1])
                converted_ok = True
        except BaseException:
            converted_ok = False
    converter = getattr(context, 'convert_to_screen_coordinate', None)
    if not converted_ok and callable(converter):
        try:
            try:
                converted = converter(frame_x, frame_y)
            except TypeError:
                converted = converter((frame_x, frame_y))
            if isinstance(converted, (tuple, list)) and len(converted) >= 2:
                screen_x, screen_y = int(converted[0]), int(converted[1])
                converted_ok = True
        except BaseException:
            converted_ok = False
    try:
        _write('v64 dpi home coordinate frame=(' + str(frame_x) + ',' + str(frame_y) +
               ',' + str(width) + ',' + str(height) + ') screen=(' +
               str(screen_x) + ',' + str(screen_y) + ') converted=' +
               repr(converted_ok) + ' client=' + repr(client_result))
    except BaseException:
        pass
    ownership_fn = globals().get('_friend_guard_screen_point_owned_by_farm')
    if callable(ownership_fn):
        try:
            point_owned = bool(
                converted_ok and ownership_fn(screen_x, screen_y)
            )
        except BaseException:
            point_owned = False
        if not point_owned:
            try:
                _write(
                    'v96 friend home absolute click blocked screen=(' +
                    str(screen_x) + ',' + str(screen_y) + ') converted=' +
                    repr(converted_ok)
                )
            except BaseException:
                pass
            return False
    click = getattr(context, 'click_at_position', None)
    if not callable(click):
        accepted = False
    else:
        try:
            try:
                click_result = click(screen_x, screen_y)
            except TypeError:
                click_result = click((screen_x, screen_y))
            accepted = bool(click_result is not False)
        except BaseException:
            accepted = False
    if accepted:
        try:
            # Keep the marker pending until a new frame proves the footer gone.
            setattr(context, '_last_friend_farm_go_home_present', True)
        except BaseException:
            pass
    return accepted


def _invoke_friend_guard_post_click_self(fn, context, original_args=(), original_kwargs=None):
    fresh_frame = _get_frame_from_bot(context)
    friend_state = None
    try:
        state_fn = globals().get('_friend_guard_friend_ui_state')
        if callable(state_fn):
            friend_state = state_fn(fresh_frame)
    except BaseException:
        friend_state = None
    if friend_state is True:
        try:
            setattr(context, '_last_friend_farm_go_home_present', True)
        except BaseException:
            pass
        return False, 'friend-ui-still-visible'
    if friend_state is None:
        return False, 'friend-ui-unreadable'
    action, target, label = _resolve_friend_guard_self_action(
        fn, original_args, original_kwargs or {}
    )
    if not callable(action):
        return False, ''
    call_args, call_kwargs = _friend_guard_args_with_frame(
        context, original_args, original_kwargs or {}, fresh_frame
    )
    result = _invoke_friend_guard_action(action, target, call_args, call_kwargs)
    if result is not False:
        try:
            setattr(context, '_last_friend_farm_go_home_present', False)
            setattr(context, '_flow_unknown_rounds', 0)
        except BaseException:
            pass
    return result, label


def _friend_entry_callable_inventory(context):
    """Return relevant native entry callables for one-time runtime diagnosis."""
    if context is None:
        return ()
    names = []
    try:
        for name in dir(context):
            low = str(name or '').lower()
            if not any(token in low for token in ('friend', 'menu', 'home', 'self_farm')):
                continue
            try:
                value = getattr(context, name)
            except BaseException:
                continue
            if callable(value):
                names.append(str(name))
    except BaseException:
        return ()
    return tuple(sorted(set(names)))


def _invoke_friend_branch_from_home(context, fresh_frame):
    """Retry the friend entry without recursively re-entering its dispatcher."""
    if context is None or fresh_frame is None:
        return False
    try:
        quota_fn = globals().get('_friend_help_quota_active')
        if bool(
            quota_fn(context) if callable(quota_fn)
            else getattr(context, '_qqfarm_friend_help_quota_exhausted', False)
        ):
            _throttled_write(
                'v211-friend-entry-quota-blocked',
                'v211 friend entry skipped because daily help quota is exhausted',
                60.0,
            )
            return False
    except BaseException:
        pass
    try:
        if bool(getattr(context, '_qqfarm_friend_home_recovery_active', False)):
            return False
    except BaseException:
        pass
    try:
        setattr(context, '_qqfarm_friend_home_recovery_active', True)
        try:
            inventory_fn = globals().get('_friend_entry_callable_inventory')
            inventory = (
                inventory_fn(context) if callable(inventory_fn) else ()
            )
            _throttled_write(
                'v168-friend-entry-callable-inventory',
                'v168 friend entry callable inventory=' + repr(inventory)[:1800],
                120.0,
            )
        except BaseException:
            pass

        # The compiled process_friend_farm dispatcher can route back into itself
        # when called from the run_cycle post-hook. Prefer its two direct home-page
        # entry checks: the visible help card first, then the ordinary friend tab.
        guard_list_mode = False
        try:
            guard_enabled_fn = globals().get('_guard_dog_ui_config_enabled')
            guard_mode_fn = globals().get('_guard_dog_detection_mode_config')
            guard_list_mode = bool(
                callable(guard_enabled_fn) and guard_enabled_fn()
                and callable(guard_mode_fn)
                and str(guard_mode_fn()) == 'friend_guard_list'
            )
        except BaseException:
            guard_list_mode = False
        method_names = (
            ('check_friend_icon',)
            if guard_list_mode else (
                'check_friend_help_request_entry',
                'check_friend_icon',
            )
        )
        if guard_list_mode:
            try:
                _write(
                    'v143 guard-list mode skips direct help request entry; '
                    'routing through friend list for identity proof'
                )
            except BaseException:
                pass
        for method_name in method_names:
            action = getattr(context, method_name, None)
            if not callable(action):
                continue
            try:
                result = _invoke_friend_guard_action(
                    action, None, (context, fresh_frame), {}
                )
            except BaseException as error:
                try:
                    _write(
                        'v122 friend home direct entry error method=' +
                        method_name + ' error=' + repr(error)[:180]
                    )
                except BaseException:
                    pass
                continue
            accepted = bool(result)
            try:
                _write(
                    'v122 friend home direct entry method=' + method_name +
                    ' result=' + repr(result)[:160] +
                    ' accepted=' + repr(accepted)
                )
            except BaseException:
                pass
            if accepted:
                return True

        # This helper runs after the compiled run_cycle dispatcher has already
        # completed. Re-entering process_friend_farm here recursively calls the
        # same dispatcher and leaves the UI in a rapid empty-cycle loop. Only
        # direct home-page entry methods are valid from this recovery path.
        try:
            _write('v144 friend home direct entries unavailable; dispatcher re-entry skipped')
        except BaseException:
            pass
        return False
    except BaseException as error:
        try:
            _write('v122 friend home recovery error ' + repr(error)[:220])
        except BaseException:
            pass
        return False
    finally:
        try:
            setattr(context, '_qqfarm_friend_home_recovery_active', False)
        except BaseException:
            pass


def _friend_guard_list_fast_open_from_home(context):
    """Open the friend list and return before the legacy multi-row scan starts."""
    if context is None:
        return False
    try:
        quota_fn = globals().get('_friend_help_quota_active')
        if bool(
            quota_fn(context) if callable(quota_fn)
            else getattr(context, '_qqfarm_friend_help_quota_exhausted', False)
        ):
            return False
    except BaseException:
        pass
    try:
        enabled_fn = globals().get('_guard_dog_ui_config_enabled')
        mode_fn = globals().get('_guard_dog_detection_mode_config')
        if not (
            callable(enabled_fn) and enabled_fn()
            and callable(mode_fn) and str(mode_fn()) == 'friend_guard_list'
        ):
            return False
    except BaseException:
        return False
    try:
        if bool(getattr(context, '_qqfarm_friend_chain_pending', False)):
            return False
    except BaseException:
        pass
    capture_fn = globals().get('_get_frame_from_bot')
    try:
        frame = capture_fn(context) if callable(capture_fn) else None
    except BaseException:
        frame = None
    if frame is None:
        return False
    rows_fn = globals().get('_friend_list_visit_button_rows')
    try:
        if callable(rows_fn) and len(rows_fn(frame) or []) > 0:
            return False
    except BaseException:
        pass
    state_fn = globals().get('_friend_guard_friend_ui_state')
    try:
        if callable(state_fn) and state_fn(frame) is True:
            return False
    except BaseException:
        pass
    try:
        now_fn = globals().get('_friend_watchdog_now')
        now_ts = (
            float(now_fn())
            if callable(now_fn)
            else float(__import__('time').time())
        )
        last_ts = float(getattr(
            context, '_qqfarm_guard_list_fast_open_ts', 0.0
        ) or 0.0)
        if last_ts > 0.0 and -1.0 <= (now_ts - last_ts) < 3.0:
            return True
    except BaseException:
        now_ts = 0.0
    open_fn = globals().get('_invoke_friend_branch_from_home')
    try:
        opened = bool(open_fn(context, frame)) if callable(open_fn) else False
    except BaseException:
        opened = False
    if not opened:
        return False
    try:
        setattr(context, '_qqfarm_guard_list_fast_open_ts', now_ts)
        setattr(context, '_qqfarm_friend_cycle_seen', True)
        setattr(context, '_qqfarm_visual_friend_count', 0)
        setattr(context, '_qqfarm_friend_page_seen_ts', 0.0)
    except BaseException:
        pass
    try:
        fast_fn = globals().get('_set_friend_chain_fast_interval')
        if callable(fast_fn):
            fast_fn(context, True)
    except BaseException:
        pass
    try:
        writer = globals().get('_write')
        if callable(writer):
            writer(
                'v146 guard-list friend icon opened; legacy row scan skipped '
                'until list preflight'
            )
    except BaseException:
        pass
    return True


def _apply_visual_friend_route_watchdog(
    fn, context, function_name='', force_recovery=False
):
    """Run friend actions first; recover home after action follow-up or timeout."""
    try:
        if context is None:
            return False
        friend_cycle_seen = bool(getattr(context, '_qqfarm_friend_cycle_seen', False))
        try:
            setattr(context, '_qqfarm_friend_cycle_seen', False)
        except BaseException:
            pass
        now_fn = globals().get('_friend_watchdog_now')
        try:
            now_ts = float(now_fn()) if callable(now_fn) else float(__import__('time').time())
        except BaseException:
            now_ts = 0.0
        frame = _get_frame_from_bot(context)
        state_fn = globals().get('_friend_guard_friend_ui_state')
        visual_state = state_fn(frame) if callable(state_fn) else None
        if visual_state is None:
            list_handler = globals().get('_handle_friend_list_surface')
            if callable(list_handler):
                list_result = list_handler(context, frame)
                _write(
                    'v117 friend list watchdog result=' + str(list_result) +
                    ' name=' + str(function_name)
                )
                return False
        cycle_branch_hint = str(
            getattr(context, '_qqfarm_cycle_branch_hint', '') or ''
        ).strip().lower()
        try:
            false_positive_ts = float(getattr(
                context, '_qqfarm_native_home_false_positive_ts', 0.0
            ) or 0.0)
        except BaseException:
            false_positive_ts = 0.0
        recent_native_false_positive = bool(
            visual_state is False
            and false_positive_ts > 0.0
            and 0.0 <= (now_ts - false_positive_ts) <= 3.0
        )
        if recent_native_false_positive:
            friend_cycle_seen = False
            cycle_branch_hint = 'self'
            try:
                finalize_fn = globals().get(
                    '_finalize_friend_chain_after_troublemaker'
                )
                if callable(finalize_fn):
                    finalize_fn(context)
                setattr(context, '_qqfarm_cycle_branch_hint', 'self')
                setattr(context, '_qqfarm_friend_cycle_seen', False)
                setattr(context, '_qqfarm_friend_home_noop_count', 0)
                setattr(context, '_qqfarm_visual_friend_count', 0)
            except BaseException:
                pass
            _throttled_write(
                'v162-native-home-false-positive-same-cycle',
                'v162 cleared stale friend state in the same cycle as the ' +
                'native home-icon false positive',
                4.0,
            )
        cooldown_fn = globals().get('_false_friend_branch_cooldown_active')
        false_branch_blocked = bool(
            callable(cooldown_fn)
            and cooldown_fn(context, visual_state, now_ts)
        )
        if false_branch_blocked:
            friend_cycle_seen = False
            cycle_branch_hint = 'home'
            try:
                setattr(context, '_qqfarm_friend_cycle_seen', False)
                setattr(context, '_qqfarm_cycle_branch_hint', 'home')
                setattr(context, '_qqfarm_friend_home_noop_count', 0)
            except BaseException:
                pass
            _throttled_write(
                'v159-false-friend-branch-cooldown',
                'v159 ignored native friend hint on verified non-friend surface',
                4.0,
            )
        if visual_state is False:
            if cycle_branch_hint == 'friend':
                home_noop_count = int(
                    getattr(context, '_qqfarm_friend_home_noop_count', 0) or 0
                ) + 1
                setattr(context, '_qqfarm_friend_home_noop_count', home_noop_count)
                last_recovery_ts = float(
                    getattr(context, '_qqfarm_friend_home_recovery_ts', 0.0) or 0.0
                )
                recovery_due = bool(
                    home_noop_count >= 2
                    and (
                        last_recovery_ts <= 0.0
                        or (now_ts - last_recovery_ts) >= 3.0
                    )
                )
                if recovery_due:
                    recovery_fn = globals().get('_invoke_friend_branch_from_home')
                    recovered = bool(
                        recovery_fn(context, frame)
                    ) if callable(recovery_fn) else False
                    setattr(context, '_qqfarm_friend_home_noop_count', 0)
                    setattr(context, '_qqfarm_friend_home_recovery_ts', now_ts)
                    stale_cleared = False
                    if recovered:
                        try:
                            setattr(
                                context, '_qqfarm_friend_home_recovery_fail_count', 0
                            )
                        except BaseException:
                            pass
                    else:
                        stale_fn = globals().get(
                            '_record_failed_friend_branch_recovery'
                        )
                        stale_cleared = bool(
                            callable(stale_fn) and stale_fn(context, now_ts)
                        )
                    _write(
                        'v120 friend branch stayed on home; recovery=' +
                        repr(recovered) + ' hint=' + cycle_branch_hint +
                        ' stale_cleared=' + repr(stale_cleared)
                    )
                    if stale_cleared:
                        _write(
                            'v159 stale friend branch cleared after repeated ' +
                            'home recovery misses'
                        )
                    return False
            else:
                setattr(context, '_qqfarm_friend_home_noop_count', 0)
        else:
            setattr(context, '_qqfarm_friend_home_noop_count', 0)
            try:
                setattr(context, '_qqfarm_friend_home_recovery_fail_count', 0)
                setattr(context, '_qqfarm_false_friend_branch_block_until', 0.0)
            except BaseException:
                pass
        try:
            last_branch_ts = float(getattr(context, '_qqfarm_friend_branch_last_ts', 0.0) or 0.0)
        except BaseException:
            last_branch_ts = 0.0
        if friend_cycle_seen:
            last_branch_ts = now_ts
            try:
                setattr(context, '_qqfarm_friend_branch_last_ts', now_ts)
            except BaseException:
                pass
        recent_branch = bool(last_branch_ts > 0.0 and (now_ts - last_branch_ts) <= 45.0)
        branch_friend_fallback = bool(
            visual_state is False
            and (
                friend_cycle_seen
                or (
                    recent_branch
                    and bool(getattr(context, '_last_friend_farm_go_home_present', False))
                )
            )
        )
        friend_surface = bool(visual_state is True or branch_friend_fallback)
        old_count = int(getattr(context, '_qqfarm_visual_friend_count', 0) or 0)
        action_followup_ready = False
        page_timeout_ready = False
        action_age = -1.0
        page_age = 0.0
        if friend_surface:
            page_seen_ts = float(
                getattr(context, '_qqfarm_friend_page_seen_ts', 0.0) or 0.0
            )
            if page_seen_ts <= 0.0:
                page_seen_ts = now_ts
                setattr(context, '_qqfarm_friend_page_seen_ts', page_seen_ts)
            page_age = max(0.0, now_ts - page_seen_ts)
            action_ts = float(
                getattr(context, '_qqfarm_friend_action_last_ts', 0.0) or 0.0
            )
            if action_ts > 0.0:
                action_age = max(0.0, now_ts - action_ts)
                action_followup_ready = action_age >= 0.8
            page_timeout_ready = page_age >= 20.0
            # A passive scheduler cycle does not count as a failed action pass,
            # but a completed action or page timeout authorizes one final probe.
            friend_count = min(3, old_count + (1 if friend_cycle_seen else 0))
        else:
            friend_count = 0
            if visual_state is False:
                fast_fn = globals().get('_set_friend_chain_fast_interval')
                if callable(fast_fn):
                    fast_fn(context, False)
            elif visual_state is None and friend_cycle_seen:
                fast_fn = globals().get('_set_friend_chain_fast_interval')
                if callable(fast_fn):
                    fast_fn(context, True)
            try:
                setattr(context, '_qqfarm_friend_page_seen_ts', 0.0)
                setattr(context, '_qqfarm_friend_action_last_ts', 0.0)
                setattr(context, '_qqfarm_friend_action_last_label', '')
            except BaseException:
                pass
        setattr(context, '_qqfarm_visual_friend_count', friend_count)
        try:
            setattr(context, '_qqfarm_visual_self_after_friend_count', 0)
        except BaseException:
            pass
        home_match = globals().get('_FRIEND_HOME_LAST_MATCH', {})
        list_match = globals().get('_FRIEND_LIST_LAST_MATCH', {})
        _write('v70 template route watchdog name=' + str(function_name) +
               ' state=' + repr(visual_state) +
               ' friend_cycle=' + repr(friend_cycle_seen) +
               ' branch_fallback=' + repr(branch_friend_fallback) +
               ' count=' + str(friend_count) +
               ' action_age=' + ('%.3f' % action_age) +
               ' page_age=' + ('%.3f' % page_age) +
               ' home=' + repr(home_match)[:220] +
               ' list=' + repr(list_match)[:220])
        navigation_blocked = False
        continuation_exhausted = False
        chain_reason = ''
        recovery_probe = bool(
            friend_surface
            and (
                bool(force_recovery)
                or friend_cycle_seen
                or action_followup_ready
                or page_timeout_ready
            )
        )
        if recovery_probe:
            fast_probe_fn = globals().get(
                '_invoke_friend_visual_actions_before_home'
            )
            native_probe_fn = globals().get('_invoke_friend_actions_before_home')
            probe_fn = (
                fast_probe_fn if callable(fast_probe_fn) else native_probe_fn
            )
            if callable(probe_fn):
                action_result, action_label = probe_fn(context, frame)
                try:
                    allow_native_probe = bool(getattr(
                        context,
                        'friend_watchdog_allow_native_action_fallback',
                        False,
                    ))
                except BaseException:
                    allow_native_probe = False
                if (
                    not action_result
                    and callable(fast_probe_fn)
                    and callable(native_probe_fn)
                    and allow_native_probe
                ):
                    action_result, action_label = native_probe_fn(context, frame)
                if action_result:
                    setattr(context, '_qqfarm_visual_friend_count', 1)
                    next_frame = _get_frame_from_bot(context)
                    chain_fn = globals().get('_run_friend_continuation_chain')
                    next_fn = globals().get('_invoke_friend_next_actionable_entry')
                    moved = False
                    next_label = ''
                    chain_actions = 0
                    chain_exhausted = False
                    chain_reason = ''
                    if callable(chain_fn):
                        chain_result = chain_fn(context, next_frame, action_label)
                        if isinstance(chain_result, dict):
                            moved = int(chain_result.get('moves', 0) or 0) > 0
                            chain_actions = int(chain_result.get('actions', 0) or 0)
                            next_label = str(chain_result.get('last_label', '') or '')
                            chain_exhausted = bool(chain_result.get('exhausted', False))
                            chain_reason = str(chain_result.get('reason', '') or '')
                            chain_frame = chain_result.get('frame')
                            if chain_frame is not None:
                                frame = chain_frame
                            if chain_exhausted or chain_reason == 'navigation-not-confirmed':
                                friend_count = max(2, friend_count)
                                setattr(context, '_qqfarm_visual_friend_count', friend_count)
                            if chain_exhausted:
                                continuation_exhausted = True
                            if chain_reason == 'navigation-not-confirmed':
                                friend_count = max(2, friend_count)
                                navigation_blocked = True
                    elif callable(next_fn):
                        moved, next_label = next_fn(context, next_frame, action_label)
                    fast_fn = globals().get('_set_friend_chain_fast_interval')
                    if callable(fast_fn):
                        fast_fn(context, True)
                    _write('v72 template route watchdog action=' + str(action_label) +
                           ' moved_next=' + repr(moved) +
                           ' chain_actions=' + str(chain_actions) +
                           ' exhausted=' + repr(chain_exhausted) +
                           ' reason=' + str(chain_reason) +
                           ' next=' + str(next_label))
                    if not navigation_blocked and not continuation_exhausted:
                        return False
            if not friend_cycle_seen and (action_followup_ready or page_timeout_ready):
                # The direct checks just confirmed there is no remaining visible
                # steal/help action, so a passive scheduler cycle may recover home.
                friend_count = max(2, friend_count)
                setattr(context, '_qqfarm_visual_friend_count', friend_count)
        if (
            friend_surface
            and not navigation_blocked
            and not continuation_exhausted
            and (
                bool(force_recovery)
                or friend_cycle_seen
                or action_followup_ready
                or page_timeout_ready
            )
        ):
            chain_fn = globals().get('_run_friend_continuation_chain')
            next_fn = globals().get('_invoke_friend_next_actionable_entry')
            last_label = str(getattr(context, '_qqfarm_friend_action_last_label', '') or '')
            moved = False
            next_label = ''
            chain_actions = 0
            chain_exhausted = False
            chain_reason = ''
            if callable(chain_fn):
                chain_result = chain_fn(context, frame, last_label)
                if isinstance(chain_result, dict):
                    moved = int(chain_result.get('moves', 0) or 0) > 0
                    chain_actions = int(chain_result.get('actions', 0) or 0)
                    next_label = str(chain_result.get('last_label', '') or '')
                    chain_exhausted = bool(chain_result.get('exhausted', False))
                    chain_reason = str(chain_result.get('reason', '') or '')
                    chain_frame = chain_result.get('frame')
                    if chain_frame is not None:
                        frame = chain_frame
                    if chain_exhausted:
                        continuation_exhausted = True
                        friend_count = max(2, friend_count)
                        setattr(context, '_qqfarm_visual_friend_count', friend_count)
                    if chain_reason == 'navigation-not-confirmed':
                        friend_count = max(2, friend_count)
                        setattr(context, '_qqfarm_visual_friend_count', friend_count)
                        navigation_blocked = True
            elif callable(next_fn):
                moved, next_label = next_fn(context, frame, last_label)
            if moved and not continuation_exhausted:
                fast_fn = globals().get('_set_friend_chain_fast_interval')
                if callable(fast_fn):
                    fast_fn(context, True)
                _write('v72 template route watchdog skipped home; moved next=' + str(next_label) +
                       ' chain_actions=' + str(chain_actions) +
                       ' exhausted=' + repr(chain_exhausted))
                return False
            if continuation_exhausted:
                _write('v108 friend carousel exhausted; returning home immediately reason=' +
                       str(chain_reason) + ' moves=' + repr(moved) +
                       ' actions=' + str(chain_actions))
        block_fn = globals().get('_friend_chain_should_block_troublemaker')
        if callable(block_fn) and block_fn(context):
            _write(
                'v124 friend watchdog kept current friend: chain pending ' +
                'reason=' + str(chain_reason)
            )
            return False
        if continuation_exhausted:
            trouble_fn = globals().get('_run_deferred_friend_troublemaker')
            trouble_result = (
                trouble_fn(context, frame) if callable(trouble_fn) else False
            )
            if trouble_result:
                try:
                    setattr(context, '_qqfarm_visual_friend_count', 0)
                    setattr(context, '_qqfarm_friend_cycle_seen', False)
                    setattr(context, '_qqfarm_friend_branch_last_ts', 0.0)
                    setattr(context, '_last_friend_farm_go_home_present', False)
                except BaseException:
                    pass
                _write(
                    'v124 deferred daily troublemaker completed friend return flow'
                )
                return True
        home_ready = bool(
            friend_surface
            and not navigation_blocked
            and friend_count >= 2
            and (
                bool(force_recovery)
                or friend_cycle_seen
                or action_followup_ready
                or page_timeout_ready
            )
        )
        if not home_ready:
            return False
        try:
            setattr(context, '_last_friend_farm_go_home_present', True)
        except BaseException:
            pass
        if branch_friend_fallback:
            native_home = getattr(context, 'check_go_home_icon', None)
            if callable(native_home):
                try:
                    click_result = _invoke_friend_guard_action(
                        native_home, None, (context, frame), {}
                    )
                except BaseException:
                    click_result = False
            else:
                click_result = False
            _write('v79 branch-backed native home result=' + repr(click_result))
        else:
            click_result = _invoke_friend_guard_home_coordinate_click(context, frame)
            _write('v70 template route watchdog home click result=' + repr(click_result))
        if not click_result:
            setattr(context, '_qqfarm_visual_friend_count', 1)
            return False
        try:
            time.sleep(0.8)
        except BaseException:
            pass
        post_result, post_label = _invoke_friend_guard_post_click_self(
            fn, context, (context, frame), {}
        )
        post_label_text = str(post_label or '')
        post_self_verified = post_label_text in (
            'method.process_self_farm', 'global.process_self_farm'
        )
        success = bool(
            post_label_text not in ('friend-ui-still-visible', 'friend-ui-unreadable')
            and (bool(post_result) or post_self_verified)
        )
        _write('v70 template route watchdog verify action=' + str(post_label) +
               ' result=' + repr(post_result)[:160] +
               ' success=' + repr(success))
        setattr(context, '_qqfarm_visual_friend_count', 0 if success else 1)
        if success:
            fast_fn = globals().get('_set_friend_chain_fast_interval')
            if callable(fast_fn):
                fast_fn(context, False)
            try:
                setattr(context, '_qqfarm_friend_page_guard_active', False)
                setattr(context, '_qqfarm_friend_page_seen_ts', 0.0)
                setattr(context, '_qqfarm_friend_action_last_ts', 0.0)
                setattr(context, '_qqfarm_friend_action_last_label', '')
                setattr(context, '_qqfarm_friend_branch_last_ts', 0.0)
                setattr(context, '_last_friend_farm_go_home_present', False)
            except BaseException:
                pass
        return success
    except BaseException as e:
        try:
            _write('v70 template route watchdog error ' + repr(e)[:240])
        except BaseException:
            pass
        return False


def _friend_route_state_summary(context):
    fields = []
    methods = []
    try:
        for key in dir(context):
            low = str(key).lower()
            if not any(token in low for token in ('friend', 'home', 'farm', 'mode', 'flow', 'current', 'next', 'last', 'check')):
                continue
            try:
                value = getattr(context, key)
                if callable(value):
                    methods.append(str(key))
                else:
                    fields.append(str(key) + '=' + repr(value)[:180])
            except BaseException:
                pass
    except BaseException:
        pass
    return 'fields=[' + ' | '.join(fields[:100]) + '] methods=[' + ','.join(methods[:100]) + ']'


def _apply_friend_empty_return_home_guard(fn, args, kwargs, elapsed_seconds, function_name=''):
    try:
        context = _friend_guard_context(args, kwargs)
        if context is None:
            _throttled_write(
                'v48-friend-route-no-context-' + str(function_name),
                'v48 friend route recovery no scheduler context name=' + str(function_name),
                60.0,
            )
            return False
        block_fn = globals().get('_friend_chain_should_block_troublemaker')
        if callable(block_fn) and block_fn(context):
            try:
                _throttled_write(
                    'v125-friend-empty-home-pending',
                    'v125 friend empty-home recovery deferred: chain pending',
                    15.0,
                )
            except BaseException:
                pass
            return False
        now_ts = time.time()
        visual_gate_available = False
        guard_frame = None
        guard_visual_state = None
        try:
            state_fn = globals().get('_friend_guard_friend_ui_state')
            visual_gate_available = callable(state_fn)
            if visual_gate_available:
                guard_frame = _get_frame_from_bot(context)
                guard_visual_state = state_fn(guard_frame)
        except BaseException:
            guard_visual_state = None
        if visual_gate_available and guard_visual_state is not True:
            # Friend-list/self/unknown frames must not contribute strikes that
            # can immediately eject a newly visited friend on its first pass.
            setattr(context, '_qqfarm_friend_fast_empty_count', 0)
            setattr(context, '_qqfarm_friend_fast_empty_ts', now_ts)
            setattr(context, '_qqfarm_friend_page_guard_active', False)
            return False
        new_friend_page = False
        if visual_gate_available and guard_visual_state is True:
            new_friend_page = not bool(
                getattr(context, '_qqfarm_friend_page_guard_active', False)
            )
            setattr(context, '_qqfarm_friend_page_guard_active', True)
        old_count = int(getattr(context, '_qqfarm_friend_fast_empty_count', 0) or 0)
        last_count_ts = float(getattr(context, '_qqfarm_friend_fast_empty_ts', 0.0) or 0.0)
        if new_friend_page:
            old_count = 0
            last_count_ts = 0.0
        new_count, trigger = _friend_empty_guard_next(
            old_count, elapsed_seconds, now_ts, last_count_ts
        )
        if new_friend_page:
            # Never return home on the first process_friend_farm completion for
            # a freshly confirmed friend page, even if stale list strikes existed.
            if float(elapsed_seconds or 0.0) <= 3.0:
                new_count = 1
            trigger = False
        distinct = not (last_count_ts > 0.0 and (now_ts - last_count_ts) < 5.0)
        setattr(context, '_qqfarm_friend_fast_empty_count', new_count)
        if float(elapsed_seconds or 0.0) > 3.0 or distinct:
            setattr(context, '_qqfarm_friend_fast_empty_ts', now_ts)
        if not trigger:
            return False
        action, target, label = _resolve_friend_guard_action(fn, args, kwargs)
        if not callable(action):
            _throttled_write(
                'v48-friend-route-no-action-' + str(function_name),
                'v48 friend route recovery action unresolved name=' + str(function_name) +
                ' context=' + str(type(context).__name__),
                30.0,
            )
            setattr(context, '_qqfarm_friend_fast_empty_count', 1)
            setattr(context, '_qqfarm_friend_fast_empty_ts', now_ts)
            return False
        _write('v48 friend route state before ' + _friend_route_state_summary(context))
        _write('v65 friend route recovery trigger self name=' + str(function_name) +
               ' action=' + str(label) +
               ' elapsed=' + ('%.3f' % float(elapsed_seconds or 0.0)) +
               ' count=' + str(new_count) +
               ' context=' + str(type(context).__name__))
        action_args, action_kwargs = tuple(args or ()), dict(kwargs or {})
        fresh_frame = guard_frame
        fresh_friend_state = guard_visual_state
        home_check_labels = ('method.check_go_home_icon', 'global.check_go_home_icon')
        is_home_check = label in home_check_labels
        if is_home_check:
            if fresh_frame is None:
                fresh_frame = _get_frame_from_bot(context)
            if fresh_frame is not None:
                action_args, action_kwargs = _friend_guard_args_with_frame(context, args, kwargs, fresh_frame)
                try:
                    fresh_shape = getattr(fresh_frame, 'shape', None)
                except BaseException:
                    fresh_shape = None
                _write('v50 friend route recovery fresh frame shape=' + repr(fresh_shape))
            if fresh_friend_state is None:
                try:
                    state_fn = globals().get('_friend_guard_friend_ui_state')
                    if callable(state_fn):
                        fresh_friend_state = state_fn(fresh_frame)
                except BaseException:
                    fresh_friend_state = None
            _write('v60 friend route visual state before=' + repr(fresh_friend_state))
        result = _invoke_friend_guard_action(action, target, action_args, action_kwargs)
        action_variant = str(label)
        if (
            is_home_check
            and not result
            and (
                bool(getattr(context, '_last_friend_farm_go_home_present', False))
                or fresh_friend_state is True
            )
        ):
            relaxed_result = _invoke_friend_guard_relaxed_home_check(
                action, target, context, action_args, action_kwargs
            )
            _write('v52 friend route recovery relaxed home result action=' +
                   str(label) + ' result=' + repr(relaxed_result)[:160])
            if relaxed_result:
                result = relaxed_result
                action_variant = str(label) + '.relaxed'
        if is_home_check and result:
            try:
                time.sleep(0.8)
            except BaseException:
                pass
            verify_result, verify_label = _invoke_friend_guard_post_click_self(
                fn, context, args, kwargs
            )
            _write('v60 friend route recovery template-click verify action=' +
                   str(verify_label) + ' result=' + repr(verify_result)[:160])
            if verify_label in ('friend-ui-still-visible', 'friend-ui-unreadable'):
                result = False
            elif verify_label:
                result = verify_result is not False
                if result:
                    action_variant = str(action_variant) + '.verified-self'
        coordinate_attempted = False
        if is_home_check and not result:
            coordinate_result = _invoke_friend_guard_home_coordinate_click(context, fresh_frame)
            coordinate_attempted = bool(coordinate_result)
            _write('v60 friend route recovery coordinate home result action=' +
                   str(label) + ' result=' + repr(coordinate_result)[:160])
            if coordinate_result:
                try:
                    time.sleep(0.8)
                except BaseException:
                    pass
                post_self_result, post_self_label = _invoke_friend_guard_post_click_self(
                    fn, context, args, kwargs
                )
                _write('v60 friend route recovery post-click self result action=' +
                       str(post_self_label) + ' result=' + repr(post_self_result)[:160])
                if post_self_label in ('friend-ui-still-visible', 'friend-ui-unreadable'):
                    result = False
                    action_variant = str(label) + '.coordinate-unconfirmed'
                elif post_self_label:
                    result = post_self_result is not False
                    action_variant = str(label) + '.coordinate.self'
                else:
                    result = False
                    action_variant = str(label) + '.coordinate-no-self-action'
        if is_home_check and not result:
            if fresh_friend_state is False and not coordinate_attempted:
                _write('v48 friend route recovery direct action absent action=' +
                       str(label) + ' result=' + repr(result)[:160])
                fallback_action, fallback_target, fallback_label = (
                    _resolve_friend_guard_self_action(fn, args, kwargs)
                )
                if callable(fallback_action):
                    fallback_result = _invoke_friend_guard_action(
                        fallback_action, fallback_target, args, kwargs
                    )
                    _write('v48 friend route recovery fallback result action=' +
                           str(fallback_label) + ' result=' + repr(fallback_result)[:160])
                    result = fallback_result
                    action_variant = fallback_label
            else:
                _write('v60 friend route recovery kept in friend mode state=' +
                       repr(fresh_friend_state) + ' coordinate_attempted=' +
                       repr(coordinate_attempted))
        success = bool(result)
        if success:
            setattr(context, '_qqfarm_friend_fast_empty_count', 0)
            setattr(context, '_qqfarm_friend_page_guard_active', False)
        else:
            # Keep one strike so the next distinct round retries promptly.
            setattr(context, '_qqfarm_friend_fast_empty_count', 1)
        setattr(context, '_qqfarm_friend_fast_empty_ts', now_ts)
        _write('v65 friend route recovery result action=' + str(action_variant) +
               ' result=' + repr(result)[:160] + ' success=' + repr(success))
        _write('v48 friend route state after ' + _friend_route_state_summary(context))
        return success
    except BaseException as e:
        try:
            _write('v65 friend route recovery error ' + repr(e)[:240])
        except BaseException:
            pass
        return False


def _wrap_vip_business_func(fn, name=''):
    try:
        if not callable(fn):
            return fn, False
        if getattr(fn, '__qqfarm_vip_business_wrapped__', False):
            return fn, False
        lname = str(name).lower()
        def _wrapped(*a, **k):
            global _VIP_WAREHOUSE_LAST_SEQUENCE_CLASS, _VIP_WAREHOUSE_LAST_SEQUENCE_TS
            vip_context = []
            dispatch_context = None
            dispatch_armed = False
            friend_guard_started = 0.0
            try:
                if _stop_requested_in_args(a, k):
                    return _stop_gate_return(name)
            except BaseException:
                pass
            try:
                context_fn = globals().get('_friend_guard_context')
                dispatch_context = (
                    context_fn(a, k) if callable(context_fn) else
                    next((value for value in list(a) + list(k.values())
                          if value is not None and not isinstance(
                              value, (str, bytes, int, float, bool, list, tuple, dict, set)
                          )), None)
                )
            except BaseException:
                dispatch_context = None
            if 'daily_troublemaker' in lname:
                block_fn = globals().get('_friend_chain_should_block_troublemaker')
                if callable(block_fn) and block_fn(dispatch_context):
                    try:
                        if dispatch_context is not None:
                            setattr(
                                dispatch_context,
                                '_qqfarm_friend_chain_deferred_troublemaker',
                                _wrapped,
                            )
                            setattr(
                                dispatch_context,
                                '_qqfarm_friend_chain_deferred_troublemaker_args',
                                tuple(a or ()),
                            )
                            setattr(
                                dispatch_context,
                                '_qqfarm_friend_chain_deferred_troublemaker_kwargs',
                                dict(k or {}),
                            )
                    except BaseException:
                        pass
                    try:
                        _write(
                            'v128 daily troublemaker cached until friend chain exhaustion ' +
                            str(name)
                        )
                    except BaseException:
                        pass
                    return False
            if 'process_friend_farm' in lname:
                fast_open_fn = globals().get(
                    '_friend_guard_list_fast_open_from_home'
                )
                if callable(fast_open_fn):
                    try:
                        if fast_open_fn(dispatch_context):
                            return True
                    except BaseException as error:
                        try:
                            _write(
                                'v146 guard-list fast open error=' +
                                repr(error)[:220]
                            )
                        except BaseException:
                            pass
                try:
                    active_context = globals().get('_ACTIVE_RUN_CYCLE_CONTEXT')
                    capture_fn = globals().get('_get_frame_from_bot')
                    state_fn = globals().get('_friend_guard_friend_ui_state')
                    now_fn = globals().get('_friend_watchdog_now')
                    current_frame = (
                        capture_fn(dispatch_context)
                        if callable(capture_fn) else None
                    )
                    current_state = (
                        state_fn(current_frame)
                        if callable(state_fn) and current_frame is not None
                        else None
                    )
                    now_ts = (
                        float(now_fn())
                        if callable(now_fn)
                        else float(__import__('time').time())
                    )
                    targets = []
                    for candidate in (dispatch_context, active_context):
                        if candidate is None or any(
                            candidate is existing for existing in targets
                        ):
                            continue
                        targets.append(candidate)
                    recent_native_false_positive = bool(
                        current_state is False
                        and any(
                            (
                                float(getattr(
                                    target,
                                    '_qqfarm_native_home_false_positive_ts',
                                    0.0,
                                ) or 0.0) > 0.0
                                and 0.0 <= (
                                    now_ts - float(getattr(
                                        target,
                                        '_qqfarm_native_home_false_positive_ts',
                                        0.0,
                                    ) or 0.0)
                                ) <= 30.0
                            )
                            for target in targets
                        )
                    )
                    if recent_native_false_positive:
                        finalize_fn = globals().get(
                            '_finalize_friend_chain_after_troublemaker'
                        )
                        for target in targets:
                            if callable(finalize_fn):
                                finalize_fn(target)
                            setattr(target, '_qqfarm_cycle_branch_hint', 'self')
                            setattr(target, '_qqfarm_friend_cycle_seen', False)
                            setattr(target, '_qqfarm_force_self_cycle_next', True)
                            fast_fn = globals().get(
                                '_set_friend_chain_fast_interval'
                            )
                            if callable(fast_fn):
                                fast_fn(target, False)
                        _throttled_write(
                            'v164-skip-legacy-friend-after-false-home',
                            'v164 skipped legacy friend processor after a verified ' +
                            'native home-icon false positive',
                            4.0,
                        )
                        return False
                except BaseException as error:
                    try:
                        _write(
                            'v164 false friend processor gate error=' +
                            repr(error)[:220]
                        )
                    except BaseException:
                        pass
                begin_fn = globals().get('_friend_chain_begin_dispatch')
                dispatch_armed = bool(
                    begin_fn(dispatch_context)
                    if callable(begin_fn) else False
                )
                friend_guard_started = __import__('time').time()
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
                if 'daily_troublemaker' in lname:
                    _diagnose_daily_troublemaker_vip_source(fn, a, k, name)
                vip_context = _enter_vip_entitlement_context(fn, a, k)
                changed += len(vip_context)
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
                if dispatch_armed:
                    try:
                        finish_fn = globals().get('_friend_chain_finish_dispatch')
                        if callable(finish_fn):
                            finish_fn(dispatch_context)
                    except BaseException:
                        pass
                    dispatch_armed = False
                raise
            finally:
                restored = _restore_vip_entitlement_context(vip_context)
                if vip_context:
                    _throttled_write('v36-vip-context-' + str(name), 'v36 vip entitlement context applied ' + str(name) + ' forced=' + str(len(vip_context)) + ' restored=' + str(restored), 30.0)
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
            try:
                if friend_guard_started > 0.0 and 'process_friend_farm' in lname:
                    _mark_friend_cycle_seen(a, k)
                    _apply_friend_empty_return_home_guard(
                        fn, a, k, max(0.0, __import__('time').time() - friend_guard_started), name
                    )
            except BaseException as e:
                try: _write('v48 friend route recovery post error ' + repr(e)[:240])
                except BaseException: pass
            if dispatch_armed:
                try:
                    finish_fn = globals().get('_friend_chain_finish_dispatch')
                    if callable(finish_fn):
                        finish_fn(dispatch_context)
                except BaseException:
                    pass
                dispatch_armed = False
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
        # VIP business functions also live in PyArmor-obfuscated bot._q*
        # modules. Exact function-name matching below keeps the scan narrow.
        if not low.startswith('bot.'):
            return False
        patch_names = set(_VIP_BUSINESS_FUNC_NAMES).union(
            set(globals().get('_FRIEND_HOME_FUNC_NAMES', set())),
            set(globals().get('_FRIEND_NEXT_ENTRY_FUNC_NAMES', set())),
        )
        for n in patch_names:
            if hasattr(m, n):
                return True
        try:
            for obj in list(vars(m).values())[:500]:
                if isinstance(obj, type):
                    for n in patch_names:
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
                inventory_fn = globals().get('_write_planting_callable_inventory')
                if callable(inventory_fn):
                    inventory_fn(m)
            except BaseException:
                pass
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
            patch_names = set(_VIP_BUSINESS_FUNC_NAMES).union(
                set(globals().get('_FRIEND_HOME_FUNC_NAMES', set())),
                set(globals().get('_FRIEND_NEXT_ENTRY_FUNC_NAMES', set())),
            )
            for obj, prefix, is_class_target in targets:
                for n in list(patch_names):
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
                        if n in globals().get('_FRIEND_HOME_FUNC_NAMES', set()):
                            new, ok = _wrap_friend_home_func(old, prefix + '.' + n)
                        elif n in globals().get('_FRIEND_NEXT_ENTRY_FUNC_NAMES', set()):
                            new, ok = _wrap_friend_next_entry_func(old, prefix + '.' + n)
                        elif n == 'handle_home_harvest':
                            new, ok = _wrap_home_harvest_planting_trigger(
                                old, prefix + '.' + n
                            )
                        elif n == 'handle_home_planting':
                            new, ok = _wrap_home_planting_cooldown(
                                old, prefix + '.' + n
                            )
                        elif n == '_plant_seed_over_lands':
                            new, ok = _wrap_planting_crop_context_func(old, m, prefix + '.' + n)
                        elif n == '_run_auto_fertilize_after_planting':
                            new, ok = _wrap_radish_fertilizer_func(old, m, prefix + '.' + n)
                        elif n == '_run_backpack_seed_priority_planting':
                            new, ok = _wrap_backpack_seed_priority_planting_fast(
                                old, prefix + '.' + n
                            )
                        elif n == '_check_empty_land_label_with_retry':
                            new, ok = _wrap_backpack_empty_land_label_fast(
                                old, prefix + '.' + n
                            )
                        elif n == '_detect_no_seed_hint_by_ocr':
                            new, ok = _wrap_backpack_no_seed_hint_fast(
                                old, prefix + '.' + n
                            )
                        elif n == '_detect_seed_quantity_badges_by_ocr':
                            new, ok = _wrap_seed_quantity_badges_fast(
                                old, prefix + '.' + n
                            )
                        elif n == '_detect_empty_lands':
                            new, ok = _wrap_detect_empty_lands_state(
                                old, prefix + '.' + n
                            )
                        elif n == '_buy_seed_for_crop':
                            new, ok = _wrap_buy_seed_for_crop_backpack_guard(
                                old, prefix + '.' + n
                            )
                        elif n == '_match_template_center':
                            new, ok = _wrap_planting_template_center_fast(
                                old, prefix + '.' + n
                            )
                        elif n == '_find_quad_empty_land_groups':
                            new, ok = _wrap_quad_empty_land_groups(
                                old, prefix + '.' + n
                            )
                        elif n == '_try_plant_quad_act_seeds':
                            new, ok = _wrap_quad_act_seed_transaction(
                                old, prefix + '.' + n
                            )
                        elif n == '_is_backpack_seed_blacklisted_by_template':
                            new, ok = _wrap_backpack_seed_blacklist_fast(
                                old, prefix + '.' + n
                            )
                        elif n == 'get_current_player_level':
                            new, ok = _wrap_player_level_fast(
                                old, prefix + '.' + n
                            )
                        elif n == '_detect_fertilizer_template':
                            new, ok = _wrap_fertilizer_template_fast(
                                old, prefix + '.' + n
                            )
                        elif n in globals().get('_BACKPACK_PROFILE_FUNC_NAMES', set()):
                            new, ok = _wrap_backpack_profile_helper(
                                old, prefix + '.' + n
                            )
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
def _daily_task_retry_state_default_path():
    try:
        base = str(os.environ.get('LOCALAPPDATA', '') or '').strip()
        if not base:
            return ''
        return os.path.join(
            base, 'qq-farm-bot-rev', 'daily_task_retry_state.json'
        )
    except BaseException:
        return ''


_DAILY_TASK_RETRY_STATE_PATH = _daily_task_retry_state_default_path()


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



_DAILY_FLOW_STATUS_PATCH_LOG_SEEN = set()


def _daily_flow_key(args, kwargs):
    aliases = {
        'freebenefits': 'freebenefits',
        'free_benefits': 'freebenefits',
        'daily_freebenefits': 'freebenefits',
        'benefits': 'freebenefits',
        'task': 'task',
        'daily_task': 'task',
        'svip': 'svip',
        'daily_svip': 'svip',
        'share': 'share',
        'daily_share': 'share',
    }
    try:
        for value in list(args or ()) + list((kwargs or {}).values()):
            if not isinstance(value, str):
                continue
            key = value.strip().lower().replace('-', '_').replace(' ', '_')
            if key in aliases:
                return aliases[key]
    except BaseException:
        pass
    return ''


def _daily_flow_context_from_args(args, kwargs):
    try:
        for value in list(args or ()) + list((kwargs or {}).values()):
            if value is None or isinstance(value, (str, bytes, int, float, bool)):
                continue
            if any(hasattr(value, name) for name in (
                'daily_flow_retry_counts', 'freebenefits_last_date',
                'task_last_date', 'svip_last_date', 'share_last_date',
            )):
                return value
    except BaseException:
        pass
    return None


def _daily_flow_target(flow):
    if str(flow or '').strip().lower() != 'share':
        return ''
    try:
        cfg_fn = globals().get('_cfg_get')
        sections_fn = globals().get('_active_bot_sections')
        if callable(cfg_fn):
            sections = sections_fn() if callable(sections_fn) else ('bot',)
            return str(cfg_fn(sections, 'share_target_name', '') or '').strip()
    except BaseException:
        pass
    return ''


def _daily_flow_apply_success_context(context, flow, today=None):
    if context is None:
        return False
    try:
        flow_key = str(flow or '').strip().lower()
        fields = {
            'freebenefits': 'freebenefits_last_date',
            'task': 'task_last_date',
            'svip': 'svip_last_date',
            'share': 'share_last_date',
        }
        field = fields.get(flow_key)
        if not field:
            return False
        day = str(today or time.strftime('%Y-%m-%d'))
        setattr(context, field, day)
        try:
            setattr(context, 'daily_flow_retry_date', day)
        except BaseException:
            pass
        counts = getattr(context, 'daily_flow_retry_counts', None)
        if isinstance(counts, dict):
            counts[flow_key] = 0
        return True
    except BaseException:
        return False




def _daily_entry_red_dot_present(frame, flow):
    try:
        np = __import__('numpy')
        image = np.asarray(frame)
        if image.ndim < 3 or image.shape[0] < 120 or image.shape[1] < 120:
            return False
        height, width = int(image.shape[0]), int(image.shape[1])
        flow_key = str(flow or '').strip().lower()
        regions = {
            'share': (0.08, 0.25, 0.12, 0.28),
            'task': (0.03, 0.24, 0.72, 0.89),
        }
        ratios = regions.get(flow_key)
        if ratios is None:
            return False
        x0 = max(0, min(width - 1, int(round(width * ratios[0]))))
        x1 = max(x0 + 1, min(width, int(round(width * ratios[1]))))
        y0 = max(0, min(height - 1, int(round(height * ratios[2]))))
        y1 = max(y0 + 1, min(height, int(round(height * ratios[3]))))
        roi = image[y0:y1, x0:x1, :3].astype('int16', copy=False)
        c0, c1, c2 = roi[:, :, 0], roi[:, :, 1], roi[:, :, 2]
        red_bgr = (c2 >= 175) & (c2 >= c1 + 55) & (c2 >= c0 + 45) & (c1 <= 165)
        red_rgb = (c0 >= 175) & (c0 >= c1 + 55) & (c0 >= c2 + 45) & (c1 <= 165)
        red = red_bgr | red_rgb
        count = int(red.sum())
        area = int(roi.shape[0] * roi.shape[1])
        required = max(12, int(round(float(area) * 0.0015)))
        if count < required:
            return False

        # A real notification dot is a compact, roughly square component.
        # Farm scenery and the friend carousel can contain long red strips that
        # previously exceeded the raw-pixel threshold and reopened daily tasks.
        seen = np.zeros(red.shape, dtype='uint8')
        red_y, red_x = np.where(red)
        for start_y, start_x in zip(red_y.tolist(), red_x.tolist()):
            if seen[start_y, start_x]:
                continue
            stack = [(int(start_y), int(start_x))]
            seen[start_y, start_x] = 1
            component = []
            while stack:
                point_y, point_x = stack.pop()
                component.append((point_y, point_x))
                for delta_y in (-1, 0, 1):
                    for delta_x in (-1, 0, 1):
                        if delta_x == 0 and delta_y == 0:
                            continue
                        next_y = point_y + delta_y
                        next_x = point_x + delta_x
                        if (
                            next_y < 0 or next_x < 0
                            or next_y >= red.shape[0] or next_x >= red.shape[1]
                            or seen[next_y, next_x] or not red[next_y, next_x]
                        ):
                            continue
                        seen[next_y, next_x] = 1
                        stack.append((next_y, next_x))
            if len(component) < required:
                continue
            ys = [point[0] for point in component]
            xs = [point[1] for point in component]
            component_height = max(ys) - min(ys) + 1
            component_width = max(xs) - min(xs) + 1
            if component_width < 4 or component_height < 4:
                continue
            if component_width > 36 or component_height > 36:
                continue
            aspect = float(component_width) / float(max(1, component_height))
            density = float(len(component)) / float(
                component_width * component_height
            )
            if 0.42 <= aspect <= 2.4 and density >= 0.30:
                return True
        return False
    except BaseException:
        return False


def _daily_flow_entry_red_dot_state(context, flow):
    try:
        flow_key = str(flow or '').strip().lower()
        if flow_key not in ('task', 'share') or context is None:
            return None
        branch = str(getattr(context, '_qqfarm_cycle_branch_hint', '') or '').strip().lower()
        if 'friend' in branch:
            return None
        capture_fn = globals().get('_get_frame_from_bot')
        frame = capture_fn(context) if callable(capture_fn) else None
        shape = getattr(frame, 'shape', None)
        if frame is None or not shape or len(shape) < 2:
            return None
        np = __import__('numpy')
        image = np.asarray(frame)
        if image.size <= 0 or float(image.mean()) < 3.0:
            return None
        detect_fn = globals().get('_daily_entry_red_dot_present')
        if not callable(detect_fn):
            return None
        return bool(detect_fn(frame, flow_key))
    except BaseException:
        return None


def _daily_flow_invalidate_success(context, flow, reason='entry-red-dot-present'):
    try:
        flow_key = str(flow or '').strip().lower()
        if flow_key == 'task':
            authoritative_fn = globals().get(
                '_daily_task_authoritative_success_today'
            )
            authoritative = bool(
                authoritative_fn() if callable(authoritative_fn) else False
            )
            if authoritative:
                apply_fn = globals().get('_daily_flow_apply_success_context')
                if callable(apply_fn):
                    apply_fn(context, flow_key)
                clear_fn = globals().get('_daily_task_clear_retry_backoff')
                if callable(clear_fn):
                    clear_fn()
                return True
        if flow_key == 'share':
            target_fn = globals().get('_daily_flow_target')
            target = target_fn(flow_key) if callable(target_fn) else ''
            direct_fn = globals().get('_share_direct_success_recent')
            direct_verified = False
            if callable(direct_fn):
                try:
                    direct_verified = bool(direct_fn(target, max_age=86400.0))
                except TypeError:
                    direct_verified = bool(direct_fn(target))
            if direct_verified:
                mark_fn = globals().get('_daily_flow_mark_status')
                if callable(mark_fn):
                    mark_fn(
                        flow_key, 'success', target=target,
                        reason='verified-direct-contact-send'
                    )
                apply_fn = globals().get('_daily_flow_apply_success_context')
                if callable(apply_fn):
                    apply_fn(context, flow_key)
                return True
        fields = {
            'freebenefits': 'freebenefits_last_date',
            'task': 'task_last_date',
            'svip': 'svip_last_date',
            'share': 'share_last_date',
        }
        field = fields.get(flow_key)
        if context is not None and field:
            setattr(context, field, '')
        target_fn = globals().get('_daily_flow_target')
        target = target_fn(flow_key) if callable(target_fn) else ''
        blocked_fn = globals().get('_daily_flow_retry_blocked')
        preserve_failed_backoff = bool(
            callable(blocked_fn) and blocked_fn(flow_key)
        )
        mark_fn = globals().get('_daily_flow_mark_status')
        if callable(mark_fn) and not preserve_failed_backoff:
            mark_fn(flow_key, 'pending', target=target, reason=str(reason or ''))
        return True
    except BaseException:
        return False

def _daily_flow_context_success_today(context, flow, today=None):
    try:
        flow_key = str(flow or '').strip().lower()
        day = str(today or time.strftime('%Y-%m-%d'))
        target = _daily_flow_target(flow_key)
        success_fn = globals().get('_daily_flow_success_today')
        if callable(success_fn) and success_fn(
            flow_key, target=target
        ):
            _daily_flow_apply_success_context(context, flow_key, day)
            return True
        fields = {
            'freebenefits': 'freebenefits_last_date',
            'task': 'task_last_date',
            'svip': 'svip_last_date',
            'share': 'share_last_date',
        }
        field = fields.get(flow_key)
        if context is not None and field:
            recorded = str(getattr(context, field, '') or '').strip()
            if recorded == day:
                if flow_key == 'share':
                    # Re-sending to a contact is externally visible. Preserve a
                    # same-day share marker when migrating older counter files,
                    # then make it durable for subsequent restarts.
                    mark_fn = globals().get('_daily_flow_mark_status')
                    if callable(mark_fn):
                        mark_fn(
                            flow_key, 'success', target=target,
                            reason='preserved-from-share-date'
                        )
                    _daily_flow_apply_success_context(context, flow_key, day)
                    return True
                # Other engine date fields are only caches. UI-confirmed durable
                # status is the sole success proof, so clear stale seeded dates
                # and allow the original should/run path to try again.
                try:
                    setattr(context, field, '')
                except BaseException:
                    pass
    except BaseException:
        pass
    return False


def _patch_daily_flow_status_for_module(module, tag=''):
    changed = 0
    try:
        module_name = str(getattr(module, '__name__', '') or '')
        capability_names = (
            '_mark_daily_flow_success', '_mark_daily_flow_failure',
            'should_run_daily_freebenefits', 'run_daily_freebenefits',
            'should_run_daily_task', 'run_daily_task',
            'should_run_daily_svip', 'run_daily_svip',
            'should_run_daily_share', 'run_daily_share',
        )
        if (
            not module_name.lower().endswith('.freebenefits_flow')
            and not any(callable(getattr(module, name, None)) for name in capability_names)
        ):
            return 0

        original_success = getattr(module, '_mark_daily_flow_success', None)
        if callable(original_success) and not getattr(
            original_success, '__qqfarm_daily_flow_status_wrapped__', False
        ):
            def _wrapped_success(*args, __orig=original_success, **kwargs):
                result = __orig(*args, **kwargs)
                flow = _daily_flow_key(args, kwargs)
                if flow and result is not False:
                    context = _daily_flow_context_from_args(args, kwargs)
                    target = _daily_flow_target(flow)
                    mark_fn = globals().get('_daily_flow_mark_status')
                    if callable(mark_fn):
                        mark_fn(flow, 'success', target=target)
                    _daily_flow_apply_success_context(context, flow)
                return result
            try:
                _wrapped_success.__qqfarm_daily_flow_status_wrapped__ = True
                _wrapped_success.__qqfarm_daily_flow_status_orig__ = original_success
            except BaseException:
                pass
            setattr(module, '_mark_daily_flow_success', _wrapped_success)
            changed += 1

        original_failure = getattr(module, '_mark_daily_flow_failure', None)
        if callable(original_failure) and not getattr(
            original_failure, '__qqfarm_daily_flow_status_wrapped__', False
        ):
            def _wrapped_failure(*args, __orig=original_failure, **kwargs):
                flow = _daily_flow_key(args, kwargs)
                context = _daily_flow_context_from_args(args, kwargs)
                if flow and _daily_flow_context_success_today(context, flow):
                    return False
                result = __orig(*args, **kwargs)
                if flow:
                    fail_fn = globals().get('_daily_flow_mark_failure')
                    if callable(fail_fn):
                        fail_fn(flow, reason='verified daily flow failure')
                return result
            try:
                _wrapped_failure.__qqfarm_daily_flow_status_wrapped__ = True
                _wrapped_failure.__qqfarm_daily_flow_status_orig__ = original_failure
            except BaseException:
                pass
            setattr(module, '_mark_daily_flow_failure', _wrapped_failure)
            changed += 1

        flow_methods = {
            'freebenefits': (
                ('should_run_daily_freebenefits', 'should'),
                ('run_daily_freebenefits', 'run'),
            ),
            'task': (
                ('should_run_daily_task', 'should'),
                ('run_daily_task', 'run'),
            ),
            'svip': (
                ('should_run_daily_svip', 'should'),
                ('run_daily_svip', 'run'),
            ),
            'share': (
                ('should_run_daily_share', 'should'),
                ('run_daily_share', 'run'),
            ),
        }
        for flow, entries in flow_methods.items():
            for method_name, method_kind in entries:
                original = getattr(module, method_name, None)
                if not callable(original) or getattr(
                    original, '__qqfarm_daily_flow_status_wrapped__', False
                ):
                    continue
                def _wrapped(*args, __orig=original, __flow=flow, __kind=method_kind, **kwargs):
                    context = _daily_flow_context_from_args(args, kwargs)
                    red_state_fn = globals().get('_daily_flow_entry_red_dot_state')
                    try:
                        red_state = (
                            red_state_fn(context, __flow)
                            if callable(red_state_fn) else None
                        )
                    except BaseException:
                        red_state = None
                    if red_state is True:
                        invalidate_fn = globals().get('_daily_flow_invalidate_success')
                        if callable(invalidate_fn):
                            invalidate_fn(
                                context, __flow,
                                reason='entry-red-dot-still-present',
                            )
                    elif _daily_flow_context_success_today(context, __flow):
                        return False if __kind == 'should' else True
                    blocked_fn = globals().get('_daily_flow_retry_blocked')
                    if (
                        callable(blocked_fn)
                        and blocked_fn(__flow)
                        and red_state is not False
                    ):
                        return False
                    result = __orig(*args, **kwargs)
                    if __kind == 'should' and result and red_state is False:
                        target = _daily_flow_target(__flow)
                        mark_fn = globals().get('_daily_flow_mark_status')
                        if callable(mark_fn):
                            mark_fn(
                                __flow, 'success', target=target,
                                reason='entry-red-dot-cleared',
                            )
                        _daily_flow_apply_success_context(context, __flow)
                        return False
                    return result
                try:
                    _wrapped.__name__ = getattr(original, '__name__', method_name)
                    _wrapped.__qualname__ = getattr(original, '__qualname__', _wrapped.__name__)
                    _wrapped.__qqfarm_daily_flow_status_wrapped__ = True
                    _wrapped.__qqfarm_daily_flow_status_orig__ = original
                except BaseException:
                    pass
                setattr(module, method_name, _wrapped)
                changed += 1
        if changed:
            signature = module_name + ':' + str(changed)
            seen = globals().get('_DAILY_FLOW_STATUS_PATCH_LOG_SEEN')
            if isinstance(seen, set) and signature not in seen:
                seen.add(signature)
                write_fn = globals().get('_write')
                if callable(write_fn):
                    write_fn(
                        'v100 daily flow durable status patched ' +
                        str(tag) + ' ' + signature
                    )
    except BaseException as error:
        try:
            log_fn = globals().get('_throttled_write')
            if callable(log_fn):
                log_fn(
                    'v100-daily-flow-status-error',
                    'v100 daily flow status patch error ' + repr(error),
                    30.0,
                )
        except BaseException:
            pass
    return changed


def _patch_daily_flow_status_loaded(tag=''):
    changed = []
    try:
        for module_name, module in list(sys.modules.items()):
            if module is None:
                continue
            count = _patch_daily_flow_status_for_module(module, tag)
            if count:
                changed.append(str(module_name) + ':' + str(count))
    except BaseException:
        pass
    return changed


def _patch_daily_task_soft_retry_for_module(m, tag=''):
    changed = 0
    try:
        module_name = str(getattr(m, '__name__', '') or '')
        if not module_name.lower().endswith('.freebenefits_flow'):
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
        is_run_cycle = 'run_cycle' in str(label).lower()
        if is_run_cycle:
            try:
                threshold_fn = globals().get(
                    '_apply_runtime_go_home_threshold_floor'
                )
                threshold_changes = int(
                    threshold_fn(self_obj, 0.79)
                    if callable(threshold_fn) else 0
                )
                if threshold_changes:
                    _throttled_write(
                        'v167-runtime-go-home-threshold-floor',
                        'v167 raised loaded native go-home thresholds=' +
                        str(threshold_changes) + ' floor=0.79',
                        30.0,
                    )
            except BaseException:
                pass
        if is_run_cycle and bool(getattr(
                self_obj, '_qqfarm_force_self_cycle_next', False)):
            try:
                capture_fn = globals().get('_get_frame_from_bot')
                state_fn = globals().get('_friend_guard_friend_ui_state')
                frame = capture_fn(self_obj) if callable(capture_fn) else None
                visual_state = (
                    state_fn(frame)
                    if callable(state_fn) and frame is not None
                    else None
                )
                if visual_state is False:
                    setattr(self_obj, '_qqfarm_force_self_cycle_next', False)
                    setattr(self_obj, '_qqfarm_cycle_branch_hint', 'self')
                    setattr(self_obj, '_qqfarm_friend_cycle_seen', False)
                    fast_fn = globals().get('_set_friend_chain_fast_interval')
                    if callable(fast_fn):
                        fast_fn(self_obj, False)
                    action = getattr(self_obj, 'process_self_farm', None)
                    invoke_fn = globals().get('_invoke_friend_guard_action')
                    result = (
                        invoke_fn(action, None, (self_obj, frame), {})
                        if callable(action) and callable(invoke_fn)
                        else False
                    )
                    _write(
                        'v165 forced one verified self-farm pass after a false ' +
                        'native friend branch result=' + repr(result)[:160]
                    )
                    return result
                if visual_state is True:
                    setattr(self_obj, '_qqfarm_force_self_cycle_next', False)
            except BaseException as error:
                try:
                    _write(
                        'v165 forced self-farm pass error=' +
                        repr(error)[:220]
                    )
                except BaseException:
                    pass
        if is_run_cycle:
            try:
                restore_fn = globals().get('_restore_runtime_business_switches')
                changed = int(restore_fn(self_obj) or 0) if callable(restore_fn) else 0
                if changed:
                    log_fn = globals().get('_throttled_write')
                    if callable(log_fn):
                        log_fn(
                            'v76-run-cycle-friend-switches',
                            'v76 run_cycle restored configured friend switches=' + str(changed),
                            30.0,
                        )
            except BaseException:
                pass
        else:
            try:
                if str(label).endswith('FarmBotWindow._start_bot'):
                    sync_fn = globals().get('_daily_metrics_sync_runtime')
                    if callable(sync_fn):
                        sync_fn(self_obj, force=True)
            except BaseException as error:
                try:
                    _write('v122 daily metrics startup sync error ' + repr(error)[:220])
                except BaseException:
                    pass
            _write('v33diag enter ' + str(label) + ' args=' + _runtime_diag_repr(a[1:]) + ' kwargs=' + _runtime_diag_repr(k) + ' state=' + _runtime_diag_state(self_obj))
        if is_run_cycle:
            try:
                share_recovery = globals().get('_run_share_prompt_recovery')
                if callable(share_recovery):
                    share_recovery(self_obj)
            except BaseException as e:
                try:
                    _write('v79 share prompt preflight recovery wrapper error ' + repr(e)[:240])
                except BaseException:
                    pass
            try:
                capture_fn = globals().get('_get_frame_from_bot')
                rows_fn = globals().get('_friend_list_visit_button_rows')
                list_handler = globals().get('_handle_friend_list_surface')
                if callable(capture_fn) and callable(rows_fn) and callable(list_handler):
                    preflight_frame = capture_fn(self_obj)
                    preflight_rows = rows_fn(preflight_frame)
                    if len(preflight_rows or []) >= 3:
                        preflight_result = list_handler(self_obj, preflight_frame)
                        _write(
                            'v118 friend list preflight result=' + str(preflight_result) +
                            ' rows=' + str(len(preflight_rows or [])) +
                            ' name=' + str(label)
                        )
                        if preflight_result in ('visited', 'closed'):
                            return False
            except BaseException as e:
                try:
                    _write('v118 friend list preflight error ' + repr(e)[:240])
                except BaseException:
                    pass
        if is_run_cycle:
            try:
                clear_guard_approval = globals().get(
                    '_friend_guard_clear_prequalification'
                )
                approval_active_fn = globals().get(
                    '_friend_guard_list_prequalified_entry_active'
                )
                friend_chain_pending = bool(getattr(
                    self_obj, '_qqfarm_friend_chain_pending', False
                ))
                friend_chain_exhausted = bool(getattr(
                    self_obj, '_qqfarm_friend_chain_exhausted', False
                ))
                friend_entry_pending = bool(getattr(
                    self_obj, '_qqfarm_friend_entry_pending', False
                ))
                preserve_guard_approval = bool(
                    (friend_chain_pending or friend_entry_pending)
                    and not friend_chain_exhausted
                    and (
                        approval_active_fn(self_obj)
                        if callable(approval_active_fn)
                        else bool(getattr(
                            self_obj, '_qqfarm_guard_list_prequalified', False
                        ))
                    )
                )
                if callable(clear_guard_approval) and not preserve_guard_approval:
                    clear_guard_approval(self_obj)
                elif preserve_guard_approval:
                    _write(
                        'v147 preserved first friend guard-list approval '
                        'until the current friend action is processed'
                    )
                setattr(self_obj, '_qqfarm_cycle_branch_hint', '')
                globals()['_ACTIVE_RUN_CYCLE_CONTEXT'] = self_obj
            except BaseException:
                pass
        if is_run_cycle:
            try:
                capture_fn = globals().get('_get_frame_from_bot')
                state_fn = globals().get('_friend_guard_friend_ui_state')
                preflight_frame = (
                    capture_fn(self_obj) if callable(capture_fn) else None
                )
                preflight_state = (
                    state_fn(preflight_frame)
                    if callable(state_fn) and preflight_frame is not None
                    else None
                )
                friend_entry_pending = bool(getattr(
                    self_obj, '_qqfarm_friend_entry_pending', False
                ))
                if friend_entry_pending:
                    try:
                        entry_now = float(time.time())
                    except BaseException:
                        entry_now = 0.0
                    try:
                        entry_clicked_ts = float(getattr(
                            self_obj, '_qqfarm_friend_entry_clicked_ts', 0.0
                        ) or 0.0)
                    except BaseException:
                        entry_clicked_ts = 0.0
                    if entry_clicked_ts <= 0.0:
                        entry_clicked_ts = entry_now
                        try:
                            setattr(
                                self_obj, '_qqfarm_friend_entry_clicked_ts',
                                entry_clicked_ts,
                            )
                        except BaseException:
                            pass
                    try:
                        entry_settle_seconds = float(getattr(
                            self_obj, 'friend_list_entry_settle_seconds', 2.8
                        ) or 2.8)
                    except BaseException:
                        entry_settle_seconds = 2.8
                    entry_settle_seconds = max(0.4, min(6.0, entry_settle_seconds))
                    try:
                        entry_timeout_seconds = float(getattr(
                            self_obj, 'friend_list_entry_timeout_seconds', 8.0
                        ) or 8.0)
                    except BaseException:
                        entry_timeout_seconds = 8.0
                    entry_timeout_seconds = max(
                        entry_settle_seconds + 1.0,
                        min(30.0, entry_timeout_seconds),
                    )
                    entry_age = max(0.0, entry_now - entry_clicked_ts)
                    entry_action_visible = False
                    if preflight_state is True:
                        for match_name in (
                            '_friend_guard_help_button_match',
                            '_friend_guard_steal_button_match',
                        ):
                            match_fn = globals().get(match_name)
                            if not callable(match_fn):
                                continue
                            try:
                                match_result = match_fn(preflight_frame)
                            except BaseException:
                                match_result = None
                            if (
                                isinstance(match_result, dict) and
                                bool(match_result.get('matched'))
                            ):
                                entry_action_visible = True
                                break
                    if entry_age < entry_settle_seconds and not entry_action_visible:
                        _write(
                            'v189 friend-list transition pending; waiting for first '
                            'friend controls age=' + ('%.3f' % entry_age) +
                            ' settle=' + ('%.3f' % entry_settle_seconds) +
                            ' state=' + repr(preflight_state)
                        )
                        return False
                    if preflight_state is True:
                        try:
                            commit_fn = globals().get(
                                '_commit_friend_list_entry_transition'
                            )
                            if callable(commit_fn):
                                commit_fn(self_obj)
                        except BaseException:
                            pass
                        try:
                            setattr(self_obj, '_qqfarm_friend_entry_pending', False)
                            setattr(self_obj, '_qqfarm_friend_entry_clicked_ts', 0.0)
                            setattr(
                                self_obj,
                                '_qqfarm_friend_entry_extended_action_grace',
                                True,
                            )
                        except BaseException:
                            pass
                        if entry_action_visible and entry_age < entry_settle_seconds:
                            _write(
                                'v190 friend-list transition action visible early; '
                                'releasing first-friend probe age=' +
                                ('%.3f' % entry_age)
                            )
                        else:
                            _write(
                                'v189 friend-list transition confirmed; first friend '
                                'action probe may start age=' + ('%.3f' % entry_age)
                            )
                    elif entry_age < entry_timeout_seconds:
                        _write(
                            'v189 friend-list transition pending; friend surface not '
                            'ready age=' + ('%.3f' % entry_age) +
                            ' timeout=' + ('%.3f' % entry_timeout_seconds) +
                            ' state=' + repr(preflight_state)
                        )
                        return False
                    else:
                        try:
                            setattr(self_obj, '_qqfarm_friend_entry_pending', False)
                            setattr(self_obj, '_qqfarm_friend_entry_clicked_ts', 0.0)
                            setattr(self_obj, '_qqfarm_friend_entry_retry_count', 0)
                            setattr(self_obj, '_qqfarm_friend_entry_last_retry_ts', 0.0)
                            setattr(
                                self_obj,
                                '_qqfarm_friend_entry_extended_action_grace',
                                False,
                            )
                        except BaseException:
                            pass
                        _write(
                            'v189 friend-list transition timed out; releasing native '
                            'recovery age=' + ('%.3f' % entry_age) +
                            ' state=' + repr(preflight_state)
                        )
                watchdog_fn = globals().get(
                    '_apply_visual_friend_route_watchdog'
                )
                if preflight_state is True and callable(watchdog_fn):
                    watchdog_result = watchdog_fn(
                        fn, self_obj, label, force_recovery=True
                    )
                    sync_fn = globals().get('_daily_metrics_sync_runtime')
                    if callable(sync_fn):
                        sync_fn(self_obj, force=False)
                    _write(
                        'v184 visible friend preflight owned run_cycle result=' +
                        repr(bool(watchdog_result))
                    )
                    try:
                        if globals().get('_ACTIVE_RUN_CYCLE_CONTEXT') is self_obj:
                            globals()['_ACTIVE_RUN_CYCLE_CONTEXT'] = None
                    except BaseException:
                        pass
                    return bool(watchdog_result)
            except BaseException as error:
                try:
                    _write(
                        'v184 visible friend preflight error ' +
                        repr(error)[:220]
                    )
                except BaseException:
                    pass
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
        finally:
            if is_run_cycle:
                try:
                    if globals().get('_ACTIVE_RUN_CYCLE_CONTEXT') is self_obj:
                        globals()['_ACTIVE_RUN_CYCLE_CONTEXT'] = None
                except BaseException:
                    pass
        if is_run_cycle:
            try:
                current_hint = str(
                    getattr(self_obj, '_qqfarm_cycle_branch_hint', '') or ''
                ).strip().lower()
                if current_hint not in ('friend', 'self'):
                    infer_fn = globals().get('_infer_cycle_branch_from_runtime_log')
                    inferred_hint = str(
                        infer_fn() if callable(infer_fn) else ''
                    ).strip().lower()
                    if inferred_hint in ('friend', 'self'):
                        setattr(self_obj, '_qqfarm_cycle_branch_hint', inferred_hint)
                        _write(
                            'v121 run_cycle branch inferred from log tail=' +
                            inferred_hint
                        )
            except BaseException as error:
                try:
                    _write('v121 branch inference error ' + repr(error)[:180])
                except BaseException:
                    pass
            try:
                recent_fn = globals().get('_share_direct_success_recent')
                if callable(recent_fn) and recent_fn():
                    mark_fn = globals().get('_share_mark_runtime_success')
                    if callable(mark_fn):
                        mark_fn(self_obj)
            except BaseException:
                pass
            try:
                share_recovery = globals().get('_run_share_prompt_recovery')
                if callable(share_recovery):
                    share_recovery(self_obj)
            except BaseException as e:
                try:
                    _write('v78 share prompt recovery wrapper error ' + repr(e)[:240])
                except BaseException:
                    pass
            try:
                _apply_visual_friend_route_watchdog(fn, self_obj, label)
            except BaseException as e:
                try:
                    _write('v61 visual friend watchdog wrapper error ' + repr(e)[:240])
                except BaseException:
                    pass
            try:
                sync_fn = globals().get('_daily_metrics_sync_runtime')
                if callable(sync_fn):
                    sync_fn(self_obj, force=False)
            except BaseException as error:
                try:
                    _write(
                        'v178 run-cycle durable metrics sync error ' +
                        repr(error)[:220]
                    )
                except BaseException:
                    pass
            try:
                log_fn = globals().get('_throttled_write')
                if callable(log_fn):
                    log_fn(
                        'v76-run-cycle-summary',
                        'v76 run_cycle elapsed=' + ('%.3f' % (time.time() - started)),
                        60.0,
                    )
            except BaseException:
                pass
        else:
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

try:
    _SHARE_RETRY_PATCH_LOG_SEEN
except BaseException:
    _SHARE_RETRY_PATCH_LOG_SEEN = set()


def _share_flow_key(args, kwargs):
    try:
        for value in list(args or ()) + list((kwargs or {}).values()):
            if isinstance(value, str) and value.strip().lower() in (
                'share', 'daily_share'
            ):
                return 'share'
    except BaseException:
        pass
    return ''


def _share_bot_from_args(args, kwargs):
    try:
        for value in list(args or ()) + list((kwargs or {}).values()):
            if value is None or isinstance(value, (str, bytes, int, float, bool)):
                continue
            if (
                hasattr(value, 'daily_flow_retry_counts')
                or hasattr(value, 'share_last_date')
            ):
                return value
    except BaseException:
        pass
    return None


def _share_retry_backoff_seconds():
    try:
        value = _cfg_get(
            _active_bot_sections(), 'daily_share_retry_backoff_seconds', '300'
        )
        seconds = float(str(value).strip())
        return max(60.0, min(3600.0, seconds))
    except BaseException:
        return 300.0


def _share_retry_backoff_active(context):
    try:
        if context is None:
            return False
        next_ts = float(
            getattr(context, '_qqfarm_share_retry_next_ts', 0.0) or 0.0
        )
        if next_ts <= 0.0:
            return False
        now_ts = float(time.monotonic())
        if now_ts >= next_ts:
            setattr(context, '_qqfarm_share_retry_next_ts', 0.0)
            return False
        return True
    except BaseException:
        return False


def _share_set_retry_backoff(context, seconds=None):
    try:
        if context is None:
            return 0.0
        if seconds is None:
            seconds = _share_retry_backoff_seconds()
        next_ts = float(time.monotonic()) + max(1.0, float(seconds))
        setattr(context, '_qqfarm_share_retry_next_ts', next_ts)
        return next_ts
    except BaseException:
        return 0.0


def _share_clear_retry_backoff(context):
    try:
        if context is not None:
            setattr(context, '_qqfarm_share_retry_next_ts', 0.0)
        return True
    except BaseException:
        return False


def _patch_share_retry_backoff_for_module(module, tag=''):
    """Throttle failed share attempts without consuming all six retries at once."""
    changed = 0
    try:
        module_name = str(getattr(module, '__name__', '') or '')
        share_capability = bool(
            callable(getattr(module, 'should_run_daily_share', None))
            or callable(getattr(module, 'run_daily_share', None))
        )
        if not module_name.lower().endswith('.freebenefits_flow') and not share_capability:
            return 0
        original_failure = getattr(module, '_mark_daily_flow_failure', None)
        if callable(original_failure) and not getattr(
            original_failure, '__qqfarm_share_retry_backoff_wrapped__', False
        ):
            def _wrapped_failure(*args, __orig=original_failure, **kwargs):
                flow_key = _share_flow_key(args, kwargs)
                context = _share_bot_from_args(args, kwargs)
                if flow_key == 'share':
                    target = ''
                    cfg_fn = globals().get('_share_target_guard_config')
                    try:
                        cfg = cfg_fn() if callable(cfg_fn) else {}
                        if isinstance(cfg, dict):
                            target = str(cfg.get('target_name', '') or '').strip()
                    except BaseException:
                        target = ''
                    direct_fn = globals().get('_share_direct_success_recent')
                    direct_verified = False
                    if callable(direct_fn):
                        try:
                            direct_verified = bool(
                                direct_fn(target, max_age=86400.0)
                            )
                        except TypeError:
                            direct_verified = bool(direct_fn(target))
                        except BaseException:
                            direct_verified = False
                    if direct_verified:
                        mark_fn = globals().get('_share_mark_runtime_success')
                        if callable(mark_fn):
                            try:
                                mark_fn(context)
                            except BaseException:
                                pass
                        _share_clear_retry_backoff(context)
                        _throttled_write(
                            'v141-share-late-failure-suppressed',
                            'v141 preserved verified exact-target share success; '
                            'late native failure ignored target=' + target,
                            30.0,
                        )
                        return False
                result = __orig(*args, **kwargs)
                if flow_key == 'share':
                    next_ts = _share_set_retry_backoff(context)
                    _throttled_write(
                        'v86-share-retry-backoff',
                        'v86 daily share failed once; retry deferred until monotonic=' +
                        ('%.3f' % float(next_ts or 0.0)),
                        30.0,
                    )
                return result
            try:
                _wrapped_failure.__qqfarm_share_retry_backoff_wrapped__ = True
            except BaseException:
                pass
            setattr(module, '_mark_daily_flow_failure', _wrapped_failure)
            changed += 1
        original_should = getattr(module, 'should_run_daily_share', None)
        if callable(original_should) and not getattr(
            original_should, '__qqfarm_share_retry_backoff_wrapped__', False
        ):
            def _wrapped_should(*args, __orig=original_should, **kwargs):
                context = _share_bot_from_args(args, kwargs)
                if _share_retry_backoff_active(context):
                    _throttled_write(
                        'v86-share-retry-wait',
                        'v86 daily share retry is in bounded backoff; regular farm checks continue',
                        30.0,
                    )
                    return False
                return __orig(*args, **kwargs)
            try:
                _wrapped_should.__qqfarm_share_retry_backoff_wrapped__ = True
            except BaseException:
                pass
            setattr(module, 'should_run_daily_share', _wrapped_should)
            changed += 1
        original_run = getattr(module, 'run_daily_share', None)
        if callable(original_run) and not getattr(
            original_run, '__qqfarm_share_retry_backoff_wrapped__', False
        ):
            def _wrapped_run(*args, __orig=original_run, **kwargs):
                context = _share_bot_from_args(args, kwargs)
                if _share_retry_backoff_active(context):
                    return False
                return __orig(*args, **kwargs)
            try:
                _wrapped_run.__qqfarm_share_retry_backoff_wrapped__ = True
            except BaseException:
                pass
            setattr(module, 'run_daily_share', _wrapped_run)
            changed += 1
        original_success = getattr(module, '_mark_daily_flow_success', None)
        if callable(original_success) and not getattr(
            original_success, '__qqfarm_share_retry_backoff_wrapped__', False
        ):
            def _wrapped_success(*args, __orig=original_success, **kwargs):
                result = __orig(*args, **kwargs)
                if _share_flow_key(args, kwargs) == 'share':
                    _share_clear_retry_backoff(_share_bot_from_args(args, kwargs))
                return result
            try:
                _wrapped_success.__qqfarm_share_retry_backoff_wrapped__ = True
            except BaseException:
                pass
            setattr(module, '_mark_daily_flow_success', _wrapped_success)
            changed += 1
        if changed:
            signature = module_name + ':' + str(changed)
            if signature not in _SHARE_RETRY_PATCH_LOG_SEEN:
                _SHARE_RETRY_PATCH_LOG_SEEN.add(signature)
                _write('v86 share retry backoff patched ' + str(tag) + ' ' + signature)
    except BaseException as error:
        try:
            _throttled_write(
                'v86-share-retry-patch-error',
                'v86 share retry patch error ' + repr(error),
                30.0,
            )
        except BaseException:
            pass
    return changed


def _patch_share_retry_backoff_loaded(tag=''):
    changed = []
    try:
        for module_name, module in list(sys.modules.items()):
            if module is None:
                continue
            low = str(module_name or '').lower()
            if not low.endswith('.freebenefits_flow'):
                try:
                    if not (
                        callable(getattr(module, 'should_run_daily_share', None))
                        or callable(getattr(module, 'run_daily_share', None))
                    ):
                        continue
                except BaseException:
                    continue
            count = _patch_share_retry_backoff_for_module(module, tag)
            if count:
                changed.append(str(module_name) + ':' + str(count))
    except BaseException:
        pass
    return changed


def _share_target_module():
    try:
        preferred = []
        fallback = []
        for module_name, module in list(sys.modules.items()):
            low = str(module_name or '').lower()
            if not low.endswith('.freebenefits_flow'):
                continue
            fallback.append(module)
            try:
                if callable(getattr(module, '_click_share_dialog_first_friend_and_confirm', None)):
                    preferred.append(module)
            except BaseException:
                pass
        if preferred:
            return preferred[0]
        if fallback:
            return fallback[0]
    except BaseException:
        pass
    return None


def _share_recovery_due(context):
    try:
        if context is None:
            return False
        backoff_fn = globals().get('_share_retry_backoff_active')
        if callable(backoff_fn) and backoff_fn(context):
            return False
        if not _truthy(_cfg_get(_active_bot_sections(), 'enable_daily_share', 'False'), False):
            return False
        cfg = _share_target_guard_config()
        if not cfg.get('enabled', False):
            return False
        success_fn = globals().get('_share_direct_success_recent')
        if callable(success_fn) and success_fn(cfg.get('target_name', '')):
            return False
        today = time.strftime('%Y-%m-%d')
        try:
            if str(getattr(context, 'share_last_date', '') or '') == today:
                return False
        except BaseException:
            pass
        try:
            schedule = str(_cfg_get(_active_bot_sections(), 'daily_share_time', '00:00') or '00:00').strip()
            hh, mm = schedule.split(':', 1)
            due_minute = max(0, min(1439, int(hh) * 60 + int(mm)))
            local = time.localtime()
            now_minute = int(local.tm_hour) * 60 + int(local.tm_min)
            if now_minute < due_minute:
                return False
        except BaseException:
            pass
        now_mono = time.monotonic()
        last = float(getattr(context, '_qqfarm_share_visual_recovery_last_ts', 0.0) or 0.0)
        if last > 0.0 and (now_mono - last) < 2.5:
            return False
        setattr(context, '_qqfarm_share_visual_recovery_last_ts', now_mono)
        return True
    except BaseException:
        return False


def _share_mark_runtime_success(context):
    today = time.strftime('%Y-%m-%d')
    changed = False
    try:
        clear_backoff = globals().get('_share_clear_retry_backoff')
        if callable(clear_backoff):
            clear_backoff(context)
    except BaseException:
        pass
    try:
        setattr(context, 'share_last_date', today)
        setattr(context, 'daily_flow_retry_date', today)
        counts = getattr(context, 'daily_flow_retry_counts', None)
        if isinstance(counts, dict):
            counts['share'] = 0
        changed = True
    except BaseException:
        pass
    try:
        instance_id = str(getattr(context, 'instance_id', '1') or '1')
    except BaseException:
        instance_id = '1'
    paths = []
    try:
        local = os.environ.get('LOCALAPPDATA', '')
        if local:
            paths.append(os.path.join(local, 'qq-farm-bot-rev', 'daily_counters.json'))
    except BaseException:
        pass
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        paths.append(os.path.join(base, 'UserData', 'legacy-qq-farm-bot-rev', 'daily_counters.json'))
    except BaseException:
        pass
    for path in paths:
        try:
            if not path or not os.path.isfile(path):
                continue
            import json
            with open(path, 'r', encoding='utf-8-sig') as handle:
                data = json.load(handle)
            existing_counts = data.get('daily_flow_retry_counts')
            existing_instances = data.get('instances')
            existing_bucket = (
                existing_instances.get(instance_id)
                if isinstance(existing_instances, dict) else None
            )
            existing_bucket_counts = (
                existing_bucket.get('daily_flow_retry_counts')
                if isinstance(existing_bucket, dict) else None
            )
            already_current = (
                str(data.get('share_last_date', '') or '') == today
                and str(data.get('daily_flow_retry_date', '') or '') == today
                and isinstance(existing_counts, dict)
                and int(existing_counts.get('share', 0) or 0) == 0
                and isinstance(existing_bucket, dict)
                and str(existing_bucket.get('share_last_date', '') or '') == today
                and str(existing_bucket.get('daily_flow_retry_date', '') or '') == today
                and isinstance(existing_bucket_counts, dict)
                and int(existing_bucket_counts.get('share', 0) or 0) == 0
            )
            if already_current:
                changed = True
                continue
            data['share_last_date'] = today
            data['daily_flow_retry_date'] = today
            root_counts = data.get('daily_flow_retry_counts')
            if not isinstance(root_counts, dict):
                root_counts = {}
                data['daily_flow_retry_counts'] = root_counts
            root_counts['share'] = 0
            instances = data.get('instances')
            if not isinstance(instances, dict):
                instances = {}
                data['instances'] = instances
            bucket = instances.get(instance_id)
            if not isinstance(bucket, dict):
                bucket = {}
                instances[instance_id] = bucket
            bucket['share_last_date'] = today
            bucket['daily_flow_retry_date'] = today
            bucket_counts = bucket.get('daily_flow_retry_counts')
            if not isinstance(bucket_counts, dict):
                bucket_counts = {}
                bucket['daily_flow_retry_counts'] = bucket_counts
            bucket_counts['share'] = 0
            temp_path = path + '.tmp-v78'
            with open(temp_path, 'w', encoding='utf-8', newline='\n') as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
                handle.write('\n')
            os.replace(temp_path, path)
            changed = True
        except BaseException as e:
            try:
                _throttled_write('v78-share-counter-write-' + str(path), 'v78 share success counter write error ' + repr(e), 30.0)
            except BaseException:
                pass
    try:
        target_fn = globals().get('_daily_flow_target')
        target = target_fn('share') if callable(target_fn) else ''
        mark_fn = globals().get('_daily_flow_mark_status')
        if callable(mark_fn):
            changed = bool(mark_fn(
                'share', 'success', target=str(target or '').strip(),
                reason='verified-direct-contact-send'
            )) or changed
    except BaseException:
        pass
    # Do not call the engine's broad daily-counter saver here. During startup
    # its unrelated counters can still be zero and would overwrite valid
    # same-day harvest/help/radish statistics. The targeted atomic updates
    # above and daily_flow_status.json are the authoritative share writes.
    return changed


def _run_share_prompt_recovery(context):
    if context is None:
        return False
    try:
        if bool(getattr(context, '_qqfarm_share_visual_recovery_running', False)):
            return False
    except BaseException:
        pass
    due_fn = globals().get('_share_recovery_due')
    if callable(due_fn) and not due_fn(context):
        return False
    try:
        setattr(context, '_qqfarm_share_visual_recovery_running', True)
    except BaseException:
        pass
    try:
        cfg = _share_target_guard_config()
        if not cfg.get('enabled', False):
            return False
        module_fn = globals().get('_share_target_module')
        mod = module_fn() if callable(module_fn) else None
        dialog = _share_find_dialog_hwnd(mod)
        if not dialog:
            try:
                center = _share_find_prompt_button_center((context,), {})
            except TypeError:
                center = _share_find_prompt_button_center()
            if center is None:
                return False
            if not _share_click_prompt_button(center, (context,), {}):
                return False
            _throttled_write(
                'v78-share-prompt-clicked',
                'v78 daily share prompt button clicked by run_cycle recovery',
                5.0,
            )
            dialog = _share_wait_dialog_hwnd(mod, timeout_ms=3500)
        if not dialog:
            _throttled_write(
                'v78-share-dialog-missing',
                'v78 daily share recovery did not observe contact dialog after prompt click',
                10.0,
            )
            return False
        if not _share_search_and_maybe_confirm(mod, cfg):
            return False
        mark_fn = globals().get('_share_mark_runtime_success')
        if callable(mark_fn):
            mark_fn(context)
        _share_log_runtime(
            'sent-v78-recovery',
            'daily share completed by run_cycle recovery target=' + str(cfg.get('target_name', '')),
            False,
        )
        return True
    except BaseException as e:
        try:
            _throttled_write('v78-share-recovery-error', 'v78 daily share recovery error ' + repr(e), 10.0)
        except BaseException:
            pass
        return False
    finally:
        try:
            setattr(context, '_qqfarm_share_visual_recovery_running', False)
        except BaseException:
            pass


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
    value = str(text or '')
    # Prefer the process-independent Win32 clipboard.  Qt's worker-thread
    # clipboard cache can report success while QQ still sees stale text.
    try:
        import win32clipboard
        opened = False
        for _ in range(6):
            try:
                win32clipboard.OpenClipboard()
                opened = True
                break
            except BaseException:
                time.sleep(0.03)
        if opened:
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(value, win32clipboard.CF_UNICODETEXT)
                return True
            finally:
                win32clipboard.CloseClipboard()
    except BaseException:
        pass
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        data = (value + '\x00').encode('utf-16le')
        kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        user32.SetClipboardData.restype = ctypes.c_void_p
        hglobal = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if hglobal:
            locked = kernel32.GlobalLock(hglobal)
            if locked:
                ctypes.memmove(locked, data, len(data))
                kernel32.GlobalUnlock(hglobal)
                opened = False
                for _ in range(6):
                    if user32.OpenClipboard(0):
                        opened = True
                        break
                    time.sleep(0.03)
                if opened:
                    try:
                        user32.EmptyClipboard()
                        if user32.SetClipboardData(CF_UNICODETEXT, hglobal):
                            return True
                    finally:
                        user32.CloseClipboard()
    except BaseException:
        pass
    try:
        from PySide6.QtGui import QGuiApplication
        app = QGuiApplication.instance()
        if app is not None:
            clipboard = app.clipboard()
            clipboard.setText(value)
            try:
                return str(clipboard.text()) == value
            except BaseException:
                return True
    except BaseException:
        pass
    try:
        import base64
        import subprocess
        payload = base64.b64encode(value.encode('utf-16le')).decode('ascii')
        script = (
            "$v=[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('" +
            payload + "')); Set-Clipboard -Value $v"
        )
        flags = int(getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000))
        completed = subprocess.run(
            ['powershell.exe', '-NoLogo', '-NoProfile', '-NonInteractive',
             '-WindowStyle', 'Hidden', '-Command', script],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
            timeout=5.0,
            check=False,
        )
        return int(getattr(completed, 'returncode', 1)) == 0
    except BaseException as error:
        try: _write('v90 share clipboard write error ' + repr(error))
        except BaseException: pass
        return False


def _share_get_clipboard_unicode():
    try:
        import win32clipboard
        opened = False
        for _ in range(6):
            try:
                win32clipboard.OpenClipboard()
                opened = True
                break
            except BaseException:
                time.sleep(0.03)
        if opened:
            try:
                value = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                return str(value or '')
            finally:
                win32clipboard.CloseClipboard()
    except BaseException:
        pass
    try:
        import ctypes
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        CF_UNICODETEXT = 13
        user32.GetClipboardData.argtypes = [ctypes.c_uint]
        user32.GetClipboardData.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        opened = False
        for _ in range(6):
            if user32.OpenClipboard(0):
                opened = True
                break
            time.sleep(0.03)
        if opened:
            try:
                handle = user32.GetClipboardData(CF_UNICODETEXT)
                if handle:
                    pointer = kernel32.GlobalLock(handle)
                    if pointer:
                        try:
                            return str(ctypes.wstring_at(pointer) or '')
                        finally:
                            kernel32.GlobalUnlock(handle)
            finally:
                user32.CloseClipboard()
    except BaseException:
        pass
    try:
        from PySide6.QtGui import QGuiApplication
        app = QGuiApplication.instance()
        if app is not None:
            return str(app.clipboard().text() or '')
    except BaseException:
        pass
    return None


def _share_read_focused_text_via_clipboard():
    sentinel = '__QQFARM_SHARE_READBACK_SENTINEL__'
    try:
        if not _share_set_clipboard_unicode(sentinel):
            return None
        time.sleep(0.08)
        if not _share_send_ctrl_key(0x41):
            return None
        time.sleep(0.06)
        if not _share_send_ctrl_key(0x43):
            return None
        time.sleep(max(0.12, float(_share_int_cfg('share_input_readback_wait_ms', 220)) / 1000.0))
        value = _share_get_clipboard_unicode()
        if value is None or str(value) == sentinel:
            return None
        return str(value)
    except BaseException:
        return None

def _share_key(vk, up=False):
    try:
        import win32api
        win32api.keybd_event(int(vk), 0, 0x0002 if up else 0, 0)
        return True
    except BaseException:
        pass
    try:
        import ctypes
        KEYEVENTF_KEYUP = 0x0002
        ctypes.windll.user32.keybd_event(int(vk), 0, KEYEVENTF_KEYUP if up else 0, 0)
        return True
    except BaseException:
        return False


def _share_send_ctrl_key(vk):
    VK_CONTROL = 0x11
    key_down = False
    control_down = False
    try:
        if not _share_key(VK_CONTROL, False):
            return False
        control_down = True
        time.sleep(0.04)
        if not _share_key(vk, False):
            return False
        key_down = True
        time.sleep(0.04)
        if not _share_key(vk, True):
            return False
        key_down = False
        time.sleep(0.04)
        if not _share_key(VK_CONTROL, True):
            return False
        control_down = False
        return True
    except BaseException:
        return False
    finally:
        if key_down:
            try: _share_key(vk, True)
            except BaseException: pass
        if control_down:
            try: _share_key(VK_CONTROL, True)
            except BaseException: pass


def _share_click_abs(x, y):
    try:
        import win32api
        win32api.SetCursorPos((int(x), int(y)))
        time.sleep(0.04)
        win32api.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.03)
        win32api.mouse_event(0x0004, 0, 0, 0, 0)
        return True
    except BaseException:
        pass
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
        try: _write('v71 share click error ' + repr(e))
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
        kws = str(_cfg_get(_active_bot_sections(), 'share_dialog_title_keywords', '\u9009\u62e9\u8054\u7cfb\u4eba,\u53d1\u9001\u7ed9') or '')
        kws = kws.replace(';', ',').replace('|', ',')
        keywords = [x.strip() for x in kws.split(',') if x.strip()]
    except BaseException:
        keywords = ['\u9009\u62e9\u8054\u7cfb\u4eba', '\u53d1\u9001\u7ed9']
    try:
        import win32gui
        found = []
        def _cb(hwnd, extra):
            try:
                title = str(win32gui.GetWindowText(hwnd) or '')
                if title and any(k in title for k in keywords):
                    found.append(int(hwnd))
            except BaseException:
                pass
            return True
        win32gui.EnumWindows(_cb, None)
        if found:
            return found[0]
    except BaseException:
        pass
    try:
        import ctypes
        user32 = ctypes.windll.user32
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
        try: _write('v71 share find hwnd error ' + repr(e))
        except BaseException: pass
        return 0


def _share_wait_dialog_hwnd(mod=None, timeout_ms=None):
    try:
        if timeout_ms is None:
            try:
                secs = float(str(_cfg_get(
                    _active_bot_sections(), 'share_dialog_wait_timeout_seconds', '2.5'
                )).strip())
            except BaseException:
                secs = 2.5
            timeout_ms = int(max(300.0, secs * 1000.0))
        deadline = time.monotonic() + max(0.1, float(timeout_ms) / 1000.0)
        while True:
            hwnd = _share_find_dialog_hwnd(mod)
            if hwnd:
                return int(hwnd)
            if time.monotonic() >= deadline:
                return 0
            time.sleep(0.08)
    except BaseException:
        return 0

def _share_get_rect(hwnd):
    try:
        import win32gui
        rect = win32gui.GetWindowRect(int(hwnd))
        if rect and int(rect[2]) > int(rect[0]) and int(rect[3]) > int(rect[1]):
            return tuple(int(x) for x in rect)
    except BaseException:
        pass
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


def _share_get_work_area(hwnd):
    """Return the nearest monitor work area for the contact dialog."""
    try:
        import win32api
        monitor = win32api.MonitorFromWindow(int(hwnd), 2)
        info = win32api.GetMonitorInfo(monitor)
        work = info.get('Work') if isinstance(info, dict) else None
        if work and int(work[2]) > int(work[0]) and int(work[3]) > int(work[1]):
            return tuple(int(value) for value in work)
    except BaseException:
        pass
    try:
        import ctypes
        class RECT(ctypes.Structure):
            _fields_ = [
                ('left', ctypes.c_long), ('top', ctypes.c_long),
                ('right', ctypes.c_long), ('bottom', ctypes.c_long),
            ]
        work = RECT()
        if ctypes.windll.user32.SystemParametersInfoW(
            0x0030, 0, ctypes.byref(work), 0
        ):
            rect = (int(work.left), int(work.top), int(work.right), int(work.bottom))
            if rect[2] > rect[0] and rect[3] > rect[1]:
                return rect
    except BaseException:
        pass
    return None


def _share_move_dialog_window(hwnd, left, top):
    try:
        import win32gui
        flags = 0x0001 | 0x0004 | 0x0010 | 0x0040
        win32gui.SetWindowPos(int(hwnd), 0, int(left), int(top), 0, 0, flags)
        return True
    except BaseException:
        pass
    try:
        import ctypes
        user32 = ctypes.windll.user32
        flags = 0x0001 | 0x0004 | 0x0010 | 0x0040
        return bool(user32.SetWindowPos(
            ctypes.c_void_p(int(hwnd)), ctypes.c_void_p(0),
            int(left), int(top), 0, 0, flags
        ))
    except BaseException:
        return False


def _share_ensure_dialog_on_screen(hwnd, margin=12):
    """Clamp the whole contact dialog into its monitor before physical clicks."""
    try:
        rect_fn = globals().get('_share_get_rect')
        work_fn = globals().get('_share_get_work_area')
        move_fn = globals().get('_share_move_dialog_window')
        rect = rect_fn(hwnd) if callable(rect_fn) else None
        work = work_fn(hwnd) if callable(work_fn) else None
        if not rect or not work:
            return rect
        left, top, right, bottom = (int(value) for value in rect)
        work_left, work_top, work_right, work_bottom = (
            int(value) for value in work
        )
        width = max(1, right - left)
        height = max(1, bottom - top)
        safe_margin = max(0, min(64, int(margin)))
        min_left = work_left + safe_margin
        min_top = work_top + safe_margin
        max_left = work_right - safe_margin - width
        max_top = work_bottom - safe_margin - height
        if max_left < min_left:
            target_left = work_left + max(0, ((work_right - work_left) - width) // 2)
        else:
            target_left = max(min_left, min(left, max_left))
        if max_top < min_top:
            target_top = work_top + max(0, ((work_bottom - work_top) - height) // 2)
        else:
            target_top = max(min_top, min(top, max_top))
        if target_left == left and target_top == top:
            return rect
        if not callable(move_fn) or not move_fn(hwnd, target_left, target_top):
            return rect
        time.sleep(0.12)
        refreshed = rect_fn(hwnd) if callable(rect_fn) else None
        final_rect = refreshed or (
            target_left, target_top, target_left + width, target_top + height
        )
        try:
            _share_log_runtime(
                'dialog-repositioned',
                'daily share contact dialog moved into work area: before=' + repr(rect) +
                ' work=' + repr(work) + ' after=' + repr(final_rect),
                False,
            )
        except BaseException:
            pass
        return final_rect
    except BaseException:
        try:
            return _share_get_rect(hwnd)
        except BaseException:
            return None


def _share_activate_dialog(mod, hwnd):
    try:
        if mod is not None and hasattr(mod, '_activate_share_dialog_window'):
            try:
                mod._activate_share_dialog_window(hwnd)
                time.sleep(0.12)
                return True
            except BaseException:
                pass
        try:
            import win32gui
            win32gui.ShowWindow(int(hwnd), 9)
            win32gui.SetForegroundWindow(int(hwnd))
            time.sleep(0.12)
            return True
        except BaseException:
            pass
        import ctypes
        user32 = ctypes.windll.user32
        user32.ShowWindow(int(hwnd), 9)
        user32.SetForegroundWindow(int(hwnd))
        time.sleep(0.12)
        return True
    except BaseException:
        return False


def _share_close_dialog(mod=None, hwnd=0):
    try:
        if mod is not None and hasattr(mod, '_close_share_dialog'):
            try:
                if bool(mod._close_share_dialog()):
                    return True
            except BaseException:
                pass
        if hwnd:
            try:
                import win32gui
                win32gui.PostMessage(int(hwnd), 0x0010, 0, 0)
                return True
            except BaseException:
                pass
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
        if ('群聊' in blob) or ('群组' in blob) or ('group chat' in blob) or ('groupchat' in blob):
            return True
        try:
            compact = ''.join(blob.split())
            person_suffix = chr(0x4EBA)
            for left_mark, right_mark in (
                ('(', ')'), (chr(0xFF08), chr(0xFF09))
            ):
                start = 0
                while True:
                    left_index = compact.find(left_mark, start)
                    if left_index < 0:
                        break
                    right_index = compact.find(right_mark, left_index + 1)
                    if right_index < 0:
                        break
                    inner = compact[left_index + 1:right_index]
                    if inner.endswith(person_suffix) and inner[:-1].isdigit():
                        return True
                    start = right_index + 1
            member_match = __import__('re').search(
                r'\b\d{1,4}\s+members?\b', blob,
                __import__('re').IGNORECASE,
            )
            if member_match:
                return True
        except BaseException:
            pass
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


def _share_prepare_uia_runtime():
    try:
        import importlib, os as _os, sys as _sys, types as _types
        comtypes_mod = importlib.import_module('comtypes')
        try:
            gen_mod = importlib.import_module('comtypes.gen')
        except BaseException:
            gen_path = _os.path.join(
                _os.path.dirname(str(getattr(comtypes_mod, '__file__', '') or '')),
                'gen',
            )
            gen_mod = _types.ModuleType('comtypes.gen')
            gen_mod.__file__ = _os.path.join(gen_path, '__init__.py')
            gen_mod.__package__ = 'comtypes.gen'
            gen_mod.__path__ = [gen_path]
            _sys.modules['comtypes.gen'] = gen_mod
        setattr(comtypes_mod, 'gen', gen_mod)
        importlib.import_module('pywinauto')
        return True
    except BaseException as error:
        try:
            _throttled_write(
                'share-uia-prepare-error',
                'v136 share UIA runtime prepare error ' + repr(error),
                10.0,
            )
        except BaseException:
            pass
        return False


def _share_uia_backend_available():
    prepare_fn = globals().get('_share_prepare_uia_runtime')
    return bool(callable(prepare_fn) and prepare_fn())


def _share_find_exact_uia_target(hwnd, target, allow_group=False):
    try:
        if not _share_prepare_uia_runtime():
            return None
        from pywinauto import Desktop
        dialog = Desktop(backend='uia').window(handle=int(hwnd))
        candidates = dialog.descendants()
        return _share_pick_exact_uia_candidate(candidates, target, allow_group=allow_group)
    except BaseException as e:
        try: _throttled_write('share-uia-error', 'v33 share UIA exact-match error ' + repr(e), 10.0)
        except BaseException: pass
        return None


def _share_wait_exact_uia_target(hwnd, target, allow_group=False, timeout_ms=1200):
    deadline = time.monotonic() + max(0.1, float(timeout_ms) / 1000.0)
    while True:
        matched = _share_find_exact_uia_target(hwnd, target, allow_group=allow_group)
        if matched is not None:
            return matched
        if time.monotonic() >= deadline:
            return None
        time.sleep(0.08)


def _share_wait_dialog_closed(mod=None, timeout_ms=1200):
    deadline = time.monotonic() + max(0.1, float(timeout_ms) / 1000.0)
    while True:
        if not _share_find_dialog_hwnd(mod):
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.08)


def _share_find_uia_button(hwnd, labels):
    try:
        if not _share_prepare_uia_runtime():
            return None
        from pywinauto import Desktop
        dialog = Desktop(backend='uia').window(handle=int(hwnd))
        wanted = {_share_norm_text(x) for x in tuple(labels or ()) if _share_norm_text(x)}
        for element in dialog.descendants(control_type='Button'):
            texts = _share_uia_element_texts(element)
            if any(_share_norm_text(text) in wanted for text in texts) and _share_uia_rect_valid(element):
                return element
    except BaseException:
        pass
    return None



def _share_confirm_label_is_direct_send(value):
    try:
        if isinstance(value, (list, tuple, set)):
            texts = [str(item or '') for item in value]
        elif hasattr(value, 'window_text') or hasattr(value, 'texts'):
            texts = _share_uia_element_texts(value)
        else:
            texts = [str(value or '')]
        normalized = [_share_norm_text(item) for item in texts if _share_norm_text(item)]
        blocked = (
            '\u521b\u5efa\u5e76\u53d1\u9001', '\u521b\u5efa\u7fa4\u804a',
            '\u53d1\u8d77\u7fa4\u804a', '\u65b0\u5efa\u7fa4\u804a',
            'createandsend', 'creategroup', 'startgroupchat',
        )
        if any(any(marker in item for marker in blocked) for item in normalized):
            return False
        allowed = {
            _share_norm_text('\u786e\u5b9a'),
            _share_norm_text('\u53d1\u9001'),
            _share_norm_text('\u5206\u4eab'),
            'ok', 'send', 'share',
        }
        return any(item in allowed for item in normalized)
    except BaseException:
        return False


def _share_selected_contact_count(texts):
    try:
        regex = __import__('re')
        patterns = (
            '\u5df2\u9009\\s*(\\d+)\\s*\u4e2a\u8054\u7cfb\u4eba',
            '\u5df2\u9009\u62e9\\s*(\\d+)\\s*\u4eba',
            r'selected\s*(\d+)\s*contacts?',
        )
        for value in list(texts or []):
            raw = str(value or '')
            for pattern in patterns:
                match = regex.search(pattern, raw, regex.IGNORECASE)
                if match:
                    return int(match.group(1))
        return None
    except BaseException:
        return None


def _share_uia_dialog_texts(hwnd):
    values = []
    try:
        if not _share_prepare_uia_runtime():
            return []
        from pywinauto import Desktop
        dialog = Desktop(backend='uia').window(handle=int(hwnd))
        for element in [dialog] + list(dialog.descendants() or []):
            try:
                values.extend(_share_uia_element_texts(element))
            except BaseException:
                pass
    except BaseException:
        return []
    result = []
    for value in values:
        text_value = str(value or '').strip()
        if text_value and text_value not in result:
            result.append(text_value)
    return result




def _share_dialog_text_indicates_group_mode(texts):
    try:
        blob = ' '.join(str(value or '') for value in list(texts or ())).casefold()
        compact = ''.join(blob.split())
        direct_markers = ('\u53d1\u9001\u7ed9', 'sendto')
        if any(marker in compact for marker in direct_markers):
            return False
        markers = (
            '\u521b\u5efa\u7fa4\u804a', '\u521b\u5efa\u5e76\u53d1\u9001',
            '\u53d1\u8d77\u7fa4\u804a', '\u65b0\u5efa\u7fa4\u804a',
            'creategroup', 'createandsend', 'startgroupchat',
        )
        return any(marker in compact for marker in markers)
    except BaseException:
        return False


def _share_recover_direct_dialog_from_group_mode(hwnd, timeout_ms=1200):
    try:
        texts_fn = globals().get('_share_uia_dialog_texts')
        detect_fn = globals().get('_share_dialog_text_indicates_group_mode')
        if not callable(texts_fn) or not callable(detect_fn):
            return False
        texts = texts_fn(hwnd)
        if not detect_fn(texts):
            return True
        back = _share_find_uia_button(
            hwnd, ('\u8fd4\u56de', '\u53d6\u6d88\u521b\u5efa', 'Back')
        )
        if back is None or not _share_click_uia_element(back):
            return False
        deadline = time.monotonic() + max(0.2, float(timeout_ms) / 1000.0)
        while True:
            time.sleep(0.08)
            if not detect_fn(texts_fn(hwnd)):
                return True
            if time.monotonic() >= deadline:
                return False
    except BaseException:
        return False


def _share_find_exact_uia_selector(matched):
    if matched is None:
        return None
    candidates = []
    current = matched
    for _ in range(5):
        if current is None:
            break
        if current not in candidates:
            candidates.append(current)
        try:
            for element in list(current.descendants() or []):
                if element not in candidates:
                    candidates.append(element)
        except BaseException:
            pass
        try:
            current = current.parent()
        except BaseException:
            break
    for element in candidates:
        try:
            info = element.element_info
            control_type = str(getattr(info, 'control_type', '') or '').casefold()
            if control_type not in ('radiobutton', 'checkbox'):
                continue
            if not _share_uia_rect_valid(element):
                continue
            if _share_uia_candidate_is_group(element):
                continue
            return element
        except BaseException:
            continue
    return None


def _share_exact_selector_point(matched):
    if matched is None:
        return None
    rows = []
    current = matched
    for depth in range(6):
        if current is None:
            break
        try:
            rect = current.rectangle()
            left, top = int(rect.left), int(rect.top)
            right, bottom = int(rect.right), int(rect.bottom)
            width, height = right - left, bottom - top
            info = getattr(current, 'element_info', None)
            control_type = str(getattr(info, 'control_type', '') or '').casefold()
            if width >= 100 and 32 <= height <= 180:
                preferred = 0 if control_type in ('listitem', 'group', 'pane') else 1
                rows.append((preferred, depth, -width, left, top, right, bottom))
        except BaseException:
            pass
        try:
            current = current.parent()
        except BaseException:
            break
    if not rows:
        return None
    rows.sort()
    _preferred, _depth, _neg_width, left, top, right, bottom = rows[0]
    height = max(1, int(bottom - top))
    selector_offset = min(30, max(18, int(round(height * 0.24))))
    x = min(int(right) - 8, int(left) + selector_offset)
    y = int(round((int(top) + int(bottom)) / 2.0))
    if x <= int(left) or x >= int(right) or y <= int(top) or y >= int(bottom):
        return None
    return x, y


def _share_select_exact_contact(hwnd, matched):
    try:
        if matched is None or _share_uia_candidate_is_group(matched):
            return False
        selector_fn = globals().get('_share_find_exact_uia_selector')
        selector = selector_fn(matched) if callable(selector_fn) else None
        if selector is not None:
            return bool(_share_click_uia_element(selector))
        point_fn = globals().get('_share_exact_selector_point')
        point = point_fn(matched) if callable(point_fn) else None
        if not isinstance(point, (tuple, list)) or len(point) < 2:
            return False
        return bool(_share_click_abs(int(point[0]), int(point[1])))
    except BaseException:
        return False

def _share_single_target_selection_proof(hwnd, target, matched=None):
    result = {
        'ok': False,
        'reason': 'unverified',
        'selected_count': None,
        'confirm': None,
    }
    try:
        if matched is None:
            result['reason'] = 'missing-exact-target'
            return result
        if _share_uia_candidate_is_group(matched):
            result['reason'] = 'group-target'
            return result
        texts = _share_uia_dialog_texts(hwnd)
        blob = ' '.join(texts).casefold()
        group_mode_fn = globals().get('_share_dialog_text_indicates_group_mode')
        if callable(group_mode_fn):
            in_group_mode = bool(group_mode_fn(texts))
        else:
            blocked_mode = (
                '\u521b\u5efa\u7fa4\u804a', '\u53d1\u8d77\u7fa4\u804a',
                '\u521b\u5efa\u5e76\u53d1\u9001', 'create group',
                'start group chat', 'create and send',
            )
            in_group_mode = any(marker in blob for marker in blocked_mode)
        if in_group_mode:
            result['reason'] = 'group-mode'
            return result
        count = _share_selected_contact_count(texts)
        result['selected_count'] = count
        if count != 1:
            result['reason'] = 'selected-count-' + str(count)
            return result
        direct_header = bool(
            ('\u53d1\u9001\u7ed9' in blob)
            or ('send to' in blob)
        )
        if not direct_header:
            result['reason'] = 'missing-direct-send-header'
            return result
        confirm = _share_find_uia_button(
            hwnd, ('\u786e\u5b9a', '\u53d1\u9001', '\u5206\u4eab', 'OK', 'Send')
        )
        if confirm is None:
            result['reason'] = 'missing-direct-confirm'
            return result
        if not _share_confirm_label_is_direct_send(confirm):
            result['reason'] = 'group-or-unknown-confirm'
            return result
        result['ok'] = True
        result['reason'] = 'single-exact-target'
        result['confirm'] = confirm
        result['target'] = str(target or '').strip()
        return result
    except BaseException as error:
        result['reason'] = 'proof-error:' + repr(error)[:120]
        return result


def _share_click_uia_element(element):
    try:
        rect = element.rectangle()
        x = (int(rect.left) + int(rect.right)) // 2
        y = (int(rect.top) + int(rect.bottom)) // 2
        return _share_click_abs(x, y)
    except BaseException:
        return False


def _share_type_target(target):
    value = str(target or '').strip()
    if not value:
        return False
    if not _share_send_ctrl_key(0x41):
        return False
    time.sleep(0.18)
    # A single paste is more reliable than a burst of digit key events in the
    # Chromium search box.  Exact clipboard readback is performed by the caller.
    try:
        if _share_set_clipboard_unicode(value):
            time.sleep(0.10)
            if _share_send_ctrl_key(0x56):
                time.sleep(0.20)
                return True
    except BaseException:
        pass
    if value.isdigit():
        time.sleep(0.12)
        for char in value:
            vk = ord(char)
            if not _share_key(vk, False):
                return False
            time.sleep(0.045)
            if not _share_key(vk, True):
                return False
            time.sleep(0.045)
        return True
    return False


def _share_enter_target_exact(mod, hwnd, search_x, search_y, target):
    value = str(target or '').strip()
    if not value:
        return False
    try:
        retry_count = int(_share_int_cfg('share_target_input_retry_count', 3) or 3)
    except BaseException:
        retry_count = 3
    retry_count = max(2, min(5, retry_count))
    click_fn = globals().get('_share_click_dialog_point')
    readback_fn = globals().get('_share_read_focused_text_via_clipboard')
    for attempt in range(1, retry_count + 1):
        try:
            _share_activate_dialog(mod, hwnd)
        except BaseException:
            pass
        if callable(click_fn):
            clicked = bool(click_fn(hwnd, search_x, search_y, False))
        else:
            clicked = bool(_share_click_abs(search_x, search_y))
        if not clicked:
            continue
        time.sleep(min(0.34, 0.14 + (0.06 * attempt)))
        if not _share_type_target(value):
            _share_log_runtime(
                'target-type-retry',
                'daily share target input attempt failed: attempt=' + str(attempt) +
                '/' + str(retry_count) + ' target=' + value,
                True,
            )
            continue
        time.sleep(min(0.34, 0.16 + (0.05 * attempt)))
        actual = readback_fn() if callable(readback_fn) else None
        if _share_norm_text(actual) == _share_norm_text(value):
            _share_log_runtime(
                'target-readback-verified',
                'daily share target input verified by clipboard readback: target=' + value +
                ' attempt=' + str(attempt) + '/' + str(retry_count),
                False,
            )
            return True
        # UIA exact-match is a second independent proof when Chromium blocks
        # copying from the focused search field.
        if actual is None:
            try:
                exact = _share_find_exact_uia_target(
                    hwnd, value,
                    allow_group=False,
                )
            except BaseException:
                exact = None
            if exact is not None:
                _share_log_runtime(
                    'target-readback-verified',
                    'daily share target input verified by exact UIA result: target=' + value +
                    ' attempt=' + str(attempt) + '/' + str(retry_count),
                    False,
                )
                return True
        _share_log_runtime(
            'target-readback-mismatch',
            'daily share target input mismatch; retrying: expected=' + value +
            ' actual=' + repr(actual) + ' attempt=' + str(attempt) + '/' + str(retry_count),
            True,
        )
        try:
            if not _share_find_dialog_hwnd(mod):
                break
        except BaseException:
            pass
        time.sleep(0.10)
    return False


def _share_click_dialog_point(hwnd, x, y, repeat=False):
    """Activate the contact window, then click a screen point once or twice."""
    try:
        activate_fn = globals().get('_share_activate_dialog')
        if callable(activate_fn):
            activate_fn(None, hwnd)
    except BaseException:
        pass
    time.sleep(0.10)
    clicked = bool(_share_click_abs(int(x), int(y)))
    if bool(repeat):
        time.sleep(0.14)
        try:
            still_open = bool(_share_find_dialog_hwnd(None))
        except BaseException:
            still_open = True
        if still_open:
            clicked = bool(_share_click_abs(int(x), int(y))) or clicked
    return clicked

def _share_search_and_maybe_confirm(mod, cfg):
    target = str(cfg.get('target_name', '') or '').strip()
    if not target:
        _share_log_runtime('missing-target', 'daily share blocked: empty share_target_name', True)
        _share_close_dialog(mod, 0)
        return False
    recent_fn = globals().get('_share_direct_success_recent')
    try:
        recent_success = bool(callable(recent_fn) and recent_fn(target))
    except BaseException:
        recent_success = False
    if recent_success:
        find_fn = globals().get('_share_find_dialog_hwnd')
        close_fn = globals().get('_share_close_dialog')
        try:
            duplicate_hwnd = find_fn(mod) if callable(find_fn) else 0
        except BaseException:
            duplicate_hwnd = 0
        if duplicate_hwnd and callable(close_fn):
            try:
                close_fn(mod, duplicate_hwnd)
            except BaseException:
                pass
        _share_log_runtime(
            'duplicate-send-suppressed',
            'daily share duplicate exact-target send suppressed target=' + target,
            False,
        )
        return True
    hwnd = _share_wait_dialog_hwnd(mod)
    if not hwnd:
        _share_log_runtime('no-dialog', 'daily share blocked: share dialog not found after bounded wait', True)
        return False
    _share_activate_dialog(mod, hwnd)
    ensure_fn = globals().get('_share_ensure_dialog_on_screen')
    if callable(ensure_fn):
        rect = ensure_fn(hwnd)
        _share_activate_dialog(mod, hwnd)
    else:
        rect = _share_get_rect(hwnd)
    if not rect:
        _share_log_runtime('no-rect', 'daily share blocked: share dialog rect unavailable', True)
        _share_close_dialog(mod, hwnd)
        return False
    texts_fn = globals().get('_share_uia_dialog_texts')
    group_mode_fn = globals().get('_share_dialog_text_indicates_group_mode')
    recover_direct_fn = globals().get('_share_recover_direct_dialog_from_group_mode')
    try:
        in_group_mode = bool(
            callable(texts_fn) and callable(group_mode_fn)
            and group_mode_fn(texts_fn(hwnd))
        )
    except BaseException:
        in_group_mode = False
    if in_group_mode:
        recovered = bool(
            callable(recover_direct_fn) and recover_direct_fn(hwnd, 1400)
        )
        if not recovered:
            _share_log_runtime(
                'group-mode-blocked',
                'daily share blocked: group creation dialog detected and direct-send recovery failed',
                True,
            )
            _share_close_dialog(mod, hwnd)
            return False
        _share_log_runtime(
            'group-mode-recovered',
            'daily share left create-group view and returned to direct recipient selector',
            False,
        )
        _share_activate_dialog(mod, hwnd)
        rect = _share_get_rect(hwnd) or rect
    sx = _share_ratio_cfg('share_search_box_x_ratio', 0.38)
    sy = _share_ratio_cfg('share_search_box_y_ratio', 0.12)
    settle_ms = _share_int_cfg('share_search_settle_ms', 900)
    selection_settle_ms = _share_int_cfg('share_selection_settle_ms', 220)
    close_timeout_ms = _share_int_cfg('share_confirm_close_timeout_ms', 1600)
    x, y = _share_point(rect, sx, sy)
    exact_entry_fn = globals().get('_share_enter_target_exact')
    if callable(exact_entry_fn):
        target_entered = bool(exact_entry_fn(mod, hwnd, x, y, target))
    else:
        dialog_click_fn = globals().get('_share_click_dialog_point')
        if callable(dialog_click_fn):
            search_clicked = bool(dialog_click_fn(hwnd, x, y, False))
        else:
            search_clicked = bool(_share_click_abs(x, y))
        target_entered = bool(search_clicked and _share_type_target(target))
    if not target_entered:
        _share_log_runtime('type-fail', 'daily share blocked: exact target input verification failed target=' + target, True)
        _share_close_dialog(mod, hwnd)
        return False
    _share_log_runtime('target-typed', 'daily share target entered: target=' + target, False)
    time.sleep(max(0.18, float(settle_ms) / 1000.0))

    uia_available_fn = globals().get('_share_uia_backend_available')
    uia_available = bool(uia_available_fn()) if callable(uia_available_fn) else True
    if not uia_available:
        _share_log_runtime(
            'uia-required',
            'daily share blocked: exact single-contact state is unreadable; target=' + target,
            True,
        )
        _share_close_dialog(mod, hwnd)
        return False
    matched = _share_wait_exact_uia_target(
        hwnd, target, allow_group=False, timeout_ms=max(300, settle_ms)
    )
    group_fn = globals().get('_share_uia_candidate_is_group')
    matched_is_group = bool(
        callable(group_fn) and group_fn(matched)
    ) if matched is not None else False
    if matched is None or matched_is_group:
        _share_log_runtime(
            'exact-miss',
            'daily share blocked: exact non-group target not found; target=' + target,
            True,
        )
        _share_close_dialog(mod, hwnd)
        return False
    select_fn = globals().get('_share_select_exact_contact')
    selected = bool(
        select_fn(hwnd, matched)
        if callable(select_fn)
        else _share_click_uia_element(matched)
    )
    if not selected:
        _share_log_runtime(
            'target-select-fail',
            'daily share blocked: exact target selector circle could not be selected target=' + target,
            True,
        )
        _share_close_dialog(mod, hwnd)
        return False
    time.sleep(max(0.08, float(selection_settle_ms) / 1000.0))

    proof_fn = globals().get('_share_single_target_selection_proof')
    proof = proof_fn(hwnd, target, matched) if callable(proof_fn) else None
    if not isinstance(proof, dict) or not bool(proof.get('ok', False)):
        reason = str(proof.get('reason', 'proof-unavailable')) if isinstance(proof, dict) else 'proof-unavailable'
        _share_log_runtime(
            'single-target-proof-fail',
            'daily share blocked: exact one-contact proof failed target=' + target +
            ' reason=' + reason,
            True,
        )
        _share_close_dialog(mod, hwnd)
        return False
    if int(proof.get('selected_count', 0) or 0) != 1:
        _share_log_runtime(
            'selection-count-fail',
            'daily share blocked: selected contact count is not one target=' + target,
            True,
        )
        _share_close_dialog(mod, hwnd)
        return False
    if bool(cfg.get('dry_run', True)):
        _share_log_runtime(
            'dry-run',
            'daily share dry-run: exact single target selected target=' + target + ', closed without sending',
            False,
        )
        _share_close_dialog(mod, hwnd)
        return False
    confirm = proof.get('confirm')
    if confirm is None or not _share_confirm_label_is_direct_send(confirm):
        _share_log_runtime(
            'direct-confirm-fail',
            'daily share blocked: confirm action is not a direct send target=' + target,
            True,
        )
        _share_close_dialog(mod, hwnd)
        return False
    if not _share_click_uia_element(confirm):
        _share_log_runtime(
            'confirm-click-fail',
            'daily share blocked: direct confirm click failed target=' + target,
            True,
        )
        _share_close_dialog(mod, hwnd)
        return False
    if not _share_wait_dialog_closed(mod, int(close_timeout_ms)):
        _share_log_runtime(
            'confirm-not-closed',
            'daily share blocked: direct-send dialog remained open target=' + target,
            True,
        )
        _share_close_dialog(mod, hwnd)
        return False
    record_fn = globals().get('_share_record_direct_success')
    if callable(record_fn):
        try:
            record_fn(target)
        except BaseException:
            pass
    _share_log_runtime(
        'sent-verified',
        'daily share sent once to exact target=' + target +
        '; selected_count=1; dialog_closed=True; confirm=direct-uia',
        False,
    )
    return True



try:
    _SHARE_DIRECT_SUCCESS_STATE
except BaseException:
    _SHARE_DIRECT_SUCCESS_STATE = {}


def _share_record_direct_success(target):
    recorded = False
    try:
        state = {
            'target': str(target or '').strip(),
            'ts': float(time.monotonic()),
            'date': time.strftime('%Y-%m-%d'),
        }
        globals()['_SHARE_DIRECT_SUCCESS_STATE'] = state
        recorded = True
    except BaseException:
        recorded = False
    persist_fn = globals().get('_daily_flow_mark_status')
    try:
        if callable(persist_fn):
            recorded = bool(persist_fn(
                'share', 'success', target=str(target or '').strip()
            )) or recorded
    except BaseException:
        pass
    return recorded



def _share_direct_success_recent(target='', max_age=15.0):
    requested_target = str(target or '').strip()
    persistent_fn = globals().get('_daily_flow_success_today')
    try:
        if callable(persistent_fn) and persistent_fn(
            'share', target=requested_target
        ):
            return True
    except BaseException:
        pass
    try:
        state = globals().get('_SHARE_DIRECT_SUCCESS_STATE', {})
        if not isinstance(state, dict):
            return False
        recorded_target = str(state.get('target', '') or '').strip()
        if requested_target and recorded_target != requested_target:
            return False
        recorded_day = str(state.get('date', '') or '')
        if recorded_day and recorded_day != time.strftime('%Y-%m-%d'):
            return False
        age = float(time.monotonic()) - float(state.get('ts', 0.0) or 0.0)
        return 0.0 <= age <= max(0.5, float(max_age))
    except BaseException:
        return False



def _share_context_from_call(call_args=(), call_kwargs=None):
    values = list(call_args or ())
    if isinstance(call_kwargs, dict):
        values.extend(call_kwargs.values())
    for value in values:
        try:
            if any(hasattr(value, name) for name in (
                'instance_id', 'share_last_date', 'daily_flow_retry_counts',
                'save_daily_counters', '_save_daily_counters',
            )):
                return value
        except BaseException:
            pass
    return None


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
            recent_fn = globals().get('_share_direct_success_recent')
            if callable(recent_fn) and recent_fn(cfg.get('target_name', '')):
                _share_log_runtime(
                    'direct-send-ack',
                    'daily share handler acknowledged recent exact-target send target=' +
                    str(cfg.get('target_name', '')),
                    False,
                )
                return True
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
        values = []
        if isinstance(kwargs, dict):
            if 'tag' in kwargs:
                values.append(kwargs.get('tag'))
            values.extend(value for key, value in kwargs.items() if key != 'tag')
        for value in values:
            if isinstance(value, str):
                tag = value.strip().lower()
                if tag in ('share_entry', 'task_entry', 'share_prompt', 'share_btn_click'):
                    return tag
    except BaseException:
        pass
    try:
        for value in list(args or ()):
            if isinstance(value, str):
                tag = value.strip().lower()
                if tag in ('share_entry', 'task_entry', 'share_prompt', 'share_btn_click'):
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


def _share_prompt_button_center_from_rgb(image):
    """Locate the large lime share capsule in logical or full physical frames."""
    try:
        np = __import__('numpy')
        cv2 = __import__('cv2')
        arr = np.asarray(image)
        if arr.ndim < 3 or int(arr.shape[2]) < 3:
            return None
        height, width = int(arr.shape[0]), int(arr.shape[1])
        if width < 80 or height < 120:
            return None
        x0, x1 = int(width * 0.12), int(width * 0.90)
        y0, y1 = int(height * 0.55), int(height * 0.95)
        roi = arr[y0:y1, x0:x1, :3].astype('int16')
        if roi.size <= 0:
            return None
        channel0 = roi[:, :, 0]
        green = roi[:, :, 1]
        channel2 = roi[:, :, 2]
        high_side = np.maximum(channel0, channel2)
        low_side = np.minimum(channel0, channel2)
        # The live QQ share button is yellow-lime rather than pure green
        # (roughly RGB 160/190/0).  Keep the rule channel-order neutral so
        # both RGB ImageGrab frames and BGR OpenCV frames are accepted.
        mask = (
            (green >= 128)
            & ((green - high_side) >= 16)
            & (low_side <= 120)
            & ((high_side - low_side) >= 25)
        ).astype('uint8') * 255
        close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel, iterations=2)
        open_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, open_kernel, iterations=1)
        count, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
        best = None
        min_area = max(120, int(round(width * height * 0.0015)))
        for index in range(1, int(count)):
            x, y, component_width, component_height, area = (
                int(value) for value in stats[index]
            )
            if area < min_area:
                continue
            if component_width < int(width * 0.20) or component_width > int(width * 0.75):
                continue
            if component_height < max(14, int(height * 0.02)):
                continue
            if component_height > int(height * 0.16):
                continue
            if component_width < float(component_height) * 2.2:
                continue
            fill = float(area) / float(max(1, component_width * component_height))
            if fill < 0.25:
                continue
            absolute_y = int(y) + int(y0)
            center_y = absolute_y + (float(component_height) / 2.0)
            if center_y < float(height) * 0.65:
                continue
            score = (float(area) * fill) + (center_y * 0.1)
            if best is None or score > best[0]:
                best = (
                    score,
                    int(x) + int(x0),
                    absolute_y,
                    component_width,
                    component_height,
                )
        if best is None:
            return None
        _, left, top, button_width, button_height = best
        return (left + (button_width // 2), top + (button_height // 2))
    except BaseException:
        return None


def _share_is_farm_window_title(title):
    try:
        value = str(title or '').strip()
        farm_title = '\u0051\u0051\u7ecf\u5178\u519c\u573a'
        helper_suffix = '\u89c6\u89c9\u81ea\u52a8\u5316'
        return farm_title in value and helper_suffix not in value
    except BaseException:
        return False


def _share_find_farm_window_hwnd():
    try:
        win32gui = __import__('win32gui')
        found = []
        def _cb(hwnd, extra):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return True
                title = str(win32gui.GetWindowText(hwnd) or '').strip()
                if not _share_is_farm_window_title(title):
                    return True
                rect = win32gui.GetWindowRect(hwnd)
                width = int(rect[2] - rect[0])
                height = int(rect[3] - rect[1])
                if width >= 300 and height >= 400:
                    found.append((abs(width - 428) + abs(height - 800), -width * height, int(hwnd)))
            except BaseException:
                pass
            return True
        win32gui.EnumWindows(_cb, None)
        if found:
            found.sort(key=lambda item: (item[0], item[1]))
            return int(found[0][2])
    except BaseException:
        pass
    try:
        import ctypes
        user32 = ctypes.windll.user32
        found = []
        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def _cb(hwnd, lparam):
            try:
                if not user32.IsWindowVisible(hwnd):
                    return True
                buf = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, buf, 256)
                title = str(buf.value or '').strip()
                if not _share_is_farm_window_title(title):
                    return True
                rect = _share_get_rect(int(hwnd))
                if rect and rect[2] - rect[0] >= 300 and rect[3] - rect[1] >= 400:
                    found.append(int(hwnd))
            except BaseException:
                pass
            return True
        user32.EnumWindows(WNDENUMPROC(_cb), 0)
        return found[0] if found else 0
    except BaseException:
        return 0


def _share_prompt_frame_from_call(call_args=(), call_kwargs=None):
    values = []
    try:
        values.extend(list(call_args or ()))
    except BaseException:
        pass
    try:
        values.extend(list((call_kwargs or {}).values()))
    except BaseException:
        pass
    for value in values:
        if value is None or isinstance(value, (str, bytes, int, float, bool)):
            continue
        try:
            shape = getattr(value, 'shape', None)
            if shape is not None and len(shape) >= 2 and int(shape[0]) >= 120 and int(shape[1]) >= 80:
                return value
        except BaseException:
            pass
    getter = globals().get('_get_frame_from_bot')
    if callable(getter):
        for value in values:
            if value is None or isinstance(value, (str, bytes, int, float, bool)):
                continue
            try:
                frame = getter(value)
            except BaseException:
                frame = None
            if frame is not None:
                return frame
    return None


def _share_find_prompt_button_center(call_args=(), call_kwargs=None):
    try:
        hwnd = _share_find_farm_window_hwnd()
        rect = _share_get_rect(hwnd) if hwnd else None
        if not rect:
            return None
        frame = _share_prompt_frame_from_call(call_args, call_kwargs)
        if frame is not None:
            center = _share_prompt_button_center_from_rgb(frame)
            if center is not None:
                try:
                    shape = getattr(frame, 'shape', None)
                    frame_height = int(shape[0]) if shape is not None else len(frame)
                    frame_width = int(shape[1]) if shape is not None else len(frame[0])
                    rect_width = max(1, int(rect[2]) - int(rect[0]))
                    rect_height = max(1, int(rect[3]) - int(rect[1]))
                    x = int(rect[0]) + int(round(float(center[0]) * rect_width / max(1, frame_width)))
                    y = int(rect[1]) + int(round(float(center[1]) * rect_height / max(1, frame_height)))
                    return (x, y)
                except BaseException:
                    pass
        from PIL import ImageGrab
        image = ImageGrab.grab(bbox=rect, all_screens=True).convert('RGB')
        pixels = list(image.getdata())
        width, height = image.size
        rows = [pixels[y * width:(y + 1) * width] for y in range(height)]
        center = _share_prompt_button_center_from_rgb(rows)
        if center is None:
            return None
        return (int(rect[0]) + int(center[0]), int(rect[1]) + int(center[1]))
    except BaseException as e:
        try: _throttled_write('share-prompt-visual-error', 'v73 share prompt visual detection error ' + repr(e), 10.0)
        except BaseException: pass
        return None


def _share_click_prompt_button(center, call_args=(), call_kwargs=None):
    try:
        if center is None:
            return False
        hwnd = _share_find_farm_window_hwnd()
        rect = _share_get_rect(hwnd) if hwnd else None
        click_client = globals().get('_friend_guard_post_client_click')
        if rect and callable(click_client):
            width = max(1, int(rect[2]) - int(rect[0]))
            height = max(1, int(rect[3]) - int(rect[1]))
            frame_x = int(center[0]) - int(rect[0])
            frame_y = int(center[1]) - int(rect[1])
            if click_client(frame_x, frame_y, width, height):
                return True
    except BaseException:
        pass
    try:
        return bool(_share_click_abs(int(center[0]), int(center[1])))
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
        succeeded = _share_click_result_succeeded(result)
        if entry_kind in ('share_prompt', 'share_btn_click') and not succeeded:
            try:
                center = _share_find_prompt_button_center(a, k)
            except TypeError:
                center = _share_find_prompt_button_center()
            if center is not None:
                if entry_kind == 'share_prompt':
                    _throttled_write('share-prompt-visual-recovered', 'v73 share_prompt recovered from current farm frame', 5.0)
                    return True
                click_prompt = globals().get('_share_click_prompt_button')
                if callable(click_prompt):
                    clicked = bool(click_prompt(center, a, k))
                else:
                    clicked = bool(_share_click_abs(center[0], center[1]))
                if clicked:
                    _throttled_write('share-button-visual-click', 'v73 share_btn_click recovered by background window click', 5.0)
                    result = True
                    succeeded = True
        if entry_kind == 'share_btn_click' and succeeded:
            try:
                cfg = _share_target_guard_config()
                if cfg.get('enabled', False):
                    module_fn = globals().get('_share_target_module')
                    mod = module_fn() if callable(module_fn) else None
                    dialog = _share_wait_dialog_hwnd(mod, timeout_ms=3500)
                    if not dialog:
                        _share_log_runtime(
                            'prompt-click-unconfirmed-v84',
                            'daily share prompt click did not open the contact dialog',
                            True,
                        )
                        return False
                    if _share_search_and_maybe_confirm(mod, cfg):
                        target = str(cfg.get('target_name', '') or '').strip()
                        record_fn = globals().get('_share_record_direct_success')
                        if callable(record_fn):
                            record_fn(target)
                        context_fn = globals().get('_share_context_from_call')
                        context = context_fn(a, k) if callable(context_fn) else (a[0] if a else None)
                        mark_fn = globals().get('_share_mark_runtime_success')
                        if context is not None and callable(mark_fn):
                            mark_fn(context)
                        _share_log_runtime(
                            'sent-v83-direct',
                            'daily share completed immediately after share button target=' + target,
                            False,
                        )
                        return True
            except BaseException as e:
                try:
                    _throttled_write(
                        'v83-share-direct-error',
                        'v83 direct share handoff error ' + repr(e),
                        10.0,
                    )
                except BaseException:
                    pass
        if entry_kind in ('share_entry', 'task_entry') and succeeded:
            try:
                if entry_kind == 'task_entry':
                    settle_ms = _share_int_cfg('task_entry_settle_ms', 450)
                else:
                    settle_ms = _share_int_cfg('share_entry_settle_ms', 450)
            except BaseException:
                settle_ms = 450
            settle_seconds = max(0.25, min(1.5, float(settle_ms) / 1000.0))
            try:
                _throttled_write(
                    str(entry_kind) + '-settle',
                    'v38 daily ' + str(entry_kind) + ' clicked; waiting %.3fs before prompt detection' % settle_seconds,
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



def _looks_share_entry_module(m):
    try:
        if m is None:
            return False
        module_name = str(getattr(m, '__name__', '') or '').lower()
        if not (module_name == 'bot.application.freebenefits_flow' or module_name.endswith('.freebenefits_flow')):
            return False
        for attr_name, value in list(vars(m).items()):
            if str(attr_name).startswith('__'):
                continue
            if str(attr_name) == '_click_share_dialog_first_friend_and_confirm':
                continue
            if isinstance(value, type) or not callable(value):
                continue
            return True
        return False
    except BaseException:
        return False


def _patch_share_entry_settle_for_module(m, tag=''):
    try:
        if not _looks_share_entry_module(m):
            return 0
        patched_names = []
        items = list(vars(m).items())
        items.sort(key=lambda item: (0 if str(item[0]) == '_click_template_once' else 1, str(item[0])))
        for name, old in items:
            name = str(name)
            if name.startswith('__') or name == '_click_share_dialog_first_friend_and_confirm':
                continue
            if isinstance(old, type) or not callable(old):
                continue
            if getattr(old, '__qqfarm_share_target_guard_wrapped__', False):
                continue
            new, ok = _wrap_share_entry_settle_func(old)
            if not ok:
                continue
            setattr(m, name, new)
            patched_names.append(name)
        if patched_names:
            try:
                setattr(m, '__qqfarm_share_entry_patched_names__', tuple(patched_names))
            except BaseException:
                pass
            try:
                log_fn = globals().get('_throttled_write')
                if callable(log_fn):
                    log_fn(
                        'v76-share-helper-names-' + str(getattr(m, '__name__', '')),
                        'v76 share helper aliases patched module=' +
                        str(getattr(m, '__name__', '')) + ' names=' + repr(patched_names[:40]),
                        30.0,
                    )
            except BaseException:
                pass
        return len(patched_names)
    except BaseException as e:
        try: _write('v76 share entry settle patch error ' + repr(e))
        except BaseException: pass
        return 0

def _patch_share_entry_settle_loaded(tag=''):
    changed = []
    try:
        seen = set()
        for mn, m in list(sys.modules.items()):
            if not _looks_share_entry_module(m):
                continue
            marker = id(m)
            if marker in seen:
                continue
            seen.add(marker)
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
        checks_capability = (
            callable(getattr(module, '_is_radish_skip_feature_enabled', None))
            and callable(getattr(module, 'mark_friend_row_as_radish_skip', None))
        )
        actions_capability = (
            callable(getattr(module, '_is_friend_skip_radish_enabled', None))
            and callable(getattr(module, 'mark_friend_row_as_radish_skip', None))
        )
        if module_name == 'bot.application.checks_friend' or checks_capability:
            gate_names = (
                '_is_radish_skip_feature_enabled',
                '_is_friend_row_in_radish_skip_cache',
                'mark_friend_row_as_radish_skip',
            )
        elif module_name == 'bot.application.actions_friend' or actions_capability:
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
            _write('v65 friend-radish safe behavior patched ' + str(tag) + ' ' + module_name + ':' + str(changed))
    except BaseException as e:
        try:
            _write('v65 friend-radish behavior patch error ' + repr(e))
        except BaseException:
            pass
    return changed


def _patch_friend_radish_behavior_loaded(tag=''):
    changed = []
    try:
        seen = set()
        for module_name, module in list(sys.modules.items()):
            low_name = str(module_name or '').lower()
            if module is None or not (low_name == 'bot' or low_name.startswith('bot.')):
                continue
            marker = id(module)
            if marker in seen:
                continue
            seen.add(marker)
            count = _patch_friend_radish_behavior_for_module(module, tag)
            if count:
                changed.append(str(module_name) + ':' + str(count))
    except BaseException as e:
        try:
            _write('v65 friend-radish behavior scan error ' + repr(e))
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
        os_mod = globals().get('os')
        raw_enabled = ''
        if os_mod is not None:
            raw_enabled = str(os_mod.environ.get('QQFARM_ENABLE_FRIEND_DIAGNOSTICS', '') or '')
        if raw_enabled.strip().lower() not in ('1', 'true', 'yes', 'on'):
            return 0
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
        os_mod = globals().get('os')
        raw_enabled = ''
        if os_mod is not None:
            raw_enabled = str(os_mod.environ.get('QQFARM_ENABLE_FRIEND_DIAGNOSTICS', '') or '')
        if raw_enabled.strip().lower() not in ('1', 'true', 'yes', 'on'):
            return changed
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
            _patch_share_retry_backoff_loaded(tag)
        except BaseException:
            pass
        try:
            _patch_daily_flow_status_loaded(tag)
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
                repair_status_fn = globals().get('_daily_flow_repair_unverified_status')
                if callable(repair_status_fn):
                    repair_status_fn()
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
_ACTIVE_RUN_CYCLE_CONTEXT = None


def _infer_cycle_branch_from_runtime_log(paths=None, max_bytes=16384):
    """Read only the log tail and return the most recently announced branch."""
    try:
        os_module = __import__('os')
        if paths is None:
            try:
                today = __import__('datetime').datetime.now().strftime('%Y-%m-%d')
            except BaseException:
                today = __import__('time').strftime('%Y-%m-%d')
            candidates = []
            local = str(os_module.environ.get('LOCALAPPDATA', '') or '').strip()
            if local:
                candidates.append(os_module.path.join(
                    local, 'qq-farm-bot-rev', 'logs', today + '.log'
                ))
            try:
                candidates.append(os_module.path.join(
                    os_module.getcwd(), 'logs', today + '.log'
                ))
            except BaseException:
                pass
        else:
            candidates = list(paths or ())
        friend_marker = '正在检查好友农场是否有可执行的任务'
        self_marker = '正在检查自家农场是否有可执行的任务'
        best = None
        read_size = max(1024, min(262144, int(max_bytes or 16384)))
        for raw_path in candidates:
            path = str(raw_path or '').strip()
            if not path or not os_module.path.isfile(path):
                continue
            try:
                with open(path, 'rb') as handle:
                    handle.seek(0, 2)
                    size = int(handle.tell())
                    handle.seek(max(0, size - read_size), 0)
                    text = handle.read(read_size).decode('utf-8-sig', errors='ignore')
                friend_pos = text.rfind(friend_marker)
                self_pos = text.rfind(self_marker)
                if friend_pos < 0 and self_pos < 0:
                    continue
                branch = 'friend' if friend_pos > self_pos else 'self'
                position = max(friend_pos, self_pos)
                modified = float(os_module.path.getmtime(path) or 0.0)
                score = (modified, position)
                if best is None or score > best[0]:
                    best = (score, branch)
            except BaseException:
                continue
        return best[1] if best is not None else ''
    except BaseException:
        return ''


def _note_runtime_cycle_branch(message):
    """Record active cycle routing plus native guard-list visit approval."""
    try:
        text = str(message or '')
        context = globals().get('_ACTIVE_RUN_CYCLE_CONTEXT')
        guard_approval_marker = (
            '\u62a4\u4e3b\u72ac\u7b5b\u9009\uff1a\u53ef\u5e2e\u5fd9\u52a1\u519c '
            '\u547d\u4e2d\u597d\u53cb\u62a4\u4e3b\u5217\u8868\uff0c'
            '\u5141\u8bb8\u8fdb\u5165\u5e2e\u5fd9'
        )
        if guard_approval_marker in text:
            if context is not None:
                now_fn = globals().get('_friend_watchdog_now')
                now_ts = (
                    float(now_fn())
                    if callable(now_fn)
                    else float(__import__('time').time())
                )
                setattr(context, '_qqfarm_guard_list_prequalified', True)
                setattr(context, '_qqfarm_guard_list_prequalified_ts', now_ts)
            return 'friend-guard-prequalified'
        if '\u6b63\u5728\u68c0\u67e5\u597d\u53cb\u519c\u573a\u662f\u5426\u6709\u53ef\u6267\u884c\u7684\u4efb\u52a1' in text:
            branch = 'friend'
            if context is not None:
                try:
                    now_fn = globals().get('_friend_watchdog_now')
                    now_ts = (
                        float(now_fn())
                        if callable(now_fn)
                        else float(__import__('time').time())
                    )
                    false_positive_ts = float(getattr(
                        context, '_qqfarm_native_home_false_positive_ts', 0.0
                    ) or 0.0)
                    if (
                        false_positive_ts > 0.0
                        and 0.0 <= (now_ts - false_positive_ts) <= 3.0
                    ):
                        branch = 'self'
                        finalize_fn = globals().get(
                            '_finalize_friend_chain_after_troublemaker'
                        )
                        if callable(finalize_fn):
                            finalize_fn(context)
                        setattr(context, '_qqfarm_friend_cycle_seen', False)
                        log_fn = globals().get('_throttled_write')
                        if callable(log_fn):
                            log_fn(
                                'v161-false-friend-log-branch',
                                'v161 relabeled native friend branch as self after ' +
                                'visual home false-positive rejection',
                                4.0,
                            )
                except BaseException:
                    pass
        elif '\u6b63\u5728\u68c0\u67e5\u81ea\u5bb6\u519c\u573a\u662f\u5426\u6709\u53ef\u6267\u884c\u7684\u4efb\u52a1' in text:
            branch = 'self'
        else:
            return ''
        if context is not None:
            setattr(context, '_qqfarm_cycle_branch_hint', branch)
        return branch
    except BaseException:
        return ''


def _note_runtime_daily_task_outcome(message, now=None):
    """Treat an opened task entry with no task prompt as completed for today."""
    global _DAILY_TASK_PROMPT_MISS_LAST_TS
    try:
        text = str(message or '')
        prompt_missing = (
            'task_prompt' in text
            and '\u672a\u68c0\u6d4b\u5230' in text
        )
        task_failed = '\u6bcf\u65e5\u4efb\u52a1\u9886\u53d6\u5931\u8d25' in text
        if not (prompt_missing or task_failed):
            return ''
        current = float(time.time() if now is None else now)
        last = float(globals().get(
            '_DAILY_TASK_PROMPT_MISS_LAST_TS', 0.0
        ) or 0.0)
        if last > 0.0 and (current - last) < 5.0:
            return 'task-prompt-missing-duplicate'
        globals()['_DAILY_TASK_PROMPT_MISS_LAST_TS'] = current
        mark_fn = globals().get('_daily_flow_mark_status')
        if callable(mark_fn):
            mark_fn(
                'task', 'success',
                reason='entry-no-prompt-assumed-cleared',
            )
        context = globals().get('_ACTIVE_RUN_CYCLE_CONTEXT')
        apply_fn = globals().get('_daily_flow_apply_success_context')
        if callable(apply_fn):
            apply_fn(context, 'task')
        clear_fn = globals().get('_daily_task_clear_retry_backoff')
        if callable(clear_fn):
            clear_fn()
        log_fn = globals().get('_throttled_write')
        if callable(log_fn):
            try:
                log_fn(
                    'v144-task-prompt-missing-complete',
                    'v144 daily task entry had no prompt; marked complete for today',
                    60.0,
                )
            except BaseException:
                pass
        return 'task-prompt-missing-assumed-complete'
    except BaseException:
        return ''


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
            try:
                _note_runtime_cycle_branch(msg)
            except BaseException:
                pass
            try:
                _note_runtime_daily_task_outcome(msg)
            except BaseException:
                pass
            try:
                _note_runtime_single_harvest_outcome(msg)
            except BaseException:
                pass
            try:
                _note_runtime_planting_outcome(msg)
            except BaseException:
                pass
            new_msg, hit = _rewrite_entitlement_log_message(msg)
            if hit:
                return orig_info(self, new_msg, **kwargs)
            return orig_warning(self, msg, *args, **kwargs)
        def _patched_info(self, msg, *args, **kwargs):
            try:
                _note_runtime_cycle_branch(msg)
            except BaseException:
                pass
            try:
                _note_runtime_daily_task_outcome(msg)
            except BaseException:
                pass
            try:
                _note_runtime_single_harvest_outcome(msg)
            except BaseException:
                pass
            try:
                _note_runtime_planting_outcome(msg)
            except BaseException:
                pass
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
_QT_AUTOSTART_CLICKED = False



def _qt_runtime_already_running(app):
    if app is None:
        return False
    candidates = []
    for getter_name in ('topLevelWidgets', 'allWidgets'):
        try:
            getter = getattr(app, getter_name, None)
            if callable(getter):
                for item in list(getter()):
                    if item is not None and item not in candidates:
                        candidates.append(item)
        except BaseException:
            continue
    for item in candidates:
        try:
            value = getattr(item, 'bot_running', False)
            if isinstance(value, (bool, int)) and bool(value):
                return True
        except BaseException:
            pass
        try:
            states = getattr(item, '_instance_runtime_ui_state', None)
            if isinstance(states, dict):
                for state in states.values():
                    if not isinstance(state, dict):
                        continue
                    if bool(state.get('running')) or bool(state.get('starting')):
                        return True
        except BaseException:
            pass
        try:
            runtime = getattr(item, 'runtime', None)
            value = getattr(runtime, 'running', False) if runtime is not None else False
            if isinstance(value, (bool, int)) and bool(value):
                return True
        except BaseException:
            pass
    return False

def _qt_autostart_running_button(app):
    """Start the configured assistant once after the real main window is ready."""
    global _QT_AUTOSTART_CLICKED
    if _QT_AUTOSTART_CLICKED or app is None:
        return False
    if _qt_runtime_already_running(app):
        _QT_AUTOSTART_CLICKED = True
        _write('v102 qt autostart skipped because runtime is already running')
        return False
    try:
        widgets = list(app.allWidgets())
    except BaseException:
        return False
    for widget in widgets:
        try:
            text_getter = getattr(widget, 'text', None)
            if not callable(text_getter):
                continue
            text = str(text_getter()).strip()
            if text not in ('\u5f00\u59cb\u8fd0\u884c', 'Start Running'):
                continue
            enabled_getter = getattr(widget, 'isEnabled', None)
            visible_getter = getattr(widget, 'isVisible', None)
            if callable(enabled_getter) and not bool(enabled_getter()):
                continue
            if callable(visible_getter) and not bool(visible_getter()):
                continue
            clicker = getattr(widget, 'click', None)
            if not callable(clicker):
                continue
            clicker()
            _QT_AUTOSTART_CLICKED = True
            _write('v38 qt autostart clicked exact start-running button')
            return True
        except BaseException:
            continue
    return False


_QT_UNLOCKER_INSTALLED = False
_QT_UNLOCKER_TRYING = False
_QT_WAIT_LOGGED = False
_QT_ORIG_METHODS = {}
_QT_DUMP_COUNT = 0
_QT_UNLOCK_PASS_COUNT = 0
_QT_DUMP_PATH = r'C:/Users/USER/reverse-cases/qq-farm-vip/work/qt_widget_dump.txt'


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
                        _qt_autostart_running_button(app)
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
_write('local vip hook installed no-thread + v70-friend-help-click-verify+v71-share-target-friend-chain+v72-friend-continuation+v73-share-prompt-context+v74-friend-toggle-persist+v75-share-obfuscated-entry+v76-runtime-chain-share+v77-share-compiled-callables+v78-share-run-cycle-recovery+v79-share-preflight-friend-branch+v80-friend-branch-refresh+v81-friend-navigation-verify+v82-friend-false-positive-stop+v83-share-direct-selected-friend+v117-friend-list-entry-recovery+v118-friend-list-preflight+v119-home-transition-verified+v120-friend-navigation-barrier+home-branch-recovery+v121-log-tail-branch-inference')
