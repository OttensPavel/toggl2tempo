from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHeaderView, QSizePolicy
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from j2toggl_core.worklog import WorkLog
from j2toggl_core.worklog_state import WorkLogState

WorkLogCollection = List[WorkLog]


class WorkLogsTableWidget(QWidget):
    def __init__(self, worklogs: WorkLogCollection = None):
        super().__init__()
        self._init_ui()

        if worklogs is not None:
            self._init_data(worklogs)

    def _init_ui(self):
        self._init_widgets()
        self._init_layouts()

    def _init_widgets(self):
        columns = ["Key", "Activity", "Description", "Date", "Time"]

        self.table = QTableWidget()

        self.table.setColumnCount(columns.__len__())
        self.table.setHorizontalHeaderLabels(columns)

        # Set columns size policy
        self.table.horizontalHeader().setSectionResizeMode(columns.index("Key"), QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(columns.index("Activity"), QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(columns.index("Description"), QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(columns.index("Date"), QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(columns.index("Time"), QHeaderView.ResizeToContents)

    def _init_layouts(self):
        mainVBox = QVBoxLayout()
        mainVBox.addWidget(self.table)

        self.setLayout(mainVBox)

    def init_data(self, worklogs: WorkLogCollection):
        self.table.setRowCount(0)

        for wl in worklogs:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # TODO: display datetimes without TZ
            row_content = [
                wl.key,
                wl.activity,
                wl.description,
                wl.startTime.strftime("%Y-%m-%d"),
                "{0} - {1}".format(wl.startTime.strftime("%H:%M"), wl.endTime.strftime("%H:%M"))]

            row_color = None
            if wl.state == WorkLogState.Incomplete:
                row_color = Qt.red
            elif wl.state == WorkLogState.New:
                row_color = Qt.darkGreen
            elif wl.state == WorkLogState.Updated or wl.state == WorkLogState.Moved:
                row_color = Qt.darkYellow

            column_position = 0
            for cellData in row_content:
                tooltip_text = wl.tooltip if column_position == 0 else None
                self._fill_cell(row_position, column_position, cellData, tooltip_text, row_color)
                column_position += 1

    def _fill_cell(self, row_position: int, column_position: int, text: str,
                   tooltip_text: str = None, text_color: QColor=None):
        item = QTableWidgetItem()
        item.setText(text)
        item.setData(Qt.ToolTipRole, tooltip_text)

        text_color = item.foreground() if text_color is None else text_color
        item.setForeground(text_color)

        self.table.setItem(row_position, column_position, item)
