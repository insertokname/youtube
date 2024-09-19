import sys
import PyQt5.QtWidgets as qt
import gui

if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    window = gui.MainWidget()
    window.show()
    sys.exit(app.exec_())
