from enum import IntFlag

import comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 as __wrapper_module__
from comtypes.gen._00020430_0000_0000_C000_000000000046_0_2_0 import (
    CoClass, Color, COMMETHOD, typelib_path, FONTBOLD, FONTSIZE,
    IUnknown, OLE_XPOS_HIMETRIC, IEnumVARIANT, VgaColor,
    OLE_YSIZE_CONTAINER, BSTR, OLE_YPOS_CONTAINER, FontEvents,
    IFontEventsDisp, Library, Unchecked, OLE_CANCELBOOL,
    OLE_YSIZE_HIMETRIC, _lcid, dispid, OLE_YPOS_HIMETRIC, OLE_HANDLE,
    Checked, DISPPROPERTY, Font, OLE_YPOS_PIXELS, Monochrome,
    IPicture, FONTITALIC, OLE_ENABLEDEFAULTBOOL, OLE_YSIZE_PIXELS,
    OLE_XSIZE_PIXELS, IDispatch, Gray, FONTUNDERSCORE,
    FONTSTRIKETHROUGH, Default, OLE_OPTEXCLUSIVE, IFontDisp, GUID,
    FONTNAME, VARIANT_BOOL, OLE_XSIZE_HIMETRIC, HRESULT, Picture,
    DISPMETHOD, StdFont, OLE_XSIZE_CONTAINER, EXCEPINFO,
    OLE_XPOS_PIXELS, IFont, StdPicture, DISPPARAMS,
    OLE_XPOS_CONTAINER, IPictureDisp, _check_version, OLE_COLOR
)


class LoadPictureConstants(IntFlag):
    Default = 0
    Monochrome = 1
    VgaColor = 2
    Color = 4


class OLE_TRISTATE(IntFlag):
    Unchecked = 0
    Checked = 1
    Gray = 2


__all__ = [
    'FONTITALIC', 'OLE_ENABLEDEFAULTBOOL', 'OLE_YSIZE_PIXELS',
    'OLE_XSIZE_PIXELS', 'Color', 'typelib_path', 'Gray',
    'OLE_TRISTATE', 'FONTBOLD', 'FONTSIZE', 'FONTUNDERSCORE',
    'Default', 'OLE_XPOS_HIMETRIC', 'OLE_OPTEXCLUSIVE', 'VgaColor',
    'OLE_YSIZE_CONTAINER', 'OLE_YPOS_CONTAINER', 'IFontDisp',
    'FontEvents', 'IFontEventsDisp', 'FONTNAME', 'Unchecked',
    'Library', 'FONTSTRIKETHROUGH', 'OLE_CANCELBOOL',
    'OLE_XSIZE_HIMETRIC', 'OLE_YSIZE_HIMETRIC', 'Picture',
    'OLE_YPOS_HIMETRIC', 'OLE_HANDLE', 'StdFont',
    'OLE_XSIZE_CONTAINER', 'OLE_XPOS_PIXELS', 'Checked', 'IFont',
    'StdPicture', 'Font', 'OLE_XPOS_CONTAINER', 'OLE_YPOS_PIXELS',
    'Monochrome', 'IPicture', 'IPictureDisp', 'LoadPictureConstants',
    'OLE_COLOR'
]

