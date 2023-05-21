import sys
from PyQt5.QtWidgets import QApplication
from app.views.disease_selection import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
