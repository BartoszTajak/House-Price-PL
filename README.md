The main goal of the application is to predict the cost of flats according to entered data by users and data scraped from the website www.OtoDom.pl.
In order to get the best results program creates a 6 regression model which compares and extracts the model with the smallest error.
Models used in the program:
1.Linear Regression
2.Decision Tree Regressor
3.Random Forest Regressor
4.SVR
5.XGBoost
6.Neural network

Program is divaided to 3 secion: 
1 Regression_OtoDom_GUI - the main GUI 
2 Regression_OtoDom_Scraping - module for scraping and converting data to panda's format
3.Regression_OtoDom_Models - section included all regression models with compare and cout the best of them.

Tabs in GUI:
TAB_1
The first tab is for scraping data from a website. Can choose the place, price, and area.
After finished downloading, data are cleaned and saved to MongoDB and .csv files.
Section "domy" , and "działaki" are unavailable yet.

TAB_2
We can use the second tab to visualization our data, saved before. There are 6 models to compare: 
Each model is split into 2 section Train and Test set, each of them consist of MSE error

TAB_3
The last tab allows us to estimate the cost of a flat for the chosen place.
In spite of all models working fine and data are up to date there are some points to improve. 
For example, data don't include the price of parking place which raise the total cost.


Below short presentation.
https://youtu.be/MCWH2MypV8s

