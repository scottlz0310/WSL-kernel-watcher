// <copyright file="AutoPauseInfoBarFormatter.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System;
using System.Collections.Generic;
using System.Linq;
using SquirrelNotifier.WinUI3.Services;

namespace SquirrelNotifier.WinUI3.Helpers;

/// <summary>
/// メイン画面の Auto-Pause 関連 InfoBar（#147 / #233）の文言と表示要否を組み立てる。
/// InfoBar への代入は呼び出し側（code-behind）の責務とし、ここでは表示すべき文言のみを返す.
/// </summary>
internal static class AutoPauseInfoBarFormatter
{
    /// <summary>
    /// Paused な agent がある間に表示する文言を返す.
    /// </summary>
    /// <param name="pausedLimits">Paused の根拠となった limit 一覧.</param>
    /// <returns>表示する文言。表示不要な場合は <see langword="null"/>.</returns>
    public static string? BuildPausedMessage(IReadOnlyList<AutoPausedLimit> pausedLimits)
    {
        ArgumentNullException.ThrowIfNull(pausedLimits);
        if (pausedLimits.Count == 0)
        {
            return null;
        }

        return string.Join(Environment.NewLine, pausedLimits.Select(paused => paused.BuildReasonText()))
            + Environment.NewLine
            + "fresh なレートリミット情報で使用率 95% 未満を確認すると自動解除されます。";
    }

    /// <summary>
    /// rateLimitAgentId を解決できないスロットを知らせる文言を返す。該当スロットは Auto-Pause gate が
    /// NotApplicable を返し、危険水域でも新規起動を止めない。以前はこれが UI に一切出ず、
    /// 保護が外れたことに気づけなかった（#233）.
    /// </summary>
    /// <param name="reviewerRateLimitAgentId">reviewer スロットの rateLimitAgentId。解決できない場合は null.</param>
    /// <param name="reviewedRateLimitAgentId">reviewed スロットの rateLimitAgentId。解決できない場合は null.</param>
    /// <returns>表示する文言。両スロットとも対象内の場合は <see langword="null"/>.</returns>
    public static string? BuildNotApplicableMessage(string? reviewerRateLimitAgentId, string? reviewedRateLimitAgentId)
    {
        List<string> slotNames = [];
        if (reviewerRateLimitAgentId is null)
        {
            slotNames.Add("reviewer");
        }

        if (reviewedRateLimitAgentId is null)
        {
            slotNames.Add("reviewed");
        }

        if (slotNames.Count == 0)
        {
            return null;
        }

        return $"{string.Join("、", slotNames)} ランチャーは Auto-Pause の対象外です。"
            + "レートリミットが危険水域でも新規起動は停止されません。"
            + "コマンドがプリセット（claude / codex / agy）のいずれとも一致しないか、"
            + "レートリミットを取得できないエージェント（copilot）が設定されています。";
    }
}
