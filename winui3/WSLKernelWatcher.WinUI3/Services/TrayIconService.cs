// <copyright file="TrayIconService.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Diagnostics.CodeAnalysis;
using System.Runtime.InteropServices;
using Microsoft.UI.Xaml;

namespace WSLKernelWatcher.WinUI3.Services;

[ExcludeFromCodeCoverage]
internal sealed class TrayIconService : IDisposable
{
    private const int WMAPP = 0x8000;
    private const int WMTRAYICON = WMAPP + 1;
    private const int NIMADD = 0x00000000;
    private const int NIMMODIFY = 0x00000001;
    private const int NIMDELETE = 0x00000002;
    private const int NIFMESSAGE = 0x00000001;
    private const int NIFICON = 0x00000002;
    private const int NIFTIP = 0x00000004;
    private const int WMLBUTTONUP = 0x0202;
    private const int WMRBUTTONUP = 0x0205;

    private readonly nint hwnd;
    private readonly uint callbackMessage = WMTRAYICON;
    private bool isAdded;
    private nint hIcon;

    public event EventHandler? LeftClick;

    public event EventHandler? RightClick;

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct NOTIFYICONDATA
    {
        public int CbSize;
        public nint HWnd;
        public uint UID;
        public uint UFlags;
        public uint UCallbackMessage;
        public nint HIcon;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 128)]
        public string SzTip;
    }

    [DllImport("shell32.dll", CharSet = CharSet.Unicode)]
    private static extern bool Shell_NotifyIcon(int dwMessage, ref NOTIFYICONDATA lpData);

    [DllImport("user32.dll")]
    private static extern nint LoadIcon(nint hInstance, nint lpIconName);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern nint LoadImage(nint hInst, string lpszName, uint uType, int cxDesired, int cyDesired, uint fuLoad);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    private static extern nint GetModuleHandle(string? lpModuleName);

    [DllImport("user32.dll")]
    private static extern bool DestroyIcon(nint hIcon);

    private const uint IMAGEICON = 1;
    private const uint LRLOADFROMFILE = 0x00000010;

    public TrayIconService(Window window)
    {
        this.hwnd = WinRT.Interop.WindowNative.GetWindowHandle(window);
    }

    public bool AddIcon(string tooltip)
    {
        if (this.isAdded)
        {
            return true;
        }

        // Try to load custom icon from Assets folder
        string iconPath = Path.Combine(AppContext.BaseDirectory, "Assets", "wsl_watcher_icon.ico");
        if (File.Exists(iconPath))
        {
            this.hIcon = LoadImage(nint.Zero, iconPath, IMAGEICON, 16, 16, LRLOADFROMFILE);
        }

        // Fallback to default application icon if custom icon fails to load
        if (this.hIcon == nint.Zero)
        {
            nint hInstance = GetModuleHandle(null);
            this.hIcon = LoadIcon(hInstance, new nint(32512)); // IDI_APPLICATION
        }

        var nid = new NOTIFYICONDATA
        {
            CbSize = Marshal.SizeOf<NOTIFYICONDATA>(),
            HWnd = this.hwnd,
            UID = 1,
            UFlags = NIFMESSAGE | NIFICON | NIFTIP,
            UCallbackMessage = this.callbackMessage,
            HIcon = this.hIcon,
            SzTip = tooltip,
        };

        this.isAdded = Shell_NotifyIcon(NIMADD, ref nid);
        return this.isAdded;
    }

    public bool UpdateTooltip(string tooltip)
    {
        if (!this.isAdded)
        {
            return false;
        }

        var nid = new NOTIFYICONDATA
        {
            CbSize = Marshal.SizeOf<NOTIFYICONDATA>(),
            HWnd = this.hwnd,
            UID = 1,
            UFlags = NIFTIP,
            SzTip = tooltip,
        };

        return Shell_NotifyIcon(NIMMODIFY, ref nid);
    }

    public bool RemoveIcon()
    {
        if (!this.isAdded)
        {
            return true;
        }

        var nid = new NOTIFYICONDATA
        {
            CbSize = Marshal.SizeOf<NOTIFYICONDATA>(),
            HWnd = this.hwnd,
            UID = 1,
        };

        this.isAdded = !Shell_NotifyIcon(NIMDELETE, ref nid);
        return !this.isAdded;
    }

    public bool ProcessWindowMessage(uint msg, nint wParam, nint lParam)
    {
        if (msg != this.callbackMessage)
        {
            return false;
        }

        switch (lParam.ToInt32())
        {
            case WMLBUTTONUP:
                this.LeftClick?.Invoke(this, EventArgs.Empty);
                return true;
            case WMRBUTTONUP:
                this.RightClick?.Invoke(this, EventArgs.Empty);
                return true;
        }

        return false;
    }

    public void Dispose()
    {
        this.RemoveIcon();
        if (this.hIcon != nint.Zero)
        {
            DestroyIcon(this.hIcon);
            this.hIcon = nint.Zero;
        }
    }
}
