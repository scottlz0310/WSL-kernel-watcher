// <copyright file="LogFollowPolicy.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System;

namespace SquirrelNotifier.WinUI3.Helpers;

/// <summary>
/// ログリストが新しい行へ自動追従するかを判定する（#232）。WinUI 型に依存しない純粋計算とし、
/// 呼び出し側が ScrollViewer の現在値を渡す。ユーザーが過去ログを読むために上へスクロール
/// している間は追従を止め、末尾付近へ戻れば再び追従を再開する.
/// </summary>
internal static class LogFollowPolicy
{
    /// <summary>末尾とみなす距離（有効ピクセル）。1 行分に満たないズレを末尾扱いにする.</summary>
    public const double DefaultThresholdPixels = 24;

    /// <summary>
    /// 新しい行を追加した後に末尾へスクロールしてよいかを判定する.
    /// </summary>
    /// <param name="verticalOffset">追加前の ScrollViewer の垂直オフセット.</param>
    /// <param name="scrollableHeight">追加前の ScrollViewer のスクロール可能高さ.</param>
    /// <param name="thresholdPixels">末尾とみなす距離.</param>
    /// <returns>追従してよい場合は true.</returns>
    public static bool ShouldFollow(
        double verticalOffset,
        double scrollableHeight,
        double thresholdPixels = DefaultThresholdPixels)
    {
        // ScrollViewer 未実体化・レイアウト未確定では NaN が渡りうる。判定不能なときは
        // 「新しい行が見えること」を優先して追従する（#232 の実害はスクロールしないこと）
        if (double.IsNaN(verticalOffset) || double.IsNaN(scrollableHeight))
        {
            return true;
        }

        // 全行が表示に収まっている間はスクロールの概念がないため常に追従扱い
        if (scrollableHeight <= 0)
        {
            return true;
        }

        double distanceFromBottom = scrollableHeight - verticalOffset;
        return distanceFromBottom <= Math.Max(0, thresholdPixels);
    }
}
