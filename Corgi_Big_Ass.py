# coding: utf-8
"""
Author: CreateNULL
Date: 2024-10-01
Description: This script processes and filters results from Dirsearch 、Feroxbuster、fscan.

"""

import sys
import re
from urllib.parse import urljoin
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget,
    QTextEdit, QMessageBox, QComboBox, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView
)

from filter.dirsearch import filter as dirsearch_filter # dirsearch 处理
from filter.feroxbuster import filter_response_data  # 导入 Feroxbuster 的过滤函数
from filter.fscan import process_fscan_data     # fscan 处理


class FilterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("扫描结果处理 GUI, By CreateNULL")
        self.setGeometry(100, 100, 800, 600)

        # 设置样式
        # 设置样式
        self.setStyleSheet(""" 
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 12px;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 4px;
                border: none;
            }
        """)

        self.main_layout = QVBoxLayout()

        # 添加页面切换按钮
        self.switch_button_layout = QHBoxLayout()
        self.dirsearch_button = QPushButton("Dirsearch")
        self.feroxbuster_button = QPushButton("Feroxbuster")
        self.fscan_button = QPushButton("Fscan")

        self.dirsearch_button.clicked.connect(self.show_dirsearch_page)
        self.feroxbuster_button.clicked.connect(self.show_feroxbuster_page)
        self.fscan_button.clicked.connect(self.show_fscan_page)

        self.switch_button_layout.addWidget(self.dirsearch_button)
        self.switch_button_layout.addWidget(self.feroxbuster_button)
        self.switch_button_layout.addWidget(self.fscan_button)

        # 添加 QStackedWidget 用于不同页面
        self.central_widget = QStackedWidget()

        # Dirsearch 页面
        self.dirsearch_page = QWidget()
        self.setup_dirsearch_page()
        self.central_widget.addWidget(self.dirsearch_page)

        # Feroxbuster 页面
        self.feroxbuster_page = QWidget()
        self.setup_feroxbuster_page()
        self.central_widget.addWidget(self.feroxbuster_page)

        # Fscan 页面
        self.fscan_page = QWidget()
        self.setup_fscan_page()  # 确保在创建 Fscan 页面时调用
        self.central_widget.addWidget(self.fscan_page)

        # 将按钮布局和 QStackedWidget 添加到主布局
        self.main_layout.addLayout(self.switch_button_layout)
        self.main_layout.addWidget(self.central_widget)

        main_widget = QWidget()
        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

    def setup_fscan_page(self):
        layout = QVBoxLayout(self.fscan_page)

        # 输入数据框
        self.data_input_label_fscan = QLabel("输入Fscan结果:")
        self.data_input_fscan = QTextEdit()
        layout.addWidget(self.data_input_label_fscan)
        layout.addWidget(self.data_input_fscan)

        # 处理按钮
        self.process_button_fscan = QPushButton("处理Fscan结果")
        self.process_button_fscan.clicked.connect(self.filter_results_fscan)
        layout.addWidget(self.process_button_fscan)

        # 使用 QTabWidget 作为输出区域
        self.tab_widget_fscan = QTabWidget()
        layout.addWidget(self.tab_widget_fscan)

    def show_dirsearch_page(self):
        self.central_widget.setCurrentIndex(0)

    def show_feroxbuster_page(self):
        self.central_widget.setCurrentIndex(1)

    def show_fscan_page(self):
        self.central_widget.setCurrentIndex(2)

    def setup_dirsearch_page(self):
        layout = QVBoxLayout(self.dirsearch_page)

        # 输入数据框
        self.data_input_label = QLabel("输入待过滤的数据:")
        self.data_input = QTextEdit()
        layout.addWidget(self.data_input_label)
        layout.addWidget(self.data_input)

        # 状态码输入
        self.dirsearch_status_code_label = QLabel("状态码 (用逗号分隔):")
        self.dirsearch_status_code_input = QLineEdit()
        layout.addWidget(self.dirsearch_status_code_label)
        layout.addWidget(self.dirsearch_status_code_input)

        # 响应大小输入
        size_layout = QHBoxLayout()
        self.dirsearch_min_size_label = QLabel("响应最小大小:")
        self.dirsearch_min_size_input = QLineEdit()
        self.dirsearch_max_size_label = QLabel("响应最大大小:")
        self.dirsearch_max_size_input = QLineEdit()
        self.size_unit_input = QComboBox()
        self.size_unit_input.addItems(["B", "KB", "MB", "GB"])  # 添加大小单位选项
        size_layout.addWidget(self.dirsearch_min_size_label)
        size_layout.addWidget(self.dirsearch_min_size_input)
        size_layout.addWidget(QLabel("到"))
        size_layout.addWidget(self.dirsearch_max_size_label)
        size_layout.addWidget(self.dirsearch_max_size_input)
        size_layout.addWidget(self.size_unit_input)  # 添加单位选择框
        layout.addLayout(size_layout)

        # 过滤路径输入
        self.dirsearch_filter_path_label = QLabel("正则提取路径:")
        self.dirsearch_filter_path_input = QLineEdit()
        layout.addWidget(self.dirsearch_filter_path_label)
        layout.addWidget(self.dirsearch_filter_path_input)

        # 过滤按钮
        self.filter_button = QPushButton("过滤")
        self.filter_button.clicked.connect(self.filter_results_dirsearch)
        layout.addWidget(self.filter_button)

        # 表格输出
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(["时间", "状态码", "响应大小", "路径", "跳转路径", "完整路径"])
        layout.addWidget(self.result_table)

    def setup_feroxbuster_page(self):
        layout = QVBoxLayout(self.feroxbuster_page)

        # 输入数据框
        self.data_input_label_ferox = QLabel("输入待过滤的数据:")
        self.data_input_ferox = QTextEdit()
        layout.addWidget(self.data_input_label_ferox)
        layout.addWidget(self.data_input_ferox)

        # 状态码、请求方法和过滤路径输入放在一行
        filter_layout = QHBoxLayout()
        self.status_code_label_ferox = QLabel("状态码 (用逗号分隔):")
        self.status_code_input_ferox = QLineEdit()
        filter_layout.addWidget(self.status_code_label_ferox)
        filter_layout.addWidget(self.status_code_input_ferox)

        self.method_label_ferox = QLabel("请求方法 (用逗号分隔):")
        self.method_input_ferox = QLineEdit()
        filter_layout.addWidget(self.method_label_ferox)
        filter_layout.addWidget(self.method_input_ferox)

        self.feroxbuster_filter_path_label = QLabel("正则提取路径:")
        self.feroxbuster_filter_path_input = QLineEdit()
        filter_layout.addWidget(self.feroxbuster_filter_path_label)
        filter_layout.addWidget(self.feroxbuster_filter_path_input)

        layout.addLayout(filter_layout)

        # 行数、字数、字节数输入放在一行
        count_layout = QHBoxLayout()

        # 行数范围
        self.line_count_min_label_ferox = QLabel("响应数据的行数:")
        self.line_count_min_input_ferox = QLineEdit()
        self.line_count_max_input_ferox = QLineEdit()
        count_layout.addWidget(self.line_count_min_label_ferox)
        count_layout.addWidget(self.line_count_min_input_ferox)
        count_layout.addWidget(QLabel("-"))
        count_layout.addWidget(self.line_count_max_input_ferox)

        # 字数范围
        self.word_count_min_label_ferox = QLabel("响应数据中的字数:")
        self.word_count_min_input_ferox = QLineEdit()
        self.word_count_max_input_ferox = QLineEdit()
        count_layout.addWidget(self.word_count_min_label_ferox)
        count_layout.addWidget(self.word_count_min_input_ferox)
        count_layout.addWidget(QLabel("-"))
        count_layout.addWidget(self.word_count_max_input_ferox)

        # 字节数范围
        self.byte_count_min_label_ferox = QLabel("响应数据中的字节书:")
        self.byte_count_min_input_ferox = QLineEdit()
        self.byte_count_max_input_ferox = QLineEdit()
        count_layout.addWidget(self.byte_count_min_label_ferox)
        count_layout.addWidget(self.byte_count_min_input_ferox)
        count_layout.addWidget(QLabel("到"))
        count_layout.addWidget(self.byte_count_max_input_ferox)

        layout.addLayout(count_layout)

        # 过滤按钮
        self.filter_button_ferox = QPushButton("过滤")
        self.filter_button_ferox.clicked.connect(self.filter_results_feroxbuster)
        layout.addWidget(self.filter_button_ferox)

        # 表格输出
        self.result_table_ferox = QTableWidget()
        self.result_table_ferox.setColumnCount(7)
        self.result_table_ferox.setHorizontalHeaderLabels(["状态码", "响应大小", "路径", "跳转路径", "行数", "字数", "请求方法"])
        layout.addWidget(self.result_table_ferox)

    def setup_fscan_page(self):
        #
        layout = QVBoxLayout(self.fscan_page)

        # 输入数据框
        self.data_input_label_fscan = QLabel("输入Fscan结果:")
        self.data_input_fscan = QTextEdit()
        self.data_input_fscan.setPlaceholderText("在此输入Fscan结果\n数据处理逻辑, 参考于 ZororoZ师傅的 https://github.com/ZororoZ/fscanOutput 😀")
        layout.addWidget(self.data_input_label_fscan)
        layout.addWidget(self.data_input_fscan)

        # 处理按钮
        self.process_button_fscan = QPushButton("处理Fscan结果")
        self.process_button_fscan.clicked.connect(self.filter_results_fscan)
        layout.addWidget(self.process_button_fscan)

        # 使用 QTabWidget 作为输出区域
        self.tab_widget_fscan = QTabWidget()
        layout.addWidget(self.tab_widget_fscan)

    def filter_results_dirsearch(self):
        output_str = self.data_input.toPlainText()
        status_codes = [sc.strip() for sc in self.dirsearch_status_code_input.text().split(',') if sc.strip()]
        min_size = self.dirsearch_min_size_input.text()
        max_size = self.dirsearch_max_size_input.text()
        size_unit = self.size_unit_input.currentText()
        filter_path = self.dirsearch_filter_path_input.text()

        try:
            min_size = float(min_size) if min_size else None
            max_size = float(max_size) if max_size else None

            if (min_size is not None and min_size < 0) or (max_size is not None and max_size < 0):
                raise ValueError("最小和最大大小必须为非负数。")

        except ValueError:
            QMessageBox.critical(self, "错误", "最小和最大大小必须为数字。")
            return

        target_url = ""
        for line in output_str.splitlines():
            if "Target:" in line:
                match = re.search(r'Target:\s+(http[^\s]+)', line)
                if match:
                    target_url = match.group(1)
                    break

            if 'dirsearch' in line or 'DIRSEARCH' in line:
                match = re.search(r'dirsearch\.?p?y?[ ]+-u\s+(http[^\s]+)', line)
                if match:
                    target_url = match.group(1)
                    break

        try:
            filtered_results = dirsearch_filter(output_str, status_codes, (min_size, max_size, size_unit), filter_path)

            self.result_table.setRowCount(0)

            for result in filtered_results:
                time = result[0]
                status_code = result[1]
                size = result[2]
                unit = result[3]
                path = result[4]
                redirect_path = result[5] if len(result) > 4 else '无'

                # 直接使用原始路径而不改变单位
                complete_path = urljoin(target_url, path)

                row_position = self.result_table.rowCount()
                self.result_table.insertRow(row_position)
                self.result_table.setItem(row_position, 0, QTableWidgetItem(time))
                self.result_table.setItem(row_position, 1, QTableWidgetItem(status_code))
                self.result_table.setItem(row_position, 2, QTableWidgetItem(f"{size} {unit}"))
                self.result_table.setItem(row_position, 3, QTableWidgetItem(path))  # 保持原始路径
                self.result_table.setItem(row_position, 4, QTableWidgetItem(redirect_path))
                self.result_table.setItem(row_position, 5, QTableWidgetItem(complete_path))

            if self.result_table.rowCount() == 0:
                QMessageBox.information(self, "结果", "没有符合条件的结果。")
            self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def filter_results_feroxbuster(self):
        output_str = self.data_input_ferox.toPlainText()
        status_codes = [sc.strip() for sc in self.status_code_input_ferox.text().split(',') if sc.strip()]
        methods = [m.strip().upper() for m in self.method_input_ferox.text().split(',') if m.strip()]

        # 行数范围
        line_count_min = self.line_count_min_input_ferox.text()
        line_count_max = self.line_count_max_input_ferox.text()
        line_count = (int(line_count_min) if line_count_min else None,
                      int(line_count_max) if line_count_max else None)

        # 字数范围
        word_count_min = self.word_count_min_input_ferox.text()
        word_count_max = self.word_count_max_input_ferox.text()
        word_count = (int(word_count_min) if word_count_min else None,
                      int(word_count_max) if word_count_max else None)

        # 字节数范围
        byte_count_min = self.byte_count_min_input_ferox.text()
        byte_count_max = self.byte_count_max_input_ferox.text()
        byte_count = (int(byte_count_min) if byte_count_min else None,
                      int(byte_count_max) if byte_count_max else None)

        # 路径过滤
        path_regex = self.feroxbuster_filter_path_input.text().strip() or None

        try:
            filtered_results = filter_response_data(
                output_str,
                methods=methods,
                line_count=line_count,
                word_count=word_count,
                byte_count=byte_count,
                path_regex=path_regex,  # 添加路径过滤
                status_codes=status_codes
            )

            self.result_table_ferox.setRowCount(0)


            for result in filtered_results:
                status_code = result['status_code']
                size = result['bytes']  # 使用字节数
                path = result['url']
                redirect_path = result.get('redirect_url', '无')  # 默认值为 '无'
                lines = result['lines']  # 行数
                words = result['words']   # 字数
                method = result.get('method', '无')  # 请求方法

                # 格式化行数和字数
                formatted_lines = f"{lines}l"
                formatted_words = f"{words}w"

                # 添加到表格中
                row_position = self.result_table_ferox.rowCount()
                self.result_table_ferox.insertRow(row_position)
                self.result_table_ferox.setItem(row_position, 0, QTableWidgetItem(status_code))
                self.result_table_ferox.setItem(row_position, 1, QTableWidgetItem(str(size)))  # 转为字符串
                self.result_table_ferox.setItem(row_position, 2, QTableWidgetItem(path))
                self.result_table_ferox.setItem(row_position, 3, QTableWidgetItem(redirect_path))
                self.result_table_ferox.setItem(row_position, 4, QTableWidgetItem(formatted_lines))  # 行数
                self.result_table_ferox.setItem(row_position, 5, QTableWidgetItem(formatted_words))   # 字数
                self.result_table_ferox.setItem(row_position, 6, QTableWidgetItem(method))  # 请求方法

            if self.result_table_ferox.rowCount() == 0:
                QMessageBox.information(self, "结果", "没有符合条件的结果。")

            self.result_table_ferox.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def filter_results_fscan(self):
        output_str = self.data_input_fscan.toPlainText()

        try:
            # 调用处理函数并获取结果
            processed_results = process_fscan_data(output_str)

            # 清空之前的 tab_widget 内容
            self.tab_widget_fscan.clear()

            # 遍历每个结果，按类型添加到标签页
            for sheet_name, data in processed_results.items():
                if data:  # 确保数据不为空
                    table_widget = QTableWidget()
                    table_widget.setRowCount(len(data) - 1)  # 数据行数减去表头
                    table_widget.setColumnCount(len(data[0]))

                    for row in range(1, len(data)):  # 从1开始跳过表头
                        for col in range(len(data[row])):
                            table_widget.setItem(row - 1, col, QTableWidgetItem(str(data[row][col])))

                    table_widget.setHorizontalHeaderLabels(data[0])  # 设置表头为数据的第一行

                    # 设置列宽自适应
                    table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
                    table_widget.resizeRowsToContents()

                    # 添加到标签页
                    self.tab_widget_fscan.addTab(table_widget, sheet_name)

                    # 设置输出表格的高度与输入框相似
                    table_widget.setMinimumHeight(self.data_input_fscan.height() * 0.75)

            if self.tab_widget_fscan.count() == 0:
                QMessageBox.information(self, "结果", "没有符合条件的结果。")

        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilterApp()
    window.show()
    sys.exit(app.exec())
