// <copyright file="ITaskSchedulerService.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace SquirrelNotifier.WinUI3.Services;

internal interface ITaskSchedulerService
{
    Task<TaskRegistrationStatus> GetStatusAsync();

    Task RegisterAsync();

    Task UnregisterAsync();

    Task RepairAsync();
}

internal enum TaskRegistrationStatus
{
    /// <summary>タスクスケジューラに未登録.</summary>
    NotRegistered,

    /// <summary>タスクスケジューラに正しい内容で登録済み.</summary>
    Registered,

    /// <summary>タスクは存在するが登録内容が現在のアプリと一致しない.</summary>
    Invalid,

    /// <summary>タスクスケジューラーの状態を取得できなかった.</summary>
    CheckFailed,
}
