using Microsoft.UI.Xaml;
using Microsoft.Windows.AppNotifications;
using WSLKernelWatcher.WinUI3.Services;

namespace WSLKernelWatcher.WinUI3;

public partial class App : Application
{
    private Window? _window;
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
        _window = new MainWindow(_watcherService, _loggingService);
        _window.Closed += OnWindowClosed;
        _window.Activate();
        _watcherService.Start();
    }

    private void OnWindowClosed(object sender, WindowEventArgs args)
    {
        _watcherService.DisposeAsync().AsTask().ConfigureAwait(false);
    }

    private void OnNotificationInvoked(AppNotificationManager sender, AppNotificationActivatedEventArgs args)
    {
        // Placeholder for activation actions (e.g., open release page)
    }
}
