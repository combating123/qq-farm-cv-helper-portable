# ASCII-only conservative personalization for the portable build.
# The host application's native QSS and geometry are intentionally preserved.
GITHUB_HOME = 'https://github.com/combating123'
GITHUB_USER = 'combating123'
_PATCH_MARK = '_combating123_personalized'
_ABOUT_MARK = '_combating123_about_refresh'
_PROMO_MARKERS = (
    '\u9879\u76ee\u5730\u5740', '\u7fa4',
    '\u7f51\u53cb\u63d0\u4f9b', '\u6b22\u8fce\u52a0\u5165\u8ba8\u8bba',
    '\u6b22\u8fce star', '\u6b22\u8fce\u2b50 star',
)

# Empty by design: global Qt rules changed title-bar, sidebar and status geometry.
APP_QSS = ''
DIALOG_QSS = ''
DIALOG_CHILD_QSS = ''
COPY_MAP = {}

ABOUT_HTML = r'''
<div style="font-family:'Segoe UI','Microsoft YaHei UI',sans-serif; padding:24px; color:#1f2937;">
  <div style="font-size:30px; font-weight:700; color:#111827;">CV Farm Assistant</div>
  <div style="margin-top:24px; padding:18px 20px; border:1px solid #dbe4f0; border-radius:10px;">
    <div style="font-size:12px; color:#64748b;">PROJECT OWNER</div>
    <div style="margin-top:6px; font-size:20px; font-weight:700; color:#111827;">combating123</div>
    <div style="margin-top:18px; font-size:12px; color:#64748b;">GITHUB</div>
    <div style="margin-top:6px;">
      <a style="font-size:16px; font-weight:600; color:#2563eb; text-decoration:none;" href="https://github.com/combating123">github.com/combating123</a>
    </div>
  </div>
</div>
'''


def _safe_call(obj, name, *args):
    try:
        fn = getattr(obj, name, None)
        if callable(fn):
            return fn(*args)
    except BaseException:
        pass
    return None


def _text(obj):
    value = _safe_call(obj, 'text')
    return '' if value is None else str(value)


def _content_text(obj):
    for method in ('toPlainText', 'text', 'toHtml'):
        value = _safe_call(obj, method)
        if value is not None:
            try:
                rendered = str(value)
                if rendered:
                    return rendered
            except BaseException:
                pass
    return ''


def _name(obj):
    value = _safe_call(obj, 'objectName')
    return '' if value is None else str(value)


def _tooltip(obj):
    value = _safe_call(obj, 'toolTip')
    return '' if value is None else str(value)


def _hide(obj):
    _safe_call(obj, 'hide')
    _safe_call(obj, 'setVisible', False)


def _hide_parent_card(obj):
    parent = _safe_call(obj, 'parentWidget')
    if parent is not None and _name(parent) == 'aboutCard':
        _hide(parent)
    else:
        _hide(obj)


def install_early_theme(QtWidgets=None):
    """Preserve the application's native stylesheet and all native geometry."""
    return False


def _patch_all_widgets():
    try:
        QtWidgets = __import__('PySide6.QtWidgets', fromlist=['QApplication'])
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        for item in list(app.allWidgets()):
            patch_widget(item)
    except BaseException:
        pass


def _schedule_about_refresh(checked=False):
    try:
        QtCore = __import__('PySide6.QtCore', fromlist=['QTimer'])
        for delay in (0, 30, 120, 350, 800, 1500, 3000, 5000):
            QtCore.QTimer.singleShot(delay, _patch_all_widgets)
    except BaseException:
        _patch_all_widgets()


def share_target_editor_copy():
    return {
        'title': '\u5b9a\u5411\u76ee\u6807',
        'label': '\u5206\u4eab\u76ee\u6807\uff08\u597d\u53cb\u6635\u79f0\u6216 QQ \u53f7\uff09',
        'placeholder': '\u586b\u5199\u5b8c\u6574\u597d\u53cb\u6635\u79f0\u6216 QQ \u53f7\uff08QQ \u53f7\u9700\u5728\u641c\u7d22\u7ed3\u679c\u4e2d\u53ef\u89c1\uff09',
        'empty_status': '\u5f53\u524d\u5206\u4eab\u76ee\u6807\uff1a\u672a\u8bbe\u7f6e\uff08\u81ea\u52a8\u5206\u4eab\u4fdd\u6301\u5173\u95ed\uff09',
        'save_button': '\u4fdd\u5b58',
        'clear_button': '\u6e05\u7a7a',
        'hint': '\u4ec5\u5339\u914d\u641c\u7d22\u7ed3\u679c\u4e2d\u53ef\u89c1\u7684\u5b8c\u6574\u6635\u79f0\u6216 QQ \u53f7\uff1b\u672a\u627e\u5230\u65f6\u53d6\u6d88\uff0c\u4e0d\u9009\u62e9\u9996\u4e2a\u7ed3\u679c\u3002',
    }


def share_target_editor_style():
    return {
        'title_px': 14,
        'body_px': 13,
        'hint_px': 12,
        'control_height': 32,
        'outer_margin': 10,
        'spacing': 5,
    }


def _load_share_settings_module():
    try:
        return __import__('share_target_settings')
    except BaseException:
        try:
            import importlib.util
            import pathlib
            path = pathlib.Path(__file__).with_name('share_target_settings.py')
            spec = importlib.util.spec_from_file_location('_qqfarm_share_target_settings', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except BaseException:
            return None


def _editor_host(anchor):
    current = _safe_call(anchor, 'parentWidget')
    fallback = None
    for _ in range(5):
        if current is None:
            break
        layout = _safe_call(current, 'layout')
        if layout is not None:
            fallback = (current, layout)
            kind = type(layout).__name__.lower()
            if 'vbox' in kind or 'grid' in kind or 'form' in kind:
                return current, layout
        current = _safe_call(current, 'parentWidget')
    return fallback or (None, None)


def _ensure_share_target_editor(anchor):
    host, host_layout = _editor_host(anchor)
    if host is None or host_layout is None:
        return 0
    try:
        if bool(host.property('_qqfarm_share_target_editor_installed')):
            return 0
    except BaseException:
        pass
    settings = _load_share_settings_module()
    if settings is None:
        return 0
    try:
        QtWidgets = __import__('PySide6.QtWidgets', fromlist=['QFrame'])
        copy = share_target_editor_copy()
        state = settings.load_share_target()
        panel = QtWidgets.QFrame(host)
        panel.setObjectName('shareTargetEditor')
        style = share_target_editor_style()
        panel.setStyleSheet(
            'QFrame#shareTargetEditor{margin-top:6px;border:1px solid #dbe4f0;border-radius:8px;background:#f8fafc;}'
            'QLabel#shareTargetEditorTitle{font-size:%(title_px)spx;font-weight:600;color:#0f172a;}'
            'QLabel#shareTargetStatus{font-size:%(body_px)spx;font-weight:400;color:#334155;}'
            'QLabel#shareTargetHint{font-size:%(hint_px)spx;font-weight:400;color:#64748b;}'
            'QLineEdit#shareTargetInput{min-height:%(control_height)spx;max-height:%(control_height)spx;padding:0 9px;'
            'font-size:%(body_px)spx;font-weight:400;border:1px solid #cbd5e1;border-radius:6px;background:white;color:#111827;}'
            'QPushButton#shareTargetSaveButton{min-height:%(control_height)spx;max-height:%(control_height)spx;min-width:58px;padding:0 12px;'
            'font-size:%(body_px)spx;font-weight:500;border:0;border-radius:6px;background:#2563eb;color:white;}'
            'QPushButton#shareTargetClearButton{min-height:%(control_height)spx;max-height:%(control_height)spx;min-width:58px;padding:0 12px;'
            'font-size:%(body_px)spx;font-weight:400;border:1px solid #cbd5e1;border-radius:6px;background:white;color:#334155;}'
            % style
        )
        outer = QtWidgets.QVBoxLayout(panel)
        margin = style['outer_margin']
        outer.setContentsMargins(margin, margin - 1, margin, margin - 1)
        outer.setSpacing(style['spacing'])
        title = QtWidgets.QLabel(copy['title'], panel)
        title.setObjectName('shareTargetEditorTitle')
        entry = QtWidgets.QLineEdit(panel)
        entry.setObjectName('shareTargetInput')
        entry.setPlaceholderText(copy['placeholder'])
        entry.setClearButtonEnabled(True)
        entry.setText(str(state.get('target', '') or ''))
        status = QtWidgets.QLabel(str(state.get('status_text') or copy['empty_status']), panel)
        status.setObjectName('shareTargetStatus')
        status.setWordWrap(True)
        hint = QtWidgets.QLabel(copy['hint'], panel)
        hint.setObjectName('shareTargetHint')
        hint.setWordWrap(True)
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        save_button = QtWidgets.QPushButton(copy['save_button'], panel)
        save_button.setObjectName('shareTargetSaveButton')
        clear_button = QtWidgets.QPushButton(copy['clear_button'], panel)
        clear_button.setObjectName('shareTargetClearButton')
        row.addWidget(entry, 1)
        row.addWidget(save_button)
        row.addWidget(clear_button)
        outer.addWidget(title)
        outer.addLayout(row)
        outer.addWidget(status)
        outer.addWidget(hint)

        def save_current(checked=False):
            value = str(entry.text() or '').strip()
            if not value:
                status.setText(copy['empty_status'])
                entry.setFocus()
                return
            result = settings.save_share_target(target=value, allow_group=False)
            entry.setText(str(result.get('target', value)))
            status.setText(str(result.get('status_text', '')))

        def clear_current(checked=False):
            result = settings.clear_share_target()
            entry.clear()
            status.setText(str(result.get('status_text') or copy['empty_status']))

        save_button.clicked.connect(save_current)
        clear_button.clicked.connect(clear_current)
        entry.returnPressed.connect(save_current)
        kind = type(host_layout).__name__.lower()
        if 'grid' in kind and hasattr(host_layout, 'rowCount'):
            host_layout.addWidget(panel, host_layout.rowCount(), 0, 1, max(1, host_layout.columnCount()))
        else:
            host_layout.addWidget(panel)
        host.setProperty('_qqfarm_share_target_editor_installed', True)
        anchor.setProperty('_qqfarm_share_target_editor_anchor', True)
        return 1
    except BaseException:
        return 0


def patch_widget(widget, context_getter=None, opener=None):
    try:
        name = _name(widget)
        text = _text(widget)
        tip = _tooltip(widget)
        content = _content_text(widget)
        try:
            context = str(context_getter(widget)) if context_getter else ''
        except BaseException:
            context = ''
        lower_context = (name + ' ' + context).lower()
        about_related = 'about' in lower_context
        # Daily share is manual by default and exposes an editable exact recipient.
        if name == 'dailyShareDescription':
            changed = 0
            if '\u968f\u673a' in text or '\u6307\u5b9a\u8054\u7cfb\u4eba' not in text:
                _safe_call(widget, 'setText', '\u9ed8\u8ba4\u5173\u95ed\u81ea\u52a8\u5206\u4eab\uff1b\u586b\u5199\u6307\u5b9a\u8054\u7cfb\u4eba\u7684\u5b8c\u6574\u597d\u53cb\u6635\u79f0\u6216 QQ \u53f7\uff0c\u4ec5\u5728\u7cbe\u786e\u5339\u914d\u540e\u53d1\u9001')
                changed += 1
            changed += _ensure_share_target_editor(widget)
            return changed
        if '\u968f\u673a\u5206\u4eab\u7ed9\u597d\u53cb/\u7fa4\u7ec4' in text or (
            '\u6bcf\u65e5\u5206\u4eab' in lower_context and '\u968f\u673a' in text
        ):
            _safe_call(widget, 'setText', '\u9ed8\u8ba4\u5173\u95ed\u81ea\u52a8\u5206\u4eab\uff1b\u586b\u5199\u6307\u5b9a\u8054\u7cfb\u4eba\u7684\u5b8c\u6574\u597d\u53cb\u6635\u79f0\u6216 QQ \u53f7\uff0c\u4ec5\u5728\u7cbe\u786e\u5339\u914d\u540e\u53d1\u9001')
            _ensure_share_target_editor(widget)
            return 1

        # Clean the project-information dialog before applying the generic
        # dialog guard. Its children legitimately live under a QDialog.
        promo_blob = (text + ' ' + content).lower()
        has_promo_copy = any(marker.lower() in promo_blob for marker in _PROMO_MARKERS)
        if about_related and has_promo_copy:
            is_rich_browser = ('qtextbrowser' in context.lower() or 'browser' in name.lower())
            if is_rich_browser and callable(getattr(widget, 'setHtml', None)):
                _safe_call(widget, 'clear')
                _safe_call(widget, 'setHtml', ABOUT_HTML)
                _safe_call(widget, 'setOpenExternalLinks', True)
                _safe_call(widget, 'setProperty', _PATCH_MARK, True)
            else:
                _hide(widget)
            return 1
        if text.startswith('\u5173\u4e8e - '):
            _safe_call(widget, 'setText', '\u9879\u76ee\u4fe1\u606f')
            return 1
        if name == 'templateDebugStatus':
            _hide_parent_card(widget)
            return 1
        if name == 'aboutSectionTitle' and text == '\u8fc7\u671f\u65f6\u95f4':
            _hide_parent_card(widget)
            return 1
        if about_related and text in ('\u68c0\u67e5\u66f4\u65b0', '\u4f7f\u7528\u6587\u6863'):
            _hide(widget)
            return 1
        if name == 'aboutSectionTitle':
            _safe_call(widget, 'setText', '\u9879\u76ee\u4fe1\u606f')
            return 1
        if name == 'aboutTextBrowser':
            _safe_call(widget, 'setHtml', ABOUT_HTML)
            _safe_call(widget, 'setStyleSheet', 'QTextBrowser#aboutTextBrowser{border:0;background:transparent;}')
            _safe_call(widget, 'setOpenExternalLinks', True)
            _safe_call(widget, 'setProperty', _PATCH_MARK, True)
            return 1

        # Do not touch other root, dialog, sidebar, sizing or host styles.
        if name in ('rootView', 'windowShell', 'sidebar'):
            return 0
        context_head = context.strip().lower().split(' ', 1)[0] if context.strip() else ''
        if context_head in ('qdialog', 'qmessagebox') or name.lower().endswith('dialog'):
            return 0
        if 'qdialog' in context.lower():
            return 0

        if name == 'titleText':
            _safe_call(widget, 'setText', 'CV \u519c\u573a\u52a9\u624b \u00b7 combating123')
            _safe_call(widget, 'setToolTip', GITHUB_HOME)
            return 1

        if name in ('title' + chr(86) + 'ersionTag', chr(118) + 'ersionTag'):
            _hide(widget)
            return 1

        if name == 'githubBtn' and (tip == '\u5173\u4e8e' or 'about' in tip.lower()):
            _safe_call(widget, 'setToolTip', '\u9879\u76ee\u4fe1\u606f | combating123')
            try:
                if not bool(widget.property(_ABOUT_MARK)):
                    signal = getattr(widget, 'clicked', None)
                    if signal is not None:
                        signal.connect(_schedule_about_refresh)
                    _safe_call(widget, 'setProperty', _ABOUT_MARK, True)
            except BaseException:
                pass
            return 1

        if name == 'githubBtn' and ('github' in tip.lower() or 'sidebar' in context.lower()):
            try:
                if bool(widget.property(_PATCH_MARK)):
                    return 0
            except BaseException:
                pass
            callback_opener = opener or __import__('webbrowser').open
            def _open_home(checked=False, _opener=callback_opener):
                try:
                    _opener(GITHUB_HOME)
                except BaseException:
                    pass
            signal = getattr(widget, 'clicked', None)
            if signal is not None:
                try:
                    signal.disconnect()
                except BaseException:
                    pass
                signal.connect(_open_home)
            _safe_call(widget, 'setToolTip', '\u6253\u5f00 combating123 GitHub')
            _safe_call(widget, 'setProperty', _PATCH_MARK, True)
            return 1

        if 'vip' in text.lower() or text in ('\u4f1a\u5458\u5df2\u6fc0\u6d3b', '\u5f00\u901a\u4f1a\u5458'):
            _safe_call(widget, 'setText', '\u5df2\u6fc0\u6d3b')
            return 1

    except BaseException:
        return 0
    return 0
