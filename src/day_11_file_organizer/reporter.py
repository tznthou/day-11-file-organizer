"""報告輸出器 - 使用 Rich 美化終端機輸出"""

from datetime import datetime

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import ClassifyResult
from .roast import RoastGenerator


class ReportPrinter:
    """使用 Rich 輸出美化報告"""

    def __init__(self) -> None:
        self.console = Console()
        self.roaster = RoastGenerator()

    def print_report(self, result: ClassifyResult) -> None:
        """輸出完整報告"""
        self.console.print()
        self._print_header()
        self.console.print()
        self._print_summary(result)
        self.console.print()

        if result.success_count > 0:
            self._print_year_chart(result)
            self.console.print()
            self._print_type_distribution(result)
            self.console.print()
            self._print_shame_board(result)
            self.console.print()

        if result.failed_count > 0:
            self._print_errors(result)
            self.console.print()

        self._print_footer()

    def _print_header(self) -> None:
        """輸出標題"""
        title = Text()
        title.append("檔案整理大師", style="bold magenta")
        title.append(" - ", style="dim")
        title.append("統計報告", style="bold cyan")

        self.console.print(
            Panel(
                title,
                border_style="bright_blue",
                padding=(0, 2),
            )
        )

    def _print_summary(self, result: ClassifyResult) -> None:
        """輸出摘要面板"""
        # 計算總大小的人類可讀格式
        total_bytes = result.total_size_bytes
        if total_bytes >= 1024 * 1024 * 1024:
            size_str = f"{total_bytes / (1024 * 1024 * 1024):.2f} GB"
        elif total_bytes >= 1024 * 1024:
            size_str = f"{total_bytes / (1024 * 1024):.2f} MB"
        elif total_bytes >= 1024:
            size_str = f"{total_bytes / 1024:.2f} KB"
        else:
            size_str = f"{total_bytes} B"

        # 建立摘要內容
        lines = [
            f"[bold green]成功[/]: {result.success_count} 個檔案",
            f"[bold red]失敗[/]: {result.failed_count} 個檔案",
            f"[bold blue]總計[/]: {result.total_count} 個檔案",
            "",
            f"[bold yellow]處理大小[/]: {size_str}",
        ]

        self.console.print(
            Panel(
                "\n".join(lines),
                title="[bold]摘要[/]",
                border_style="blue",
                padding=(1, 2),
            )
        )

    def _print_year_chart(self, result: ClassifyResult) -> None:
        """輸出年份分佈 ASCII 長條圖"""
        dist = result.year_distribution
        if not dist:
            return

        max_count = max(dist.values())
        max_bar_width = 30
        current_year = datetime.now().year

        self.console.print("[bold]年份分佈[/]")
        self.console.print()

        for year, count in dist.items():
            bar_width = int((count / max_count) * max_bar_width) if max_count > 0 else 0
            bar = "\u2588" * bar_width
            percentage = (count / result.success_count) * 100 if result.success_count > 0 else 0

            # 依年份遠近上色
            age = current_year - year
            if age >= 10:
                color = "red"
            elif age >= 5:
                color = "yellow"
            elif age >= 3:
                color = "bright_yellow"
            else:
                color = "green"

            self.console.print(f"  {year} [{color}]{bar}[/] {count} ({percentage:.1f}%)")

    def _print_type_distribution(self, result: ClassifyResult) -> None:
        """輸出類型分佈表格"""
        dist = result.type_distribution
        if not dist:
            return

        table = Table(
            title="檔案類型分佈",
            box=box.ROUNDED,
            header_style="bold magenta",
        )
        table.add_column("類型", style="cyan", justify="center")
        table.add_column("數量", style="green", justify="right")
        table.add_column("佔比", style="yellow", justify="right")

        total = sum(dist.values())
        for file_type, count in dist.items():
            percentage = (count / total) * 100 if total > 0 else 0
            table.add_row(file_type.upper(), str(count), f"{percentage:.1f}%")

        self.console.print(table)

    def _print_shame_board(self, result: ClassifyResult) -> None:
        """輸出大檔案羞辱榜"""
        top_files = result.top_large_files
        if not top_files:
            return

        table = Table(
            title="[bold red]大檔案羞辱榜 Top 5[/]",
            box=box.DOUBLE_EDGE,
            header_style="bold red",
            border_style="red",
            show_lines=True,
        )
        table.add_column("排名", style="bold", justify="center", width=6)
        table.add_column("檔名", style="cyan", max_width=35, overflow="ellipsis")
        table.add_column("大小", style="yellow", justify="right", width=10)
        table.add_column("年份", style="magenta", justify="center", width=6)
        table.add_column("吐槽", style="red", max_width=45, overflow="fold")

        medals = ["\U0001f947", "\U0001f948", "\U0001f949", "4", "5"]

        for i, f in enumerate(top_files):
            roast = self.roaster.generate_roast(f)
            table.add_row(
                medals[i],
                f.filename,
                f.size_display,
                str(f.year),
                roast,
            )

        self.console.print(table)

    def _print_errors(self, result: ClassifyResult) -> None:
        """輸出錯誤列表"""
        failed = result.failed_files
        if not failed:
            return

        table = Table(
            title="[bold red]處理失敗的檔案[/]",
            box=box.SIMPLE,
            header_style="bold red",
        )
        table.add_column("檔案", style="cyan", max_width=50, overflow="ellipsis")
        table.add_column("錯誤訊息", style="red", max_width=40)

        for f in failed[:10]:  # 最多顯示 10 個
            table.add_row(f.filename, f.error_message)

        if len(failed) > 10:
            self.console.print(f"[dim]...還有 {len(failed) - 10} 個錯誤，請查看 error.txt[/]")

        self.console.print(table)

    def _print_footer(self) -> None:
        """輸出頁尾"""
        footer = Text()
        footer.append("整理完成！", style="bold green")
        footer.append(" 詳細錯誤請查看目標資料夾中的 ", style="dim")
        footer.append("error.txt", style="bold yellow")

        self.console.print(Panel(footer, border_style="dim", padding=(0, 2)))
