import sys
import views
from PyQt5.QtWidgets import QApplication

app = QApplication([])
app.setStyle("fusion")
window = views.TestUtility()
window.show()
sys.exit(app.exec_())
