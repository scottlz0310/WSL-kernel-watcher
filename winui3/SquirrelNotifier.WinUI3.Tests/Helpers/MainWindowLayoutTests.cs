using FluentAssertions;
using SquirrelNotifier.WinUI3.Helpers;
using Xunit;

namespace SquirrelNotifier.WinUI3.Tests.Helpers;

public class MainWindowLayoutTests
{
    [Theory]
    [InlineData(0, 80)]
    [InlineData(400, 80)]
    [InlineData(580, 260)]
    [InlineData(900, 580)]
    public void GetSettingsMaxHeight_ShouldReserveSpaceForOtherPanes(double workspaceHeight, double expected)
    {
        MainWindowLayout.GetSettingsMaxHeight(workspaceHeight).Should().Be(expected);
    }
}
