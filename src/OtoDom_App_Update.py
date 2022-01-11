import sys
from OtoDomScraping import *
from OtoDom_Models import *
from PySide6.QtCore import *
from PySide6.QtWidgets import  *
from datetime import datetime
import unicodedata

# the main class
class App(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setFixedSize(430, 380)
        self.setWindowTitle('Oto Dom Web Scraping')
        self.statusBar().showMessage('')
        self.setStyleSheet('Fusion')

        # Timer which changes value (every 0.5sec) status_Bar
        self.timer = QTimer()
        self.timer.timeout.connect(self.Clock)  # clock
        self.timer.start(500)
        self.table_widget = MyTableWidget()
        self.setCentralWidget(self.table_widget)
        self.show()
    # Clock
    def Clock(self):
        now = datetime.now()
        formatData = now.strftime('%H:%M:%S  %d-%m-%y')
        self.statusBar().showMessage(formatData)

    # Exit program after pressing ESC
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

# the class includes button, layout and other widgets
class MyTableWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.Load_places_from_csv() # load from  csv files all polish city, town ,etc
        self.Load_Mongo() # load from Mongodb all places scraped before
        self.layout = QGridLayout()# create Layout
        self.path= ''
        self.progres = 100


#-------------------- create tabs------------------------------------------------------------------
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        # Add tabs
        self.tabs.addTab(self.tab1, "Web Scsraping")
        self.tabs.addTab(self.tab2, "Machine learning")
        self.tabs.addTab(self.tab3, "Tool Predict")

#-----------EditLine and ComboBox------------------------------------------------------------------
        completer = QCompleter(self.LISTA)
        self.city = QLineEdit(self)
        self.city.setCompleter(completer)
        self.city.setPlaceholderText("Enter place")
        self.city_predict = QComboBox(self)
        self.city_predict.addItems(self.data_predict)
        self.city_predict.setPlaceholderText("Choose place")
        self.distans_to_centrum = QLineEdit(self)
        self.distans_to_centrum.setPlaceholderText("Enter distans to city centrum")
        self.enter_area = QLineEdit(self)
        self.enter_area.setPlaceholderText("Enter area of flat")
        self.Year_of_build = QLineEdit(self)
        self.Year_of_build.setPlaceholderText("Year of build")
        self.rooms = QLineEdit(self)
        self.rooms.setPlaceholderText("Rooms")
        self.level = QLineEdit(self)
        self.level.setPlaceholderText("level")
        self.level_in_block = QLineEdit(self)
        self.level_in_block.setPlaceholderText("Level in Block")
        self.type_maret = QComboBox(self)
        self.type_maret.addItems(['pierwotny', 'wtórny'])
        self.heading = QComboBox(self)
        self.heading.addItems(['gazowe', 'elektryczne', 'kotłowe' , 'miejskie' , 'piec kaflowy' , 'inne' ])
        self.type_building = QComboBox(self)
        self.type_building.addItems(['apartamentowiec', 'blok', 'dom wolnostojący' , 'kamienica' , 'szeregowiec' , 'loft' , 'plomba'])
        self.condition = QComboBox(self)
        self.condition.addItems(['do remontu', 'do wykończenia' , '  '])
        self.distance = QComboBox(self)
        self.distance.addItems(['0 km', '+ 5 km', '+ 10 km', '+ 15 km', '+ 25 km', '+ 50 km', '+ 70 km'])
        self.type = QComboBox(self)
        self.type.addItems(['mieszkanie', 'dom', 'dzialka'])
        self.form_of_the_property = QComboBox(self)
        self.form_of_the_property.addItems(['pełna własność', 'spółdzielcze wł z KW', 'spółdzielcze własnościowe' , 'udział'])
        self.text = QLineEdit(self)
        self.text.setText(os.getcwd())
        self.price_min = QLineEdit(self)
        self.price_min.setPlaceholderText("Enter min price (PLN)")
        self.price_max = QLineEdit(self)
        self.price_max.setPlaceholderText("Enter max price (PLN)")
        self.area_min = QLineEdit(self)
        self.area_min.setPlaceholderText("Enter min area (m²) ")
        self.area_max = QLineEdit(self)
        self.area_max.setPlaceholderText("Enter max area (m²) ")
        self.DataSet_Mongo = QComboBox()
        self.DataSet_Mongo.setFixedSize(390,25)
        self.DataSet_Mongo.addItems(self.data)

#-----------QPushButton----------------------------------------------------------------------------
        self.Start_Scraping = QPushButton('Start Scraping', self)
        self.Start_Scraping.clicked.connect(self.Start_Scraping_funck)
        self.Start_Scraping.setDisabled(True)
        self.Save_as = QPushButton('Save', self)
        # self.Save_as.setStyleSheet("background-color: rgb(25, 25, 25); color: rgb(157, 168, 168)")
        self.Save_as.clicked.connect(self.Save)
        self.Save_as.setDisabled(True)
        self.Refresh = QPushButton('Refresh Mango', self)
        self.Refresh.setFixedSize(100, 25)
        self.Refresh.clicked.connect(self.Refresh_Mongo)
        self.Create_model = QPushButton('Create and show model', self)
        self.Create_model.setFixedSize(140,25)
        self.Create_model.clicked.connect(self.Create_model_func)
        self.Compare_all_models = QPushButton('Compare all models ', self)
        self.Compare_all_models.setFixedSize(140,25)
        self.Compare_all_models.clicked.connect(self.Compare_all_models_func)
        self.Predict_Price = QPushButton('Predict_Price', self)
        self.Predict_Price.clicked.connect(self.Tool_Ptedict)

#----------------------QProgressBar----------------------------------------------------------------
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

#----------------------QCheckBox-------------------------------------------------------------------
        self.LinearRegression = QCheckBox()
        self.LinearRegression.setText('LinearRegression')
        self.DecisionTreeRegressor = QCheckBox(self)
        self.DecisionTreeRegressor.setText('DecisionTreeRegressor')
        self.RandomForestRegressor = QCheckBox(self)
        self.RandomForestRegressor.setText('RandomForestRegressor')
        self.SVR = QCheckBox(self)
        self.SVR.setText('SVR')
        self.XGBoost = QCheckBox(self)
        self.XGBoost.setText('XGBoost')
        self.Neural_network = QCheckBox(self)
        self.Neural_network.setText('Neural network')

#---------------------- QTimer --------------------------------------------------------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.Save_Button_Disable_or_Enable)  # zmienia status Save Disable_or_Enable
        self.timer.timeout.connect(self.Start_Scraping_Button_Disable_or_Enable)  # zmienia status Start Scraping Disable_or_Enable
        # self.timer.timeout.connect(lambda: self.Progres_Bar())
        self.timer.timeout.connect(self.Progres_Bar)
        self.timer.start(500)

#---------------------- Layout Tab 1 --------------------------------------------------------------
        self.tab1.layout = QGridLayout(self)
        self.tab1.layout.addWidget(self.city,0,0)
        self.tab1.layout.addWidget(self.text, 8, 0, 1, 2)
        self.tab1.layout.addWidget(self.price_min, 4, 0)
        self.tab1.layout.addWidget(self.price_max, 5, 0)
        self.tab1.layout.addWidget(self.area_min, 6, 0)
        self.tab1.layout.addWidget(self.area_max, 7, 0)
        self.tab1.layout.addWidget(self.distance, 1, 0)
        self.tab1.layout.addWidget(self.type, 2, 0)
        self.tab1.layout.addWidget(self.Start_Scraping, 0, 1, 1, 2)
        self.tab1.layout.addWidget(self.Save_as, 8, 2)
        self.tab1.layout.addWidget(self.progressBar, 9, 0, 1, 6)

#---------------------- Layout Tab 2 --------------------------------------------------------------
        self.tab2.layout = QGridLayout(self)
        self.tab2.layout.addWidget(self.Create_model, 1, 0 ,1,1)
        self.tab2.layout.addWidget(self.Compare_all_models, 1, 1)
        self.tab2.layout.addWidget(self.DataSet_Mongo,0,0)
        self.tab2.layout.addWidget(self.LinearRegression, 2, 0)
        self.tab2.layout.addWidget(self.DecisionTreeRegressor, 3, 0)
        self.tab2.layout.addWidget(self.RandomForestRegressor, 4, 0)
        self.tab2.layout.addWidget(self.SVR, 5, 0)
        self.tab2.layout.addWidget(self.XGBoost, 6, 0)
        self.tab2.layout.addWidget(self.Neural_network, 7, 0)
        self.tab2.layout.addWidget(self.Refresh, 1, 2)

# ---------------------- Layout Tab 3 --------------------------------------------------------------
        self.tab3.layout = QGridLayout(self)
        self.tab3.layout.addWidget(self.city_predict,0,0)
        self.tab3.layout.addWidget(self.distans_to_centrum,1,0)
        self.tab3.layout.addWidget(self.rooms,1,1)
        self.tab3.layout.addWidget(self.enter_area,2,0)
        self.tab3.layout.addWidget(self.level,2,1)
        self.tab3.layout.addWidget(self.Year_of_build,3,0)
        self.tab3.layout.addWidget(self.level_in_block,3,1)
        self.tab3.layout.addWidget(self.type_maret,4,0)
        self.tab3.layout.addWidget(self.form_of_the_property,4,1)
        self.tab3.layout.addWidget(self.heading,5,0)
        self.tab3.layout.addWidget(self.type_building,0,1)
        self.tab3.layout.addWidget(self.condition,5,1)
        self.tab3.layout.addWidget(self.Predict_Price, 8, 0,1,0)

# ---------------------- Add tabs to widget -------------------------------------------------------
        self.tab2.setLayout(self.tab2.layout)
        self.tab1.setLayout(self.tab1.layout)
        self.tab3.setLayout(self.tab3.layout)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    # Check that chosen city is on CSV list if not appear messagebox with wrong place
    def Start_Scraping_funck(self):
        if self.city.text() in self.LISTA:
            pass
        else:
            return self.MessageBox_wrong()
        # Load data from all EditLine and Combobox which were entered to windows
        rodzaj = self.type.currentText()
        city_name = self.city.text().replace('Ł', 'L') if 'Ł'  in self.city.text() else (self.city.text().replace('ł', 'l') if 'ł' in self.city.text() else self.city.text() )
        city = unicodedata.normalize('NFKD', city_name).encode('ascii', 'ignore').decode("utf8")
        string = lambda x: (x.split()[1]) if x != '0 km' else '0'
        radius = int(string(self.distance.currentText()))
        price_min = self.price_min.text()
        price_max = self.price_max.text()
        area_min = self.area_min.text()
        area_max = self.area_max.text()
        # Check that price and area are digital value or empty
        if (price_min.isdigit() == True or price_min == '') and \
                (price_max.isdigit() == True or price_max == '') and \
                (area_min.isdigit() == True or area_min == '') and \
                (area_max.isdigit() == True or area_max == ''):
            pass
        else:
            return self.MessageBox_wrong_digital()
        # Create an object in OtoDomScraping to data scraping
        self.parometers = [city, radius, rodzaj, price_min, price_max, area_min, area_max]
        self.obiekt = OtoDomWebScraping(city, radius, rodzaj, price_min, price_max, area_min, area_max)
        self.MessageBox_start()

    # Window with a question to proceed with scraping
    def MessageBox_start(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        cleanlooks = QStyleFactory.create('cleanlooks')
        msgBox.setStyle(cleanlooks)
        msgBox.setText("Found  {value} offerts \n Start Scraping ? ".format(value=self.obiekt.base_info()))
        self.progres = int(self.obiekt.base_info())
        msgBox.setWindowTitle("Next step?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.exec()
        # After press YES scraping is start
        if msgBox.standardButton(msgBox.clickedButton()) == QMessageBox.Yes:
            self.threadpool = QThreadPool()
            self.worker = WorkerThread(self.parometers,self.path,self.name_Mongo,self.city)
            self.threadpool.start(self.worker)
        else:
            pass

    # Window with incorrect place
    def MessageBox_wrong(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        cleanlooks = QStyleFactory.create('cleanlooks')
        msgBox.setStyle(cleanlooks)
        msgBox.setText("Invalid place , select from the list")
        msgBox.setWindowTitle("Invalid place")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    # Window with a message that value for price or area is not digital
    def MessageBox_wrong_digital(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        cleanlooks = QStyleFactory.create('cleanlooks')
        msgBox.setStyle(cleanlooks)
        msgBox.setText("Invalid value for price or area")
        msgBox.setWindowTitle("Invalid value")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    # load csv file (polish city)
    def Load_places_from_csv(self):
        df = pd.read_csv(r"C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\csv_files\miasta.csv", sep=';')
        BIG_NAME = df['Nazwa miejscowości '].tolist()
        SMALL_NAME = df['miasta'].tolist()
        self.LISTA = BIG_NAME + SMALL_NAME

    # Save button is enabled after defining place
    def Save_Button_Disable_or_Enable(self):
        if self.city.text() in self.LISTA:
            self.Save_as.setDisabled(False)
        else:
            self.Save_as.setDisabled(True)

    # 'StartCraping' button is enabled after defining place and saving path
    def Start_Scraping_Button_Disable_or_Enable(self):
        if self.city.text() in self.LISTA and self.path != '':
            self.Start_Scraping.setDisabled(False)
        else:
            self.Start_Scraping.setDisabled(True)

    # the function which creates name of files to save according data from Editlines and Comboboxes
    def Save(self):
        rodzaj = self.type.currentText()
        city_name = self.city.text().replace('Ł', 'L') if 'Ł'  in self.city.text() else (self.city.text().replace('ł', 'l') if 'ł' in self.city.text() else self.city.text() )
        city = unicodedata.normalize('NFKD', city_name).encode('ascii', 'ignore').decode("utf8")
        string = lambda x: (x.split()[1]) if x != '0 km' else '0'
        radius = string(self.distance.currentText())
        price_min = '0' if self.price_min.text() == '' else str(self.price_min.text())
        price_max = '' if self.price_max.text() == '' else str(self.price_max.text())
        area_min = '0' if self.area_min.text() == '' else str(self.area_min.text())
        area_max = '' if self.area_max.text() == '' else str(self.area_max.text())
        self.name = city + '_' + rodzaj + '_' + 'rad_' + radius + '_' + 'p_min_' + price_min + '_' + 'p_max_' + price_max + '_' + 'a_min_' + area_min + '_' + 'a_max_' + area_max + '.csv'
        self.name_Mongo = city + '_' + rodzaj + '_' + 'rad_' + radius + '_' + 'p_min_' + price_min + '_' + 'p_max_' + price_max + '_' + 'a_min_' + area_min + '_' + 'a_max_' + area_max
        www = QFileDialog.getSaveFileName(self, dir=self.name)
        self.path = www[0]
        return self.text.setText(self.path), self.path,self.name_Mongo

    def Progres_Bar(self):
        self.progressBar.setMaximum(self.progres)
        try:
            self.progressBar.setValue(counter)
        except:
            self.progressBar.setValue(0)

    # Scraping process is done
    def MessageBox_scraping_is_done(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        cleanlooks = QStyleFactory.create('cleanlooks')
        msgBox.setStyle(cleanlooks)
        msgBox.setText("Scraping Proces is finished")
        msgBox.setWindowTitle("Proces Done")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    # the message includes predicting price
    def MessageBox_Price(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        cleanlooks = QStyleFactory.create('cleanlooks')
        msgBox.setStyle(cleanlooks)
        msgBox.setText(f'Price according to enter data is {str(int(self.price[0]))} PLN ')
        msgBox.setWindowTitle("Price")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()

    # display places saved in MongoDB
    def Load_Mongo(self):
        mongo_db = pymongo.MongoClient("mongodb://localhost:27017/")
        self.data = [i for i in mongo_db.list_database_names() if "_db" in i or 'rad' in i ]
        self.data_predict = [i.split('_')[0] for i in mongo_db.list_database_names() if "_db" in i or 'rad' in i]
        return self.data ,self.data_predict

    # refresh Combobox with places from Mongodb
    def Refresh_Mongo(self):
        self.DataSet_Mongo.clear()
        mongo_db = pymongo.MongoClient("mongodb://localhost:27017/")
        self.data = [i for i in mongo_db.list_database_names() if "_db" in i or 'rad' in i ]
        self.DataSet_Mongo.addItems(self.data)

    # create model according to chosen Checkbox
    def Create_model_func(self):
        model = Models(self.DataSet_Mongo.currentText())
        model.Load_from_Mongo()
        model.Split_Date_for_Test_and_Train()
        if self.LinearRegression.isChecked():
            model.LinearRegression()
        if self.DecisionTreeRegressor.isChecked():
            model.DecisionTreeRegressor()
        if self.RandomForestRegressor.isChecked():
            model.RandomForest()
        if self.SVR.isChecked():
            model.SVR()
        if self.XGBoost.isChecked():
            model.xgboost()
        if self.Neural_network.isChecked():
            model.Neural_Network()
        else:
            pass

    # function display class TableView
    def Compare_all_models_func (self):
        model_results = Models_Results(self.DataSet_Mongo.currentText())
        self.results = model_results.Compare_All_Results()
        results = list(self.results['Results'])
        self.sub_window = TableView(results)
        self.sub_window.show()

    # function create an object in OtoDom Models to count price
    def Tool_Ptedict(self):
       city_pred =  self.city_predict.currentText()
       distans_to_centrum_pred = self.distans_to_centrum.text()
       enter_area_pred = self.enter_area.text()
       Year_of_build_pred =self.Year_of_build.text()
       type_maret_pred = self.type_maret.currentText()
       heading_pred = self.heading.currentText()
       type_building_pred = self.type_building.currentText()
       condition_pred = self.condition.currentText()
       rooms_pred = self.rooms.text()
       level_pred = self.level.text()
       level_in_block_pred = self.level_in_block.text()
       form_of_the_property_pred = self.form_of_the_property.currentText()
       # print(city_pred,distans_to_centrum_pred,enter_area_pred,Year_of_build_pred,type_maret_pred,heading_pred,type_building_pred,condition_pred,rooms_pred,level_pred,
       #       level_in_block_pred,form_of_the_property_pred)
       if (distans_to_centrum_pred.isdigit() == True and distans_to_centrum_pred != '') and \
           (rooms_pred.isdigit() == True and rooms_pred != '') and \
               (level_pred.isdigit() == True and level_pred != '') and \
               (level_in_block_pred.isdigit() == True and level_in_block_pred != '') and \
               (enter_area_pred.isdigit() == True and enter_area_pred != '') and \
            (Year_of_build_pred.isdigit() == True and Year_of_build_pred != '') :
        pass
       else:
           return self.MessageBox_wrong_digital()

       price_result = Tool_Predict(city_pred,distans_to_centrum_pred,enter_area_pred,Year_of_build_pred,type_maret_pred,heading_pred,type_building_pred,condition_pred,rooms_pred,level_pred,
             level_in_block_pred,form_of_the_property_pred)
       price_result.Load_from_Mongo_pred()
       price_result.Price_count()
       price_result.Split_Date_for_Test_and_Train()
       price_result.Compare_All_Results()
       self.price = price_result.Temp_LinRegres()
       return self.MessageBox_Price()



# the class TableView creates a new window with compared data MSE ( comparing all models and count MSE )
class TableView(QTableWidget):
    def __init__(self ,results):
        QTableWidget.__init__(self)
        lista =['Method','MSE error']
        self.setFixedSize(215, 215)
        tableWidget = QTableWidget(self)
        tableWidget.setStyleSheet("background-color: rgb(25, 25, 25); color: rgb(157, 168, 168)")
        tableWidget.setFixedSize(215,215)
        tableWidget.setRowCount(6)
        tableWidget.setColumnCount(2)
        tableWidget.setHorizontalHeaderLabels(lista)
        Method_list = ['LinearRegression' , 'DecisionTreeRegressor' , 'RandomForest' , 'SVR' , 'Xgbxgboost_reg' ,'Neural_Network'  ]
        for i ,y in enumerate(Method_list):
             item = QTableWidgetItem(str(y))
             tableWidget.setItem(i,0,item)
        for i, y in enumerate(results):
            item = QTableWidgetItem(str(y))
            tableWidget.setItem(i, 1, item)

# the class created for multiprocessing
class WorkerThread(QRunnable):
    def __init__(self,parometers,path,name_Mongo,city):
        super().__init__()
        self.parometers = parometers
        self.path = path
        self.name_Mongo = name_Mongo
        self.city = city

    @Slot()
    def run(self):
        self.obiekt = OtoDomWebScraping(self.parometers[0],self.parometers[1],self.parometers[2],self.parometers[3],
        self.parometers[4],self.parometers[5],self.parometers[6])
        self.obiekt.stepIncreased.connect(self.temp)
        self.obiekt.WebScraping(self.path)
        self.obiekt.Convert_and_Clean_Date(self.path)
        city_name = self.city.text().replace('Ł', 'L') if 'Ł'  in self.city.text() else (self.city.text().replace('ł', 'l') if 'ł' in self.city.text() else self.city.text() )
        city = unicodedata.normalize('NFKD', city_name).encode('ascii', 'ignore').decode("utf8")
        self.obiekt.Save_to_Mongo(self.name_Mongo, city)
    # function get current value during scraping process
    def temp(self,val):
        global counter
        counter = val

if __name__ == '__main__':
 app = QApplication(sys.argv)
 app.setStyle('Fusion')
 window = App()
 window.show()
 app.exec()