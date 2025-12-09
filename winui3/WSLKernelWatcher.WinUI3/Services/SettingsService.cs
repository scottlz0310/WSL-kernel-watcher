// <copyright file="SettingsService.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System.Text.Json;

namespace WSLKernelWatcher.WinUI3.Services;

public class SettingsService
{
    private readonly string settingsPath;
    private readonly AppSettings settings;

    public AppSettings Settings => this.settings;

    public event EventHandler? SettingsChanged;

    public SettingsService()
    {
        string appDataPath = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        string appFolder = Path.Combine(appDataPath, "WSLKernelWatcher");
        Directory.CreateDirectory(appFolder);
        this.settingsPath = Path.Combine(appFolder, "settings.json");

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

public class AppSettings
{
    public int CheckIntervalHours { get; set; } = 2;
}
