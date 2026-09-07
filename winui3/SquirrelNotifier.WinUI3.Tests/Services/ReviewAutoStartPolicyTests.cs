// <copyright file="ReviewAutoStartPolicyTests.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using FluentAssertions;
using SquirrelNotifier.WinUI3.Services;

namespace SquirrelNotifier.WinUI3.Tests.Services;

// 判定対象の enum は internal のため、InlineData では名前で受け取り Enum.Parse で解決する
public sealed class ReviewAutoStartPolicyTests
{
    [Theory]
    [InlineData(true, "opened", false, "Start")]
    [InlineData(true, "synchronized", false, "Start")]
    [InlineData(true, "re-review-requested", false, "Start")]
    [InlineData(false, "opened", false, "SkippedDisabled")]
    [InlineData(false, "opened", true, "SkippedDisabled")]
    [InlineData(false, "review-posted", false, "SkippedDisabled")]
    [InlineData(true, "review-posted", false, "SkippedUnsupportedReason")]
    [InlineData(true, "", false, "SkippedUnsupportedReason")]
    [InlineData(true, "review-posted", true, "SkippedUnsupportedReason")]
    [InlineData(true, "opened", true, "SkippedBusy")]
    [InlineData(true, "re-review-requested", true, "SkippedBusy")]
    public void Evaluate_ShouldDecideAutoStart(bool autoStartEnabled, string reason, bool isReviewBusy, string expectedOutcome)
    {
        ReviewAutoStartOutcome result = ReviewAutoStartPolicy.Evaluate(autoStartEnabled, reason, isReviewBusy);

        result.Should().Be(Enum.Parse<ReviewAutoStartOutcome>(expectedOutcome));
    }

    [Theory]
    [InlineData("Manual", true)]
    [InlineData("Automatic", false)]
    public void AllowsAutoPauseOverridePrompt_ShouldOnlyPromptForManualStart(string trigger, bool expected)
    {
        bool result = ReviewAutoStartPolicy.AllowsAutoPauseOverridePrompt(Enum.Parse<ReviewStartTrigger>(trigger));

        result.Should().Be(expected);
    }

    [Theory]
    [InlineData("SkippedUnsupportedReason")]
    [InlineData("SkippedBusy")]
    public void DescribeSkipReason_ShouldReturnReason_WhenSkippedWhileEnabled(string outcome)
    {
        ReviewAutoStartPolicy.DescribeSkipReason(Enum.Parse<ReviewAutoStartOutcome>(outcome))
            .Should().NotBeNullOrWhiteSpace();
    }

    // 設定 off のときに行を残すと、off の挙動が現行と変わってしまうため記録しない
    [Theory]
    [InlineData("Start")]
    [InlineData("SkippedDisabled")]
    public void DescribeSkipReason_ShouldReturnNull_WhenNothingToRecord(string outcome)
    {
        ReviewAutoStartPolicy.DescribeSkipReason(Enum.Parse<ReviewAutoStartOutcome>(outcome))
            .Should().BeNull();
    }
}
