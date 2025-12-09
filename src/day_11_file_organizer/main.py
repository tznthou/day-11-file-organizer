"""檔案整理大師 - 主程式"""

import argparse
import os
import shutil
import sys
from datetime import datetime

from rich.console import Console
from rich.prompt import Prompt

from .models import ClassifyResult, FileStats
from .reporter import ReportPrinter

# 檢查 tkinter 是否可用
try:
    import tkinter as tk
    from tkinter import filedialog

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

# 檔案分類對應表
EXTENSION_MAPPING = {
    ".doc": "doc",
    ".docx": "doc",
    ".xls": "xls",
    ".xlsx": "xls",
    ".ppt": "ppt",
    ".pptx": "ppt",
    ".pdf": "pdf",
    ".txt": "txt",
    ".jpg": "jpg",
    ".jpeg": "jpg",
    ".png": "png",
    ".gif": "gif",
    ".mp3": "mp3",
    ".mp4": "mp4",
    ".mov": "mov",
    ".zip": "zip",
    ".rar": "rar",
    ".7z": "7z",
}


def get_folder_path_gui(prompt: str) -> str:
    """使用 tkinter 選擇資料夾"""
    if not TKINTER_AVAILABLE:
        return ""
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title=prompt)
    root.destroy()
    return folder_path


def get_folder_path_cli(prompt: str) -> str:
    """使用命令列輸入資料夾路徑"""
    path = Prompt.ask(f"[cyan]{prompt}[/]")
    # 展開 ~ 為家目錄
    path = os.path.expanduser(path)
    return path


def clean_empty_folders(folder: str, console: Console) -> int:
    """
    清理空資料夾（從最深層開始往上清理）

    Args:
        folder: 要清理的資料夾路徑
        console: Rich Console 物件

    Returns:
        int: 清理的空資料夾數量
    """
    cleaned_count = 0

    # 從最深層開始往上遍歷
    for root, dirs, files in os.walk(folder, topdown=False):
        # 跳過根目錄本身
        if root == folder:
            continue

        # 檢查是否為空資料夾（沒有檔案，也沒有子資料夾）
        try:
            if not os.listdir(root):
                os.rmdir(root)
                console.print(f"[dim]清理空資料夾: {root}[/]")
                cleaned_count += 1
        except OSError:
            # 無法刪除（可能有權限問題或其他原因）
            pass

    return cleaned_count


def classify_files_by_year_and_type(
    source_folder: str, target_folder: str
) -> ClassifyResult:
    """
    依照年份和類型分類檔案

    Args:
        source_folder: 來源資料夾路徑
        target_folder: 目標資料夾路徑

    Returns:
        ClassifyResult: 分類結果統計
    """
    result = ClassifyResult(source_folder=source_folder, target_folder=target_folder)
    console = Console()

    # 遍歷資料夾及其子資料夾
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            # 跳過隱藏檔案
            if file.startswith("."):
                continue

            file_path = os.path.join(root, file)

            try:
                # 獲取檔案資訊
                file_stat = os.stat(file_path)
                file_mtime = datetime.fromtimestamp(file_stat.st_mtime)
                file_year = file_mtime.year

                # 獲取檔案的副檔名
                file_extension = os.path.splitext(file)[1].lower()

                # 根據副檔名確定目標資料夾名稱
                if file_extension in EXTENSION_MAPPING:
                    folder_name = EXTENSION_MAPPING[file_extension]
                elif file_extension:
                    folder_name = file_extension[1:]  # 移除開頭的點
                else:
                    folder_name = "other"

                # 建立 FileStats
                stats = FileStats(
                    original_path=file_path,
                    filename=file,
                    size_bytes=file_stat.st_size,
                    modified_time=file_mtime,
                    year=file_year,
                    file_type=folder_name,
                    success=True,
                )

                # 定義目標資料夾路徑
                target_folder_by_year = os.path.join(target_folder, str(file_year))
                target_folder_by_type = os.path.join(target_folder_by_year, folder_name)

                # 創建目標資料夾（如果不存在）
                os.makedirs(target_folder_by_type, exist_ok=True)

                # 處理同名檔案
                target_file_path = os.path.join(target_folder_by_type, file)
                if os.path.exists(target_file_path):
                    # 加上時間戳避免覆蓋
                    name, ext = os.path.splitext(file)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_name = f"{name}_{timestamp}{ext}"
                    target_file_path = os.path.join(target_folder_by_type, new_name)

                # 移動檔案到目標資料夾
                shutil.move(file_path, target_file_path)
                console.print(f"[dim]移動: {file}[/]")

                result.files.append(stats)

            except PermissionError as e:
                stats = FileStats(
                    original_path=file_path,
                    filename=file,
                    size_bytes=0,
                    modified_time=datetime.now(),
                    year=0,
                    file_type="unknown",
                    success=False,
                    error_message=f"權限不足: {e}",
                )
                result.files.append(stats)
                console.print(f"[red]權限錯誤: {file}[/]")

            except FileNotFoundError as e:
                stats = FileStats(
                    original_path=file_path,
                    filename=file,
                    size_bytes=0,
                    modified_time=datetime.now(),
                    year=0,
                    file_type="unknown",
                    success=False,
                    error_message=f"檔案不存在: {e}",
                )
                result.files.append(stats)
                console.print(f"[red]找不到檔案: {file}[/]")

            except Exception as e:
                stats = FileStats(
                    original_path=file_path,
                    filename=file,
                    size_bytes=0,
                    modified_time=datetime.now(),
                    year=0,
                    file_type="unknown",
                    success=False,
                    error_message=str(e),
                )
                result.files.append(stats)
                console.print(f"[red]錯誤: {file} - {e}[/]")

    # 寫入錯誤記錄
    errors = result.failed_files
    if errors:
        error_file_path = os.path.join(target_folder, "error.txt")
        with open(error_file_path, "w", encoding="utf-8") as f:
            f.write(f"錯誤記錄 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            for err in errors:
                f.write(f"檔案: {err.original_path}\n")
                f.write(f"錯誤: {err.error_message}\n")
                f.write("-" * 30 + "\n")

    return result


def run() -> None:
    """主程式入口"""
    console = Console()

    # 解析命令列參數
    parser = argparse.ArgumentParser(
        description="檔案整理大師 - 依年份/類型分類檔案",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  file-organizer                           # 互動模式
  file-organizer --source ~/Downloads --target ~/Organized
  file-organizer -s ./messy -t ./clean
        """,
    )
    parser.add_argument(
        "-s", "--source", type=str, help="來源資料夾路徑"
    )
    parser.add_argument(
        "-t", "--target", type=str, help="目標資料夾路徑"
    )
    parser.add_argument(
        "--no-gui", action="store_true", help="強制使用 CLI 模式（不使用 GUI 選擇器）"
    )
    parser.add_argument(
        "--clean", action="store_true", help="處理完成後清理來源資料夾中的空資料夾"
    )

    args = parser.parse_args()

    console.print()
    console.print("[bold magenta]歡迎使用檔案整理大師！[/]")
    console.print()

    # 決定使用 GUI 還是 CLI
    use_gui = TKINTER_AVAILABLE and not args.no_gui

    # 獲取來源資料夾
    if args.source:
        source_folder = os.path.expanduser(args.source)
    elif use_gui:
        console.print("[dim]請選擇來源資料夾...[/]")
        source_folder = get_folder_path_gui("選擇來源資料夾（要整理的資料夾）")
    else:
        source_folder = get_folder_path_cli("輸入來源資料夾路徑")

    if not source_folder:
        console.print("[yellow]未指定來源資料夾，程式結束[/]")
        return

    if not os.path.isdir(source_folder):
        console.print(f"[bold red]錯誤：來源資料夾不存在: {source_folder}[/]")
        return

    console.print(f"[green]來源資料夾: {source_folder}[/]")

    # 獲取目標資料夾
    if args.target:
        target_folder = os.path.expanduser(args.target)
    elif use_gui:
        console.print("[dim]請選擇目標資料夾...[/]")
        target_folder = get_folder_path_gui("選擇目標資料夾（整理後存放的位置）")
    else:
        target_folder = get_folder_path_cli("輸入目標資料夾路徑")

    if not target_folder:
        console.print("[yellow]未指定目標資料夾，程式結束[/]")
        return

    # 自動建立目標資料夾
    if not os.path.exists(target_folder):
        os.makedirs(target_folder, exist_ok=True)
        console.print(f"[dim]已建立目標資料夾: {target_folder}[/]")

    console.print(f"[green]目標資料夾: {target_folder}[/]")
    console.print()

    # 確認來源和目標不同
    if os.path.abspath(source_folder) == os.path.abspath(target_folder):
        console.print("[bold red]錯誤：來源和目標資料夾不能相同！[/]")
        return

    # 執行檔案分類
    console.print("[bold cyan]開始整理檔案...[/]")
    console.print()

    result = classify_files_by_year_and_type(source_folder, target_folder)

    # 輸出報告
    printer = ReportPrinter()
    printer.print_report(result)

    # 清理空資料夾（如果指定 --clean）
    if args.clean:
        console.print()
        console.print("[bold yellow]清理空資料夾...[/]")
        cleaned = clean_empty_folders(source_folder, console)
        if cleaned > 0:
            console.print(f"[green]已清理 {cleaned} 個空資料夾[/]")
        else:
            console.print("[dim]沒有需要清理的空資料夾[/]")


if __name__ == "__main__":
    run()
