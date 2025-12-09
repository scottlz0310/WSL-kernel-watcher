using System.Runtime.InteropServices;
using Microsoft.UI.Xaml;

namespace WSLKernelWatcher.WinUI3.Services;

public class TrayIconService : IDisposable
{
    private const int WM_APP = 0x8000;
    private const int WM_TRAYICON = WM_APP + 1;
    private const int NIM_ADD = 0x00000000;
    private const int NIM_MODIFY = 0x00000001;
    private const int NIM_DELETE = 0x00000002;
    private const int NIF_MESSAGE = 0x00000001;
    private const int NIF_ICON = 0x00000002;
    private const int NIF_TIP = 0x00000004;
    private const int WM_LBUTTONUP = 0x0202;
    private const int WM_RBUTTONUP = 0x0205;

    private readonly nint _hwnd;
    private readonly uint _callbackMessage = WM_TRAYICON;
    private bool _isAdded;

    public event EventHandler? LeftClick;
    public event EventHandler? RightClick;

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct NOTIFYICONDATA
    {
        public int cbSize;
        public nint hWnd;
        public uint uID;
        public uint uFlags;
        public uint uCallbackMessage;
        public nint hIcon;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
        public string szTip;
    }

    [DllImport("shell32.dll", CharSet = CharSet.Unicode)]
    private static extern bool Shell_NotifyIcon(int dwMessage, ref NOTIFYICONDATA lpData);

    [DllImport("user32.dll")]
    private static extern nint LoadIcon(nint hInstance, nint lpIconName);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    private static extern nint GetModuleHandle(string? lpModuleName);

    [DllImport("user32.dll")]
    private static extern bool DestroyIcon(nint hIcon);

    public TrayIconService(Window window)
    {
        _hwnd = WinRT.Interop.WindowNative.GetWindowHandle(window);
    }

    public bool AddIcon(string tooltip)
    {
        if (_isAdded)
            return true;

        var hInstance = GetModuleHandle(null);
        var hIcon = LoadIcon(hInstance, new nint(32512)); // IDI_APPLICATION

        var nid = new NOTIFYICONDATA
        {
            cbSize = Marshal.SizeOf<NOTIFYICONDATA>(),
            hWnd = _hwnd,
            uID = 1,
            uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP,
            uCallbackMessage = _callbackMessage,
            hIcon = hIcon,
            szTip = tooltip
        };

        _isAdded = Shell_NotifyIcon(NIM_ADD, ref nid);
        return _isAdded;
    }

    public bool UpdateTooltip(string tooltip)
    {
        if (!_isAdded)
            return false;

        var hInstance = GetModuleHandle(null);
        var hIcon = LoadIcon(hInstance, new nint(32512));

        var nid = new NOTIFYICONDATA
        {
            cbSize = Marshal.SizeOf<NOTIFYICONDATA>(),
            hWnd = _hwnd,
            uID = 1,
            uFlags = NIF_TIP,
            szTip = tooltip
        };

        return Shell_NotifyIcon(NIM_MODIFY, ref nid);
    }

    public bool RemoveIcon()
    {
        if (!_isAdded)
            return true;

        var nid = new NOTIFYICONDATA
        {
            cbSize = Marshal.SizeOf<NOTIFYICONDATA>(),
            hWnd = _hwnd,
            uID = 1
        };

        _isAdded = !Shell_NotifyIcon(NIM_DELETE, ref nid);
        return !_isAdded;
    }

    public bool ProcessWindowMessage(uint msg, nint wParam, nint lParam)
    {
        if (msg != _callbackMessage)
            return false;

        switch (lParam.ToInt32())
        {
            case WM_LBUTTONUP:
                LeftClick?.Invoke(this, EventArgs.Empty);
                return true;
            case WM_RBUTTONUP:
                RightClick?.Invoke(this, EventArgs.Empty);
                return true;
        }

        return false;
    }

    public void Dispose()
    {
        RemoveIcon();
    }
}
