// <copyright file="SettingsService.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Text.Json;

namespace WSLKernelWatcher.WinUI3.Services;

internal sealed class SettingsService
{
    private readonly string _settingsDirectory;
    private readonly string _settingsPath;
    private readonly AppSettings _settings;

    public AppSettings Settings => this._settings;

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

        this._settingsDirectory = settingsDirectory;
        Directory.CreateDirectory(this._settingsDirectory);
        this._settingsPath = Path.Combine(this._settingsDirectory, "settings.json");

        this._settings = this.LoadSettings();
    }

    private AppSettings LoadSettings()
    {
        try
        {
            if (File.Exists(this._settingsPath))
            {
                string json = File.ReadAllText(this._settingsPath);
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
            string json = JsonSerializer.Serialize(this._settings, new JsonSerializerOptions
            {
                WriteIndented = true,
            });
            File.WriteAllText(this._settingsPath, json);
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

        this._settings.CheckIntervalHours = hours;
        this.SaveSettings();
    }
}

internal sealed class AppSettings
{
    public int CheckIntervalHours { get; set; } = 2;
}
