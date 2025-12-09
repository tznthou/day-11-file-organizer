"""資料模型定義"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class FileStats:
    """單一檔案的統計資訊"""

    original_path: str
    filename: str
    size_bytes: int
    modified_time: datetime
    year: int
    file_type: str
    success: bool
    error_message: str = ""

    @property
    def size_mb(self) -> float:
        """檔案大小（MB）"""
        return self.size_bytes / (1024 * 1024)

    @property
    def size_display(self) -> str:
        """人類可讀的檔案大小"""
        if self.size_bytes >= 1024 * 1024 * 1024:
            return f"{self.size_bytes / (1024 * 1024 * 1024):.1f} GB"
        elif self.size_bytes >= 1024 * 1024:
            return f"{self.size_mb:.1f} MB"
        elif self.size_bytes >= 1024:
            return f"{self.size_bytes / 1024:.1f} KB"
        else:
            return f"{self.size_bytes} B"

    @property
    def age_years(self) -> int:
        """檔案年齡（年）"""
        return datetime.now().year - self.year


@dataclass
class ClassifyResult:
    """分類結果彙總"""

    files: List[FileStats] = field(default_factory=list)
    source_folder: str = ""
    target_folder: str = ""

    @property
    def total_count(self) -> int:
        """總檔案數"""
        return len(self.files)

    @property
    def success_count(self) -> int:
        """成功移動的檔案數"""
        return sum(1 for f in self.files if f.success)

    @property
    def failed_count(self) -> int:
        """失敗的檔案數"""
        return sum(1 for f in self.files if not f.success)

    @property
    def total_size_bytes(self) -> int:
        """成功移動的總大小"""
        return sum(f.size_bytes for f in self.files if f.success)

    @property
    def year_distribution(self) -> Dict[int, int]:
        """年份分佈（只計算成功的）"""
        dist: Dict[int, int] = {}
        for f in self.files:
            if f.success:
                dist[f.year] = dist.get(f.year, 0) + 1
        return dict(sorted(dist.items()))

    @property
    def type_distribution(self) -> Dict[str, int]:
        """類型分佈（只計算成功的，按數量排序）"""
        dist: Dict[str, int] = {}
        for f in self.files:
            if f.success:
                dist[f.file_type] = dist.get(f.file_type, 0) + 1
        return dict(sorted(dist.items(), key=lambda x: -x[1]))

    @property
    def top_large_files(self) -> List[FileStats]:
        """前 5 大檔案"""
        successful = [f for f in self.files if f.success]
        return sorted(successful, key=lambda x: -x.size_bytes)[:5]

    @property
    def failed_files(self) -> List[FileStats]:
        """失敗的檔案列表"""
        return [f for f in self.files if not f.success]
