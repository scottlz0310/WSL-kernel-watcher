// <copyright file="LoggingService.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Diagnostics;
using System.IO;

namespace WSLKernelWatcher.WinUI3.Services;

internal sealed class LoggingService
{
    private const long MaxBytes = 1_000_000; // 1MB
    private readonly string logDirectory;
    private readonly string logFilePath;

    public event EventHandler<string>? LogAppended;

    public LoggingService()
    {
        this.logDirectory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "WSLKernelWatcher", "logs");
        Directory.CreateDirectory(this.logDirectory);
        this.logFilePath = Path.Combine(this.logDirectory, "winui3.log");
    }

    public string LogDirectory => this.logDirectory;

    public async Task WriteAsync(string message)
    {
        string line = $"[{DateTimeOffset.Now:yyyy-MM-dd HH:mm:ss}] {message}";
        await this.RotateIfNeededAsync().ConfigureAwait(false);
        try
        {
            await File.AppendAllTextAsync(this.logFilePath, line + Environment.NewLine).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Failed to write log: {ex.Message}");
        }

        this.LogAppended?.Invoke(this, line);
    }

    private Task RotateIfNeededAsync()
    {
        try
        {
            var info = new FileInfo(this.logFilePath);
            if (info.Exists && info.Length > MaxBytes)
            {
                string archive = Path.Combine(this.logDirectory, $"winui3-{DateTimeOffset.Now:yyyyMMddHHmmss}.log");
                File.Move(this.logFilePath, archive, true);
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Failed to rotate log: {ex.Message}");
        }

        return Task.CompletedTask;
    }
}
