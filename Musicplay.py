import sys
import threading
from os.path import expanduser
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
#from pydub import AudioSegment
import acrcloud
import CameraCap

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.parent = parent
        self.setWindowFlag(Qt.FramelessWindowHint)

        # for handling title_bar movement
        self.start = QPoint(0, 0)
        self.pressing = False

        # for controlling camera
        self.cam_detect = False
        self.capturing = False

        # creates player and playlist
        self.player = QMediaPlayer()
        self.currentPlaylist = QMediaPlaylist()

        # 0- stopped, 1- playing 2-paused
        self.userAction = -1

        self.player.mediaStatusChanged.connect(self.player_mediaStatusChanged)
        self.player.stateChanged.connect(self.player_stateChanged)
        self.player.positionChanged.connect(self.player_positionChanged)
        self.player.volumeChanged.connect(self.player_volumeChanged)

        # creates UI
        self.player_ui()

    def player_ui(self):
        uic.loadUi("mainwindow.ui", self)
        self.pause_btn.hide()
        self.play_btn.show()
        self.set_connection()
        self.show()

    def set_connection(self):
        self.add_acr.clicked.connect(self.open_acr_file)
        self.add_btn.clicked.connect(self.openFile)
        self.vol_slider.valueChanged.connect(self.changeVolume)
        self.vol_slider.setValue(100)
        self.seek_slider.sliderMoved.connect(self.seekPosition)
        self.play_btn.clicked.connect(self.playHandler)
        self.pause_btn.clicked.connect(self.pauseHandler)
        self.rewind_btn.clicked.connect(self.prev_playlist_item)
        self.forward_btn.clicked.connect(self.next_playlist_item)
        self.close_btn.clicked.connect(self.close_player)
        self.minimize_btn.clicked.connect(self.minimize_player)
        self.maximize_btn.clicked.connect(self.maximize_player)
        self.camera_btn.clicked.connect(self.camera_capture)

    # def resizeEvent(self, QResizeEvent):
    #     super(MyBar, self).resizeEvent(QResizeEvent)
    #     self.title.setFixedWidth(self.parent.width())

    def camdetect(self):
            while self.cam_detect:
                if self.cap.pause:
                    self.pauseHandler()
                    self.cap.pause = False
                elif self.cap.play:
                    self.playHandler()
                    self.cap.play = False

    def camera_capture(self):
        if not self.capturing:
            self.capturing = True
            self.cam_detect = True
            self.cap = CameraCap.CameraCap()
            self.cap.cam_capture = True
            self.cap.camera()
            threading.Thread(target=self.cap.detect).start()
            threading.Thread(target=self.camdetect).start()
        elif self.capturing:
            self.capturing = False
            self.cam_detect = False
            self.cap.cam_capture = False
            self.cap.cam_close()


    def mousePressEvent(self, event):
        self.start = self.title_bar.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.title_bar.mapToGlobal(event.pos())
            self.movement = self.end - self.start
            self.setGeometry(self.mapToGlobal(self.movement).x(), self.mapToGlobal(self.movement).y(), self.width(), self.height())
            self.start = self.end

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False

    def close_player(self):
        self.closeEvent(self.close)

    def maximize_player(self):
        QMessageBox.warning(QMessageBox(), "SORRY", "Under Construction")

    def minimize_player(self):
        self.showMinimized()

    def acr(self):
        start_min = 0
        start_sec = 0

        end_min = 0
        end_sec = 5

        # Time to milliseconds
        start_time = start_min * 60 * 1000 + start_sec * 1000
        end_time = end_min * 60 * 1000 + end_sec * 1000
        config = {
            'key': 'ADD YOUR ARP API KEY HERE',
            'secret': 'ADD YOUR ARP API SECRET HERE',
            'host': 'ADD ARD HOST URL',

        }
        file = "r.mp3"
        audio = acrcloud.recognizer(config, file)
        self.acr1.setText(str(audio['metadata']['music'][0]['external_metadata']['spotify']['album']['name']))
        self.acr2.setText(str(audio['metadata']['music'][0]['external_metadata']['spotify']['artists'][0]['name']))

    def playHandler(self):
        self.userAction = 1
        if self.player.state() == QMediaPlayer.StoppedState:
            if self.player.mediaStatus() == QMediaPlayer.NoMedia:
                if self.currentPlaylist.mediaCount() == 0:
                    self.openFile()
                if self.currentPlaylist.mediaCount() != 0:
                    self.play_btn.hide()
                    self.pause_btn.show()
                    self.player.setPlaylist(self.currentPlaylist)
            elif self.player.mediaStatus() == QMediaPlayer.LoadedMedia:
                self.play_btn.hide()
                self.pause_btn.show()
                self.player.play()
            elif self.player.mediaStatus() == QMediaPlayer.BufferedMedia:
                self.play_btn.hide()
                self.pause_btn.show()
                self.player.play()
        elif self.player.state() == QMediaPlayer.PlayingState:
            pass
        elif self.player.state() == QMediaPlayer.PausedState:
            self.play_btn.hide()
            self.pause_btn.show()
            self.player.play()

    def pauseHandler(self):
        self.userAction = 2
        self.play_btn.show()
        self.pause_btn.hide()
        self.player.pause()

    def stopHandler(self):
        self.userAction = 0
        if self.player.state() == QMediaPlayer.PlayingState:
            self.stopState = True
            self.player.stop()
        elif self.player.state() == QMediaPlayer.PausedState:
            self.player.stop()
        elif self.player.state() == QMediaPlayer.StoppedState:
            pass

    def player_mediaStatusChanged(self):
        if self.player.mediaStatus() == QMediaPlayer.LoadedMedia and self.userAction == 1:
            song_duration = self.player.duration()
            self.displaySongInfo()
            self.seek_slider.setRange(0, song_duration)
            self.song_duration.setText(
                '%d:%02d' % (int(song_duration / 60000), int((song_duration / 1000) % 60)))
            self.player.play()

    def player_stateChanged(self):
        if self.player.state() == QMediaPlayer.StoppedState:
            self.player.stop()

    def player_positionChanged(self, position, senderType=False):
        if senderType == False:
            self.seek_slider.setValue(position)
        # update the text label
        self.song_elapsed_time.setText('%d:%02d' % (int(position / 60000), int((position / 1000) % 60)))

    def seekPosition(self, position):
        sender = self.sender()
        if isinstance(sender, QSlider):
            if self.player.isSeekable():
                self.player.setPosition(position)

    def player_volumeChanged(self):
        pass

    def changeVolume(self, value):
        self.player.setVolume(value)

    def increaseVolume(self):
        vol = self.player.volume()
        vol = min(vol + 5, 100)
        self.player.setVolume(vol)

    def decreaseVolume(self):
        vol = self.player.volume()
        vol = max(vol - 5, 0)
        self.player.setVolume(vol)

    def open_acr_file(self):
        fileChoosen = QFileDialog.getOpenFileUrl(self, 'Open Music File for audio recognition', expanduser('~'), 'Audio (*.mp3 *.ogg *.wav)',
                                                 '*.mp3 *.ogg *.wav')
        print(fileChoosen)
        if fileChoosen != None:
            self.acr()

    def openFile(self):
        fileChoosen = QFileDialog.getOpenFileUrl(self, 'Open Music File', expanduser('~'), 'Audio (*.mp3 *.ogg *.wav)',
                                                 '*.mp3 *.ogg *.wav')
        if fileChoosen != None:
            self.currentPlaylist.addMedia(QMediaContent(fileChoosen[0]))

    def addFiles(self):
        folderChoosen = QFileDialog.getExistingDirectory(self, 'Open Music Folder', expanduser('~'))
        if folderChoosen != None:
            it = QDirIterator(folderChoosen)
            it.next()
            while it.hasNext():
                if it.fileInfo().isDir() == False and it.filePath() != '.':
                    fInfo = it.fileInfo()
                    print(it.filePath(), fInfo.suffix())
                    if fInfo.suffix() in ('mp3', 'ogg', 'wav'):
                        print('added file ', fInfo.fileName())
                        self.currentPlaylist.addMedia(QMediaContent(QUrl.fromLocalFile(it.filePath())))
                it.next()

    def displaySongInfo(self):
        meta_data_key_list = self.player.availableMetaData()
        song_year = self.player.metaData(meta_data_key_list[13])
        song_author = self.player.metaData(meta_data_key_list[3])
        thumbnail_image = self.player.metaData(meta_data_key_list[11])
        song_title = self.player.metaData(meta_data_key_list[12])
        self.song_name.setText(str(song_title))
        self.author_name.setText(str(song_author[0]))
        self.year.setText(str(song_year))
        self.thumbnail.setPixmap(QPixmap.fromImage(thumbnail_image))

    def prev_playlist_item(self):
        self.player.playlist().previous()

    def next_playlist_item(self):
        self.player.playlist().next()


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', 'Pres Yes to Close.', QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.player.stop()
            qApp.quit()
        else:
            try:
                event.ignore()
            except AttributeError:
                pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
