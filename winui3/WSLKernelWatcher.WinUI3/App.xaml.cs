// <copyright file="App.xaml.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Diagnostics.CodeAnalysis;
using Microsoft.UI.Xaml;
using Microsoft.Windows.AppNotifications;
using WSLKernelWatcher.WinUI3.Services;

namespace WSLKernelWatcher.WinUI3;

[ExcludeFromCodeCoverage]
[System.Diagnostics.CodeAnalysis.SuppressMessage("Design", "CA1515", Justification = "WinUI entry point requires public accessibility")]
public partial class App : Application
{
    private MainWindow? _window;
    private readonly NotificationService _notificationService = new();
    private readonly LoggingService _loggingService = new();
    private readonly SettingsService _settingsService = new();
    private readonly KernelWatcherService _watcherService;

    public App()
    {
        InitializeComponent();
        AppNotificationManager.Default.NotificationInvoked += this.OnNotificationInvoked;
        AppNotificationManager.Default.Register();
        this._notificationService.Initialize();

        // Create watcher service with settings
        var interval = TimeSpan.FromHours(this._settingsService.Settings.CheckIntervalHours);
        this._watcherService = new KernelWatcherService(this._notificationService, this._loggingService, interval);
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        // Check for command-line arguments
        string[] commandLineArgs = Environment.GetCommandLineArgs();
        bool showWindow = !commandLineArgs.Contains("--tray") && !commandLineArgs.Contains("-t");

        this._window = new MainWindow(this._watcherService, this._loggingService, this._settingsService, showWindow);
        this._window.Closed += this.OnWindowClosed;

        // Activate window if it should be shown
        if (showWindow)
        {
            this._window.Activate();
        }

        this._watcherService.Start();
    }

    private void OnWindowClosed(object sender, WindowEventArgs args)
    {
        this._watcherService.DisposeAsync().AsTask().ConfigureAwait(false);
    }

    private void OnNotificationInvoked(AppNotificationManager sender, AppNotificationActivatedEventArgs args)
    {
        // Show window when notification is clicked
        if (this._window != null)
        {
            this._window.DispatcherQueue.TryEnqueue(() => this._window.ShowWindowFromTray());
        }
    }
}
