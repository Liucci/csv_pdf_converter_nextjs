from reportlab.platypus import Flowable, Spacer

class TableHorizontal(Flowable):
    def __init__(self, table1, table2, space=20):
        super().__init__()
        self.table1 = table1
        self.table2 = table2
        self.space = space
        self._width1, self._height1 = self.table1.wrap(0, 0)
        self._width2, self._height2 = self.table2.wrap(0, 0)

    def wrap(self, availWidth, availHeight):
        total_width = self._width1 + self.space + self._width2
        max_height = max(self._height1, self._height2)
        return total_width, max_height

    def draw(self):
        self.canv.saveState()
        # 高さの最大値からのオフセットで上詰めに描画
        max_height = max(self._height1, self._height2)
        self.table1.drawOn(self.canv, 0, max_height - self._height1)
        self.table2.drawOn(self.canv, self._width1 + self.space, max_height - self._height2)
        self.canv.restoreState()
        
    def split(self, availWidth, availHeight):
        # ページ縦幅を超えているかチェック
        total_height = max(self._height1, self._height2)
        if total_height <= availHeight:
            # ページ内に収まるなら分割不要
            return [self]

        # table1 と table2 を縦方向に分割 (split()があれば呼ぶ)
        split1 = self.table1.split(availWidth, availHeight) if hasattr(self.table1, 'split') else [self.table1]
        split2 = self.table2.split(availWidth, availHeight) if hasattr(self.table2, 'split') else [self.table2]

        max_pages = max(len(split1), len(split2))
        flowables = []

        for i in range(max_pages):
            t1 = split1[i] if i < len(split1) else Spacer(self._width1, 0)
            t2 = split2[i] if i < len(split2) else Spacer(self._width2, 0)

            flowables.append(TableHorizontal(t1, t2, space=self.space))

        return flowables
