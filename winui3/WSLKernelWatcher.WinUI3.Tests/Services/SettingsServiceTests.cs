using FluentAssertions;
using WSLKernelWatcher.WinUI3.Services;

namespace WSLKernelWatcher.WinUI3.Tests.Services;

public class SettingsServiceTests : IDisposable
{
    private readonly string _testSettingsPath;
    private readonly SettingsService _settingsService;

    public SettingsServiceTests()
    {
        // Use a temporary settings file for testing
        _testSettingsPath = Path.Combine(Path.GetTempPath(), $"test_settings_{Guid.NewGuid()}.json");
        _settingsService = new SettingsService();
    }

    public void Dispose()
    {
        // Clean up test settings file
        if (File.Exists(_testSettingsPath))
        {
            File.Delete(_testSettingsPath);
        }
    }

    [Fact]
    public void Settings_ShouldHaveDefaultValues()
    {
        // Arrange & Act
        AppSettings settings = _settingsService.Settings;

        // Assert
        settings.CheckIntervalHours.Should().Be(2);
    }

    [Fact]
    public void UpdateCheckInterval_ShouldUpdateSettings()
    {
        // Arrange
        const int newInterval = 5;

        // Act
        _settingsService.UpdateCheckInterval(newInterval);

        // Assert
        _settingsService.Settings.CheckIntervalHours.Should().Be(newInterval);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    [InlineData(25)]
    [InlineData(100)]
    public void UpdateCheckInterval_ShouldThrowForInvalidValues(int invalidInterval)
    {
        // Act & Assert
        Action act = () => _settingsService.UpdateCheckInterval(invalidInterval);
        act.Should().Throw<ArgumentOutOfRangeException>();
    }

    [Theory]
    [InlineData(1)]
    [InlineData(12)]
    [InlineData(24)]
    public void UpdateCheckInterval_ShouldAcceptValidValues(int validInterval)
    {
        // Act
        Action act = () => _settingsService.UpdateCheckInterval(validInterval);

        // Assert
        act.Should().NotThrow();
        _settingsService.Settings.CheckIntervalHours.Should().Be(validInterval);
    }

    [Fact]
    public void SettingsChanged_ShouldBeRaisedWhenSettingsUpdated()
    {
        // Arrange
        bool eventRaised = false;
        _settingsService.SettingsChanged += (_, _) => eventRaised = true;

        // Act
        _settingsService.UpdateCheckInterval(3);

        // Assert
        eventRaised.Should().BeTrue();
    }
}
