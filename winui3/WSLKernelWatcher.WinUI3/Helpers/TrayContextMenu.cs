using System.Runtime.InteropServices;

namespace WSLKernelWatcher.WinUI3.Helpers;

public class TrayContextMenu : IDisposable
{
    private const int MF_STRING = 0x00000000;
    private const int MF_SEPARATOR = 0x00000800;
    private const int TPM_LEFTALIGN = 0x0000;
    private const int TPM_BOTTOMALIGN = 0x0020;

    private nint _hMenu;
    private readonly Dictionary<int, Action> _menuActions = new();
    private int _nextCommandId = 1;

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern nint CreatePopupMenu();

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern bool AppendMenu(nint hMenu, int uFlags, nint uIDNewItem, string lpNewItem);

    [DllImport("user32.dll")]
    private static extern bool SetForegroundWindow(nint hWnd);

    [DllImport("user32.dll")]
    private static extern bool GetCursorPos(out POINT lpPoint);

    [DllImport("user32.dll")]
    private static extern int TrackPopupMenu(nint hMenu, uint uFlags, int x, int y, int nReserved, nint hWnd, nint prcRect);

    [DllImport("user32.dll")]
    private static extern bool DestroyMenu(nint hMenu);

    [StructLayout(LayoutKind.Sequential)]
    private struct POINT
    {
        public int X;
        public int Y;
    }

    public TrayContextMenu()
    {
        _hMenu = CreatePopupMenu();
    }

    public void AddMenuItem(string text, Action action)
    {
        int commandId = _nextCommandId++;
        AppendMenu(_hMenu, MF_STRING, new nint(commandId), text);
        _menuActions[commandId] = action;
    }

    public void AddSeparator()
    {
        AppendMenu(_hMenu, MF_SEPARATOR, nint.Zero, string.Empty);
    }

    public void Show(nint hwnd)
    {
        SetForegroundWindow(hwnd);
        GetCursorPos(out POINT pt);

        int selectedId = TrackPopupMenu(_hMenu, TPM_LEFTALIGN | TPM_BOTTOMALIGN, pt.X, pt.Y, 0, hwnd, nint.Zero);

        if (selectedId > 0 && _menuActions.TryGetValue(selectedId, out var action))
        {
            action?.Invoke();
        }
    }

    public void Dispose()
    {
        if (_hMenu != nint.Zero)
        {
            DestroyMenu(_hMenu);
            _hMenu = nint.Zero;
        }
    }
}
