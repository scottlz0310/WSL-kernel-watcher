// <copyright file="App.xaml.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using Microsoft.UI.Xaml;
using Microsoft.Windows.AppNotifications;
using WSLKernelWatcher.WinUI3.Services;

namespace WSLKernelWatcher.WinUI3;

public partial class App : Application
{
    private MainWindow? window;
    private readonly NotificationService notificationService = new();
    private readonly LoggingService loggingService = new();
    private readonly SettingsService settingsService = new();
    private readonly KernelWatcherService watcherService;

    public App()
    {
        InitializeComponent();
        AppNotificationManager.Default.NotificationInvoked += this.OnNotificationInvoked;
        AppNotificationManager.Default.Register();
        this.notificationService.Initialize();

        // Create watcher service with settings
        var interval = TimeSpan.FromHours(this.settingsService.Settings.CheckIntervalHours);
        this.watcherService = new KernelWatcherService(this.notificationService, this.loggingService, interval);
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        // Check for command-line arguments
        string[] commandLineArgs = Environment.GetCommandLineArgs();
        bool showWindow = !commandLineArgs.Contains("--tray") && !commandLineArgs.Contains("-t");

        this.window = new MainWindow(this.watcherService, this.loggingService, this.settingsService, showWindow);
        this.window.Closed += this.OnWindowClosed;

        // Activate window if it should be shown
        if (showWindow)
        {
            this.window.Activate();
        }

        this.watcherService.Start();
    }

    private void OnWindowClosed(object sender, WindowEventArgs args)
    {
        this.watcherService.DisposeAsync().AsTask().ConfigureAwait(false);
    }

    private void OnNotificationInvoked(AppNotificationManager sender, AppNotificationActivatedEventArgs args)
    {
        // Show window when notification is clicked
        if (this.window != null)
        {
            this.window.DispatcherQueue.TryEnqueue(() => this.window.ShowWindowFromTray());
        }
    }
}
