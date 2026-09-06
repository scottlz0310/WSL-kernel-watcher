// <copyright file="ReviewEventParseResult.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System;
using System.Collections.Generic;
using SquirrelNotifier.WinUI3.Models;

namespace SquirrelNotifier.WinUI3.Services;

/// <summary>review event payload のパース結果の種類（#230）.</summary>
internal enum ReviewEventParseStatus
{
    /// <summary>payload を解釈できた。イベント 0 件（空キュー）も含む.</summary>
    Parsed,

    /// <summary>JSON として解釈できない、または想定スキーマから 1 件もイベントを構築できなかった.</summary>
    Malformed,
}

/// <summary>
/// <see cref="ReviewEventParser.Parse"/> の結果。「解釈できて 0 件（空キュー）」と
/// 「payload が壊れていて 0 件」を呼び出し元が区別できるようにするために持つ（#230）.
/// </summary>
internal sealed record ReviewEventParseResult(ReviewEventParseStatus Status, IReadOnlyList<ReviewEvent> Events)
{
    public static ReviewEventParseResult Malformed { get; } =
        new(ReviewEventParseStatus.Malformed, Array.Empty<ReviewEvent>());

    public static ReviewEventParseResult Empty { get; } =
        new(ReviewEventParseStatus.Parsed, Array.Empty<ReviewEvent>());

    public static ReviewEventParseResult Parsed(IReadOnlyList<ReviewEvent> events)
        => new(ReviewEventParseStatus.Parsed, events);
}
