from bs4 import BeautifulSoup as bs
import requests
import time
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import googlemaps
import pymongo
from PySide6.QtCore import *


# the main class
class OtoDomWebScraping(QObject):
    stepIncreased = Signal(int)

    def __init__(self,city,radius,rodzaj,*new):
        super().__init__()
        self.city = city
        self.radius = radius
        self.rodzaj = rodzaj
        self.new = new


    # function display amount of offerts
    def base_info(self):

        link_base =  r'https://www.otodom.pl/pl/oferty/sprzedaz/{rodzaj}/{city}?priceMin={min_price}&priceMax={max_price}&areaMin={min_area}&areaMax={max_area}&distanceRadius={radius}&limit=72&page='.format(
            rodzaj=self.rodzaj, city=self.city, radius=self.radius , min_price = self.new[0] ,max_price = self.new[1], min_area = self.new[2] , max_area = self.new[3])

        # Link to current website
        link = link_base + '1'
        r = requests.get(link)
        soup = bs(r.content, "html.parser")
        # count amount of offerts
        adds_no = soup.find_all('span', {'class': 'css-klxieh e1ia8j2v11'})[0].get_text()

        return adds_no

    # main funtion to scraping
    def WebScraping(self,filepath):
        numer = 0
        # primary link
        link_base =  r'https://www.otodom.pl/pl/oferty/sprzedaz/{rodzaj}/{city}?priceMin={min_price}&priceMax={max_price}&areaMin={min_area}&areaMax={max_area}&distanceRadius={radius}&limit=72&page='.format(
            rodzaj=self.rodzaj, city=self.city, radius=self.radius , min_price = self.new[0] ,max_price = self.new[1], min_area = self.new[2] , max_area = self.new[3])
        # Link to current website
        link = link_base + '1'
        df = pd.DataFrame()
        r = requests.get(link)
        soup = bs(r.content, "html.parser")

        # count amount of offerts
        adds_no = soup.find_all('span', {'class': 'css-klxieh e1ia8j2v11'})[0].get_text()

        # count amount pages with offerts
        pages = int(np.ceil(int(adds_no) / 72))

        # load data from next pages
        for page in range(1, (pages + 1)):

            try:
             articles = soup.find_all('ul', {'class': 'css-14cy79a e3x1uf06'})[1].select('article')
            except:
             time.sleep(5)
             articles = soup.find_all('ul', {'class': 'css-14cy79a e3x1uf06'})[1].select('article')

            hrefs = ['https://www.otodom.pl' + href['href'] for href in soup.find_all('a', {'class': 'css-jf4j3r es62z2j27'})][3:]
            # lists to store data
            col_names_to_add = ['Tytul', 'Cena', 'Lokalizacja', 'URL']
            column_names = []
            data_to_add = []
            data_csv = []


            # jump from one to next one link(offer) on the current page
            for article_no, article_href in enumerate(hrefs):

                self.stepIncreased.emit(numer)
                numer +=1

                try:
                    print("Page: " + str(page) + '/' + str(pages) + ", advertisement: " + str(article_no + 1) + '/' + str( len(hrefs)))

                    # move to next link  (article_href)
                    time.sleep(0.3)
                    r_off = requests.get(article_href)
                    off_page = bs(r_off.content, "html.parser")

                    # Title
                    offer_title = articles[article_no].find_all("h3", {"class": "css-1oq8pdj es62z2j24"})[0].get_text()
                    # Price
                    item_price = off_page.find_all('strong', {'class': 'css-b114we eu6swcv14'})[0].get_text().replace( "\xa0","")[:-2]
                    # Loc.
                    localisation = articles[article_no].p.span.get_text()
                    # Add data to list
                    data_to_add.extend([offer_title, item_price, localisation, article_href])
                    # parameters
                    parameters = off_page.find_all("div", {'class': 'css-1d9dws4 egzohkh2'})

                    # List of parameters
                    param_list = parameters[0].find_all("div")

                    contetnt_idx = list(range(0, len(param_list), 3))

                    # Load parameters
                    col_names = []
                    data = []

                    # Add names of  parameters to correct list
                    for param_no in contetnt_idx:
                        col_names.append(param_list[param_no].get_text().split(":")[0])
                        data.append(param_list[param_no].get_text().split(":")[1])

                    # Add contents of the list to the current offer
                    col_names_to_add.extend(col_names)
                    data_to_add.extend(data)

                    # Add offer to frame
                    data_csv.append(data_to_add)
                    column_names.append(col_names_to_add)

                    # clean the list
                    col_names_to_add = ['Tytul', 'Cena', 'Lokalizacja', 'URL']
                    data_to_add = []



                except:
                    # Error message
                    print("Error! Page: " + str(page - 1))

                    # clean the list
                    col_names_to_add = ['Tytul', 'Cena', 'Lokalizacja', 'URL']
                    data_to_add = []

            # update frame, link by link
            for element in range(len(data_csv)):
                df = df.append(pd.DataFrame([data_csv[element]], columns=column_names[element]), sort=False)

            # update link - next page
            page = int(page+1)
            link = link_base + str(page)
            print("Next page will be: " + link)
            r = requests.get(link)
            soup = bs(r.content, "html.parser")


        self.df = df
        # save data to csv
        # df.to_csv(filepath, sep=';', index=False, encoding='utf-8-sig')

    def Convert_and_Clean_Date(self,filepath):

        df = self.df
        # set index
        df.index = np.arange(1, len(df) + 1)
        # remove unnecessary rows
        df.drop(df[df['Piętro'] == 'poddasze'].index, inplace=True)
        df.drop(df[df['Piętro'] == 'suterena'].index, inplace=True)
        df.drop(df[df['Liczba pokoi'] == 'więcej niż 10'].index, inplace=True)

        # lambda function to replace the value
        def replace_non_number(roww):
            if (roww['Piętro'] == '> 10'):
                return 11
            elif (roww['Piętro'] == 'parter'):
                return 0
            else:
                return roww['Piętro']

        # replace names to digital value
        df['Piętro'] = df.apply(lambda roww: replace_non_number(roww), axis=1)
        df = df.reset_index(drop=True)

        # replace names to digital value
        df['Rynek'] = df['Rynek'].apply(lambda data: 0 if data == 'wtórny' else 1)

        # Deleting  columns (too many missing values)
        df.drop(['Dostępne od', 'Czynsz', 'Obsługa zdalna', 'Materiał budynku', 'Okna'], axis=1, inplace=True)

        # Deleting  rows with  (nan)
        df.dropna(inplace=True)

        # counting distance to the city center
        geolocator = Nominatim(user_agent="usr")
        city_center_string = self.city+'  centrum'
        city_center = list(geolocator.geocode(city_center_string))[-1]
        loc = [data for data in df['Lokalizacja']]
        locations = []

        for i, location in enumerate(loc):
            print(i)
            try:
                locations.append(geolocator.geocode(location))
            except:
                locations.append("NONE")

        # create lists (loc.lat, loc.long) - unzipped to list
        locations_coordinations = list(zip(*[
            (location.latitude, location.longitude) if (location != None and location != "NONE") else ('None', 'None')
            for location in locations]))  # Jesli nie ma 'None','None'

        locations_coordinations = [list(element) for element in locations_coordinations]  # Convert to mutable (list)

        # removing  None
        indices = [index for index, value in enumerate(locations_coordinations[0]) if value == 'None']
        indices.sort(reverse=True)
        # removing loop
        for index_del in indices:
            del locations_coordinations[0][index_del]
            del locations_coordinations[1][index_del]

        # count  manhattan distance
        manhattan_distance = [(abs(location[0] - city_center[0]) + abs(location[1] - city_center[1])) for location in
                              zip(locations_coordinations[0], locations_coordinations[1])]  # Obl. Manhattan Distance
        manhattan_distance = [element * 111 for element in manhattan_distance]  # 1 degree = 111 kilometers

        manhattan = pd.Series(manhattan_distance, name='manhattan[km]')  # Utworzenie serii z manhattan distance

        # reset index and adding manhatan column
        df = df.reset_index(drop=True)
        df = df.drop(index=indices)
        df = df.reset_index(drop=True)
        df['manhattan'] = manhattan

        # replace ',' to  '.' in price
        df.drop(df[df['Cena'] == 'Zapytaj o ce'].index, inplace=True)
        df['Cena'] = df['Cena'].apply(lambda data: str(data.replace(',', '.')))
        df['Cena'] = df['Cena'].apply(lambda data: str(data.replace(' ', '')))
        df['Cena'] = df['Cena'].apply(lambda data: str(data.replace('E', '')))
        df['Cena'] = df['Cena'].astype(float)

        # removing m2 in area
        df['Powierzchnia'] = df['Powierzchnia'].apply(lambda data: data.split(' ')[0])
        df['Powierzchnia'] = df['Powierzchnia'].apply(lambda data: float(data.replace(',', '.')))

        # removing unnecessary columns
        df.drop(['Tytul', 'Lokalizacja', 'URL'], axis=1, inplace=True)

        # One hot encode and add to frame
        Heading = pd.get_dummies(df, columns=['Rodzaj zabudowy', 'Ogrzewanie', 'Stan wykończenia','Forma własności'])
        df = pd.concat([df, Heading], axis=1)  # wstawienie do DataFrame

        # counting distance and duration with google API
        gmaps = googlemaps.Client(key='xxx')
        API_LIST_distance = []
        API_LIST_duration = []

        for i, y in zip(locations_coordinations[0], locations_coordinations[1]):
            result = gmaps.distance_matrix(city_center, (i, y), mode='driving')
            distance = (result['rows'][0]['elements'][0]['distance']['text'])
            duration = (result['rows'][0]['elements'][0]['duration']['text'])
            API_LIST_distance.append(distance)
            API_LIST_duration.append(duration)

        API_Google_Distance = pd.Series(API_LIST_distance,name='API_Google_Distance')
        API_Google_Duration = pd.Series(API_LIST_duration,name='API_Google_Duration')

        df['API_Google_Distance'] = API_Google_Distance
        df['API_Google_Duration'] = API_Google_Duration


        #  dropping duplicate columns
        df.drop(['Ogrzewanie', 'Stan wykończenia', 'Forma własności', 'Rodzaj zabudowy'], axis=1, inplace=True)
        # dropping duplicate columns
        df_clear = df.T.drop_duplicates().T

        # removing unnecessary columns
        df_clear = df_clear.drop(columns=['manhattan', 'API_Google_Duration', 'Stan wykończenia_do zamieszkania'])

        # rename colums
        df_clear = df_clear.rename(
            columns={'Forma własności_spółdzielcze wł. z KW': 'Forma własności_spółdzielcze wł z KW'})

        # removing min. and km
        df_clear['API_Google_Distance'] = df_clear['API_Google_Distance'].apply(lambda data: float(data.split(" ")[0]))
        df_clear['API_Google_Distance'] = df_clear['API_Google_Distance'].apply(lambda data: 0 if (data == 1) else data)

        def rm_sigma(dataFrame, col_name='Cena', sigma=2):
            mean = dataFrame[col_name].mean()
            std = dataFrame[col_name].std()
            sigma_thresh_up = sigma * std + mean
            sigma_thres_down = mean - sigma * std
            dataFrame = dataFrame[(dataFrame[col_name] < sigma_thresh_up) & (dataFrame[col_name] > sigma_thres_down)]
            return dataFrame

        # removing misfit values
        df_clear = rm_sigma(df_clear, col_name='Cena', sigma=2).reset_index(drop=True)
        # save
        df_clear.to_csv(filepath, sep=';', index=False, encoding='utf-8-sig')
        self.df_clear = df_clear

   # function to save our frame to Mongo
    def Save_to_Mongo(self,city,city_short):

        df_clear = self.df_clear
        mongo_db = pymongo.MongoClient("mongodb://localhost:27017/")
        # name our base
        db_Mongo_name =  city

        # deleting base if exist
        for db_n in mongo_db.list_database_names():
            if (db_n == db_Mongo_name):
                mongo_db.drop_database(db_Mongo_name)

        # create base
        flats_db_date = mongo_db[db_Mongo_name]

        # split frame to X and Y
        X = df_clear.drop(columns=['Cena'])
        Y = df_clear['Cena']
        flats_db_x = city_short + '_' + 'flats_x'
        flats_db_y = city_short + '_' + 'flats_y'
        flats_db_date[flats_db_x].insert_many(X.to_dict('records'))
        flats_db_date[flats_db_y].insert_many(Y.to_frame().to_dict('records'))


if __name__ == '__main__':
    pass




