# ASCII-only UI personalization for the portable build.
GITHUB_HOME = 'https://github.com/combating123'
GITHUB_USER = 'combating123'
_PATCH_MARK = '_combating123_personalized'
_ABOUT_MARK = '_combating123_about_refresh'

ABOUT_HTML = r'''
<div style="font-family:'Segoe UI','Microsoft YaHei UI',sans-serif; padding:42px; color:#edf7ff; background:#050814;">
  <table width="100%" cellspacing="0" cellpadding="0" style="background:#0a1222; border:1px solid #22314a;">
    <tr>
      <td colspan="2" style="padding:34px 36px 26px 36px; border-bottom:1px solid #22314a;">
        <div style="font-size:38px; font-weight:800; color:#ffffff;">QQ Farm Studio</div>
      </td>
    </tr>
    <tr>
      <td width="40%" style="padding:26px 36px; border-right:1px solid #22314a;">
        <div style="font-size:12px; color:#8292ad;">OWNER</div>
        <div style="font-size:22px; font-weight:700; color:#ffffff; margin-top:8px;">combating123</div>
      </td>
      <td style="padding:26px 36px;">
        <div style="font-size:12px; color:#8292ad;">GITHUB</div>
        <a style="font-size:18px; font-weight:700; color:#65fbd2; text-decoration:none;" href="https://github.com/combating123">github.com/combating123</a>
      </td>
    </tr>
  </table>
</div>
'''

APP_QSS = r'''
/* QQ Farm Studio: dark command-center visual system */
QWidget {
    background:#050814;
    color:#dce8f8;
    font-family:"Segoe UI","Microsoft YaHei UI";
    font-size:14px;
    selection-background-color:#65fbd2;
    selection-color:#050814;
}
QWidget#rootView, QFrame#windowShell {
    background:#050814;
    border:none;
}
QFrame#sidebar {
    background:#070c18;
    border:none;
    border-right:1px solid #1a2840;
}
QFrame#contentShell, QStackedWidget, QScrollArea, QScrollArea > QWidget > QWidget {
    background:#080e1b;
    border:none;
}
QFrame {
    background:#0a1222;
    border-color:#1b2a42;
}
QLabel { background:transparent; color:#cbd8ea; }
QLabel#titleText {
    color:#ffffff;
    font-size:19px;
    font-weight:800;
    letter-spacing:1px;
}
QLabel#aboutSectionTitle { color:#65fbd2; font-size:13px; font-weight:800; }
QToolButton {
    background:transparent;
    color:#8fa0ba;
    border:1px solid transparent;
    border-radius:12px;
    min-height:42px;
    padding:0 14px;
}
QToolButton:hover { background:#101d31; color:#ffffff; border-color:#263a57; }
QToolButton:pressed { background:#172940; }
QToolButton#navBtn, QToolButton#navBtnActive {
    min-height:48px;
    padding:0 16px;
    text-align:left;
    font-weight:700;
}
QToolButton#navBtn { color:#8292ad; background:transparent; }
QToolButton#navBtn:hover { color:#ffffff; background:#101d31; }
QToolButton#navBtnActive {
    color:#050814;
    background:#65fbd2;
    border-color:#65fbd2;
}
QPushButton {
    min-height:38px;
    padding:0 18px;
    color:#dce8f8;
    background:#101b2e;
    border:1px solid #263954;
    border-radius:10px;
    font-weight:700;
}
QPushButton:hover { color:#ffffff; background:#162641; border-color:#65fbd2; }
QPushButton:pressed { background:#0b1526; }
QPushButton[studioRole="primaryAction"] {
    min-height:46px;
    color:#04100d;
    background:#65fbd2;
    border:1px solid #65fbd2;
    border-radius:12px;
    font-size:15px;
    font-weight:800;
}
QPushButton[studioRole="primaryAction"]:hover { background:#8cffdf; border-color:#8cffdf; }
QLabel[studioRole="statusPill"], QPushButton[studioRole="statusPill"] {
    color:#65fbd2;
    background:#0d2725;
    border:1px solid #285c54;
    border-radius:13px;
    padding:5px 14px;
    font-weight:800;
}
QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser, QSpinBox, QDoubleSpinBox {
    color:#dce8f8;
    background:#060b15;
    border:1px solid #22324b;
    border-radius:10px;
    padding:8px 10px;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border:1px solid #65fbd2;
}
QComboBox {
    min-height:38px;
    color:#edf7ff;
    background:#0d1728;
    border:1px solid #263954;
    border-radius:10px;
    padding:0 34px 0 12px;
}
QComboBox:hover, QComboBox:focus { border-color:#65fbd2; }
QComboBox QAbstractItemView {
    color:#dce8f8;
    background:#0a1222;
    border:1px solid #263954;
    selection-background-color:#65fbd2;
    selection-color:#050814;
    outline:0;
}
QCheckBox, QRadioButton { color:#b9c8dc; spacing:8px; background:transparent; }
QCheckBox::indicator, QRadioButton::indicator { width:18px; height:18px; }
QCheckBox::indicator:checked, QRadioButton::indicator:checked { background:#65fbd2; border:2px solid #65fbd2; }
QGroupBox {
    color:#edf7ff;
    background:#0a1222;
    border:1px solid #1d2c45;
    border-radius:14px;
    margin-top:14px;
    padding-top:14px;
    font-weight:800;
}
QGroupBox::title { subcontrol-origin:margin; left:14px; padding:0 7px; color:#65fbd2; }
QTabWidget::pane { background:#0a1222; border:1px solid #1d2c45; border-radius:12px; }
QTabBar::tab { color:#8292ad; background:#080e1b; padding:10px 18px; border:none; }
QTabBar::tab:selected { color:#65fbd2; background:#0f1b2e; }
QHeaderView::section { color:#8fa0ba; background:#0d1728; border:none; border-bottom:1px solid #263954; padding:9px; }
QTableView, QTreeView, QListView { color:#dce8f8; background:#070c16; border:1px solid #1d2c45; alternate-background-color:#0a1323; }
QProgressBar { color:#dce8f8; background:#07101e; border:1px solid #22324b; border-radius:7px; text-align:center; }
QProgressBar::chunk { background:#65fbd2; border-radius:6px; }
QScrollBar:vertical { width:10px; background:#070c16; margin:2px; }
QScrollBar::handle:vertical { min-height:28px; background:#2a3b56; border-radius:5px; }
QScrollBar::handle:vertical:hover { background:#65fbd2; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QScrollBar:horizontal { height:10px; background:#070c16; margin:2px; }
QScrollBar::handle:horizontal { min-width:28px; background:#2a3b56; border-radius:5px; }
QFrame#aboutCard { background:#050814; border:1px solid #22314a; border-radius:18px; }
QTextBrowser#aboutTextBrowser { background:#050814; color:#dce8f8; border:none; padding:0; }
QToolTip { color:#edf7ff; background:#101b2e; border:1px solid #65fbd2; padding:6px; }
'''

COPY_MAP = {
    '\u8fd0\u884c\u63a7\u5236': '\u5de5\u4f5c\u53f0',
    '\u53c2\u6570\u8bbe\u7f6e': '\u81ea\u52a8\u5316\u914d\u7f6e',
    '\u597d\u53cb\u5c4f\u853d': '\u597d\u53cb\u7b56\u7565',
    '\u597d\u53cb\u62a4\u4e3b': '\u5b88\u62a4\u4e2d\u5fc3',
    '\u5f00\u59cb\u8fd0\u884c': '\u542f\u52a8\u5de5\u4f5c\u6d41',
    '\u5c0f\u7a0b\u5e8f\u5e73\u53f0\u9009\u62e9': '\u8fd0\u884c\u76ee\u6807',
    '\u663e\u793a\u5c0f\u7a0b\u5e8f': '\u7a97\u53e3\u8054\u52a8',
    '\u5355\u5f00\u7248': '\u5355\u5b9e\u4f8b',
    '\u591a\u5f00\u7248': '\u591a\u5b9e\u4f8b',
}


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


def _set_role(widget, role):
    _safe_call(widget, 'setProperty', 'studioRole', role)
    style = _safe_call(widget, 'style')
    if style is not None:
        _safe_call(style, 'unpolish', widget)
        _safe_call(style, 'polish', widget)


def _patch_all_widgets():
    try:
        QtWidgets = __import__('PySide6.QtWidgets', fromlist=['QApplication'])
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        _safe_call(app, 'setStyleSheet', APP_QSS)
        for item in list(app.allWidgets()):
            patch_widget(item)
    except BaseException:
        pass


def _schedule_about_refresh(checked=False):
    try:
        QtCore = __import__('PySide6.QtCore', fromlist=['QTimer'])
        for delay in (0, 30, 120, 350, 800):
            QtCore.QTimer.singleShot(delay, _patch_all_widgets)
    except BaseException:
        _patch_all_widgets()


def patch_widget(widget, context_getter=None, opener=None):
    try:
        name = _name(widget)
        text = _text(widget)
        tip = _tooltip(widget)
        try:
            context = str(context_getter(widget)) if context_getter else ''
        except BaseException:
            context = ''
        lower_context = (name + ' ' + context).lower()
        about_related = 'about' in lower_context

        if name in ('rootView', 'windowShell'):
            _safe_call(widget, 'setStyleSheet', APP_QSS)
            return 1

        if name == 'sidebar':
            _safe_call(widget, 'setMinimumWidth', 176)
            _safe_call(widget, 'setMaximumWidth', 176)
            _set_role(widget, 'commandRail')
            return 1

        if name == 'titleText':
            _safe_call(widget, 'setText', 'QQ Farm Studio | combating123')
            _safe_call(widget, 'setToolTip', GITHUB_HOME)
            return 1

        if name in ('title' + chr(86) + 'ersionTag', chr(118) + 'ersionTag'):
            _hide(widget)
            return 1

        if name == 'githubBtn' and (tip == '\u5173\u4e8e' or 'about' in tip.lower()):
            _safe_call(widget, 'setToolTip', '\u9879\u76ee\u540d\u7247 | combating123')
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
            _safe_call(widget, 'setText', 'STUDIO ACTIVE')
            _set_role(widget, 'statusPill')
            return 1

        if text in COPY_MAP:
            _safe_call(widget, 'setText', COPY_MAP[text])
            if text == '\u5f00\u59cb\u8fd0\u884c':
                _set_role(widget, 'primaryAction')
            return 1

        if text.startswith('\u5173\u4e8e - '):
            _safe_call(widget, 'setText', 'QQ Farm Studio  /  PROJECT PROFILE')
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
            _safe_call(widget, 'setText', 'PROJECT PROFILE')
            _safe_call(widget, 'setStyleSheet', 'color:#65fbd2;font-size:13px;font-weight:800;letter-spacing:2px;')
            return 1

        if name == 'aboutTextBrowser':
            _safe_call(widget, 'setHtml', ABOUT_HTML)
            _safe_call(widget, 'setStyleSheet', 'QTextBrowser#aboutTextBrowser{border:0;background:#050814;color:#dce8f8;padding:0;}')
            _safe_call(widget, 'setOpenExternalLinks', True)
            _safe_call(widget, 'setProperty', _PATCH_MARK, True)
            parent = _safe_call(widget, 'parentWidget')
            if parent is not None:
                _safe_call(parent, 'setStyleSheet', 'QFrame#aboutCard{background:#050814;border:1px solid #22314a;border-radius:18px;padding:10px;}')
            return 1
    except BaseException:
        return 0
    return 0
