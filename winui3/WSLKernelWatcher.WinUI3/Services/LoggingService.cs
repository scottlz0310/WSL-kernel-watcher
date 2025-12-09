using System.Diagnostics;
using System.IO;

namespace WSLKernelWatcher.WinUI3.Services;

public sealed class LoggingService
{
    private const long MaxBytes = 1_000_000; // 1MB
    private readonly string _logDirectory;
    private readonly string _logFilePath;

    public event EventHandler<string>? LogAppended;

    public LoggingService()
    {
        _logDirectory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "WSLKernelWatcher", "logs");
        Directory.CreateDirectory(_logDirectory);
        _logFilePath = Path.Combine(_logDirectory, "winui3.log");
    }

    public string LogDirectory => _logDirectory;

    public async Task WriteAsync(string message)
    {
        var line = $"[{DateTimeOffset.Now:yyyy-MM-dd HH:mm:ss}] {message}";
        await RotateIfNeededAsync().ConfigureAwait(false);
        try
        {
            await File.AppendAllTextAsync(_logFilePath, line + Environment.NewLine).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Failed to write log: {ex.Message}");
        }

        LogAppended?.Invoke(this, line);
    }

    private Task RotateIfNeededAsync()
    {
        try
        {
            var info = new FileInfo(_logFilePath);
            if (info.Exists && info.Length > MaxBytes)
            {
                var archive = Path.Combine(_logDirectory, $"winui3-{DateTimeOffset.Now:yyyyMMddHHmmss}.log");
                File.Move(_logFilePath, archive, true);
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Failed to rotate log: {ex.Message}");
        }

        return Task.CompletedTask;
    }
}
