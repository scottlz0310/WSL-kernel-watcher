// <copyright file="TrayContextMenu.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Runtime.InteropServices;

namespace WSLKernelWatcher.WinUI3.Helpers;

internal sealed class TrayContextMenu : IDisposable
{
    private const int MFSTRING = 0x00000000;
    private const int MFSEPARATOR = 0x00000800;
    private const int TPMLEFTALIGN = 0x0000;
    private const int TPMBOTTOMALIGN = 0x0020;
    private const int TPMRETURNCMD = 0x0100;
    private nint hMenu;
    private readonly Dictionary<int, Action> menuActions = new();
    private int nextCommandId = 1000; // Start from 1000 to avoid conflicts

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

    [DllImport("user32.dll")]
    private static extern bool PostMessage(nint hWnd, uint msg, nint wParam, nint lParam);

    private const uint WMNULL = 0x0000;

    [StructLayout(LayoutKind.Sequential)]
    private struct POINT
    {
        public int X;
        public int Y;
    }

    public TrayContextMenu()
    {
        this.hMenu = CreatePopupMenu();
    }

    public void AddMenuItem(string text, Action action)
    {
        int commandId = this.nextCommandId++;
        AppendMenu(this.hMenu, MFSTRING, new nint(commandId), text);
        this.menuActions[commandId] = action;
    }

    public void AddSeparator()
    {
        AppendMenu(this.hMenu, MFSEPARATOR, nint.Zero, string.Empty);
    }

    public void Show(nint hwnd)
    {
        SetForegroundWindow(hwnd);
        GetCursorPos(out POINT pt);

        // TPM_RETURNCMD makes TrackPopupMenu return the selected command ID directly
        int selectedId = TrackPopupMenu(this.hMenu, TPMLEFTALIGN | TPMBOTTOMALIGN | TPMRETURNCMD, pt.X, pt.Y, 0, hwnd, nint.Zero);

        // Post a message to ensure the menu is properly closed
        PostMessage(hwnd, WMNULL, nint.Zero, nint.Zero);

        if (selectedId > 0 && this.menuActions.TryGetValue(selectedId, out Action? action))
        {
            action?.Invoke();
        }
    }

    public bool ProcessCommand(int commandId)
    {
        if (this.menuActions.TryGetValue(commandId, out Action? action))
        {
            action?.Invoke();
            return true;
        }

        return false;
    }

    public void Dispose()
    {
        if (this.hMenu != nint.Zero)
        {
            DestroyMenu(this.hMenu);
            this.hMenu = nint.Zero;
        }
    }
}
