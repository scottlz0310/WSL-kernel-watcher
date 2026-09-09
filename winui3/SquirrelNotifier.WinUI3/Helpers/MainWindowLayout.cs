namespace SquirrelNotifier.WinUI3.Helpers;

/// <summary>設定の拡大時にも他のペインと仕切りの表示領域を確保する.</summary>
internal static class MainWindowLayout
{
    public static double GetSettingsMaxHeight(double workspaceHeight)
    {
        // 設定ヘッダーと余白、3 ペインの最低高さ、仕切りの領域を残す。
        return Math.Max(80, workspaceHeight - 320);
    }
}
