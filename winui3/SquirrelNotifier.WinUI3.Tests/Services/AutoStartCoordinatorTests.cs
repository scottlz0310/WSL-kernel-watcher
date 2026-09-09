// <copyright file="AutoStartCoordinatorTests.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

using System;
using System.Threading.Tasks;
using FluentAssertions;
using Moq;
using SquirrelNotifier.WinUI3.Services;

namespace SquirrelNotifier.WinUI3.Tests.Services;

public sealed class AutoStartCoordinatorTests
{
    [Theory]
    [InlineData("Registered", true, "登録済み", true, false)]
    [InlineData("NotRegistered", false, "未登録", false, true)]
    [InlineData("Invalid", false, "要修復", true, false)]
    [InlineData("CheckFailed", null, "確認に失敗しました", false, false)]
    public void DescribeStatus_ShouldMapTaskStatusToPresentation(
        string statusName,
        bool? expectedToggleIsOn,
        string expectedStatusText,
        bool expectedRepairEnabled,
        bool expectedOnboardingOpen)
    {
        TaskRegistrationStatus status = Enum.Parse<TaskRegistrationStatus>(statusName);
        AutoStartStatusPresentation presentation = AutoStartCoordinator.DescribeStatus(status);

        presentation.ToggleIsOn.Should().Be(expectedToggleIsOn);
        presentation.StatusText.Should().Be(expectedStatusText);
        presentation.IsRepairEnabled.Should().Be(expectedRepairEnabled);
        presentation.IsOnboardingOpen.Should().Be(expectedOnboardingOpen);
    }

    [Fact]
    public async Task RefreshStatusAsync_ShouldApplyPresentationWhileSuppressingToggle()
    {
        var scheduler = new Mock<ITaskSchedulerService>();
        scheduler.Setup(service => service.GetStatusAsync())
            .ReturnsAsync(TaskRegistrationStatus.Registered);
        var coordinator = new AutoStartCoordinator(scheduler.Object);
        AutoStartStatusPresentation? actual = null;
        bool wasSuppressed = false;

        await coordinator.RefreshStatusAsync(presentation =>
        {
            actual = presentation;
            wasSuppressed = coordinator.IsToggleSuppressed;
        });

        actual.Should().NotBeNull();
        actual!.StatusText.Should().Be("登録済み");
        wasSuppressed.Should().BeTrue();
        coordinator.IsToggleSuppressed.Should().BeFalse();
    }

    [Fact]
    public async Task RefreshStatusAsync_ShouldReturnCheckFailedPresentationWhenStatusThrows()
    {
        var scheduler = new Mock<ITaskSchedulerService>();
        scheduler.Setup(service => service.GetStatusAsync())
            .ThrowsAsync(new InvalidOperationException("状態取得失敗"));
        var coordinator = new AutoStartCoordinator(scheduler.Object);
        AutoStartStatusPresentation? actual = null;

        await coordinator.RefreshStatusAsync(presentation => actual = presentation);

        actual.Should().NotBeNull();
        actual!.ToggleIsOn.Should().BeNull();
        actual.StatusText.Should().Be("確認に失敗しました");
    }

    [Fact]
    public async Task ToggleAsync_ShouldConfirmAndRegisterWhileKeepingOperationPending()
    {
        var scheduler = new Mock<ITaskSchedulerService>();
        var coordinator = new AutoStartCoordinator(scheduler.Object);
        AutoStartConfirmation? actualConfirmation = null;
        bool wasSuppressed = false;

        AutoStartOperationResult result = await coordinator.ToggleAsync(
            true,
            confirmation =>
            {
                actualConfirmation = confirmation;
                wasSuppressed = coordinator.IsToggleSuppressed;
                return Task.FromResult(true);
            });

        result.Status.Should().Be(AutoStartOperationStatus.Completed);
        result.ShouldRefresh.Should().BeTrue();
        actualConfirmation.Should().NotBeNull();
        actualConfirmation!.Title.Should().Be("自動起動を設定します");
        actualConfirmation.Message.Should().Contain("--tray");
        wasSuppressed.Should().BeTrue();
        coordinator.IsToggleSuppressed.Should().BeFalse();
        scheduler.Verify(service => service.RegisterAsync(), Times.Once);
    }

    [Fact]
    public async Task ToggleAsync_ShouldRestoreToggleAndSkipOperationWhenCancelled()
    {
        var scheduler = new Mock<ITaskSchedulerService>();
        var coordinator = new AutoStartCoordinator(scheduler.Object);

        AutoStartOperationResult result = await coordinator.ToggleAsync(
            false,
            _ => Task.FromResult(false));

        result.Status.Should().Be(AutoStartOperationStatus.CancelledByUser);
        result.ToggleIsOn.Should().BeTrue();
        result.ShouldRefresh.Should().BeFalse();
        scheduler.Verify(service => service.UnregisterAsync(), Times.Never);
    }

    [Fact]
    public async Task ToggleAsync_ShouldReturnFailureAndResetOperationStateWhenOperationThrows()
    {
        var scheduler = new Mock<ITaskSchedulerService>();
        scheduler.Setup(service => service.RegisterAsync())
            .ThrowsAsync(new InvalidOperationException("登録失敗"));
        var coordinator = new AutoStartCoordinator(scheduler.Object);

        AutoStartOperationResult result = await coordinator.ToggleAsync(true, _ => Task.FromResult(true));

        result.Status.Should().Be(AutoStartOperationStatus.Failed);
        result.ErrorTitle.Should().Be("自動起動の設定に失敗しました");
        result.ErrorMessage.Should().Be("登録失敗");
        result.ShouldRefresh.Should().BeTrue();
        coordinator.IsToggleSuppressed.Should().BeFalse();
    }

    [Fact]
    public async Task ToggleAsync_ShouldSkipReentrantOperationDuringConfirmation()
    {
        var scheduler = new Mock<ITaskSchedulerService>();
        var coordinator = new AutoStartCoordinator(scheduler.Object);
        var entered = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        var confirmation = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);

        Task<AutoStartOperationResult> first = coordinator.ToggleAsync(
            true,
            _ =>
            {
                entered.SetResult(true);
                return confirmation.Task;
            });
        await entered.Task;

        AutoStartOperationResult second = await coordinator.ToggleAsync(true, _ => Task.FromResult(true));

        second.Status.Should().Be(AutoStartOperationStatus.SkippedBusy);
        confirmation.SetResult(false);
        (await first).Status.Should().Be(AutoStartOperationStatus.CancelledByUser);
    }

    [Fact]
    public async Task RepairAsync_ShouldReturnFailureAndResetOperationStateWhenRepairThrows()
    {
        var scheduler = new Mock<ITaskSchedulerService>();
        scheduler.Setup(service => service.RepairAsync())
            .ThrowsAsync(new InvalidOperationException("修復失敗"));
        var coordinator = new AutoStartCoordinator(scheduler.Object);

        AutoStartOperationResult result = await coordinator.RepairAsync();

        result.Status.Should().Be(AutoStartOperationStatus.Failed);
        result.ErrorTitle.Should().Be("タスク修復に失敗しました");
        result.ErrorMessage.Should().Be("修復失敗");
        coordinator.IsToggleSuppressed.Should().BeFalse();
    }
}
