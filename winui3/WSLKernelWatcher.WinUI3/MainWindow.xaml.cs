// <copyright file="MainWindow.xaml.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Diagnostics.CodeAnalysis;
using System.Runtime.InteropServices;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.Graphics;
using WinRT;
using WSLKernelWatcher.WinUI3.Helpers;
using WSLKernelWatcher.WinUI3.Services;

namespace WSLKernelWatcher.WinUI3;

[ExcludeFromCodeCoverage]
internal sealed partial class MainWindow : Window
{
    private readonly KernelWatcherService service;
    private readonly LoggingService loggingService;
    private readonly SettingsService settingsService;
    private readonly ObservableCollection<string> logEntries = new();
    private readonly TrayIconService trayIconService;
    private TrayContextMenu? contextMenu;
    private readonly nint hwnd;

    private delegate nint WndProcDelegate(nint hWnd, uint msg, nint wParam, nint lParam);

    private readonly WndProcDelegate? newWndProcDelegate;
    private readonly nint oldWndProc;

    [DllImport("user32.dll")]
    private static extern nint SetWindowLongPtr(nint hWnd, int nIndex, nint dwNewLong);

    [DllImport("user32.dll")]
    private static extern nint CallWindowProc(nint lpPrevWndFunc, nint hWnd, uint msg, nint wParam, nint lParam);

    [DllImport("user32.dll")]
    private static extern bool ShowWindow(nint hWnd, int nCmdShow);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern nint LoadImage(nint hInst, string lpszName, uint uType, int cxDesired, int cyDesired, uint fuLoad);

    [DllImport("user32.dll")]
    private static extern nint SendMessage(nint hWnd, uint msg, nint wParam, nint lParam);

    private const int GWLWNDPROC = -4;
    private const int SWHIDE = 0;
    private const int SWSHOW = 5;
    private const uint WMSETICON = 0x0080;
    private const uint WMCOMMAND = 0x0111;
    private const uint ICONSMALL = 0;
    private const uint ICONBIG = 1;
    private const uint IMAGEICON = 1;
    private const uint LRLOADFROMFILE = 0x00000010;

    internal MainWindow(KernelWatcherService service, LoggingService loggingService, SettingsService settingsService, bool showWindow = true)
    {
        InitializeComponent();

        // Set window size (WinUI3 requires this in code)
        this.hwnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
        Microsoft.UI.WindowId windowId = Microsoft.UI.Win32Interop.GetWindowIdFromWindow(this.hwnd);
        var appWindow = Microsoft.UI.Windowing.AppWindow.GetFromWindowId(windowId);
        appWindow.Resize(new SizeInt32(520, 360));

        // Set window icon
        this.SetWindowIcon();

        this.service = service;
        this.loggingService = loggingService;
        this.settingsService = settingsService;
        this.service.StatusChanged += this.OnStatusChanged;
        this.loggingService.LogAppended += this.OnLogAppended;
        LogList.ItemsSource = this.logEntries;

        // Load settings
        CheckIntervalBox.Value = this.settingsService.Settings.CheckIntervalHours;

        // Setup tray icon
        this.trayIconService = new TrayIconService(this);
        this.trayIconService.LeftClick += this.OnTrayIconLeftClick;
        this.trayIconService.RightClick += this.OnTrayIconRightClick;
        this.trayIconService.AddIcon("WSL Kernel Watcher");

        // Hook window messages to process tray icon messages
        this.newWndProcDelegate = new WndProcDelegate(this.NewWndProc);
        this.oldWndProc = SetWindowLongPtr(this.hwnd, GWLWNDPROC, Marshal.GetFunctionPointerForDelegate(this.newWndProcDelegate));

        // Hide window if requested
        if (!showWindow)
        {
            ShowWindow(this.hwnd, SWHIDE);
        }
    }

    private nint NewWndProc(nint hWnd, uint msg, nint wParam, nint lParam)
    {
        // Process tray icon messages
        this.trayIconService?.ProcessWindowMessage(msg, wParam, lParam);

        // Process WM_COMMAND messages for context menu
        if (msg == WMCOMMAND)
        {
            int commandId = wParam.ToInt32() & 0xFFFF;
            if (this.contextMenu?.ProcessCommand(commandId) == true)
            {
                return nint.Zero;
            }
        }

        // Call original window procedure
        return CallWindowProc(this.oldWndProc, hWnd, msg, wParam, lParam);
    }

    public void ShowWindowFromTray()
    {
        ShowWindow(this.hwnd, SWSHOW);
        this.Activate();
    }

    public void HideWindowToTray()
    {
        ShowWindow(this.hwnd, SWHIDE);
    }

    private void SetWindowIcon()
    {
        try
        {
            string iconPath = Path.Combine(AppContext.BaseDirectory, "Assets", "wsl_watcher_icon.ico");
            if (File.Exists(iconPath))
            {
                nint hIconSmall = LoadImage(nint.Zero, iconPath, IMAGEICON, 16, 16, LRLOADFROMFILE);
                nint hIconBig = LoadImage(nint.Zero, iconPath, IMAGEICON, 32, 32, LRLOADFROMFILE);

                if (hIconSmall != nint.Zero)
                {
                    SendMessage(this.hwnd, WMSETICON, new nint(ICONSMALL), hIconSmall);
                }

                if (hIconBig != nint.Zero)
                {
                    SendMessage(this.hwnd, WMSETICON, new nint(ICONBIG), hIconBig);
                }
            }
        }
        catch
        {
            // Ignore errors when loading icon
        }
    }

    private async void OnCheckNow(object sender, RoutedEventArgs e)
    {
        await this.service.CheckOnceAsync();
    }

    private void OnExit(object sender, RoutedEventArgs e)
    {
        this.HideWindowToTray();
    }

    private void OnTrayIconLeftClick(object? sender, EventArgs e)
    {
        this.ShowWindowFromTray();
    }

    private void OnTrayIconRightClick(object? sender, EventArgs e)
    {
        this.contextMenu?.Dispose();
        this.contextMenu = new TrayContextMenu();
        this.contextMenu.AddMenuItem("開く(&O)", () => this.DispatcherQueue.TryEnqueue(this.ShowWindowFromTray));
        this.contextMenu.AddMenuItem("今すぐチェック(&C)", () => this.DispatcherQueue.TryEnqueue(async () => await this.service.CheckOnceAsync()));
        this.contextMenu.AddSeparator();
        this.contextMenu.AddMenuItem("終了(&X)", () => this.DispatcherQueue.TryEnqueue(this.ExitApplication));
        this.contextMenu.Show(this.hwnd);
    }

    private void ExitApplication()
    {
        this.trayIconService?.Dispose();
        this.contextMenu?.Dispose();
        this.Close();
    }

    private void OnStatusChanged(object? sender, string message)
    {
        _ = this.DispatcherQueue.TryEnqueue(() => StatusText.Text = message);
    }

    private void OnLogAppended(object? sender, string line)
    {
        _ = this.DispatcherQueue.TryEnqueue(() =>
        {
            this.logEntries.Add(line);
            const int maxEntries = 200;
            if (this.logEntries.Count > maxEntries)
            {
                this.logEntries.RemoveAt(0);
            }
        });
    }

    private void OnOpenLogFolder(object sender, RoutedEventArgs e)
    {
        try
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = this.loggingService.LogDirectory,
                UseShellExecute = true,
            });
        }
        catch
        {
            // ignore
        }
    }

    private void OnCheckIntervalChanged(NumberBox sender, NumberBoxValueChangedEventArgs args)
    {
        if (double.IsNaN(args.NewValue) || args.NewValue < 1 || args.NewValue > 24)
        {
            return;
        }

        try
        {
            this.settingsService.UpdateCheckInterval((int)args.NewValue);
        }
        catch
        {
            // ignore
        }
    }
}
