// <copyright file="SettingsService.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Text.Json;

namespace WSLKernelWatcher.WinUI3.Services;

internal sealed class SettingsService
{
    private readonly string settingsDirectory;
    private readonly string settingsPath;
    private readonly AppSettings settings;

    public AppSettings Settings => this.settings;

    public event EventHandler? SettingsChanged;

    public SettingsService()
        : this(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "WSLKernelWatcher"))
    {
    }

    internal SettingsService(string settingsDirectory)
    {
        if (string.IsNullOrWhiteSpace(settingsDirectory))
        {
            throw new ArgumentException("設定保存先のディレクトリが不正です。", nameof(settingsDirectory));
        }

        this.settingsDirectory = settingsDirectory;
        Directory.CreateDirectory(this.settingsDirectory);
        this.settingsPath = Path.Combine(this.settingsDirectory, "settings.json");

        this.settings = this.LoadSettings();
    }

    private AppSettings LoadSettings()
    {
        try
        {
            if (File.Exists(this.settingsPath))
            {
                string json = File.ReadAllText(this.settingsPath);
                AppSettings? settings = JsonSerializer.Deserialize<AppSettings>(json);
                if (settings != null)
                {
                    return settings;
                }
            }
        }
        catch
        {
            // Ignore errors and use default settings
        }

        return new AppSettings();
    }

    public void SaveSettings()
    {
        try
        {
            string json = JsonSerializer.Serialize(this.settings, new JsonSerializerOptions
            {
                WriteIndented = true,
            });
            File.WriteAllText(this.settingsPath, json);
            this.SettingsChanged?.Invoke(this, EventArgs.Empty);
        }
        catch
        {
            // Ignore save errors
        }
    }

    public void UpdateCheckInterval(int hours)
    {
        if (hours < 1 || hours > 24)
        {
            throw new ArgumentOutOfRangeException(nameof(hours), "Check interval must be between 1 and 24 hours");
        }

        this.settings.CheckIntervalHours = hours;
        this.SaveSettings();
    }
}

internal sealed class AppSettings
{
    public int CheckIntervalHours { get; set; } = 2;
}
