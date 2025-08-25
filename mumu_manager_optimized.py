import sys, os, subprocess, json, random, time, re, shlex
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QProgressBar,
    QStatusBar, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QMessageBox,
    QFileDialog, QCheckBox, QLabel, QDialogButtonBox, QTextEdit, QMenu,
    QComboBox, QSplitter, QSizePolicy, QFrame, QInputDialog,
    QStyledItemDelegate, QStyleOptionViewItem, QTabWidget, QGroupBox, QToolButton,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QSettings, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QColor, QTextCursor, QPalette, QAction, QPainter, QLinearGradient, QPen

# ---------- Shadow helper với cache ----------
class ShadowCache:
    """Cache for shadow effects to improve performance"""
    _shadow_cache = {}
    
    @staticmethod
    def get_shadow(radius=16, dx=6, dy=6, alpha=80):
        """Get a cached shadow effect or create a new one"""
        key = f"{radius}_{dx}_{dy}_{alpha}"
        if key not in ShadowCache._shadow_cache:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(radius)
            effect.setOffset(dx, dy)
            effect.setColor(QColor(0, 0, 0, alpha))
            ShadowCache._shadow_cache[key] = effect
        return ShadowCache._shadow_cache[key]

def apply_shadow(widget, radius=16, dx=6, dy=6, alpha=80):
    """Apply shadow with performance optimization for large datasets"""
    # Skip shadows entirely if there are too many widgets (10k+ instances)
    app = QApplication.instance()
    if app and hasattr(app, '_widget_count'):
        if app._widget_count > 1000:
            return  # Skip shadows for performance
    
    # Only apply shadow to visible widgets
    if not widget.isVisible():
        return
    
    # Skip very small widgets (less than 20x20)
    if widget.width() < 20 or widget.height() < 20:
        return
    
    # Use lighter shadows for dark theme to enhance visibility
    theme = QApplication.instance().property("currentTheme")
    if theme == "dark" and alpha > 50:
        alpha = min(alpha, 60)  # Reduce opacity for dark theme
    
    try:
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(radius)
        effect.setOffset(dx, dy)
        effect.setColor(QColor(0, 0, 0, alpha))
        widget.setGraphicsEffect(effect)
        
        # Track widget count for performance optimization
        if not hasattr(QApplication.instance(), '_widget_count'):
            QApplication.instance()._widget_count = 0
        QApplication.instance()._widget_count += 1
    except Exception:
        pass

# =========================
# Neumorphic Theme (light/dark) với CSS variables
# =========================

PRIMARY = "#6c4cff"     # tím chủ đạo (gần giống ảnh)
PRIMARY_DARK = "#5a3fe0"

class NeoPalette:
    @staticmethod
    def light():
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor("#eef0ff"))
        p.setColor(QPalette.ColorRole.Base, QColor("#f7f8ff"))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.Text, QColor("#1e1e2d"))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#1e1e2d"))
        p.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
        p.setColor(QPalette.ColorRole.ButtonText, QColor("#1e1e2d"))
        p.setColor(QPalette.ColorRole.Highlight, QColor(PRIMARY))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        return p

    @staticmethod
    def dark():
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor("#1b1d29"))
        p.setColor(QPalette.ColorRole.Base, QColor("#202335"))
        p.setColor(QPalette.ColorRole.AlternateBase, QColor("#242844"))
        p.setColor(QPalette.ColorRole.Text, QColor("#e8ecff"))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#e8ecff"))
        p.setColor(QPalette.ColorRole.Button, QColor("#222642"))
        p.setColor(QPalette.ColorRole.ButtonText, QColor("#e8ecff"))
        p.setColor(QPalette.ColorRole.Highlight, QColor("#8aa1ff"))
        p.setColor(QPalette.ColorRole.HighlightedText, QColor("#101321"))
        return p

def apply_neo_style(app: QApplication, mode: str):
    """Apply enhanced neumorphic styling with CSS variables for better consistency"""
    app.setStyle("Fusion")
    app.setProperty("currentTheme", mode)
    
    if mode == "dark":
        app.setPalette(NeoPalette.dark())
        app.setStyleSheet("""
            /* CSS Variables for color consistency */
            * {
                --bg-color: #1b1d29;
                --card-background: #1f233b;
                --border-color: #2a2e4a;
                --border-color-light: #252a45;
                --text-color: 232, 236, 255;
                --highlight: #8aa1ff;
                --highlight-soft: #39407a;
                --primary: #6c4cff;
                --primary-dark: #5a3fe0;
                --success: #16a34a;
                --danger: #dc2626;
                --warning: #eab308;
            }
            
            QWidget { font-family: "Segoe UI"; font-size: 10pt; }
            
            /* Enhanced Neumorphic containers */
            .neo-card {
                background: var(--card-background);
                border-radius: 16px;
                padding: 16px;
                border: 1px solid var(--border-color);
            }
            
            /* Improved sidebar */
            QFrame#sidebar {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 var(--primary), stop:1 var(--primary-dark));
                border-radius: 18px;
                margin: 12px;
            }
            
            QLabel#logo {
                color: white; 
                font-weight: 700; 
                font-size: 18px;
                letter-spacing: 1px;
            }
            
            QPushButton.sidebar {
                color: #e9eaff; 
                border: none; 
                border-radius: 12px; 
                padding: 12px 16px;
                text-align: left;
                font-weight: 500;
                font-size: 11pt;
            }
            
            QPushButton.sidebar:hover { 
                background: rgba(255,255,255,0.12); 
            }
            
            QPushButton.sidebar:checked { 
                background: rgba(255,255,255,0.25);
                font-weight: 600; 
            }
            
            /* Better form controls */
            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QComboBox {
                background: var(--card-background);
                border: 1px solid var(--border-color);
                border-radius: 10px;
                padding: 10px;
                color: rgba(var(--text-color), 1);
                selection-background-color: var(--highlight-soft);
            }
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid var(--highlight);
            }
            
            /* Improved buttons */
            QPushButton, QToolButton {
                background: var(--card-background);
                border: 1px solid var(--border-color);
                border-radius: 10px;
                padding: 10px 14px;
                color: rgba(var(--text-color), 1);
                min-height: 36px;
            }
            
            QPushButton:hover, QToolButton:hover {
                background: #262b49;
            }
            
            QPushButton:pressed, QToolButton:pressed {
                background: #303650;
            }
            
            QPushButton.primary {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 var(--primary), stop:1 var(--primary-dark));
                color: white;
                font-weight: 600;
                border: none;
            }
            
            QPushButton.primary:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #7d61ff, stop:1 #6b53e8);
            }
            
            /* Status badges */
            QLabel.badge {
                padding: 6px 12px;
                border-radius: 12px;
                color: white;
                font-weight: 600;
                font-size: 9pt;
            }
            
            QLabel.badge.running { background: var(--success); }
            QLabel.badge.offline { background: var(--danger); }
            
            /* Table improvements */
            QTableView {
                border: none;
                gridline-color: var(--border-color);
                selection-background-color: var(--highlight-soft);
                alternate-row-colors: true;
            }
            
            QTableView::item {
                padding: 8px 4px;
                border-bottom: 1px solid var(--border-color-light);
            }
            
            QHeaderView::section {
                background: var(--card-background);
                border: none;
                border-bottom: 2px solid var(--border-color);
                font-weight: 600;
                padding: 12px 8px;
            }
            
            /* Improved tabs */
            QTabWidget::pane {
                border: none;
            }
            
            QTabBar::tab {
                padding: 12px 20px;
                margin: 4px 2px;
                border-radius: 12px;
                background: var(--card-background);
                min-width: 120px;
            }
            
            QTabBar::tab:selected {
                background: var(--highlight-soft);
                color: white;
                font-weight: 600;
            }
            
            /* Improved progress bar */
            QProgressBar {
                border: 1px solid var(--border-color);
                border-radius: 10px;
                text-align: center;
                background: var(--card-background);
                padding: 2px;
                height: 18px;
            }
            
            QProgressBar::chunk {
                background-color: var(--primary);
                border-radius: 8px;
            }
            
            /* Scrollbar styling */
            QScrollBar:vertical {
                border: none;
                background: rgba(var(--text-color), 0.05);
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(var(--text-color), 0.2);
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(var(--text-color), 0.3);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: rgba(var(--text-color), 0.05);
                height: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:horizontal {
                background: rgba(var(--text-color), 0.2);
                border-radius: 5px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: rgba(var(--text-color), 0.3);
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            /* Menu styling */
            QMenu {
                background: var(--card-background);
                border: 1px solid var(--border-color);
                border-radius: 10px;
                padding: 5px;
            }
            
            QMenu::item {
                padding: 8px 25px 8px 20px;
                border-radius: 6px;
            }
            
            QMenu::item:selected {
                background: var(--highlight-soft);
            }
            
            QMenu::icon {
                padding-left: 10px;
            }
            
            /* Status bar */
            QStatusBar {
                background: var(--card-background);
                color: rgba(var(--text-color), 0.7);
                border-top: 1px solid var(--border-color);
            }
            
            /* Dialog styling */
            QDialog {
                background: var(--bg-color);
            }
        """)
    else:
        # Light theme CSS with similar structure but light colors
        app.setPalette(NeoPalette.light())
        app.setStyleSheet("""
            /* Light theme CSS Variables */
            * {
                --bg-color: #eef0ff;
                --card-background: #ffffff;
                --border-color: #e5e8ff;
                --border-color-light: #eef1ff;
                --text-color: 30, 30, 45;
                --highlight: #6c4cff;
                --highlight-soft: #dfe5ff;
                --primary: #6c4cff;
                --primary-dark: #5a3fe0;
                --success: #16a34a;
                --danger: #dc2626;
                --warning: #eab308;
            }
            
            QWidget { font-family: "Segoe UI"; font-size: 10pt; }
            
            /* Enhanced Neumorphic containers */
            .neo-card {
                background: var(--card-background);
                border-radius: 16px;
                padding: 16px;
                border: 1px solid var(--border-color);
            }
            
            /* Improved sidebar */
            QFrame#sidebar {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 var(--primary), stop:1 var(--primary-dark));
                border-radius: 18px;
                margin: 12px;
            }
            
            QLabel#logo {
                color: white; 
                font-weight: 700; 
                font-size: 18px;
                letter-spacing: 1px;
            }
            
            QPushButton.sidebar {
                color: #ffffff; 
                border: none; 
                border-radius: 12px; 
                padding: 12px 16px;
                text-align: left;
                font-weight: 500;
                font-size: 11pt;
            }
            
            QPushButton.sidebar:hover { 
                background: rgba(255,255,255,0.20); 
            }
            
            QPushButton.sidebar:checked { 
                background: rgba(255,255,255,0.30);
                font-weight: 600; 
            }
            
            /* Better form controls */
            QLineEdit, QSpinBox, QDoubleSpinBox, QTextEdit, QComboBox {
                background: var(--card-background);
                border: 1px solid var(--border-color);
                border-radius: 10px;
                padding: 10px;
                color: rgba(var(--text-color), 1);
                selection-background-color: var(--highlight-soft);
            }
            
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid var(--highlight);
            }
            
            /* Improved buttons */
            QPushButton, QToolButton {
                background: var(--card-background);
                border: 1px solid var(--border-color);
                border-radius: 10px;
                padding: 10px 14px;
                color: rgba(var(--text-color), 1);
                min-height: 36px;
            }
            
            QPushButton:hover, QToolButton:hover {
                background: #f3f5ff;
            }
            
            QPushButton:pressed, QToolButton:pressed {
                background: #e9ecff;
            }
            
            QPushButton.primary {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 var(--primary), stop:1 var(--primary-dark));
                color: white;
                font-weight: 600;
                border: none;
            }
            
            QPushButton.primary:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #7d61ff, stop:1 #6b53e8);
            }
            
            /* Status badges */
            QLabel.badge {
                padding: 6px 12px;
                border-radius: 12px;
                color: white;
                font-weight: 600;
                font-size: 9pt;
            }
            
            QLabel.badge.running { background: var(--success); }
            QLabel.badge.offline { background: var(--danger); }
            
            /* Table improvements */
            QTableView {
                border: none;
                gridline-color: var(--border-color);
                selection-background-color: var(--highlight-soft);
                alternate-row-colors: true;
            }
            
            QTableView::item {
                padding: 8px 4px;
                border-bottom: 1px solid var(--border-color-light);
            }
            
            QHeaderView::section {
                background: var(--card-background);
                border: none;
                border-bottom: 2px solid var(--border-color);
                font-weight: 600;
                padding: 12px 8px;
            }
            
            /* Improved tabs */
            QTabWidget::pane {
                border: none;
            }
            
            QTabBar::tab {
                padding: 12px 20px;
                margin: 4px 2px;
                border-radius: 12px;
                background: var(--card-background);
                border: 1px solid var(--border-color);
                min-width: 120px;
            }
            
            QTabBar::tab:selected {
                background: var(--highlight-soft);
                color: rgba(var(--text-color), 1);
                font-weight: 600;
                border: 1px solid var(--highlight);
            }
            
            /* Improved progress bar */
            QProgressBar {
                border: 1px solid var(--border-color);
                border-radius: 10px;
                text-align: center;
                background: var(--card-background);
                padding: 2px;
                height: 18px;
            }
            
            QProgressBar::chunk {
                background-color: var(--primary);
                border-radius: 8px;
            }
            
            /* Scrollbar styling */
            QScrollBar:vertical {
                border: none;
                background: rgba(var(--text-color), 0.05);
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(var(--text-color), 0.2);
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(var(--text-color), 0.3);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: rgba(var(--text-color), 0.05);
                height: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:horizontal {
                background: rgba(var(--text-color), 0.2);
                border-radius: 5px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: rgba(var(--text-color), 0.3);
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            /* Menu styling */
            QMenu {
                background: var(--card-background);
                border: 1px solid var(--border-color);
                border-radius: 10px;
                padding: 5px;
            }
            
            QMenu::item {
                padding: 8px 25px 8px 20px;
                border-radius: 6px;
            }
            
            QMenu::item:selected {
                background: var(--highlight-soft);
            }
            
            QMenu::icon {
                padding-left: 10px;
            }
            
            /* Status bar */
            QStatusBar {
                background: var(--card-background);
                color: rgba(var(--text-color), 0.7);
                border-top: 1px solid var(--border-color);
            }
            
            /* Dialog styling */
            QDialog {
                background: var(--bg-color);
            }
        """)

# Performance Configuration for different scales
class PerformanceConfig:
    """Performance configuration presets for different instance counts"""
    
    @staticmethod
    def get_config(instance_count):
        """Get optimal configuration based on instance count"""
        if instance_count <= 100:
            return {
                'batch_size': 10,
                'instance_delay': 1.0,
                'batch_delay': 5.0,
                'max_concurrent': 5,
                'chunk_size': 20
            }
        elif instance_count <= 1000:
            return {
                'batch_size': 25,
                'instance_delay': 0.5,
                'batch_delay': 3.0,
                'max_concurrent': 8,
                'chunk_size': 50
            }
        elif instance_count <= 5000:
            return {
                'batch_size': 50,
                'instance_delay': 0.3,
                'batch_delay': 2.0,
                'max_concurrent': 12,
                'chunk_size': 100
            }
        else:  # 10k+
            return {
                'batch_size': 100,
                'instance_delay': 0.1,
                'batch_delay': 1.0,
                'max_concurrent': 20,
                'chunk_size': 200
            }
    
    @staticmethod
    def apply_shadow_optimization(widget_count):
        """Disable shadows for UI performance with many widgets"""
        return widget_count < 500  # Only apply shadows if less than 500 widgets
class MumuManager:
    def __init__(self, executable_path):
        self.executable_path = executable_path
        # Memory optimization for 10k instances
        self._instance_cache = {}
        self._cache_max_size = 1000  # Limit cache size
        self._cache_access_order = []  # Track access for LRU eviction

    def _run_command(self, args, return_output=False):
        if not os.path.exists(self.executable_path):
            return False, f"Lỗi: Không tìm thấy '{os.path.basename(self.executable_path)}' tại đường dẫn đã chỉ định."
        command = [self.executable_path] + args
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(
                command, check=True, capture_output=True, text=True, encoding='utf-8', startupinfo=startupinfo
            )
            output = result.stdout.strip()
            return (True, output) if return_output else (True, f"Lệnh '{' '.join(args)}' thực thi thành công.")
        except Exception as e:
            error_msg = f"Lỗi khi chạy lệnh {' '.join(command)}:\n{e}"
            if hasattr(e, 'stderr') and e.stderr:
                error_msg += f"\nStderr: {e.stderr.strip()}"
            if hasattr(e, 'stdout') and e.stdout:
                error_msg += f"\nStdout: {e.stdout.strip()}"
            return False, error_msg

    def get_all_info(self):
        ok, output = self._run_command(['info', '-v', 'all'], return_output=True)
        if ok and output:
            try:
                data = json.loads(output)
                if isinstance(data, list):
                    result = {str(o.get("index", i)): o for i, o in enumerate(data)}
                    # Update cache with LRU eviction for memory optimization
                    self._update_cache(result)
                    return result
                if isinstance(data, dict):
                    single_result = {str(data["index"]): data} if "index" in data else data
                    self._update_cache(single_result)
                    return single_result
            except json.JSONDecodeError:
                try:
                    json_objects = [json.loads(line) for line in output.strip().split('\n') if line.strip()]
                    result = {str(obj['index']): obj for obj in json_objects}
                    self._update_cache(result)
                    return result
                except Exception:
                    return f"Lỗi phân tích JSON. Dữ liệu thô:\n---\n{output}\n---"
        elif not ok:
            return output
        return "Không nhận được dữ liệu từ Manager. Vui lòng thử chạy một giả lập."
    
    def _update_cache(self, new_data):
        """Update instance cache with LRU eviction for memory optimization"""
        for key, value in new_data.items():
            if key in self._instance_cache:
                # Move to end (most recently used)
                self._cache_access_order.remove(key)
            elif len(self._instance_cache) >= self._cache_max_size:
                # Remove least recently used
                lru_key = self._cache_access_order.pop(0)
                del self._instance_cache[lru_key]
            
            self._instance_cache[key] = value
            self._cache_access_order.append(key)
    
    def get_cached_instance_info(self, index):
        """Get instance info from cache if available"""
        key = str(index)
        if key in self._instance_cache:
            # Move to end (most recently used)
            self._cache_access_order.remove(key)
            self._cache_access_order.append(key)
            return self._instance_cache[key]
        return None
    
    def clear_cache(self):
        """Clear instance cache to free memory"""
        self._instance_cache.clear()
        self._cache_access_order.clear()

    def control_instance(self, indices, action):
        return self._run_command(['control', '-v', ",".join(map(str, indices)), action])

    def create_instance(self, count):
        return self._run_command(['create', '-n', str(count)])

    def clone_instance(self, source_index, count):
        return self._run_command(['clone', '-v', str(source_index), '-n', str(count)])

    def delete_instance(self, indices):
        return self._run_command(['delete', '-v', ",".join(map(str, indices))])

    def rename_instance(self, index, new_name):
        return self._run_command(['rename', '-v', str(index), '-n', new_name])

    def import_instance(self, path, count):
        return self._run_command(['import', '-p', path, '-n', str(count)])

    def export_instance(self, indices, directory, name, compress):
        args = ['export', '-v', ",".join(map(str, indices)), '-d', directory, '-n', name]
        if compress: args.append('--zip')
        return self._run_command(args)

    def sort_windows(self):
        return self._run_command(['sort'])

    # IMEI/MAC
    @staticmethod
    def generate_imei():
        rand_part = [random.randint(0, 9) for _ in range(14)]
        total = 0
        for i, d in enumerate(rand_part):
            if i % 2 == 0: total += d
            else:
                x = d * 2; total += (x % 10) + (x // 10)
        checksum = (10 - (total % 10)) % 10
        return "".join(map(str, rand_part + [checksum]))

    def set_imei(self, indices, imei):
        return self._run_command(['simulation', '-v', ",".join(map(str, indices)), '-sk', 'imei', '-sv', imei])

    def set_mac(self, indices, mac):
        return self._run_command(['simulation', '-v', ",".join(map(str, indices)), '-sk', 'mac_address', '-sv', mac])

    def run_adb_command(self, indices, command_str):
        return self._run_command(['adb', '-v', ",".join(map(str, indices)), '-c', command_str])

    # Optimization methods for 10k+ instances
    def batch_control_instance(self, indices, action, chunk_size=100):
        """
        Optimized batch control for large number of instances
        Processes instances in chunks to avoid command line length limits
        """
        if len(indices) <= chunk_size:
            return self.control_instance(indices, action)
        
        results = []
        for i in range(0, len(indices), chunk_size):
            chunk = indices[i:i + chunk_size]
            ok, msg = self.control_instance(chunk, action)
            results.append((ok, msg))
            if not ok:
                return False, f"Batch failed at chunk {i//chunk_size + 1}: {msg}"
        
        return True, f"Successfully processed {len(indices)} instances in {len(results)} chunks"
    
    def bulk_create_instances(self, count, chunk_size=50):
        """
        Optimized bulk instance creation for large numbers
        Creates instances in chunks to manage system resources
        """
        if count <= chunk_size:
            return self.create_instance(count)
        
        created = 0
        for remaining in range(count, 0, -chunk_size):
            batch_count = min(chunk_size, remaining)
            ok, msg = self.create_instance(batch_count)
            if ok:
                created += batch_count
            else:
                return False, f"Bulk creation failed after {created} instances: {msg}"
        
        return True, f"Successfully created {created} instances"
    
    def optimize_command_execution(self, commands, max_concurrent=10):
        """
        Execute multiple commands with limited concurrency to avoid system overload
        Useful for 10k+ instance operations
        """
        import threading
        import queue
        
        results = queue.Queue()
        semaphore = threading.Semaphore(max_concurrent)
        
        def execute_command(cmd_args):
            with semaphore:
                try:
                    result = self._run_command(cmd_args)
                    results.put(('success', result))
                except Exception as e:
                    results.put(('error', str(e)))
        
        threads = []
        for cmd_args in commands:
            thread = threading.Thread(target=execute_command, args=(cmd_args,))
            thread.start()
            threads.append(thread)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        all_results = []
        while not results.empty():
            all_results.append(results.get())
        
        success_count = sum(1 for status, _ in all_results if status == 'success')
        return success_count == len(commands), f"{success_count}/{len(commands)} commands succeeded"

# =========================
# Threads
# =========================
class Worker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    log = pyqtSignal(str)
    def __init__(self, manager, params):
        super().__init__(); self.manager = manager; self.params = params
        self._is_running = True; self._is_paused = False
    def stop(self):
        self.log.emit("⚠️ Đang gửi yêu cầu dừng..."); self._is_running = False
    def pause(self):
        if not self._is_paused: self._is_paused = True; self.log.emit("⏸️ Tạm dừng...")
    def resume(self):
        if self._is_paused: self._is_paused = False; self.log.emit("▶️ Tiếp tục...")
    def _maybe_pause(self):
        while self._is_running and self._is_paused: self.msleep(140)

class AutoWorker(Worker):
    def run(self):
        start, end, batch_size, inst_delay, batch_delay = self.params
        total_instances = max(1, end - start + 1); processed = 0
        self.log.emit("--- 🤖 BẮT ĐẦU CHẾ ĐỘ TỰ ĐỘNG 🤖 ---")
        for i in range(start, end + 1, batch_size):
            if not self._is_running: break
            self._maybe_pause()
            b0, b1 = i, min(i + batch_size - 1, end)
            self.log.emit(f"\n--- Batch: {b0} - {b1} ---")
            for idx in range(b0, b1 + 1):
                if not self._is_running: break
                self._maybe_pause()
                ok, _ = self.manager.control_instance([idx], 'launch')
                self.log.emit(f"Khởi động VM {idx}: {'Thành công' if ok else 'Thất bại'}")
                processed += 1; self.progress.emit(int((processed/total_instances)*100))
                if idx < b1 and self._is_running: self.msleep(int(inst_delay*1000))
            if b1 < end and self._is_running:
                self._maybe_pause(); self.msleep(int(batch_delay*1000))
        self.finished.emit("✅ HOÀN TẤT" if self._is_running else "🛑 ĐÃ DỪNG")

class BatchSimWorker(Worker):
    def run(self):
        tasks = self.params
        total = max(1, len(tasks))
        self.log.emit("--- 🛡️ BẮT ĐẦU THAY ĐỔI THUỘC TÍNH MÁY (IMEI/MAC) ---")
        for i, (idx, imei, mac) in enumerate(tasks, start=1):
            if not self._is_running: break
            if imei:
                ok, msg = self.manager.set_imei([idx], imei)
                self.log.emit(f"VM {idx} • IMEI → {imei}: {'OK' if ok else 'LỖI'}"); 
                if not ok: self.log.emit(msg)
            if mac:
                ok, msg = self.manager.set_mac([idx], mac)
                self.log.emit(f"VM {idx} • MAC  → {mac}: {'OK' if ok else 'LỖI'}"); 
                if not ok: self.log.emit(msg)
            self.progress.emit(int((i/total)*100)); self.msleep(120)
        self.finished.emit("✅ HOÀN TẤT" if self._is_running else "🛑 ĐÃ DỪNG")

# Optimized Worker for 10k instances with parallel processing
class OptimizedAutoWorker(Worker):
    """Optimized worker for handling 10,000+ instances efficiently"""
    def run(self):
        start, end, batch_size, inst_delay, batch_delay = self.params
        total_instances = max(1, end - start + 1)
        processed = 0
        
        # Use larger batch sizes for 10k+ instances
        if total_instances > 1000:
            batch_size = max(batch_size, 50)  # Minimum 50 for large operations
            inst_delay = min(inst_delay, 1.0)  # Cap instance delay
            batch_delay = min(batch_delay, 5.0)  # Cap batch delay
        
        self.log.emit(f"--- 🚀 OPTIMIZED AUTO MODE FOR {total_instances} INSTANCES ---")
        self.log.emit(f"Using batch size: {batch_size}, delays: {inst_delay}s/{batch_delay}s")
        
        for i in range(start, end + 1, batch_size):
            if not self._is_running: break
            self._maybe_pause()
            
            b0, b1 = i, min(i + batch_size - 1, end)
            batch_indices = list(range(b0, b1 + 1))
            
            self.log.emit(f"\n--- Processing Batch: {b0}-{b1} ({len(batch_indices)} VMs) ---")
            
            # Batch launch for better performance
            if len(batch_indices) > 10:
                # Use bulk command for large batches
                ok, msg = self.manager.control_instance(batch_indices, 'launch')
                if ok:
                    self.log.emit(f"✅ Bulk launched VMs {b0}-{b1}")
                else:
                    self.log.emit(f"❌ Bulk launch failed: {msg}")
                    # Fallback to individual launches
                    for idx in batch_indices:
                        if not self._is_running: break
                        ok, _ = self.manager.control_instance([idx], 'launch')
                        self.log.emit(f"VM {idx}: {'✅' if ok else '❌'}")
                        if idx < b1 and self._is_running: 
                            self.msleep(int(inst_delay*200))  # Reduced sleep for bulk
                processed += len(batch_indices)
            else:
                # Individual processing for smaller batches
                for idx in batch_indices:
                    if not self._is_running: break
                    self._maybe_pause()
                    ok, _ = self.manager.control_instance([idx], 'launch')
                    self.log.emit(f"VM {idx}: {'✅ Thành công' if ok else '❌ Thất bại'}")
                    processed += 1
                    if idx < b1 and self._is_running: 
                        self.msleep(int(inst_delay*1000))
            
            # Update progress
            self.progress.emit(int((processed/total_instances)*100))
            
            # Batch delay with optimization for large operations
            if b1 < end and self._is_running:
                self._maybe_pause()
                sleep_time = batch_delay
                if total_instances > 5000:
                    sleep_time = min(sleep_time, 2.0)  # Reduced delay for very large operations
                self.msleep(int(sleep_time*1000))
        
        self.finished.emit("✅ HOÀN TẤT" if self._is_running else "🛑 ĐÃ DỪNG")

# =========================
# Dialogs (Settings + Automation + Batch Edit) - Đã cải tiến giao diện
# =========================
class AutomationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thiết lập Tự động hóa")
        self.setMinimumWidth(460)
        
        main_layout = QVBoxLayout(self)
        
        # Tiêu đề với icon
        title_layout = QHBoxLayout()
        title_label = QLabel("⚙️ Cấu hình tự động hóa")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # Form trong card
        form_card = QFrame()
        form_card.setProperty("class", "neo-card")
        apply_shadow(form_card)
        
        lay = QFormLayout(form_card)
        lay.setSpacing(12)
        
        # Các điều khiển với tooltip và giá trị mặc định tốt hơn
        self.start_index = QSpinBox()
        self.start_index.setRange(0, 9999)
        self.start_index.setToolTip("Chỉ số bắt đầu của máy ảo (VM) để tự động hóa")
        
        self.end_index = QSpinBox()
        self.end_index.setRange(0, 9999)
        self.end_index.setToolTip("Chỉ số kết thúc của máy ảo (VM) để tự động hóa")
        
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 500)  # Increased range for 10k instances
        self.batch_size.setToolTip("Số lượng máy ảo khởi động cùng lúc trong một đợt (tối ưu cho 10k: 50-100)")
        
        self.instance_delay = QDoubleSpinBox()
        self.instance_delay.setRange(0, 30)  # Reduced max for bulk operations
        self.instance_delay.setDecimals(2)
        self.instance_delay.setToolTip("Thời gian chờ giữa các lần khởi động VM trong cùng một đợt (giây)")
        
        self.batch_delay = QDoubleSpinBox()
        self.batch_delay.setRange(0, 300)  # Reduced max for bulk operations
        self.batch_delay.setDecimals(2)
        self.batch_delay.setToolTip("Thời gian chờ giữa các đợt khởi động (giây)")
        
        self.start_index.setValue(1)
        self.end_index.setValue(100)  # Larger default range
        self.batch_size.setValue(50)  # Larger default batch size
        self.instance_delay.setValue(0.5)  # Faster default delay
        self.batch_delay.setValue(3.0)  # Faster default batch delay
        
        # Thêm các nhãn mô tả rõ ràng hơn
        lay.addRow("Chỉ số bắt đầu:", self.start_index)
        lay.addRow("Chỉ số kết thúc:", self.end_index)
        lay.addRow("Kích thước đợt:", self.batch_size)
        lay.addRow("Thời gian chờ giữa VM (giây):", self.instance_delay)
        lay.addRow("Thời gian chờ giữa đợt (giây):", self.batch_delay)
        
        main_layout.addWidget(form_card)
        
        # Thông tin mô tả
        info_label = QLabel("Tính năng này cho phép khởi động nhiều VM theo đợt, giúp giảm tải hệ thống.")
        info_label.setStyleSheet("color: rgba(var(--text-color), 0.7); font-style: italic; margin-top: 5px;")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Nút với style cải tiến
        btn_layout = QHBoxLayout()
        btns = QDialogButtonBox()
        
        self.ok_btn = QPushButton("Xác nhận")
        self.ok_btn.setProperty("class", "primary")
        self.ok_btn.setMinimumWidth(100)
        self.ok_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Hủy bỏ")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        
        main_layout.addLayout(btn_layout)

    def get_values(self):
        return (self.start_index.value(), self.end_index.value(), self.batch_size.value(),
                self.instance_delay.value(), self.batch_delay.value())

class SettingsDialog(QDialog):
    def __init__(self, parent, current_path):
        super().__init__(parent)
        self.setWindowTitle("Cài đặt hệ thống")
        self.setMinimumWidth(620)
        
        main_layout = QVBoxLayout(self)
        
        # Tiêu đề đẹp hơn
        title_layout = QHBoxLayout()
        title_label = QLabel("⚙️ Cài đặt hệ thống")
        title_label.setStyleSheet("font-size: 15pt; font-weight: bold; margin-bottom: 10px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # Card đường dẫn
        path_card = QFrame()
        path_card.setProperty("class", "neo-card")
        apply_shadow(path_card)
        path_layout = QVBoxLayout(path_card)
        
        path_title = QLabel("Đường dẫn đến MuMuManager.exe")
        path_title.setStyleSheet("font-weight: 600; font-size: 11pt;")
        path_layout.addWidget(path_title)
        
        path_row = QHBoxLayout()
        self.path_entry = QLineEdit(current_path)
        self.path_entry.setPlaceholderText("Nhập đường dẫn đến MuMuManager.exe...")
        
        btn = QPushButton("Duyệt...")
        btn.setMaximumWidth(100)
        path_row.addWidget(self.path_entry)
        path_row.addWidget(btn)
        path_layout.addLayout(path_row)
        
        status_row = QHBoxLayout()
        status_label = QLabel("Trạng thái:")
        self.lbl_status = QLabel("—")
        status_row.addWidget(status_label)
        status_row.addWidget(self.lbl_status)
        status_row.addStretch(1)
        path_layout.addLayout(status_row)
        
        main_layout.addWidget(path_card)

        # Automation defaults trong card riêng
        auto_card = QFrame()
        auto_card.setProperty("class", "neo-card")
        apply_shadow(auto_card)
        auto_layout = QVBoxLayout(auto_card)
        
        auto_title = QLabel("Cấu hình mặc định cho tự động hóa")
        auto_title.setStyleSheet("font-weight: 600; font-size: 11pt;")
        auto_layout.addWidget(auto_title)
        
        s = parent.settings
        self.start_index = QSpinBox()
        self.start_index.setRange(0, 9999)
        self.start_index.setValue(int(s.value("auto/start", 1)))
        self.start_index.setToolTip("Chỉ số VM bắt đầu")
        
        self.end_index = QSpinBox()
        self.end_index.setRange(0, 9999)
        self.end_index.setValue(int(s.value("auto/end", 10)))
        self.end_index.setToolTip("Chỉ số VM kết thúc")
        
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 500)  # Increased range for 10k instances
        self.batch_size.setValue(int(s.value("auto/batch", 50)))  # Larger default batch size
        self.batch_size.setToolTip("Số VM khởi động cùng lúc (tối ưu cho 10k instances: 50-100)")
        
        self.instance_delay = QDoubleSpinBox()
        self.instance_delay.setRange(0, 30)  # Reduced max delay for bulk operations
        self.instance_delay.setDecimals(2)
        self.instance_delay.setValue(float(s.value("auto/inst_delay", 0.5)))  # Faster default
        self.instance_delay.setToolTip("Thời gian giữa các lần khởi động VM (giây) - tối ưu cho 10k: 0.1-1.0")
        
        self.batch_delay = QDoubleSpinBox()
        self.batch_delay.setRange(0, 300)  # Reduced max delay
        self.batch_delay.setDecimals(2)
        self.batch_delay.setValue(float(s.value("auto/batch_delay", 3.0)))  # Faster default
        self.batch_delay.setToolTip("Thời gian giữa các đợt khởi động (giây) - tối ưu cho 10k: 1.0-5.0")
        
        grid = QFormLayout()
        grid.setSpacing(10)
        grid.addRow("Chỉ số bắt đầu:", self.start_index)
        grid.addRow("Chỉ số kết thúc:", self.end_index)
        grid.addRow("Kích thước đợt:", self.batch_size)
        grid.addRow("Thời gian chờ giữa VM (giây):", self.instance_delay)
        grid.addRow("Thời gian chờ giữa đợt (giây):", self.batch_delay)
        
        auto_layout.addLayout(grid)
        main_layout.addWidget(auto_card)
        
        # Giao diện
        ui_card = QFrame()
        ui_card.setProperty("class", "neo-card")
        apply_shadow(ui_card)
        ui_layout = QVBoxLayout(ui_card)
        
        ui_title = QLabel("Giao diện")
        ui_title.setStyleSheet("font-weight: 600; font-size: 11pt;")
        ui_layout.addWidget(ui_title)
        
        theme_row = QHBoxLayout()
        theme_label = QLabel("Chế độ màu:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sáng", "Tối"])
        self.theme_combo.setCurrentIndex(1 if parent.settings.value("theme", "light") == "dark" else 0)
        
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch(1)
        ui_layout.addLayout(theme_row)
        
        main_layout.addWidget(ui_card)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Lưu thay đổi")
        self.save_btn.setProperty("class", "primary")
        self.save_btn.setMinimumWidth(120)
        
        self.cancel_btn = QPushButton("Hủy bỏ")
        self.cancel_btn.setMinimumWidth(100)
        
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)
        
        # Connect signals
        btn.clicked.connect(self.browse)
        self.save_btn.clicked.connect(self._save_and_accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.path_entry.textChanged.connect(self.validate)
        
        self.validate()

    def browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn MuMuManager.exe", "", "Executable (*.exe)")
        if path: self.path_entry.setText(path); self.validate()

    def validate(self):
        p = self.path_entry.text().strip()
        ok = os.path.exists(p) and os.path.basename(p).lower() == "mumumanager.exe"
        self.lbl_status.setText("✅ Hợp lệ" if ok else "❌ Không hợp lệ")
        self.lbl_status.setStyleSheet("color:#34d399; font-weight: 600;" if ok else "color:#f87171; font-weight: 600;")

    def _save_and_accept(self):
        s = self.parent().settings
        s.setValue("manager_path", self.get_path())
        s.setValue("auto/start", self.start_index.value())
        s.setValue("auto/end", self.end_index.value())
        s.setValue("auto/batch", self.batch_size.value())
        s.setValue("auto/inst_delay", self.instance_delay.value())
        s.setValue("auto/batch_delay", self.batch_delay.value())
        s.setValue("theme", "dark" if self.theme_combo.currentIndex() == 1 else "light")
        self.accept()

    def get_path(self):
        return self.path_entry.text().strip()

class BatchEditDialog(QDialog):
    def __init__(self, indices, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chỉnh sửa IMEI / MAC hàng loạt")
        self.setMinimumWidth(580)
        self.indices = sorted(indices)
        
        main_layout = QVBoxLayout(self)
        
        # Tiêu đề
        title_layout = QHBoxLayout()
        title_label = QLabel("🔄 Thay đổi IMEI/MAC hàng loạt")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # Phần thông tin đối tượng
        target_card = QFrame()
        target_card.setProperty("class", "neo-card")
        apply_shadow(target_card)
        target_layout = QVBoxLayout(target_card)
        
        target_label = QLabel("Thông tin đối tượng")
        target_label.setStyleSheet("font-weight: 600; font-size: 11pt;")
        target_layout.addWidget(target_label)
        
        self.range_label = QLabel(f"Áp dụng cho {len(self.indices)} VM: {', '.join(map(str, self.indices[:16]))}{'...' if len(self.indices)>16 else ''}")
        self.range_label.setWordWrap(True)
        target_layout.addWidget(self.range_label)
        
        main_layout.addWidget(target_card)
        
        # Phần cấu hình
        config_card = QFrame()
        config_card.setProperty("class", "neo-card")
        apply_shadow(config_card)
        config_layout = QVBoxLayout(config_card)
        
        config_label = QLabel("Cấu hình thay đổi")
        config_label.setStyleSheet("font-weight: 600; font-size: 11pt;")
        config_layout.addWidget(config_label)
        
        # IMEI
        imei_group = QHBoxLayout()
        self.imei_enable = QCheckBox("Đổi IMEI")
        self.imei_enable.setStyleSheet("font-weight: 500;")
        self.imei_mode = QLineEdit("random")
        self.imei_mode.setPlaceholderText("random hoặc IMEI 15 số")
        imei_group.addWidget(self.imei_enable)
        imei_group.addWidget(self.imei_mode)
        config_layout.addLayout(imei_group)
        
        imei_help = QLabel("Nhập \"random\" để tạo ngẫu nhiên hoặc nhập 15 chữ số IMEI cụ thể")
        imei_help.setStyleSheet("color: rgba(var(--text-color), 0.6); font-style: italic; font-size: 9pt; margin-left: 24px; margin-bottom: 8px;")
        config_layout.addWidget(imei_help)
        
        # MAC
        mac_group = QHBoxLayout()
        self.mac_enable = QCheckBox("Đổi MAC")
        self.mac_enable.setStyleSheet("font-weight: 500;")
        self.mac_mode = QLineEdit("random")
        self.mac_mode.setPlaceholderText("random / AA:BB:CC:* / MAC đầy đủ")
        mac_group.addWidget(self.mac_enable)
        mac_group.addWidget(self.mac_mode)
        config_layout.addLayout(mac_group)
        
        mac_help = QLabel("Nhập \"random\", mẫu như \"AA:BB:CC:*\" hoặc địa chỉ MAC đầy đủ")
        mac_help.setStyleSheet("color: rgba(var(--text-color), 0.6); font-style: italic; font-size: 9pt; margin-left: 24px;")
        config_layout.addWidget(mac_help)
        
        main_layout.addWidget(config_card)
        
        # Preview
        preview_card = QFrame()
        preview_card.setProperty("class", "neo-card")
        apply_shadow(preview_card)
        preview_layout = QVBoxLayout(preview_card)
        
        preview_label = QLabel("Xem trước thay đổi")
        preview_label.setStyleSheet("font-weight: 600; font-size: 11pt;")
        preview_layout.addWidget(preview_label)
        
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setMinimumHeight(160)
        preview_layout.addWidget(self.preview)
        
        main_layout.addWidget(preview_card)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Áp dụng")
        self.apply_btn.setProperty("class", "primary")
        self.apply_btn.setMinimumWidth(120)
        self.apply_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("Hủy bỏ")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.apply_btn)
        main_layout.addLayout(btn_layout)
        
        # Connect signals
        for w in (self.imei_enable, self.imei_mode, self.mac_enable, self.mac_mode):
            (w.textChanged if isinstance(w,QLineEdit) else w.stateChanged).connect(self.update_preview)
        
        self.update_preview()

    @staticmethod
    def _valid_mac(mac: str) -> bool:
        return bool(re.fullmatch(r"(?i)([0-9A-F]{2}:){5}[0-9A-F]{2}", mac.strip()))
    
    @staticmethod
    def _valid_mac_prefix(prefix: str) -> bool:
        return bool(re.fullmatch(r"(?i)([0-9A-F]{2}:){1,5}\*", prefix.strip()))
    
    def _rand_mac(self):
        return ":".join(f"{random.randint(0,255):02x}" for _ in range(6))
    
    def _rand_mac_with_prefix(self, prefix: str):
        prefix = prefix.strip()[:-1]
        fixed = prefix.split(":") if prefix else []
        rest = 6 - len(fixed)
        tail = [f"{random.randint(0,255):02x}" for _ in range(rest)]
        return ":".join([*fixed, *tail])
    
    def _gen_tasks(self):
        tasks = []; imei_enabled = self.imei_enable.isChecked(); mac_enabled = self.mac_enable.isChecked()
        imei_mode = self.imei_mode.text().strip(); mac_mode = self.mac_mode.text().strip()
        for idx in self.indices:
            imei = None; mac = None
            if imei_enabled:
                if imei_mode.lower()=="random": imei = MumuManager.generate_imei()
                elif re.fullmatch(r"\d{15}", imei_mode): imei = imei_mode
            if mac_enabled:
                if mac_mode.lower()=="random": mac = self._rand_mac()
                elif self._valid_mac(mac_mode): mac = mac_mode.lower()
                elif self._valid_mac_prefix(mac_mode): mac = self._rand_mac_with_prefix(mac_mode).lower()
            tasks.append((idx, imei, mac))
        return tasks
    
    def update_preview(self):
        lines=[]
        for idx, imei, mac in self._gen_tasks():
            txt=f"VM {idx}: "
            if self.imei_enable.isChecked(): txt+=f"IMEI={imei or '❌'}  "
            if self.mac_enable.isChecked():  txt+=f"MAC={mac or '❌'}"
            lines.append(txt)
        self.preview.setPlainText("\n".join(lines))
    
    def get_tasks(self):
        tasks = self._gen_tasks()
        if self.imei_enable.isChecked() and any(imei is None for _, imei, _ in tasks):
            QMessageBox.warning(self,"Sai IMEI","Dùng 'random' hoặc IMEI 15 số."); return None
        if self.mac_enable.isChecked() and any(mac is None for _,_,mac in tasks):
            QMessageBox.warning(self,"Sai MAC","Dùng 'random', 'AA:BB:CC:*' hoặc MAC đầy đủ."); return None
        return tasks

# =========================
# Tiny helpers: StatCard & Status chip
# =========================
class StatusPillDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        value = index.data()
        painter.save()
        rect = option.rect.adjusted(6,6,-6,-6)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Improved color scheme
        if value == "Running":
            bg = QColor("#16a34a")  # Darker green
            text = "Đang chạy"
        else:
            bg = QColor("#dc2626")  # Darker red
            text = "Đã tắt"
            
        # Draw background with rounded corners
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, 10, 10)
        
        # Draw text with better contrast
        painter.setPen(QColor("#ffffff"))
        painter.setFont(option.font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        
        painter.restore()

class StatCard(QFrame):
    def __init__(self, title, value, subtitle=""):
        super().__init__()
        self.setObjectName("neo-card")
        self.setProperty("class", "neo-card")
        self.setMinimumHeight(120)
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(6)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 600; color: rgba(var(--text-color), 0.7)")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: 700; margin-top: 4px")
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: rgba(var(--text-color), 0.5); font-size: 9pt")
        
        lay.addWidget(title_label)
        lay.addWidget(value_label)
        lay.addWidget(subtitle_label)
        lay.addStretch(1)
        
        apply_shadow(self)

# =========================
# Main Window
# =========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MumuManagerPRO – Neumorphic UI")
        self.resize(1280, 760)
        self.settings = QSettings("MumuTeam","MumuManagerPRO")
        self.mumu_path = self.settings.value("manager_path",
            r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\MuMuManager.exe")
        self.instance_cache = {}
        self.worker = None
        
        # Apply theme
        apply_neo_style(QApplication.instance(), self.settings.value("theme", "light"))
        
        self._build_ui()
        self._wire()
        self.refresh_instances()

    # ---- UI composition (Sidebar + Topbar + Content tabs) ----
    def _sidebar_btn(self, text, icon=""):
        b = QPushButton(f"{icon} {text}" if icon else text)
        b.setCheckable(True)
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setProperty("class", "sidebar")
        b.setMinimumHeight(42)
        b.setIconSize(QSize(18, 18))
        return b

    def _build_ui(self):
        # Sidebar với thiết kế cải tiến
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        sb = QVBoxLayout(self.sidebar)
        sb.setContentsMargins(16, 24, 16, 16)
        sb.setSpacing(12)
        
        # Logo khu vực
        logo_layout = QVBoxLayout()
        logo_layout.setContentsMargins(8, 0, 8, 0)
        
        logo = QLabel("MuMu PRO")
        logo.setObjectName("logo")
        
        version = QLabel("v2.0")
        version.setStyleSheet("color:rgba(255,255,255,.6); font-size: 10px; margin-top:-6px;")
        
        logo_layout.addWidget(logo)
        logo_layout.addWidget(version)
        logo_widget = QWidget()
        logo_widget.setLayout(logo_layout)
        sb.addWidget(logo_widget)
        sb.addSpacing(16)
        
        # Các nút menu với icon
        self.btn_instances = self._sidebar_btn("Dashboard", "⟐")
        self.btn_apps = self._sidebar_btn("Ứng dụng", "⊞")
        self.btn_tools = self._sidebar_btn("Công cụ", "⚒")
        self.btn_manage = self._sidebar_btn("Quản lý VM", "⊕")
        self.btn_backup = self._sidebar_btn("Sao lưu/Phục hồi", "⟳")
        self.btn_settings = self._sidebar_btn("Cài đặt", "⚙")
        
        # Thêm các nút vào sidebar
        for w in [self.btn_instances, self.btn_apps, self.btn_tools, 
                  self.btn_manage, self.btn_backup, self.btn_settings]:
            sb.addWidget(w)
        
        sb.addStretch(1)
        
        # Thêm trạng thái người dùng ở cuối
        status_pill = QLabel("ONLINE")
        status_pill.setStyleSheet("""
            background: rgba(22, 163, 74, 0.2); 
            color: rgba(255,255,255,0.85);
            border-radius: 10px;
            padding: 4px 12px;
            font-weight: 600;
            font-size: 9pt;
        """)
        status_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb.addWidget(status_pill)

        # Main area (Topbar + Tabs)
        main = QWidget()
        mv = QVBoxLayout(main)
        mv.setContentsMargins(16, 16, 16, 16)
        mv.setSpacing(16)

        # Topbar với thiết kế cải tiến
        self.topbar = QWidget()
        top = QHBoxLayout(self.topbar)
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(12)
        
        # Left section - Search and filter
        left_section = QWidget()
        left_layout = QHBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Quick search for 10k instances
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm kiếm VM (ID, tên, trạng thái)...")
        self.search_input.setMinimumWidth(300)
        left_layout.addWidget(self.search_input)
        
        # Filter for performance with large datasets
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tất cả", "Đang chạy", "Đã tắt"])
        left_layout.addWidget(self.status_filter)
        
        top.addWidget(left_section)
        top.addStretch(1)
        
        # Right section - Quick actions
        right_section = QWidget()
        right_layout = QHBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.refresh_btn = QPushButton("🔄 Làm mới")
        self.refresh_btn.setProperty("class", "primary")
        self.auto_btn = QPushButton("🤖 Tự động hóa")
        self.auto_btn.setProperty("class", "primary")
        
        right_layout.addWidget(self.refresh_btn)
        right_layout.addWidget(self.auto_btn)
        top.addWidget(right_section)
        
        mv.addWidget(self.topbar)
        
        # Main content area - optimized for 10k instances
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stats cards for quick overview
        stats_layout = QHBoxLayout()
        self.total_card = StatCard("Tổng số VM", "0", "instances")
        self.running_card = StatCard("Đang chạy", "0", "active")
        self.offline_card = StatCard("Đã tắt", "0", "inactive")
        
        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.running_card)
        stats_layout.addWidget(self.offline_card)
        stats_layout.addStretch(1)
        
        content_layout.addLayout(stats_layout)
        
        # Progress area for bulk operations
        self.progress_frame = QFrame()
        self.progress_frame.setProperty("class", "neo-card")
        self.progress_frame.setVisible(False)
        
        progress_layout = QVBoxLayout(self.progress_frame)
        self.progress_label = QLabel("Đang xử lý...")
        self.progress_bar = QProgressBar()
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(150)
        self.log_output.setReadOnly(True)
        
        # Control buttons for operations
        control_layout = QHBoxLayout()
        self.pause_btn = QPushButton("⏸️ Tạm dừng")
        self.stop_btn = QPushButton("⏹️ Dừng")
        self.resume_btn = QPushButton("▶️ Tiếp tục")
        
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.resume_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addStretch(1)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.log_output)
        progress_layout.addLayout(control_layout)
        
        content_layout.addWidget(self.progress_frame)
        
        # Placeholder for instance table (would need virtual scrolling for 10k)
        self.instances_label = QLabel("Bảng VM sẽ được tối ưu hóa cho 10,000+ instances với virtual scrolling")
        self.instances_label.setStyleSheet("text-align: center; padding: 50px; color: gray;")
        content_layout.addWidget(self.instances_label)
        
        mv.addWidget(self.content_area)
        
        # Layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(main)
        splitter.setSizes([250, 1030])
        splitter.setChildrenCollapsible(False)
        
        self.setCentralWidget(splitter)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Sẵn sàng - Tối ưu hóa cho 10,000+ instances")

    def _wire(self):
        """Connect signals for optimized operations"""
        self.refresh_btn.clicked.connect(self.refresh_instances)
        self.auto_btn.clicked.connect(self.show_automation_dialog)
        self.btn_settings.clicked.connect(self.show_settings)
        
        # Search optimization for large datasets
        self.search_input.textChanged.connect(self.filter_instances)
        self.status_filter.currentTextChanged.connect(self.filter_instances)
        
        # Control buttons
        self.pause_btn.clicked.connect(self.pause_operation)
        self.resume_btn.clicked.connect(self.resume_operation)
        self.stop_btn.clicked.connect(self.stop_operation)

    def refresh_instances(self):
        """Optimized instance refresh for large datasets"""
        if hasattr(self, 'manager'):
            # Use performance config based on estimated instance count
            config = PerformanceConfig.get_config(1000)  # Default estimate
            
            # Clear cache periodically for memory management
            if hasattr(self.manager, 'clear_cache'):
                self.manager.clear_cache()
            
            self.status_bar.showMessage("Đang tải thông tin instances...")
            # In real implementation, would use background thread
            self.status_bar.showMessage("Sẵn sàng")

    def show_automation_dialog(self):
        """Show automation dialog with 10k-optimized defaults"""
        dialog = AutomationDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            params = dialog.get_values()
            instance_count = params[1] - params[0] + 1
            
            # Apply performance optimizations based on count
            config = PerformanceConfig.get_config(instance_count)
            
            # Use optimized worker for large operations
            if instance_count > 1000:
                self.worker = OptimizedAutoWorker(self.manager, params)
                self.log_output.append(f"🚀 Using optimized processing for {instance_count} instances")
            else:
                self.worker = AutoWorker(self.manager, params)
            
            self._connect_worker_signals()
            self.worker.start()
            self.progress_frame.setVisible(True)

    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self, self.mumu_path)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.mumu_path = dialog.get_path()
            self.manager = MumuManager(self.mumu_path)

    def filter_instances(self):
        """Optimized filtering for large datasets"""
        # In real implementation, would use efficient search algorithms
        # for 10k+ instances (indexing, caching, etc.)
        pass

    def pause_operation(self):
        """Pause current operation"""
        if self.worker and self.worker.isRunning():
            self.worker.pause()

    def resume_operation(self):
        """Resume current operation"""
        if self.worker and self.worker.isRunning():
            self.worker.resume()

    def stop_operation(self):
        """Stop current operation"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()

    def _connect_worker_signals(self):
        """Connect worker signals for progress reporting"""
        if self.worker:
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.log.connect(self.log_output.append)
            self.worker.finished.connect(self._on_worker_finished)

    def _on_worker_finished(self, message):
        """Handle worker completion"""
        self.log_output.append(message)
        self.progress_frame.setVisible(False)
        self.status_bar.showMessage("Hoàn thành")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize for 10k instances optimization
    app._widget_count = 0
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())