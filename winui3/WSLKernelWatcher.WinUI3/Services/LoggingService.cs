// <copyright file="LoggingService.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Diagnostics;
using System.IO;

namespace WSLKernelWatcher.WinUI3.Services;

internal sealed class LoggingService
{
    private const long DefaultMaxBytes = 1_000_000; // 1MB
    private readonly string logDirectory;
    private readonly string logFilePath;
    private readonly long maxBytes;

    public event EventHandler<string>? LogAppended;

    public LoggingService()
        : this(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "WSLKernelWatcher", "logs"), DefaultMaxBytes)
    {
    }

    internal LoggingService(string logDirectory, long maxBytes = DefaultMaxBytes)
    {
        if (string.IsNullOrWhiteSpace(logDirectory))
        {
            throw new ArgumentException("ログの出力先ディレクトリが不正です。", nameof(logDirectory));
        }

        if (maxBytes <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(maxBytes), "ログファイルの最大サイズは 1 バイト以上である必要があります。");
        }

        this.logDirectory = logDirectory;
        this.maxBytes = maxBytes;
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
            if (info.Exists && info.Length > this.maxBytes)
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
