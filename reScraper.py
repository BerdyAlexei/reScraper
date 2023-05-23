import requests, requests_html, urllib, bs4, pandas, json, pathlib, os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QFont,QFontDatabase, QPalette, QIcon, QIntValidator
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QPoint
from PyQt5.QtWidgets import QComboBox, QCheckBox, QLabel, QLineEdit, QPushButton, QPlainTextEdit, QTextEdit

# Made by Alejandro Morales Jaime (also known as Berdy Alexei). (づ￣ 3￣)づ

class RWidgets():
    def __init__(self):
        pass

    @staticmethod
    def configBasic(widget, x, y, width, height, text, style, cursor):
        widget.move(x, y)
        widget.setFixedSize(width, height)
        if cursor:
            widget.setCursor(cursor)
        widget.setPlaceholderText(text) if (isinstance(widget, QComboBox) or isinstance(widget, QPlainTextEdit)) else widget.setText(text)

        try:
            widget.setStyleSheet(pathlib.Path(style).read_text())
        except:
            pass

    class RPushButton(QPushButton):
        def __init__(self, x, y, width, height, text, style, cursor, *args, **kwargs):
            super().__init__(*args, **kwargs)
            RWidgets.configBasic(self, x, y, width, height, text, style, cursor)

    class RCheckBox(QCheckBox):
        def __init__(self, x, y, width, height, text, style, cursor, *args, **kwargs):
            super().__init__(*args, **kwargs)
            RWidgets.configBasic(self, x, y, width, height, text, style, cursor)

    class RTextEdit(QTextEdit):
        def __init__(self, x, y, width, height, text, style, cursor, *args, **kwargs):
            super().__init__(*args, **kwargs)
            RWidgets.configBasic(self, x, y, width, height, text, style, cursor)

    class RLineEdit(QLineEdit):
        def __init__(self, x, y, width, height, text, style, cursor, *args, **kwargs):
            super().__init__(*args, **kwargs)
            RWidgets.configBasic(self, x, y, width, height, text, style, cursor)

    class SLineEdit(QLineEdit):
        clicked = pyqtSignal()
        def __init__(self, x, y, width, height, text, style, cursor, *args, **kwargs):
            super().__init__(*args, **kwargs)
            RWidgets.configBasic(self, x, y, width, height, text, style, cursor)

        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton: self.clicked.emit()
            else: super().mousePressEvent(event)

    class RComboBox(QComboBox):
        def __init__(self, x, y, width, height, text, style, cursor, *args, **kwargs):
            super().__init__(*args, **kwargs)
            RWidgets.configBasic(self, x, y, width, height, text, style, cursor)

    class RPlainTextEdit(QPlainTextEdit):
        def __init__(self, x, y, width, height, text, style, cursor, *args, **kwargs):
            super().__init__(*args, **kwargs)
            RWidgets.configBasic(self, x, y, width, height, text, style, cursor)

    class RLabel(QLabel):
        def __init__(self, x, y, width, height, text, style, cursor, *args, **kwargs):
            super().__init__(*args, **kwargs)
            RWidgets.configBasic(self, x, y, width, height, text, style, cursor)

class reScraper(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(352, 256)
        self.setWindowTitle('reScraper')
        self.setWindowIcon(QIcon('./data/resources/reScraper.ico'))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        with open('./data/data.json','r', encoding='utf-8') as f:
            self.data=json.load(f)
        
        with open(f'./data/lang/{self.data["lang"]}.json','r') as f:
            self.lang=json.load(f)

        self.enabled = True

        self.searchText = RWidgets.RLineEdit(16, 16, 320, 32, 'Jass Design Group', None, None)
        self.engineSelect = RWidgets.RComboBox(16, 64, 160, 32, None, None, Qt.PointingHandCursor)
        
        self.pageFrom = RWidgets.RLineEdit(192, 64, 64, 32, '1', None, None)
        self.pageFrom.setValidator(QIntValidator(0, 99, self))
        self.pageTo = RWidgets.RLineEdit(272, 64, 64, 32, '16', None, None)
        self.pageTo.setValidator(QIntValidator(0, 99, self))

        self.addKeyword = RWidgets.RLineEdit(16, 112, 320, 32, self.lang['copyRight'], None, None)

        self.startSearch = RWidgets.RPushButton(16, 160, 152, 32, self.lang['startSearch'], None, Qt.PointingHandCursor)
        self.closeApplication = RWidgets.RPushButton(184, 160,  152, 32, self.lang['closeApplication'], None, Qt.PointingHandCursor)

        self.loadBar = QtWidgets.QProgressBar()
        self.loadBar.setFixedHeight(32)
        self.loadBar.setFixedWidth(320)
        self.loadBar.setFormat(None)
        self.loadBar.move(16, 208)
        self.loadText = RWidgets.RLabel(16, 208, 320, 32, None, None, None)
        

        for widget, toolTip in {
            self.searchText : self.lang['toolTip']['searchText'],
            self.engineSelect : self.lang['toolTip']['engineSelect'],
            self.pageFrom : self.lang['toolTip']['pageFrom'],
            self.pageTo : self.lang['toolTip']['pageTo'],
            self.addKeyword : self.lang['toolTip']['addKeyword']

        }.items():
            widget.setToolTip(toolTip)

        for widget in [
            self.searchText,
            self.pageFrom,
            self.pageTo,
            self.addKeyword,
            self.loadText

        ]:
            widget.setAlignment(QtCore.Qt.AlignCenter)

        for index, item in enumerate([
            'Bing',
            'Google',
            'Yahoo!'
        ]):
            self.engineSelect.addItem(item)
            self.engineSelect.setItemIcon(
                index, 
                QIcon(
                    self.data['folder']['resources']
                     + item
                     + '.ico' 
                    )
            )

        for widget in [
            self.searchText,
            self.engineSelect,
            self.pageFrom,
            self.pageTo,
            self.addKeyword,
            self.startSearch,
            self.closeApplication,
            self.loadBar,
            self.loadText

        ]:
            self.layout().addWidget(widget)

        def loadBar():
            self.loadBar.setMaximum(0)
            self.loadBar.setValue(1)

        def enable():
            if (
                self.searchText.text()
                and self.pageFrom.text()
                and self.pageTo.text()
                and self.enabled == True
            ):
                self.startSearch.setEnabled(True)

            else:
                self.startSearch.setDisabled(True)
            
        def start():
            engine = self.engineSelect.currentIndex()

            fileJSON = './temp/temp.json'
            fileXLSX = './output/{}All.xlsx'.format(self.engineSelect.currentText().lower())
            fileSORT = './output/{}Sort.xlsx'.format(self.engineSelect.currentText().lower())

            start = int(self.pageFrom.text()) - 1
            if start < 0:
                start = 0

            end = int(self.pageTo.text())
            if end <= start:
                end = (start + 1)

            text = self.searchText.text()
            keyword = self.addKeyword.text().split(',')
            keyword.append(text)

            _thread(engine, text, start, end, fileJSON, fileXLSX, fileSORT, keyword)

        def _enable(bool):
            self.startSearch.setDisabled(True)

            if bool:
                self.startSearch.setEnabled

            self.enabled = bool

            loadBar()
            enable()
            
            

        def _thread(engine, text, start, end, fileJSON, fileXLSX, fileSORT, keyword):
            _enable(False)
            
            self.thread = searchThread(engine, text, start, end, fileJSON, fileXLSX, fileSORT, keyword)

            self.thread.enable.connect(lambda: _enable(True))
            self.thread.loadMaximum.connect(lambda value: self.loadBar.setMaximum(value))
            self.thread.loadValue.connect(lambda value: self.loadBar.setValue(value + 1))
            self.thread.loadText.connect(lambda string: self.loadText.setText(string))

            self.thread.start()
       
        for widget in [
            self.searchText,
            self.pageFrom,
            self.pageTo
        ]:
            widget.textChanged.connect(lambda: enable())

        self.startSearch.clicked.connect(lambda: start())
        self.closeApplication.clicked.connect(lambda: QtWidgets.QApplication.quit())

        loadBar()


    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
        super(reScraper, self).mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.pos() + delta)
        self.oldPos = event.globalPos()
        super(reScraper, self).mouseMoveEvent(event)

class searchThread(QThread):
    enable = pyqtSignal()
    loadMaximum = pyqtSignal(int)
    loadValue = pyqtSignal(int)
    loadText = pyqtSignal(str)

    def __init__(self, engine, text, start, end, fileJSON, fileXLSX, fileSORT, keyword):
        super().__init__()
        self.engine = engine
        self.text = text
        self.pageFrom = start
        self.pageTo = end
        self.fileJSON = fileJSON
        self.fileXLSX = fileXLSX
        self.fileSORT = fileSORT
        self.keyword = keyword

    def json2xlsx(self, data, fileJSON, fileXLSX, fileSORT, keyword):
        def JSONtoXLSX(fileJSON, fileXLSX):
            set = pandas.read_json(fileJSON)
            set.to_excel(fileXLSX, index = False)

        def sort(fileXLSX, fileSORT, keyword):
            set = pandas.read_excel(fileXLSX)
            sort = set[~set.apply(lambda row: all(palabra not in str(row) for palabra in keyword), axis = 1)]

            sort.to_excel(fileSORT, index = False)

            save(None)

        def save(data):
            with open(fileJSON, 'w') as f:
                json.dump(data, f, indent = 4)

        save(data)
        JSONtoXLSX(fileJSON, fileXLSX)
        sort(fileXLSX, fileSORT, keyword)

        self.enable.emit()
        self.loadText.emit(None)
        os.system('start output')

    def bing(self, search, start, end, fileJSON, fileXLSX, fileSORT, keyword):
        results = []
        search = search.replace(' ', '+')

        self.loadMaximum.emit(end)
        for i in range(start, end, 1):
            self.loadValue.emit(i)

            data = bs4.BeautifulSoup(
                requests.get(
                    'https://www.bing.com/search?q={}&rdr=1&first={}'.format(search, i+1),
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
                    }
                ).text,
                'html.parser'
            )

            completeData = data.find_all('li', {'class': 'b_algo'})

            for item in completeData:
                result = {}
                result['Title'] = item.find('a').text
                result['link'] = item.find('a').get('href')
                result['Description'] = item.find('div', {'class': 'b_caption'}).text
                results.append(result)
                
                self.loadText.emit(str(result['Title']))
        
        self.json2xlsx(results, fileJSON, fileXLSX, fileSORT, keyword)
    
    def google(self, text, start, end, fileJSON, fileXLSX, fileSORT, keyword):
        def search(text, start, end):
            results = []

            self.loadText.emit('···')
            self.loadMaximum.emit(end)
            for page in range(start, (end + 1)):
                self.loadValue.emit(page)

                results.extend(parse(response(text, page)))

            return results
        
        def parse(response):
            identifierTitle     = 'h3'
            identifierResult    = '.tF2Cxc'
            identifierText      = '.VwiC3b'
            identifierLink      = '.yuRUbf a'

            results = response.html.find(identifierResult)
            output = []

            for result in results:
                elementTitle    = result.find(identifierTitle, first = True)
                elementLink     = result.find(identifierLink, first = True)
                elementText     = result.find(identifierText, first = True)

                if elementTitle is not None and elementLink is not None and elementText is not None:
                    item = {
                        'title': elementTitle.text,
                        'link': elementLink.attrs['href'],
                        'text': elementText.text
                    }

                    output.append(item)
            
            return output
        
        def response(text, page):
            query = urllib.parse.quote_plus(text)
            index = (page - 1) * 10

            url = f'http://www.google.co.uk/search?q={query}&start={index}'
            response = get(url)

            return response
        
        
        def get(url):
            try:
                session = requests_html.HTMLSession()
                response = session.get(url, verify = False)

                return response

            except requests.exceptions.RequestException:
                pass
        
        self.json2xlsx(search(text, start, end), fileJSON, fileXLSX, fileSORT, keyword)

    def yahoo(self, search, start, end, fileJSON, fileXLSX, fileSORT, keyword):
        results = []
    
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
        }
        
        self.loadMaximum.emit(end)
        for page in range(start, end + 1):
            self.loadValue.emit(page)

            url = f'https://search.yahoo.com/search?p={search}&b={page * 10}'
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = bs4.BeautifulSoup(response.text, 'html.parser')
            
            search_results = soup.select('.algo-sr')
            
            for result in search_results:
                title = result.select_one('.title a').text
                link = result.select_one('.title a')['href']
                description = result.select_one('.compText').text
                
                results.append({
                    'title': title,
                    'link': link,
                    'description': description
                })

                self.loadText.emit(title)
    
        self.json2xlsx(results, fileJSON, fileXLSX, fileSORT, keyword)


    def run(self):
        if self.engine == 0:
            self.bing(self.text, self.pageFrom, self.pageTo, self.fileJSON, self.fileXLSX, self.fileSORT, self.keyword)

        elif self.engine == 1:
            self.google(self.text, self.pageFrom, self.pageTo, self.fileJSON, self.fileXLSX, self.fileSORT, self.keyword)

        elif self.engine == 2:
            self.yahoo(self.text, self.pageFrom, self.pageTo, self.fileJSON, self.fileXLSX, self.fileSORT, self.keyword)

if __name__ == '__main__':
    application = QtWidgets.QApplication([])
    application.setPalette(QPalette())
    application.setStyleSheet(pathlib.Path('data/resources/css/main.css').read_text())
    application.setFont(QFont(QFontDatabase.applicationFontFamilies(QFontDatabase.addApplicationFont('./data/resources/fonts/SometypeMono-Regular.ttf'))[0], 10))

    mainWindow = reScraper()
    mainWindow.show()

    application.exec_()