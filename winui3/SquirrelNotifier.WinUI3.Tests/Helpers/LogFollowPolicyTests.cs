// <copyright file="LogFollowPolicyTests.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using FluentAssertions;
using SquirrelNotifier.WinUI3.Helpers;
using Xunit;

namespace SquirrelNotifier.WinUI3.Tests.Helpers;

public class LogFollowPolicyTests
{
    [Theory]
    // 全行が表示に収まっている（スクロール不能）
    [InlineData(0, 0, true)]
    [InlineData(0, -1, true)]
    // 末尾にいる
    [InlineData(400, 400, true)]
    // 末尾付近（既定しきい値 24px 以内）
    [InlineData(380, 400, true)]
    [InlineData(376, 400, true)]
    // 過去ログを読むために上へスクロール中
    [InlineData(375, 400, false)]
    [InlineData(0, 400, false)]
    [InlineData(100, 400, false)]
    public void ShouldFollow_ByScrollPosition(double verticalOffset, double scrollableHeight, bool expected)
    {
        LogFollowPolicy.ShouldFollow(verticalOffset, scrollableHeight).Should().Be(expected);
    }

    [Theory]
    [InlineData(double.NaN, 400)]
    [InlineData(100, double.NaN)]
    [InlineData(double.NaN, double.NaN)]
    public void ShouldFollow_UndeterminableLayout_ShouldFollow(double verticalOffset, double scrollableHeight)
    {
        // レイアウト未確定で判定できない場合は「新しい行が見えること」を優先する
        LogFollowPolicy.ShouldFollow(verticalOffset, scrollableHeight).Should().BeTrue();
    }

    [Theory]
    [InlineData(300, 400, 100, true)]
    [InlineData(299, 400, 100, false)]
    [InlineData(400, 400, 0, true)]
    [InlineData(399, 400, 0, false)]
    [InlineData(399, 400, -10, false)]
    public void ShouldFollow_WithExplicitThreshold(
        double verticalOffset,
        double scrollableHeight,
        double thresholdPixels,
        bool expected)
    {
        LogFollowPolicy.ShouldFollow(verticalOffset, scrollableHeight, thresholdPixels).Should().Be(expected);
    }
}
