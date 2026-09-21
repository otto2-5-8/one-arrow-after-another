param(
    [Parameter(Mandatory = $true)][int]$ProcessId,
    [Parameter(Mandatory = $true)][string]$Out
)

Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;using System.Text;using System.Runtime.InteropServices;
public class WinCap {
  delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] static extern int GetWindowTextLength(IntPtr h);
  [DllImport("user32.dll")] static extern int GetClassName(IntPtr h, StringBuilder s, int c);
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern int GetSystemMetrics(int i);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
  public static IntPtr best = IntPtr.Zero;
  public static string bestInfo = "";
  public static void Find(uint target) {
    best = IntPtr.Zero; long area = -1;
    EnumWindows((h,l) => {
      if (!IsWindowVisible(h)) return true;
      if (GetWindowTextLength(h) == 0) return true;
      uint pid; GetWindowThreadProcessId(h, out pid);
      if (pid != target) return true;
      var sb = new StringBuilder(256); GetClassName(h, sb, 256);
      if (sb.ToString() == "ConsoleWindowClass") return true;
      RECT r; GetWindowRect(h, out r);
      long a = (long)(r.R - r.L) * (r.B - r.T);
      if (a > area) { area = a; best = h; bestInfo = sb.ToString(); }
      return true;
    }, IntPtr.Zero);
  }
}
"@

[WinCap]::SetProcessDPIAware() | Out-Null

[WinCap]::Find([uint32]$ProcessId)
$hwnd = [WinCap]::best
if ($hwnd -eq [IntPtr]::Zero) { Write-Host "no-window-for-pid"; exit 2 }

[WinCap]::ShowWindow($hwnd, 9) | Out-Null
[WinCap]::SetForegroundWindow($hwnd) | Out-Null
# HWND_TOPMOST, SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW
[WinCap]::SetWindowPos($hwnd, [IntPtr](-1), 0, 0, 0, 0, 0x0001 -bor 0x0002 -bor 0x0040) | Out-Null
Start-Sleep -Milliseconds 350

$rect = New-Object WinCap+RECT
[WinCap]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
# SM_CXSIZEFRAME + SM_CXPADDEDBORDER = 边框，SM_CYCAPTION = 标题栏
$frame = [WinCap]::GetSystemMetrics(32)
$padded = [WinCap]::GetSystemMetrics(92)
$caption = [WinCap]::GetSystemMetrics(4)
if (-not $padded) { $padded = 5 }
if (-not $frame) { $frame = $padded }
if (-not $caption) { $caption = 29 }
$border = $frame + $padded
$fullW = $rect.R - $rect.L
$fullH = $rect.B - $rect.T
$cropX = $border
$cropY = $caption + $border
$cropW = $fullW - 2 * $border
$cropH = $fullH - $caption - 2 * $border
if ($env:CAPTURE_DEBUG) {
    Write-Host "dbg window=${fullW}x${fullH} frame=$frame padded=$padded caption=$caption border=$border"
}

$full = New-Object System.Drawing.Bitmap($fullW, $fullH)
$g = [System.Drawing.Graphics]::FromImage($full)
$g.CopyFromScreen($rect.L, $rect.T, 0, 0, (New-Object System.Drawing.Size($fullW, $fullH)))
$g.Dispose()
$client = $full.Clone(
    (New-Object System.Drawing.Rectangle($cropX, $cropY, $cropW, $cropH)),
    $full.PixelFormat
)
$client.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$client.Dispose(); $full.Dispose()

# 放回普通层级，避免窗口一直压在最上面
[WinCap]::SetWindowPos($hwnd, [IntPtr](-2), 0, 0, 0, 0, 0x0001 -bor 0x0002) | Out-Null
Write-Host "saved $Out ($cropW x $cropH) class=$([WinCap]::bestInfo)"
