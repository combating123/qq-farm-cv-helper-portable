# ASCII-only UI personalization for the portable build.
GITHUB_HOME = 'https://github.com/combating123'
GITHUB_USER = 'combating123'
_PATCH_MARK = '_combating123_personalized'

ABOUT_HTML = '''
<div style="font-family:'Microsoft YaHei UI','Segoe UI',sans-serif; color:#17345f; padding:24px 26px;">
  <table width="100%" cellspacing="0" cellpadding="0" style="background:#edf5ff; border:1px solid #d5e6ff; border-radius:16px;">
    <tr><td style="padding:24px;">
      <div style="font-size:12px; letter-spacing:2px; color:#5f83b8;">PERSONAL PORTABLE EDITION</div>
      <div style="font-size:28px; font-weight:800; color:#176bff; margin-top:7px;">QQ \u7ecf\u5178\u519c\u573a\u52a9\u624b</div>
      <div style="font-size:15px; color:#587399; margin-top:8px;">\u5355\u76ee\u5f55\u4fbf\u643a\u8fd0\u884c \u00b7 \u8bbe\u7f6e\u6570\u636e\u6301\u4e45\u4fdd\u7559 \u00b7 \u4e2a\u4eba\u5316\u754c\u9762</div>
    </td></tr>
  </table>
  <table width="100%" cellspacing="10" cellpadding="0" style="margin-top:14px;">
    <tr>
      <td width="50%" style="background:#f8fbff; border:1px solid #e0e9f7; border-radius:12px; padding:14px 16px;">
        <div style="font-size:12px; color:#8798b2;">OWNER</div><div style="font-size:18px; font-weight:700; color:#213f70; margin-top:4px;">combating123</div>
      </td>
      <td width="50%" style="background:#f8fbff; border:1px solid #e0e9f7; border-radius:12px; padding:14px 16px;">
        <div style="font-size:12px; color:#8798b2;">BUILD</div><div style="font-size:18px; font-weight:700; color:#213f70; margin-top:4px;">v2.2.5 Portable</div>
      </td>
    </tr>
  </table>
  <div style="margin-top:18px; padding:17px 19px; background:#176bff; border-radius:12px;">
    <div style="font-size:12px; color:#dbe9ff; margin-bottom:6px;">GITHUB PROFILE</div>
    <a style="font-size:18px; font-weight:700; color:#ffffff; text-decoration:none;" href="https://github.com/combating123">github.com/combating123 &#8599;</a>
  </div>
  <div style="font-size:12px; color:#93a2b8; margin-top:16px; text-align:center;">\u754c\u9762\u4e0e\u4fbf\u643a\u4f53\u9a8c\u7531 combating123 \u7ef4\u62a4</div>
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


def _name(obj):
    value = _safe_call(obj, 'objectName')
    return '' if value is None else str(value)


def _tooltip(obj):
    value = _safe_call(obj, 'toolTip')
    return '' if value is None else str(value)


def _hide(obj):
    try:
        parent = _safe_call(obj, 'parentWidget')
        if parent is not None and _name(parent) == 'aboutCard':
            _safe_call(parent, 'hide')
            _safe_call(parent, 'setVisible', False)
        else:
            _safe_call(obj, 'hide')
            _safe_call(obj, 'setVisible', False)
    except BaseException:
        _safe_call(obj, 'hide')
        _safe_call(obj, 'setVisible', False)


def patch_widget(widget, context_getter=None, opener=None):
    try:
        name = _name(widget)
        text = _text(widget)
        tip = _tooltip(widget)
        try:
            context = str(context_getter(widget)) if context_getter else ''
        except BaseException:
            context = ''
        about_related = ('about' in (name + ' ' + context).lower())

        if name == 'titleText':
            _safe_call(widget, 'setText', 'QQ Farm Helper | combating123')
            _safe_call(widget, 'setToolTip', GITHUB_HOME)
            return 1
        if name == 'githubBtn' and tip == '\u5173\u4e8e':
            _safe_call(widget, 'setToolTip', '\u5173\u4e8e combating123')
            return 1

        # Sidebar GitHub icon: replace the original project target with the owner's profile.
        if name == 'githubBtn' and ('github' in tip.lower() or 'sidebar' in context.lower()):
            try:
                if bool(widget.property(_PATCH_MARK)):
                    return 0
            except BaseException:
                pass
            callback_opener = opener
            if callback_opener is None:
                callback_opener = __import__('webbrowser').open
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
            _safe_call(widget, 'setToolTip', '\u6253\u5f00 combating123 \u7684 GitHub \u4e3b\u9875')
            _safe_call(widget, 'setProperty', _PATCH_MARK, True)
            return 1

        # Remove update, documentation and expiry actions from the About view.
        if name == 'aboutSectionTitle' and text == '\u8fc7\u671f\u65f6\u95f4':
            _hide(widget)
            return 1
        if about_related and text in ('\u68c0\u67e5\u66f4\u65b0', '\u4f7f\u7528\u6587\u6863'):
            _hide(widget)
            return 1
        if name == 'aboutSectionTitle' and text == '\u5173\u4e8e\u672c\u7a0b\u5e8f':
            _safe_call(widget, 'setText', 'GitHub')
            return 1
        if name == 'aboutTextBrowser':
            _safe_call(widget, 'setHtml', ABOUT_HTML)
            _safe_call(widget, 'setStyleSheet', 'QTextBrowser#aboutTextBrowser{border:0;background:#ffffff;padding:2px;}')
            _safe_call(widget, 'setOpenExternalLinks', True)
            _safe_call(widget, 'setProperty', _PATCH_MARK, True)
            return 1
    except BaseException:
        return 0
    return 0
