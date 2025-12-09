using Microsoft.UI.Xaml;
using Microsoft.Windows.AppNotifications;
using WSLKernelWatcher.WinUI3.Services;

namespace WSLKernelWatcher.WinUI3;

public partial class App : Application
{
    private MainWindow? _window;
    private readonly NotificationService _notificationService = new();
    private readonly LoggingService _loggingService = new();
    private readonly KernelWatcherService _watcherService;

    public App()
    {
        InitializeComponent();
        AppNotificationManager.Default.NotificationInvoked += OnNotificationInvoked;
        AppNotificationManager.Default.Register();
        _notificationService.Initialize();
        _watcherService = new KernelWatcherService(_notificationService, _loggingService);
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        // Check for command-line arguments
        var commandLineArgs = Environment.GetCommandLineArgs();
        bool showWindow = !commandLineArgs.Contains("--tray") && !commandLineArgs.Contains("-t");

        _window = new MainWindow(_watcherService, _loggingService, showWindow);
        _window.Closed += OnWindowClosed;

        // Activate window if it should be shown
        if (showWindow)
        {
            _window.Activate();
        }

        _watcherService.Start();
    }

    private void OnWindowClosed(object sender, WindowEventArgs args)
    {
        _watcherService.DisposeAsync().AsTask().ConfigureAwait(false);
    }

    private void OnNotificationInvoked(AppNotificationManager sender, AppNotificationActivatedEventArgs args)
    {
        // Show window when notification is clicked
        if (_window != null)
        {
            _window.DispatcherQueue.TryEnqueue(() => _window.ShowWindowFromTray());
        }
    }
}
