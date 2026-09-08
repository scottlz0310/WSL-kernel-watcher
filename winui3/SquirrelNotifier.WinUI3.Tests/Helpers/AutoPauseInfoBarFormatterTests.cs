// <copyright file="AutoPauseInfoBarFormatterTests.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using FluentAssertions;
using SquirrelNotifier.WinUI3.Helpers;
using SquirrelNotifier.WinUI3.Services;

namespace SquirrelNotifier.WinUI3.Tests.Helpers;

public sealed class AutoPauseInfoBarFormatterTests
{
    private static readonly DateTimeOffset _observedAt = new(2026, 9, 7, 12, 0, 0, TimeSpan.Zero);

    [Fact]
    public void BuildPausedMessage_ShouldReturnNull_WhenNothingIsPaused()
    {
        AutoPauseInfoBarFormatter.BuildPausedMessage([]).Should().BeNull();
    }

    [Fact]
    public void BuildPausedMessage_ShouldListEveryPausedAgentAndReleaseCondition()
    {
        string? message = AutoPauseInfoBarFormatter.BuildPausedMessage(
            [CreatePausedLimit("claude-code", 96), CreatePausedLimit("codex", 99)]);

        message.Should().NotBeNull();
        message!.Should().Contain("96%").And.Contain("99%");
        message.Split(Environment.NewLine).Should().HaveCount(3);
        message.Should().EndWith("fresh なレートリミット情報で使用率 95% 未満を確認すると自動解除されます。");
    }

    [Theory]
    [InlineData("claude-code", "agy", null)]
    [InlineData(null, "agy", "reviewer")]
    [InlineData("claude-code", null, "reviewed")]
    [InlineData(null, null, "reviewer、reviewed")]
    public void BuildNotApplicableMessage_ShouldNameOnlyUnprotectedSlots(
        string? reviewerAgentId,
        string? reviewedAgentId,
        string? expectedSlotNames)
    {
        string? message = AutoPauseInfoBarFormatter.BuildNotApplicableMessage(reviewerAgentId, reviewedAgentId);

        if (expectedSlotNames is null)
        {
            message.Should().BeNull();
            return;
        }

        message.Should().StartWith($"{expectedSlotNames} ランチャーは Auto-Pause の対象外です。");
    }

    private static AutoPausedLimit CreatePausedLimit(string agentId, double usedPercentage)
        => new(agentId, "five-hour", "5時間枠", usedPercentage, _observedAt.AddHours(5), _observedAt);
}
