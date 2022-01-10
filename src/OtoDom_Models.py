import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn import metrics
from sklearn.svm import SVR
import pickle
import pymongo
import xgboost as xgb
import tensorflow as tf
import os

# class count and create a visualization
class Models:
    def __init__(self ,city):
        self.city =city
        self.short_city = city.split('_')[0]

    # load data from Mongo
    def Load_from_Mongo(self):
        # Connect with mongo client
        mongo_db = pymongo.MongoClient("mongodb://localhost:27017/")
        # Connect to database
        string = self.city
        flats_db = mongo_db[string]

        # Get data for machine learning from collections
        string_x = '{city}_flats_x'.format(city=self.short_city)
        string_y = '{city}_flats_y'.format(city=self.short_city)
        city_flats_x = flats_db[string_x]
        city_flats_y = flats_db[string_y]


        # Define X and Y variables (input and output of our ML models)
        X = []
        Y = []

        # Find data in database and fill lists
        for x in city_flats_x.find():
            X.append(x)

        for y in city_flats_y.find():
            Y.append(y)

        # Convert lists into dataframe (remove id field)
        self.X = pd.DataFrame(X).drop('_id', axis=1)
        self.Y = pd.DataFrame(Y).drop('_id', axis=1)

    # split data for test and train
    def Split_Date_for_Test_and_Train(self):

         self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.X, self.Y, test_size=0.2, random_state=10)
         min_max_scaler = MinMaxScaler()
         self.X_train_norm = min_max_scaler.fit_transform(self.X_train)
         self.X_test_norm = min_max_scaler.transform(self.X_test)

    def LinearRegression(self):
        mypath = r'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\LinearRegression'
        arr = os.listdir(mypath)
        if f'{self.city}.sav' in arr:
            sklearn_linear = pickle.load(open(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\LinearRegression\{self.city}.sav', 'rb'))
            Y_predictions_train = sklearn_linear.predict(self.X_train_norm)
            Y_predictions_test = sklearn_linear.predict(self.X_test_norm)
        else:
            sklearn_linear = LinearRegression()
            sklearn_linear.fit(self.X_train_norm, self.Y_train)
            Y_predictions_train = sklearn_linear.predict(self.X_train_norm)
            Y_predictions_test = sklearn_linear.predict(self.X_test_norm)
            pickle.dump(sklearn_linear, open(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\LinearRegression\{self.city}.sav', 'wb'))

        MSE_train_LinearRegression = round(metrics.mean_squared_error(self.Y_train, Y_predictions_train, squared=False), 2)
        MSE_test_LinearRegression = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 12) ,sharey=True  )
        ax1.scatter(list(range(len(self.Y_train))), self.Y_train, c='r', alpha=0.6, s=60)
        ax1.scatter(list(range(len(self.Y_train))), Y_predictions_train, c='g', alpha=0.6, s=60)
        ax1.set_title( f"Train Date , MSE =  {MSE_train_LinearRegression}" )
        ax1.set_ylabel('Price in PLN')
        ax1.grid()
        ax2.scatter(list(range(len(self.Y_test))), self.Y_test, c='y', alpha=0.6, s=60)
        ax2.scatter(list(range(len(self.Y_test))), Y_predictions_test, c='b', alpha=0.6, s=60)
        ax2.set_title( f"Test Date , MSE =  {MSE_test_LinearRegression}" )
        self.city = (self.city.replace('_', ' ').replace(' rad ', ' radius ').replace(' p ', ' price ').replace(' a ',' area ')).capitalize()
        fig.suptitle(f'LinearRegression for {self.city}')
        plt.show()

    def DecisionTreeRegressor (self):

        mypath = r'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\DecisionTreeRegressor'
        arr = os.listdir(mypath)
        if f'{self.city}.sav' in arr:
            tree_regr = pickle.load(open(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\DecisionTreeRegressor\{self.city}.sav', 'rb'))
            Y_predictions_train = tree_regr.predict(self.X_train_norm)
            Y_predictions_test = tree_regr.predict(self.X_test_norm)
        else:
            tree_regr = DecisionTreeRegressor(max_depth=16)
            tree_regr.fit(self.X_train_norm, self.Y_train)
            Y_predictions_train = tree_regr.predict(self.X_train_norm)
            Y_predictions_test = tree_regr.predict(self.X_test_norm)
            pickle.dump(tree_regr, open(rf'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\DecisionTreeRegressor\{self.city}.sav', 'wb'))

        MSE_train_tree_regr = round(metrics.mean_squared_error(self.Y_train, Y_predictions_train, squared=False), 2)
        MSE_test_tree_regr =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 12))
        ax1.scatter(list(range(len(self.Y_train))), self.Y_train, c='r', alpha=0.6, s=60)
        ax1.scatter(list(range(len(self.Y_train))), Y_predictions_train, c='b', alpha=0.6, s=60)
        ax1.set_title( f"Train Date , MSE =  {MSE_train_tree_regr}" )
        ax1.set_ylabel('Price in PLN')
        ax2.scatter(list(range(len(self.Y_test))), Y_predictions_test, c='y', alpha=0.6, s=60)
        ax2.scatter(list(range(len(self.Y_test))), self.Y_test, c='b', alpha=0.6, s=60)
        ax2.set_title( f"Test Date , MSE =  {MSE_test_tree_regr}" )
        self.city = (self.city.replace('_', ' ').replace(' rad ', ' radius ').replace(' p ', ' price ').replace(' a ',' area ')).capitalize()
        fig.suptitle(f'DecisionTreeRegressor for {self.city}')
        plt.show()

    def RandomForest (self):
        mypath = r'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\RandomForest'
        arr = os.listdir(mypath)
        if  f'{self.city}.sav' in arr:
            RandomForest = pickle.load(open(rf'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\RandomForest\{self.city}.sav', 'rb'))
            Y_predictions_train = RandomForest.predict(self.X_train_norm)
            Y_predictions_test = RandomForest.predict(self.X_test_norm)
        else:
            RandomForest = RandomForestRegressor()
            RandomForest.fit(self.X_train_norm, self.Y_train.values.ravel())
            Y_predictions_train = RandomForest.predict(self.X_train_norm)
            Y_predictions_test = RandomForest.predict(self.X_test_norm)
            pickle.dump(RandomForest, open(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\RandomForest\{self.city}.sav', 'wb'))

        MSE_train_RandomForest = round(metrics.mean_squared_error(self.Y_train, Y_predictions_train, squared=False), 2)
        MSE_test_RandomForest =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 12))
        ax1.scatter(list(range(len(self.Y_train))), self.Y_train, c='r', alpha=0.6, s=60)
        ax1.scatter(list(range(len(self.Y_train))), Y_predictions_train, c='b', alpha=0.6, s=60)
        ax1.set_title( f"Train Date , MSE =  {MSE_train_RandomForest}" )
        ax1.set_ylabel('Price in PLN')
        ax2.scatter(list(range(len(self.Y_test))), Y_predictions_test, c='y', alpha=0.6, s=60)
        ax2.scatter(list(range(len(self.Y_test))), self.Y_test, c='b', alpha=0.6, s=60)
        ax2.set_title( f"Test Date , MSE =  {MSE_test_RandomForest}" )
        self.city = (self.city.replace('_', ' ').replace(' rad ', ' radius ').replace(' p ', ' price ').replace(' a ', ' area ')).capitalize()
        fig.suptitle(f'RandomForest for {self.city}')
        plt.show()

    def SVR (self):
        mypath = r'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\SVR'
        arr = os.listdir(mypath)
        if f'{self.city}.sav' in arr:
            svr_rbf = pickle.load(open(rf'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\SVR\{self.city}.sav', 'rb'))
            Y_predictions_train = svr_rbf.predict(self.X_train_norm)
            Y_predictions_test = svr_rbf.predict(self.X_test_norm)
        else:
            svr_rbf = SVR(kernel='rbf', C=100000, gamma=100.1, epsilon=10.4)
            svr_rbf.fit(self.X_train_norm, self.Y_train.values.ravel())
            Y_predictions_train = svr_rbf.predict(self.X_train_norm)
            Y_predictions_test = svr_rbf.predict(self.X_test_norm)
            pickle.dump(svr_rbf, open(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\SVR\{self.city}.sav', 'wb'))

        MSE_train_svr = round(metrics.mean_squared_error(self.Y_train, Y_predictions_train, squared=False), 2)
        MSE_test_svr =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 12))
        # ############## SVR TRAIN #################################################
        ax1.scatter(list(range(len(self.Y_train))), self.Y_train['Cena'], c='r')
        ax1.scatter(list(range(len(self.Y_train))), Y_predictions_train, c='y')
        ax1.legend(['Dane treningowe', 'Predykcja'])
        ax1.set_title( f"Train Date , MSE =  {MSE_train_svr}" )
        ax1.set_ylabel('Price in PLN')
        # ############## SVR TEST #################################################
        ax2.scatter(list(range(len(self.Y_test))), self.Y_test['Cena'], c='red')
        ax2.scatter(list(range(len(self.Y_test))), Y_predictions_test, c='y')
        ax2.legend(['Dane testowe', 'Predykcja'])
        ax2.set_title( f"Test Date , MSE =  {MSE_test_svr}" )
        fig.suptitle(f'SVR for {self.city}')
        plt.show()

    def xgboost (self):

        mypath = r'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\gbxgboost_reg'
        arr = os.listdir(mypath)
        if f'{self.city}.sav' in arr:
            gboost_reg = pickle.load(open(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\gbxgboost_reg\{self.city}.sav',"rb"))
            Y_predictions_train = gboost_reg.predict(self.X_train_norm)
            Y_predictions_test = gboost_reg.predict(self.X_test_norm)
        else:
            gboost_reg = xgb.XGBRegressor()
            gboost_reg.fit(self.X_train_norm, self.Y_train)
            Y_predictions_train = gboost_reg.predict(self.X_train_norm)
            Y_predictions_test = gboost_reg.predict(self.X_test_norm)


            pickle.dump(gboost_reg, open(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\gbxgboost_reg\{self.city}.sav', 'wb'))

        MSE_train_xgboost = round(metrics.mean_squared_error(self.Y_train, Y_predictions_train, squared=False), 2)
        MSE_test_xgboost =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 12))
        ax1.scatter(list(range(len(self.Y_train))), self.Y_train['Cena'], c='r')
        ax1.scatter(list(range(len(self.Y_train))), Y_predictions_train, c='y')
        ax1.legend(['Dane treningowe', 'Predykcja'])
        ax1.set_title( f"Train Date , MSE =  {MSE_train_xgboost}" )
        ax1.set_ylabel('Price in PLN')
        ax2.scatter(list(range(len(self.Y_test))), self.Y_test['Cena'], c='red')
        ax2.scatter(list(range(len(self.Y_test))), Y_predictions_test, c='y')
        ax2.legend(['Dane testowe', 'Predykcja'])
        ax2.set_title( f"Test Date , MSE =  {MSE_test_xgboost}" )
        self.city = (self.city.replace('_', ' ').replace(' rad ', ' radius ').replace(' p ', ' price ').replace(' a ',
                                                                                                               ' area ')).capitalize()
        fig.suptitle(f'xgboost for {self.city}')
        plt.show()

    def Neural_Network (self):

        mypath = r'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_Neural_Network_models'
        arr = os.listdir(mypath)
        if self.city in arr:
            model = tf.keras.models.load_model(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_Neural_Network_models/{self.city}')
            Y_predictions_train = model.predict(self.X_train_norm)
            Y_predictions_test = model.predict(self.X_test_norm)
            MSE_train = round(metrics.mean_squared_error(self.Y_train, Y_predictions_train, squared=False), 2)
            MSE_test = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
        else:
            model = tf.keras.models.Sequential()
            model.add(tf.keras.layers.Dense(30, activation='relu', input_shape=(self.X_train_norm.shape[1],)))
            model.add(tf.keras.layers.Dense(30, activation='relu'))
            model.add(tf.keras.layers.Dense(30, activation='relu'))
            model.add(tf.keras.layers.Dense(1))
            model.compile(optimizer='adam', loss='mean_absolute_percentage_error')
            model.fit(self.X_train_norm, self.Y_train, epochs=100, verbose=1)
            Y_predictions_train = model.predict(self.X_train_norm)
            Y_predictions_test = model.predict(self.X_test_norm)
            MSE_train = round(metrics.mean_squared_error(self.Y_train, Y_predictions_train, squared=False), 2)
            MSE_test = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
            model.save(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_Neural_Network_models/{self.city}')



        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 12))
        ax1.scatter(list(range(len(self.Y_train))), self.Y_train['Cena'], c='r')
        ax1.scatter(list(range(len(self.Y_train))), Y_predictions_train, c='y')
        ax1.legend(['Dane treningowe', 'Predykcja'])
        ax1.set_title( f"Train Date , MSE =  {MSE_train}" )
        ax1.set_ylabel('Price in PLN')
        ax2.scatter(list(range(len(self.Y_test))), self.Y_test['Cena'], c='red')
        ax2.scatter(list(range(len(self.Y_test))), Y_predictions_test, c='y')
        ax2.legend(['Dane testowe', 'Predykcja'])
        ax2.set_title( f"Test Date , MSE =  {MSE_test}" )
        self.city = (self.city.replace('_', ' ').replace(' rad ', ' radius ').replace(' p ', ' price ').replace(' a ',' area ')).capitalize()
        fig.suptitle(f'Neural_Network for {self.city}')
        plt.show()

# class which counts MSE for all method and choose the best result
class Models_Results(Models):

    def __init__(self ,city):
        super().__init__(city)
        Models.Load_from_Mongo(self)
        Models.Split_Date_for_Test_and_Train(self)

    def Compare_All_Results(self):
        '''Function to compare all models and find the least MSE error

        parameters:
        self.city - str
        self.X_train_norm -numpy
        self.Y_train -numpy
        self.Y_test -numpy

        return:
        Returning value : pandas DataFrame
        '''

        mypath = r'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\LinearRegression'
        arr = os.listdir(mypath)
        if f'{self.city}.sav' in arr:
            sklearn_linear = pickle.load(open(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_other_models\LinearRegression\{self.city}.sav', 'rb'))
            Y_predictions_test = sklearn_linear.predict(self.X_test_norm)
            MSE_test_LinearRegression = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
        else:
            sklearn_linear = LinearRegression()
            sklearn_linear.fit(self.X_train_norm, self.Y_train)
            Y_predictions_test = sklearn_linear.predict(self.X_test_norm)
            MSE_test_LinearRegression =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        tree_regr = DecisionTreeRegressor(max_depth=16)
        tree_regr.fit(self.X_train_norm, self.Y_train)
        Y_predictions_test = tree_regr.predict(self.X_test_norm)
        MSE_test_DecisionTreeRegressor = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        regr = RandomForestRegressor()
        regr.fit(self.X_train_norm, self.Y_train.values.ravel())
        Y_predictions_test = regr.predict(self.X_test_norm)
        MSE_test_RandomForestRegressor =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        svr_rbf = SVR(kernel='rbf', C=100000, gamma=100.1, epsilon=10.4)
        svr_rbf.fit(self.X_train_norm, self.Y_train.values.ravel())
        Y_predictions_test = svr_rbf.predict(self.X_test_norm)
        MSE_test_svr_rbf =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        xgb_regr = xgb.XGBRegressor()
        xgb_regr.fit(self.X_train_norm, self.Y_train)
        Y_predictions_test = xgb_regr.predict(self.X_test_norm)
        MSE_test_xgb_regr =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        mypath = r'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_Neural_Network_models'
        arr = os.listdir(mypath)
        if self.city in arr:
            model = tf.keras.models.load_model(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_Neural_Network_models/{self.city}')
            Y_predictions_test = model.predict(self.X_test_norm)
            MSE_test_Neural_Network = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
        else:
            model = tf.keras.models.Sequential()
            model.add(tf.keras.layers.Dense(30, activation='relu', input_shape=(self.X_train_norm.shape[1],)))
            model.add(tf.keras.layers.Dense(30, activation='relu'))
            model.add(tf.keras.layers.Dense(1))
            model.compile(optimizer='adam', loss='mean_absolute_percentage_error')
            model.fit(self.X_train_norm, self.Y_train, epochs=100, verbose=1)
            Y_predictions_test = model.predict(self.X_test_norm)
            MSE_test_Neural_Network = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False),2)
            model.save(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_Neural_Network_models/{self.city}')

        Lista_Metods = ['LinearRegression', 'RandomForestRegressor', 'DecisionTreeRegressor','SVR', 'XGBRegressor', 'Neural_Network']
        Lista_Results = [MSE_test_LinearRegression, MSE_test_RandomForestRegressor, MSE_test_DecisionTreeRegressor, MSE_test_svr_rbf, MSE_test_xgb_regr,MSE_test_Neural_Network]

        df_Metods = pd.Series(Lista_Metods , name= 'Method')
        df_Results = pd.Series(Lista_Results , name= 'Results')
        df = pd.concat([df_Metods,df_Results ] , axis=1)
        return  df

#  class counts price according to entered data and choose model with the least MSE error
class Tool_Predict(Models):
    def __init__(self ,city,distans_to_centrum_pred,enter_area_pred,Year_of_build_pred,type_maret_pred,
                 heading_pred,type_building_pred,condition_pred,rooms_pred,level_pred,level_in_block_pred,
                 form_of_the_property_pred):

        # parameters of our flat
        self.city = city
        self.distans_to_centrum_pred =distans_to_centrum_pred
        self.enter_area_pred =enter_area_pred
        self.Year_of_build_pred =Year_of_build_pred
        self.type_maret_pred =type_maret_pred
        self.heading_pred =heading_pred
        self.type_building_pred =type_building_pred
        self.condition_pred =condition_pred
        self.rooms_pred =rooms_pred
        self.level_pred =level_pred
        self.level_in_block_pred = level_in_block_pred
        self.form_of_the_property_pred = form_of_the_property_pred


    # load data from Mongodb
    def Load_from_Mongo_pred(self):
        # Connect with mongo client
        mongo_db = pymongo.MongoClient("mongodb://localhost:27017/")

        # Connect to database
        www = [i for i in mongo_db.list_database_names() if self.city in i]
        flats_db = mongo_db[www[0]]
        # Get data for machine learning from collections
        string_x = '{city}_flats_x'.format(city=self.city)
        string_y = '{city}_flats_y'.format(city=self.city)
        city_flats_x = flats_db[string_x]
        city_flats_y = flats_db[string_y]
        # Define X and Y variables (input and output of our ML models)
        X = []
        Y = []
        # Find data in database and fill lists
        for x in city_flats_x.find():
            X.append(x)
        for y in city_flats_y.find():
            Y.append(y)
        # Convert lists into dataframe (remove id field)
        self.X = pd.DataFrame(X).drop('_id', axis=1)
        self.Y = pd.DataFrame(Y).drop('_id', axis=1)

    # function to create DataFrame (1 row) with all parameters of our flat
    def Price_count(self):
          '''Function to create DataFrame (1 row) with all parameters of our flat

            parameters:
            Many parameters

            return:
            Returning value : pandas
          '''

          market = 1 if self.type_maret_pred == 'pierwotny' else 0
          data_dict = {
            'Powierzchnia': [self.enter_area_pred],
            'Liczba pokoi': [self.rooms_pred],
            'Rynek' : [market],
            'Piętro' : [self.level_pred],
            'Liczba pięter' :[self.level_in_block_pred],
            'Rok budowy' : [self.Year_of_build_pred],
            'Rodzaj zabudowy_apartamentowiec' : [0],
            'Rodzaj zabudowy_blok' : [0],
            'Rodzaj zabudowy_dom wolnostojący' : [0],
            'Rodzaj zabudowy_kamienica' : [0],
            'Rodzaj zabudowy_loft': [0],
            'Rodzaj zabudowy_plomba' : [0],
            'Rodzaj zabudowy_szeregowiec' : [0],
            'Ogrzewanie_elektryczne' : [0],
            'Ogrzewanie_gazowe' : [0],
            'Ogrzewanie_inne' : [0],
            'Ogrzewanie_kotłownia' : [0],
            'Ogrzewanie_miejskie' : [0],
            'Ogrzewanie_piece kaflowe': [0],
            'Stan wykończenia_do remontu' : [0],
            'Stan wykończenia_do wykończenia' : [0],
            'Forma własności_pełna własność' : [0],
            'Forma własności_spółdzielcze wł z KW' : [0],
            'Forma własności_spółdzielcze własnościowe' : [0],
            'Forma własności_udział': [0],
            'API_Google_Distance' : [self.distans_to_centrum_pred]
            }

          # change default value to new one , chosen by user
          for i, y in zip(data_dict, data_dict.values()):
              data_dict[i] = [1] if self.heading_pred in i else ([1] if self.type_building_pred in i else ([1] if self.form_of_the_property_pred in i else ( [1] if self.condition_pred in i else y )))

          self.companies = pd.DataFrame(data=data_dict)
          return self.companies

    # split data
    def Split_Date_for_Test_and_Train(self):
         '''Function to split data got from Mongodb

            parameters:
            self.companies - pandas
            self.X_test - pandas
            self.Y_train - pandas
            self.X_train - pandas
         '''
         # add missing columns and change the order of columns
         panda_list = list(set(self.companies.columns.to_list()) - set(self.X.columns.to_list()))
         for i in panda_list:
             self.X[i] = 0
         missing_column = self.companies.columns.to_list()
         self.X = self.X[missing_column]

         self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.X, self.Y, test_size=0.2, random_state=10)
         min_max_scaler = MinMaxScaler()
         self.X_train_norm = min_max_scaler.fit_transform(self.X_train)
         self.X_test_norm = min_max_scaler.transform(self.X_test)

         self.X_companies_norm = min_max_scaler.transform(self.companies) # 1 row

    # compare MSE errors of all models
    def Compare_All_Results(self):
        '''Function to compare all models and find the least MSE error

        parameters:
        self.X_train_norm -numpy
        self.Y_train -numpy
        self.Y_test -numpy

        return:
        Returning value : str
        '''
        sklearn_linear = LinearRegression()
        sklearn_linear.fit(self.X_train_norm, self.Y_train)
        Y_predictions_test = sklearn_linear.predict(self.X_test_norm)
        MSE_test_LinearRegression =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        tree_regr = DecisionTreeRegressor(max_depth=16)
        tree_regr.fit(self.X_train_norm, self.Y_train)
        Y_predictions_test = tree_regr.predict(self.X_test_norm)
        MSE_test_DecisionTreeRegressor = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        regr = RandomForestRegressor()
        regr.fit(self.X_train_norm, self.Y_train.values.ravel())
        Y_predictions_test = regr.predict(self.X_test_norm)
        MSE_test_RandomForestRegressor =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        svr_rbf = SVR(kernel='rbf', C=100000, gamma=100.1, epsilon=10.4)
        svr_rbf.fit(self.X_train_norm, self.Y_train.values.ravel())
        Y_predictions_test = svr_rbf.predict(self.X_test_norm)
        MSE_test_svr_rbf =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        xgb_regr = xgb.XGBRegressor()
        xgb_regr.fit(self.X_train_norm, self.Y_train)
        Y_predictions_test = xgb_regr.predict(self.X_test_norm)
        MSE_test_xgb_regr =round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)

        mypath = r'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_Neural_Network_models'
        arr = os.listdir(mypath)
        if self.city in arr:
            model = tf.keras.models.load_model(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_Neural_Network_models/{self.city}')
            Y_predictions_test = model.predict(self.X_test_norm)
            MSE_test_Neural_Network = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False), 2)
        else:
            model = tf.keras.models.Sequential()
            model.add(tf.keras.layers.Dense(30, activation='relu', input_shape=(self.X_train_norm.shape[1],)))
            model.add(tf.keras.layers.Dense(30, activation='relu'))
            model.add(tf.keras.layers.Dense(1))
            model.compile(optimizer='adam', loss='mean_absolute_percentage_error')
            model.fit(self.X_train_norm, self.Y_train, epochs=100, verbose=1)
            Y_predictions_test = model.predict(self.X_test_norm)
            MSE_test_Neural_Network = round(metrics.mean_squared_error(self.Y_test, Y_predictions_test, squared=False),2)
            model.save(fr'C:\Users\barto\PycharmProjects\WebScraping\Ultimate Project\Saved_Neural_Network_models/{self.city}')


        Lista_Metods = ['LinearRegression', 'RandomForestRegressor', 'DecisionTreeRegressor','SVR', 'XGBRegressor', 'Neural_Network']
        Lista_Results = [MSE_test_LinearRegression, MSE_test_RandomForestRegressor, MSE_test_DecisionTreeRegressor, MSE_test_svr_rbf, MSE_test_xgb_regr,MSE_test_Neural_Network]

        # make a new frame ,sort value and return the best one
        df_Metods = pd.Series(Lista_Metods , name= 'Method')
        df_Results = pd.Series(Lista_Results , name= 'Results')
        df = pd.concat([df_Metods,df_Results ] , axis=1)
        df = df.sort_values('Results')
        df = df.reset_index(drop=True)
        self.best_results = df.loc[0,'Method']
        return  self.best_results

    # function to prediction price
    def Temp_LinRegres(self):
        '''Function to predict price, according to the latest RMSE error and data entered by users

        parameters:
        self.X_companies_norm - numpy

        return:
        Returning value : int
        '''
        if self.best_results == 'LinearRegression':
            sklearn_linear = LinearRegression()
            sklearn_linear.fit(self.X_train_norm, self.Y_train)
            Y_predictions_test = sklearn_linear.predict(self.X_companies_norm)
            return Y_predictions_test

        if self.best_results == 'RandomForestRegressor':
            tree_regr = DecisionTreeRegressor(max_depth=16)
            tree_regr.fit(self.X_train_norm, self.Y_train)
            Y_predictions_test = tree_regr.predict(self.X_companies_norm)
            return Y_predictions_test

        if self.best_results == 'DecisionTreeRegressor':
            regr = RandomForestRegressor()
            regr.fit(self.X_train_norm, self.Y_train.values.ravel())
            Y_predictions_test = regr.predict(self.X_companies_norm)
            return Y_predictions_test

        if self.best_results == 'SVR':
            svr_rbf = SVR(kernel='rbf', C=100000, gamma=100.1, epsilon=10.4)
            svr_rbf.fit(self.X_train_norm, self.Y_train.values.ravel())
            Y_predictions_test = svr_rbf.predict(self.X_companies_norm)
            return Y_predictions_test

        if self.best_results == 'XGBRegressor':
            xgb_regr = xgb.XGBRegressor()
            xgb_regr.fit(self.X_train_norm, self.Y_train)
            Y_predictions_test = xgb_regr.predict(self.X_companies_norm)
            return Y_predictions_test

if __name__ == '__main__':
    pass






