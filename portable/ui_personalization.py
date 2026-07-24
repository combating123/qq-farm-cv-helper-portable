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
