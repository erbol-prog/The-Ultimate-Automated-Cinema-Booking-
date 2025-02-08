import sys
from PyQt5.QtGui import QLinearGradient, QColor, QBrush, QPalette, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
                             QHBoxLayout, QFrame, QLabel, QToolButton, QGraphicsDropShadowEffect, QStackedWidget,
                             QGraphicsOpacityEffect)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import (QUrl, Qt, QPropertyAnimation, QPoint, QEvent, QEasingCurve, QRect,
                          QSequentialAnimationGroup, QParallelAnimationGroup, QTimer)


class HoverWidgetMixin:
    def enterEvent(self, event):
        if self.window() and hasattr(self.window(), 'cursor_overlay'):
            self.window().cursor_overlay.onHover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.window() and hasattr(self.window(), 'cursor_overlay'):
            self.window().cursor_overlay.onHover(False)
        super().leaveEvent(event)

class LayoutHForMenu(QHBoxLayout):
    def __init__(self, button, label):
        super().__init__()
        self.label = label
        self.button = button
        self.addWidget(button,Qt.AlignLeft)
        self.addWidget(label)
        self.button.setVisible(False)
        self.label.setVisible(False)
        self.setSpacing(0)


class GlassButton(HoverWidgetMixin, QPushButton):
    def __init__(self, text):
        super().__init__()
        self.setFixedSize(115, 50)
        self.setText(text)
        self.setStyleSheet("""
                    QPushButton{
                        color: white;
                        font-size: 22px;
                        border-bottom: 1px solid rgba(255,0,200,0.4);
                        border-radius: 0px;
                    }
                    QPushButton:hover{
                        border-color: pink
                    }
                    """)

class MenuWidgetButton(HoverWidgetMixin,QToolButton):
    def __init__(self, image=None):
        super().__init__()
        self.setMinimumSize(50,50)
        self.setMaximumSize(55,55)
        if image:
            self.setIcon(QIcon(image))
        self.setStyleSheet("""
                QToolButton {
                    color: #ff00c8;
                    background: rgba(255,0,200,0.3);
                    padding:8px 16px;
                    border-radius:5px;
                    font-weight:500;
                }
                QToolButton:hover {
                    background: rgba(255,10,200,0.9);
                    border-radius: 0px;
                    padding: 10px;
                    margin: -5px;
                }
            """)
        self.highlight_anim = QPropertyAnimation(self, b"geometry")
        self.highlight_anim.setDuration(300)
        self.highlight_anim.setEasingCurve(QEasingCurve.OutBack)
        self.original_geometry = None

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.original_geometry is None:
            self.original_geometry = self.geometry()
        rect = self.geometry()
        new_rect = QRect(rect.x(), rect.y(), rect.width()+5, rect.height()+5)
        self.highlight_anim.stop()
        self.highlight_anim.setStartValue(rect)
        self.highlight_anim.setEndValue(new_rect)
        self.highlight_anim.start()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self.original_geometry is not None:
            self.highlight_anim.stop()
            self.highlight_anim.setStartValue(self.geometry())
            self.highlight_anim.setEndValue(self.original_geometry)
            self.highlight_anim.start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cinema X")
        self.central_widget = QWidget()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setCentralWidget(self.central_widget)
        self.stacked_widget = QStackedWidget()
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.stacked_widget, alignment=Qt.AlignCenter)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('''
                QScrollBar{
                    background: transparent;
                }
                QScrollBar::handle{
                    background: transparent;
                    border-radius: 2px;
                }
        ''')

        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.2, QColor("#141e30"))
        gradient.setColorAt(0.8, QColor("#0f2027"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        self.setFixedSize(1440, 918)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.view = QWebEngineView()
        self.home_url = QUrl("https://erbolsk.pythonanywhere.com")
        self.view.setUrl(self.home_url)
        self.view.setFixedSize(1440,918)

        menu_button = MenuWidgetButton("images/menu_v2.png")
        home_button = MenuWidgetButton("images/home_v2.png")
        back_button = MenuWidgetButton("images/back_v2.png")
        quit_button = MenuWidgetButton("images/quit_v1.png")

        self.menu_show_up = False
        menu_button.pressed.connect(self.menu_expand)
        back_button.pressed.connect(self.view.back)
        home_button.pressed.connect(self.go_to_home)
        quit_button.pressed.connect(lambda : QApplication.quit())

        self.menu = QFrame()
        self.menu.setStyleSheet("""
        QFrame{
            background-color: rgba(0, 0, 0, 0.3);
            border-radius: 15px
        }
        """)

        menu_layout = QVBoxLayout(self.menu)
        menu_label = GlassButton("Menu")
        home_label = GlassButton("Home")
        back_label = GlassButton("Back")
        quit_label = GlassButton("Quit")
        menu_label.pressed.connect(self.menu_expand)
        home_label.pressed.connect(self.go_to_home)
        back_label.pressed.connect(self.view.back)
        quit_label.pressed.connect(lambda : QApplication.quit())

        self.menu_lays = LayoutHForMenu(menu_button, menu_label)
        self.home_lays = LayoutHForMenu(home_button, home_label)
        self.back_lays = LayoutHForMenu(back_button, back_label)
        self.quit_lays = LayoutHForMenu(quit_button, quit_label)
        menu_layout.addLayout(self.menu_lays)
        menu_layout.addLayout(self.home_lays)
        menu_layout.addLayout(self.back_lays)
        menu_layout.addLayout(self.quit_lays)
        menu_button.setVisible(True)
        menu_layout.setSpacing(5)
        menu_layout.setContentsMargins(5,5,5,5)
        menu_layout.setAlignment(Qt.AlignLeft)
        self.menu.resize(60,60)
        self.main_layout.addWidget(self.view)
        self.menu.setParent(self.view)
        self.menu.setMouseTracking(True)
        self.menu.move(20, 50)

        self.enter_page = QWidget()
        self.enter_page.setStyleSheet("background-color: rgba(15, 15, 34, 0.6)")
        layout = QHBoxLayout(self.enter_page)
        logo = QLabel()
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(250,250)
        logo.setStyleSheet("""
            QLabel{
                image:none;
                border-image: url(images/logo_bb.png);
                background-color: transparent;
            }   
        """)
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.69)
        logo.setGraphicsEffect(opacity_effect)
        enter_button = GlassButton("E N T E R")
        enter_widget = QWidget()
        enter_widget.setStyleSheet("""
        background: qlineargradient(
                    spread: pad,
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgb(89, 0, 84),
                    stop: 1 black
                ); border-radius: 15px;
                """)
        enter_widget.setFixedSize(800,600)
        layout.addWidget(enter_widget, alignment=Qt.AlignCenter)
        enter_layout = QVBoxLayout(enter_widget)
        label_cinema = QLabel("AIT-Cinema")
        label_cinema.setFixedSize(300,60)
        label_cinema.setAlignment(Qt.AlignCenter)
        label_cinema.setStyleSheet("""
                        QLabel{
                            color: white; 
                            background-color: rgba(25,0,0,0.2);
                            border-bottom: 2px solid white;
                            font-size: 36px; font-weight: 900;
                        }           
                        """)
        enter_layout.setSpacing(15)
        enter_layout.addWidget(logo, alignment=Qt.AlignCenter)
        enter_layout.addWidget(label_cinema, alignment=Qt.AlignCenter)
        enter_layout.addWidget(enter_button, alignment=Qt.AlignCenter)
        enter_button.setStyleSheet("""
                        QPushButton {
                            image: none;
                            color: white;
                            background: rgba(255,0,200,0.7);
                            padding:8px 16px;
                            border-radius: 10px;
                            font-weight: 900;
                            font-size: 24px;
                        }
                        QPushButton:hover {
                            background: rgba(255,10,200,0.9);
                        }
                    """)
        enter_button.setFixedSize(300,60)
        button_shadow = QGraphicsDropShadowEffect()
        button_shadow.setBlurRadius(100)
        button_shadow.setOffset(0, 10)
        button_shadow.setColor(QColor(245, 53, 170, 255))
        logo_shadow = QGraphicsDropShadowEffect()
        logo_shadow.setBlurRadius(100)
        logo_shadow.setOffset(0, 10)
        logo_shadow.setColor(QColor(245, 53, 170, 255))
        label_shadow = QGraphicsDropShadowEffect()
        label_shadow.setBlurRadius(100)
        label_shadow.setOffset(0, 10)
        label_shadow.setColor(QColor(245, 53, 170, 255))

        enter_button.setGraphicsEffect(button_shadow)
        logo.setGraphicsEffect(logo_shadow)
        label_cinema.setGraphicsEffect(label_shadow)
        enter_button.clicked.connect(self.enter)

        self.stacked_widget.addWidget(self.enter_page)
        self.stacked_widget.addWidget(self.view)
        self.stacked_widget.setCurrentWidget(self.enter_page)
        self.animation = QPropertyAnimation(self.menu, b"geometry")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_background)
        self.timer.start(50)
        self.gradient_position = 0

    def setCurrentIndexAnimated(self, index):
            current_widget = self.currentWidget()
            next_widget = self.widget(index)

            if current_widget == next_widget:
                return
            current_widget.setGeometry(self.geometry())
            next_widget.setGeometry(self.geometry())
            if index > self.currentIndex():
                next_widget.move(self.width(), 0)
            else:  # Slide to the right
                next_widget.move(-self.width(), 0)
            next_widget.show()
            current_animation = QPropertyAnimation(current_widget, b"pos")
            current_animation.setDuration(500)
            current_animation.setEasingCurve(QEasingCurve.InOutQuad)
            current_animation.setStartValue(current_widget.pos())
            current_animation.setEndValue(
                current_widget.pos() + (-self.width() if index > self.currentIndex() else self.width(), 0)
            )

            next_animation = QPropertyAnimation(next_widget, b"pos")
            next_animation.setDuration(500)
            next_animation.setEasingCurve(QEasingCurve.InOutQuad)
            next_animation.setStartValue(next_widget.pos())
            next_animation.setEndValue(self.geometry().topLeft())
            animation_group = QParallelAnimationGroup(self)
            animation_group.addAnimation(current_animation)
            animation_group.addAnimation(next_animation)
            def on_animation_finished():
                self.setCurrentIndex(index)
                next_widget.move(self.geometry().topLeft())

            animation_group.finished.connect(on_animation_finished)
            animation_group.start()

    def update_background(self):
        self.gradient_position = (self.gradient_position + 1) % 100
        self.enter_page.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    spread: pad,
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(39, 0, 54, 205),
                    stop: {self.gradient_position / 100} rgba(89, 0, 84, 205),
                    stop: 1 rgba(3, 10, 28, 205)
                );
            }}
        """)

    def enter(self):
        self.stacked_widget.setCurrentWidget(self.view)

    def menu_expand(self):
        sequential_group = QSequentialAnimationGroup(self)

        intermediate_animation = QPropertyAnimation(self.menu, b"geometry")
        intermediate_animation.setDuration(0)
        intermediate_animation.setEasingCurve(QEasingCurve.InOutQuad)
        original_geometry = self.menu.geometry()
        intermediate_geometry = QRect(self.menu.geometry().x(),self.menu.geometry().y(),60, 220)
        intermediate_animation.setStartValue(original_geometry)
        intermediate_animation.setEndValue(intermediate_geometry)

        full_animation = QPropertyAnimation(self.menu, b"geometry")
        full_animation.setDuration(500)
        full_animation.setEasingCurve(QEasingCurve.InOutQuad)
        full_geometry = QRect(self.menu.geometry().x(),self.menu.geometry().y(),170, 220)
        full_animation.setStartValue(intermediate_geometry)
        full_animation.setEndValue(full_geometry)

        if self.menu_show_up:
            full_animation.setStartValue(self.menu.geometry())
            full_animation.setEndValue(intermediate_geometry)
            intermediate_animation.setDirection(QPropertyAnimation.Backward)
            for label in [self.menu_lays.label, self.home_lays.label, self.back_lays.label, self.quit_lays.label]:
                label.setVisible(False)
            sequential_group.addAnimation(full_animation)
            sequential_group.addAnimation(intermediate_animation)
            self.menu_show_up = False
            sequential_group.start()
            sequential_group.finished.connect(lambda : self.menu.setGraphicsEffect(None))

        else:
            sequential_group.addAnimation(intermediate_animation)
            self.menu_show_up = True
            for button in [self.home_lays.button, self.back_lays.button, self.quit_lays.button]:
                button.setVisible(True)
            for label in [self.menu_lays.label, self.home_lays.label, self.back_lays.label, self.quit_lays.label]:
                label.setVisible(True)
            sequential_group.addAnimation(full_animation)
            sequential_group.start()
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(30)
            shadow.setOffset(0, 0)
            shadow.setColor(QColor(245, 53, 170, 89))
            self.menu.setGraphicsEffect(shadow)

    def go_to_home(self):
        self.view.setUrl(self.home_url)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            pos = self.mapFromGlobal(event.globalPos())
            self.cursor_overlay.moveCursor(pos)
        if event.type() == event.MouseButtonPress:
            if self.isVisible():
                if not self.geometry().contains(event.globalPos()):
                    self.hide()
        return super(MainWindow, self).eventFilter(obj, event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.cursor_overlay.moveCursor(event.pos())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    if window.isHidden():
        sys.exit(app.exec_())
    sys.exit(app.exec_())
