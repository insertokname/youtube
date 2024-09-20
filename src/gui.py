from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal

import os
import cache
import parsing
import pytubefix as pt

class DragAndDropWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag and Drop")
        self.resize(720, 480)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            print(f)



class DownloadThread(QThread):
    update_text = pyqtSignal(str)
    finished_download = pyqtSignal(list)

    def __init__(self, links, videoCache, videosFolder):
        super().__init__()
        self.links = links
        self.videoCache = videoCache
        self.videosFolder = videosFolder

    def run(self):
        # This code will be run in the worker thread
        error_links = []
        for link in self.links:
            try:
                pt.YouTube(link).streams.get_highest_resolution(progressive=True).download(self.videosFolder)
                self.update_text.emit(f"downloading:   {link}")  # Emit signal to update GUI
                self.videoCache.update_cache([link])
            except Exception as e:
                error_links.append(link)
                self.update_text.emit(f"Couldn't download video: {link}\nError: {e}\nSkipping!")
        self.update_text.emit("Finished downloading!")
        self.finished_download.emit(error_links)

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Layout setup
        layout = QtWidgets.QVBoxLayout()

        # select videos folder
        self.videoButton = QtWidgets.QPushButton('Select Videos Folder', self)
        self.videoButton.clicked.connect(self.openFolderDialog)
        layout.addWidget(self.videoButton)

        # select message file
        self.messageButton = QtWidgets.QPushButton('Select Message File', self)
        self.messageButton.clicked.connect(self.openFileDialog)
        self.messageButton.setVisible(False)
        layout.addWidget(self.messageButton)

        # Text area to display file contents
        self.textEdit = QtWidgets.QTextBrowser(self)
        self.textEdit.setVisible(False)
        layout.addWidget(self.textEdit)

        self.downloadVideoButton = QtWidgets.QPushButton('Download New Videos', self)
        self.downloadVideoButton.setVisible(False) 
        self.downloadVideoButton.clicked.connect(self.downloadVideos)
        layout.addWidget(self.downloadVideoButton)

        self.decisionHbox = QtWidgets.QHBoxLayout()
        self.decisionButtonIgnore = QtWidgets.QPushButton("Ignore in future", self)
        self.decisionButtonIgnore.setVisible(False)
        self.decisionButtonIgnore.clicked.connect(self.ignoreVideos)
        self.decisionButtonRetry = QtWidgets.QPushButton("Retry now", self)
        self.decisionButtonRetry.setVisible(False)        
        self.decisionButtonRetry.clicked.connect(self.retryDownload)
        self.decisionHbox.addWidget(self.decisionButtonIgnore)
        self.decisionHbox.addWidget(self.decisionButtonRetry)
        layout.addLayout(self.decisionHbox)

        self.setLayout(layout)
        self.setWindowTitle('Video Downloader')
        self.setGeometry(200, 500, 800, 700)

    def openFileDialog(self):
        # Open a file dialog to select a text file
        options = QtWidgets.QFileDialog.Options()
        fileName, _ =QtWidgets.QFileDialog.getOpenFileName(self, "Select a Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if fileName:
            self.openMessages(fileName)
        
    def openFolderDialog(self):
        # Open a file dialog to select a text file
        options = QtWidgets.QFileDialog.Options()
        folderName =QtWidgets.QFileDialog.getExistingDirectory(self, "Select Videos Folder ", options=options)
        
        if folderName:
            self.videosFolder = folderName
            self.videoCache = cache.Cache(os.path.join(folderName, "video_cache.pkl"))
            self.messageButton.setVisible(True)
            self.textEdit.setVisible(False)
            self.textEdit.setText("")
            self.downloadVideoButton.setVisible(False)
            self.new_links = []

    def openMessages(self, filename: str):
        try:    
            with open(filename,'r',encoding="utf8") as file:
                data = file.read()
                links = parsing.find_links_str(data)
                self.new_links = self.videoCache.find_new_strings(links)
                self.textEdit.setVisible(True)
                if len(self.new_links) == 0:
                    self.textEdit.setText("No new videos!")
                else:
                    self.textEdit.setText(f"New videos:\n{'\n'.join(self.new_links)}")
                    self.downloadVideoButton.setVisible(True)
        except Exception as e:
            print(f"couldn't open file: {filename}!\nGot error: {e}")

    def downloadVideos(self):
        self.textEdit.setText("Downloading...")
        self.thread = DownloadThread(self.new_links, self.videoCache, self.videosFolder)
        self.thread.update_text.connect(self.updateText)
        self.thread.finished_download.connect(self.finishedUpdate)
        self.thread.start() 

    def updateText(self, text):
        self.textEdit.append(text)
    
    def finishedUpdate(self, error_links):
        self.new_links = error_links
        if len(error_links)>0:
            self.textEdit.append("Some links couldn't be downloaded!\nTry again downloading or ignore them in the future?")
            self.decisionButtonIgnore.setVisible(True)
            self.decisionButtonRetry.setVisible(True)
        self.downloadVideoButton.setVisible(False)

    def ignoreVideos(self):
        self.videoCache.update_cache(self.new_links)
        self.textEdit.append("Ignored errored videos!")
        self.decisionButtonIgnore.setVisible(False)
        self.decisionButtonRetry.setVisible(False)

    def retryDownload(self):
        self.textEdit.append("Attempting download again...")
        self.thread = DownloadThread(self.new_links, self.videoCache, self.videosFolder)
        self.thread.update_text.connect(self.updateText)
        self.thread.finished_download.connect(self.finishedUpdate)
        self.thread.start() 