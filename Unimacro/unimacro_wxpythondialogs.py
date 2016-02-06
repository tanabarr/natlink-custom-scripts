
import wx


def InputBox(text, prompt="Unimacro Input", default=""):
    """this one kills Dragon"""
    app = wx.PySimpleApp()
    dialog = wx.TextEntryDialog(None,
    text, prompt, default, style=wx.OK|wx.CANCEL)
    if dialog.ShowModal() == wx.ID_OK:
        result = dialog.GetValue()
    else:
        result = None
    dialog.Destroy()
    return result
