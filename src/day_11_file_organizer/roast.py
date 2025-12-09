"""毒舌吐槽產生器"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import FileStats


class RoastGenerator:
    """檔案吐槽產生器 - 毒舌版"""

    # 檔名關鍵字吐槽
    FILENAME_ROASTS = {
        "備份": [
            "備份狂魔！你是不是覺得硬碟空間不要錢？",
            "備份這麼多份，原檔在哪你還記得嗎？",
            "備份強迫症確診，建議就醫",
            "備份的備份的備份...你在拍乘法表嗎？",
        ],
        "最終": [
            "又一個『最終版』，我看這輩子都最終不了",
            "最終版就像減肥計畫，永遠有下一個最終版",
            "『最終版』三個字是這世界上最大的謊言",
        ],
        "最終版": [
            "敢叫最終版？那後面的 v2、v3 是什麼？幽靈嗎？",
            "最終版永遠不是最終的，跟你的前任一樣",
        ],
        "final": [
            "final_final_真的final_這次真的final_拜託是final.docx",
            "final 是一種信仰，不是事實",
            "The final countdown... 然後還有 final_v2",
        ],
        "副本": [
            "副本套副本，你以為這是《乘法表》？",
            "副本數量比你的存款還多，可喜可賀",
        ],
        "copy": [
            "Ctrl+C 狂魔現身！鍵盤都要被你按壞了",
            "Copy paste 工程師的典範",
        ],
        "新增": [
            "新增了什麼？新增了更多困惑和混亂",
        ],
        "修改": [
            "修改到連你媽都認不出來了吧",
            "修改無數次，結果跟原版一樣爛",
        ],
        "test": [
            "測試檔案活到現在...這測試是要測到地老天荒？",
            "test 檔案比你的工作態度還持久",
        ],
        "temp": [
            "『暫時』的東西活得比你的新年目標還久",
            "temp 檔案：我只是暫時的（活了 5 年）",
        ],
        "untitled": [
            "連名字都懶得取，這檔案是路邊撿的嗎？",
            "Untitled：我沒有名字，但我有故事（才怪）",
        ],
        "未命名": [
            "未命名就是未來會忘記這是什麼的意思",
            "連名字都不配擁有的檔案",
        ],
        "node_modules": [
            "打包 node_modules？這是什麼邪教儀式？",
            "node_modules 打包？你是想毀滅世界嗎？",
        ],
        "新建": [
            "新建文件夾.zip 裡面是新建文件夾嗎？俄羅斯套娃？",
        ],
        "desktop": [
            "桌面檔案備份...你的桌面是有多亂？",
        ],
    }

    # 檔案年齡吐槽（依年份）
    AGE_ROASTS = {
        10: [
            "這檔案都可以小學畢業了，你還留著幹嘛？",
            "考古學家來電！這化石級檔案該進博物館了",
            "十年了，這檔案比很多婚姻還持久",
            "這檔案見證了三任總統、五支 iPhone",
        ],
        7: [
            "七年之癢都過了，該放手了吧？",
            "這檔案比你的上一段感情還長壽",
        ],
        5: [
            "這檔案都可以上幼稒園了，還不送走？",
            "五年了，連 Windows 都換了兩版",
        ],
        3: [
            "三年了，疫情都結束了，這檔案還在",
        ],
    }

    # 檔案大小吐槽（依 MB）
    SIZE_ROASTS = {
        500: [
            "半個 G！你是把整個專案打包進去了？",
            "這檔案比有些人的硬碟還大",
            "500MB 以上應該要收停車費",
        ],
        100: [
            "這麼肥是要撐爆硬碟嗎？數位減肥了解一下",
            "100MB 以上的檔案都該被審判",
            "你的 SSD 正在哭泣，聽到了嗎？",
        ],
        50: [
            "肥成這樣，建議送去數位健身房",
            "50MB 的檔案，每一 MB 都是浪費",
        ],
        20: [
            "不算小了，比我的夢想還要肥",
        ],
    }

    # 類型特定吐槽
    TYPE_ROASTS = {
        "ppt": [
            "PPT 戰士！會議的噩夢製造機",
            "簡報一時爽，做簡報火葬場",
            "PPT 工程師，用動畫解決一切問題",
        ],
        "doc": [
            "Word 文件：排版永遠神秘歪掉的存在",
            "doc 檔案，開啟的人都會嘆氣",
        ],
        "xls": [
            "Excel 大師！公式套公式，出錯找到死",
            "試算表：讓簡單的事變複雜的藝術",
        ],
        "pdf": [
            "PDF：印出來比螢幕上好看的唯一格式",
        ],
        "zip": [
            "壓縮檔：不知道裡面是什麼的神秘盒子",
            "zip 檔案，打開可能有驚喜（或驚嚇）",
        ],
        "rar": [
            "RAR 檔？什麼年代了還在用 RAR？",
        ],
        "exe": [
            "exe 檔留這麼久，是在收藏病毒嗎？",
        ],
        "dmg": [
            "安裝檔留著幹嘛？你以為會用第二次？",
        ],
    }

    # 預設吐槽（沒有命中任何條件時）
    DEFAULT_ROASTS = [
        "這檔案目前逃過一劫，但我正在盯著它",
        "暫時沒什麼好說的，但不代表它沒問題",
        "看起來人畜無害，但誰知道呢",
        "普通的檔案，普通的浪費空間",
    ]

    def generate_roast(self, file: "FileStats") -> str:
        """
        為檔案產生吐槽語句

        優先順序：
        1. 檔名關鍵字
        2. 檔案年齡
        3. 檔案大小
        4. 檔案類型
        5. 預設吐槽
        """
        candidates: list[str] = []
        filename_lower = file.filename.lower()

        # 檢查檔名關鍵字（可累積多個）
        for keyword, messages in self.FILENAME_ROASTS.items():
            if keyword.lower() in filename_lower:
                candidates.extend(messages)

        # 檢查年齡（只取最嚴重的一級）
        age = file.age_years
        for min_age in sorted(self.AGE_ROASTS.keys(), reverse=True):
            if age >= min_age:
                candidates.extend(self.AGE_ROASTS[min_age])
                break

        # 檢查大小（只取最嚴重的一級）
        size_mb = file.size_mb
        for min_size in sorted(self.SIZE_ROASTS.keys(), reverse=True):
            if size_mb >= min_size:
                candidates.extend(self.SIZE_ROASTS[min_size])
                break

        # 檢查類型
        if file.file_type.lower() in self.TYPE_ROASTS:
            candidates.extend(self.TYPE_ROASTS[file.file_type.lower()])

        # 隨機選擇一個吐槽
        if candidates:
            return random.choice(candidates)

        # 沒有命中任何條件，使用預設吐槽
        return random.choice(self.DEFAULT_ROASTS)
