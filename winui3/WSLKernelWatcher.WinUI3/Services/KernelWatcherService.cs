// <copyright file="KernelWatcherService.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Diagnostics;
using System.Diagnostics.CodeAnalysis;
using System.Net.Http;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace WSLKernelWatcher.WinUI3.Services;

[ExcludeFromCodeCoverage]
internal sealed class KernelWatcherService : IAsyncDisposable
{
    private readonly TimeSpan interval;
    private readonly HttpClient httpClient;
    private readonly NotificationService notificationService;
    private readonly LoggingService loggingService;
    private readonly CancellationTokenSource cts = new();
    private Task? loopTask;
    private static readonly Regex VersionRegex = new("(\\d+\\.\\d+\\.\\d+\\.\\d+)", RegexOptions.Compiled);

    public event EventHandler<string>? StatusChanged;

    public KernelWatcherService(NotificationService notificationService, LoggingService loggingService, TimeSpan? interval = null)
    {
        this.interval = interval ?? TimeSpan.FromHours(2);
        this.notificationService = notificationService;
        this.loggingService = loggingService;
        this.httpClient = new HttpClient();
        this.httpClient.DefaultRequestHeaders.UserAgent.ParseAdd("WSL-Kernel-Watcher-WinUI3/0.1");
    }

    public void Start()
    {
        this.loopTask ??= Task.Run(() => this.RunAsync(this.cts.Token));
    }

    public async Task CheckOnceAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            await this.ReportStatusAsync("Checking kernel versions...").ConfigureAwait(false);
            string? current = await GetCurrentKernelVersionAsync(cancellationToken).ConfigureAwait(false);
            string? latest = await this.GetLatestKernelVersionAsync(cancellationToken).ConfigureAwait(false);

            if (string.IsNullOrWhiteSpace(current) || string.IsNullOrWhiteSpace(latest))
            {
                await this.ReportStatusAsync("Unable to determine versions (WSL or GitHub API failed)").ConfigureAwait(false);
                return;
            }

            await this.ReportStatusAsync($"Current: {current} | Latest: {latest}").ConfigureAwait(false);

            if (IsLatestNewer(latest, current))
            {
                await this.ReportStatusAsync("Newer kernel detected. Sending notification.").ConfigureAwait(false);
                this.notificationService.NotifyUpdateAvailable(current, latest);
            }
            else
            {
                await this.ReportStatusAsync("Already up to date.").ConfigureAwait(false);
            }
        }
        catch (Exception ex)
        {
            await this.ReportStatusAsync($"Error: {ex.Message}").ConfigureAwait(false);
        }
    }

    private async Task RunAsync(CancellationToken token)
    {
        using var timer = new PeriodicTimer(this.interval);
        while (!token.IsCancellationRequested)
        {
            await this.CheckOnceAsync(token).ConfigureAwait(false);
            try
            {
                await timer.WaitForNextTickAsync(token).ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                break;
            }
        }
    }

    private static async Task<string?> GetCurrentKernelVersionAsync(CancellationToken token)
    {
        try
        {
            var psi = new ProcessStartInfo
            {
                FileName = "wsl.exe",
                Arguments = "uname -r",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            };

            using var process = new Process { StartInfo = psi, EnableRaisingEvents = true };
            process.Start();

            Task<string> outputTask = process.StandardOutput.ReadToEndAsync();
            Task<string> _ = process.StandardError.ReadToEndAsync();
            await process.WaitForExitAsync(token).ConfigureAwait(false);

            if (process.ExitCode != 0)
            {
                return null;
            }

            string output = await outputTask.ConfigureAwait(false);
            return output.Trim();
        }
        catch
        {
            return null;
        }
    }

    private async Task<string?> GetLatestKernelVersionAsync(CancellationToken token)
    {
        try
        {
            using var request = new HttpRequestMessage(HttpMethod.Get, "https://api.github.com/repos/microsoft/WSL2-Linux-Kernel/releases/latest");
            HttpResponseMessage response = await this.httpClient.SendAsync(request, token).ConfigureAwait(false);
            if (!response.IsSuccessStatusCode)
            {
                return null;
            }

            string content = await response.Content.ReadAsStringAsync(token).ConfigureAwait(false);
            using var doc = JsonDocument.Parse(content);
            if (!doc.RootElement.TryGetProperty("tag_name", out JsonElement tag))
            {
                return null;
            }

            return tag.GetString();
        }
        catch
        {
            return null;
        }
    }

    private static bool IsLatestNewer(string latest, string current)
    {
        Match currentMatch = VersionRegex.Match(current);
        Match latestMatch = VersionRegex.Match(latest);
        if (!currentMatch.Success || !latestMatch.Success)
        {
            return false;
        }

        if (!Version.TryParse(currentMatch.Groups[1].Value, out Version? currentVer))
        {
            return false;
        }

        if (!Version.TryParse(latestMatch.Groups[1].Value, out Version? latestVer))
        {
            return false;
        }

        return latestVer > currentVer;
    }

    private async Task ReportStatusAsync(string message)
    {
        this.StatusChanged?.Invoke(this, message);
        await this.loggingService.WriteAsync(message).ConfigureAwait(false);
    }

    public async ValueTask DisposeAsync()
    {
        this.cts.Cancel();
        this.httpClient.Dispose();
        if (this.loopTask is not null)
        {
            try
            {
                await this.loopTask.ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                // Expected during shutdown
            }
        }

        this.cts.Dispose();
    }
}
