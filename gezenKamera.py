import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap
import cv2

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Pencere ayarları
        self.setWindowTitle("PyQt Kamera")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Kamera başlatma
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Kamera açılamadı!")
            sys.exit()
            
        # Görüntü etiketi
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)
        
        # Timer ile kameradan görüntü al
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        
        # Boyutlandırma ayarları
        self.edge_margin = 10
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.resize_start_pos = QPoint()
        self.resize_start_geometry = QRect()
        
        # Başlangıç boyutu
        self.resize(320, 240)
        self.setMinimumSize(320, 240)
    
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.width(), self.height()))
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(q_img))
    
    def get_resize_edge(self, pos):
        """Hangi kenardan boyutlandırma yapıldığını tespit eder"""
        rect = self.rect()
        if pos.x() <= self.edge_margin:  # Sol kenar
            return 'left'
        elif pos.x() >= rect.width() - self.edge_margin:  # Sağ kenar
            return 'right'
        elif pos.y() <= self.edge_margin:  # Üst kenar
            return 'top'
        elif pos.y() >= rect.height() - self.edge_margin:  # Alt kenar
            return 'bottom'
        return None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edge = self.get_resize_edge(event.pos())
            if edge:
                self.resizing = True
                self.resize_edge = edge
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
            else:
                self.dragging = True
                self.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        screen_rect = QApplication.desktop().availableGeometry()
        
        if self.dragging:
            new_pos = event.globalPos() - self.offset
            # Ekran sınırlarını kontrol et
            new_pos.setX(max(screen_rect.left(), min(new_pos.x(), screen_rect.right() - self.width())))
            new_pos.setY(max(screen_rect.top(), min(new_pos.y(), screen_rect.bottom() - self.height())))
            self.move(new_pos)
        
        elif self.resizing and self.resize_edge:
            delta = event.globalPos() - self.resize_start_pos
            new_geom = QRect(self.resize_start_geometry)
            
            if self.resize_edge == 'left':
                new_left = min(new_geom.left() + delta.x(), new_geom.right() - self.minimumWidth())
                new_geom.setLeft(max(screen_rect.left(), new_left))
            elif self.resize_edge == 'right':
                new_right = min(screen_rect.right(), new_geom.right() + delta.x())
                new_geom.setRight(max(new_geom.left() + self.minimumWidth(), new_right))
            elif self.resize_edge == 'top':
                new_top = min(new_geom.top() + delta.y(), new_geom.bottom() - self.minimumHeight())
                new_geom.setTop(max(screen_rect.top(), new_top))
            elif self.resize_edge == 'bottom':
                new_bottom = min(screen_rect.bottom(), new_geom.bottom() + delta.y())
                new_geom.setBottom(max(new_geom.top() + self.minimumHeight(), new_bottom))
            
            self.setGeometry(new_geom)
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
    
    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())