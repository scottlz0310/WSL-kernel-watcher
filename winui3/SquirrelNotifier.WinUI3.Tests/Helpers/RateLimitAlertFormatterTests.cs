// <copyright file="RateLimitAlertFormatterTests.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using FluentAssertions;
using SquirrelNotifier.WinUI3.Helpers;
using SquirrelNotifier.WinUI3.Services;

namespace SquirrelNotifier.WinUI3.Tests.Helpers;

// 失敗理由の enum は internal のため、InlineData では名前で受け取り Enum.Parse で解決する
public sealed class RateLimitAlertFormatterTests
{
    [Theory]
    [InlineData("CommandNotFound", "codex コマンドが見つかりませんでした")]
    [InlineData("Timeout", "応答しませんでした（タイムアウト）")]
    [InlineData("Unknown", "codex にログイン済みか確認する")]
    public void BuildCodexFailureMessage_ShouldDescribeReason(string reason, string expectedFragment)
    {
        string message = RateLimitAlertFormatter.BuildCodexFailureMessage(
            "codex",
            Enum.Parse<CodexRateLimitFailureReason>(reason));

        message.Should().StartWith("codex の");
        message.Should().Contain(expectedFragment);
    }

    [Fact]
    public void BuildCodexFailureMessage_ShouldFallBackToUnknownMessage_WhenReasonIsNull()
    {
        // 理由を判別できなかった場合も Unknown と同じ文面にする（未ログインを断定しない）
        string message = RateLimitAlertFormatter.BuildCodexFailureMessage("codex", null);

        message.Should().Be(RateLimitAlertFormatter.BuildCodexFailureMessage("codex", CodexRateLimitFailureReason.Unknown));
    }

    [Fact]
    public void BuildMissingStatusMessage_ShouldPointToStatuslineDocument()
    {
        string message = RateLimitAlertFormatter.BuildMissingStatusMessage("claude-code");

        message.Should().StartWith("claude-code の");
        message.Should().Contain("docs/statusline-integration.md");
    }

    [Fact]
    public void BuildReadFailureMessage_ShouldIncludeDetail()
    {
        string message = RateLimitAlertFormatter.BuildReadFailureMessage("agy (Antigravity CLI)", "アクセスが拒否されました");

        message.Should().Be("agy (Antigravity CLI) のレートリミット状態の読み取りに失敗しました: アクセスが拒否されました");
    }

    [Theory]
    [InlineData(new string[0], null)]
    [InlineData(new[] { "claude-code" }, "claude-code")]
    [InlineData(new[] { "claude-code", "agy (Antigravity CLI)" }, "claude-code、agy (Antigravity CLI)")]
    public void BuildLegacySchemaMessage_ShouldJoinAgentNamesOrReturnNull(string[] agentNames, string? expectedNames)
    {
        string? message = RateLimitAlertFormatter.BuildLegacySchemaMessage(agentNames);

        if (expectedNames is null)
        {
            message.Should().BeNull();
            return;
        }

        message.Should().StartWith($"{expectedNames} の statusline snapshot が旧形式");
        message.Should().Contain("Auto-Pause は機能しません");
    }

    [Fact]
    public void BuildLegacySchemaMessage_ShouldThrow_WhenAgentNamesIsNull()
    {
        Action act = () => RateLimitAlertFormatter.BuildLegacySchemaMessage(null!);

        act.Should().Throw<ArgumentNullException>();
    }
}
