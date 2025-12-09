using System.Collections.ObjectModel;
using System.Diagnostics;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Windows.Graphics;
using WSLKernelWatcher.WinUI3.Services;

namespace WSLKernelWatcher.WinUI3;

public sealed partial class MainWindow : Window
{
    private readonly KernelWatcherService _service;
    private readonly LoggingService _loggingService;
    private readonly ObservableCollection<string> _logEntries = new();

    public MainWindow(KernelWatcherService service, LoggingService loggingService)
    {
        InitializeComponent();

        // Set window size (WinUI3 requires this in code)
        var hwnd = WinRT.Interop.WindowNative.GetWindowHandle(this);
        var windowId = Microsoft.UI.Win32Interop.GetWindowIdFromWindow(hwnd);
        var appWindow = Microsoft.UI.Windowing.AppWindow.GetFromWindowId(windowId);
        appWindow.Resize(new SizeInt32(520, 360));

        _service = service;
        _loggingService = loggingService;
        _service.StatusChanged += OnStatusChanged;
        _loggingService.LogAppended += OnLogAppended;
        LogList.ItemsSource = _logEntries;
    }

    private async void OnCheckNow(object sender, RoutedEventArgs e)
    {
        await _service.CheckOnceAsync();
    }

    private void OnExit(object sender, RoutedEventArgs e)
    {
        Close();
    }

    private void OnStatusChanged(object? sender, string message)
    {
        _ = DispatcherQueue.TryEnqueue(() => StatusText.Text = message);
    }

    private void OnLogAppended(object? sender, string line)
    {
        _ = DispatcherQueue.TryEnqueue(() =>
        {
            _logEntries.Add(line);
            const int maxEntries = 200;
            if (_logEntries.Count > maxEntries)
            {
                _logEntries.RemoveAt(0);
            }
        });
    }

    private void OnOpenLogFolder(object sender, RoutedEventArgs e)
    {
        try
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = _loggingService.LogDirectory,
                UseShellExecute = true,
            });
        }
        catch
        {
            // ignore
        }
    }
}
