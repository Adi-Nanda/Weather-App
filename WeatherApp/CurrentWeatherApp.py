# Display current weather

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLineEdit, QLabel, QMainWindow, QListWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
import sys
import requests

class WeatherApp(QMainWindow):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.heading_label = QLabel("Weather Today", self)
        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("Enter city")
        self.search_button = QPushButton(self)
        self.search_icon = QIcon(QPixmap("icons/searchicon.png"))
        self.grid_menu_layout = QGridLayout()
        self.temp_unit = "metric" # metric = C , imperial = F

        self.weather_data = None
        self.final_geodata  = None

        self.initUI()

    def initUI(self):
        self.setGeometry(350, 60, 800, 650)
        self.setWindowTitle("Weather APP")

        self.search_button.setIcon(self.search_icon)
        self.search_button.setFixedSize(60, 60)
        self.search_button.setIconSize(QSize(25, 25))
        self.city_input.setMaximumSize(800, 50)

        self.heading_label.setObjectName("heading")
        self.search_button.setObjectName("search_button")
        self.setStyleSheet("""
                        QMainWindow{
                            background-image: url(icons/background1.jpg);
                            background-position: center;
                            background-repeat: no-repeat;
                        }
                        QLabel#heading{
                            font-size: 40px;
                            font-family: Roboto;
                            color: white;
                            font-weight: bold;
                            margin: 30px;
                        }
                        QPushButton#search_button{
                            border-radius: 30px;
                            background-color: hsl(4, 0%, 100%);
                        }
                        QPushButton#search_button:hover{
                            background-color: hsl(4, 0%, 60%);
                        }
                        QPushButton#search_button:pressed{
                                background-color: hsl(4, 0%, 80%);
                        }             
                        QLineEdit{
                            font-size: 25px;
                            font-family: Roboto;
                            background: white;
                            color: black;
                            border-radius: 25px;
                            padding: 0px 15px;
                        }
                """)
        self.grid_menu_layout.addWidget(self.city_input, 0, 0)
        self.grid_menu_layout.addWidget(self.search_button, 0, 1)
        self.grid_menu_layout.setContentsMargins(25, 0, 25, 0)

        vbox_menu = QVBoxLayout()
        vbox_menu.addWidget(self.heading_label)
        vbox_menu.addLayout(self.grid_menu_layout)

        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_menu_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        heading_input_group = QWidget()
        heading_input_group.setLayout(vbox_menu)

        self.setMenuWidget(heading_input_group)

        # Get the label's ideal width and set it as the window's minimum width
        heading_width = self.heading_label.sizeHint().width()
        self.setMinimumWidth(heading_width + 20)

        self.search_button.clicked.connect(self.on_search)

    def on_search(self):
        self.setCentralWidget(None)
        try:
            self.grid_menu_layout.removeWidget(self.list_buttons)
        except Exception:
            pass

        if self.city_input.text() == '':
            return
        elif not self.city_input.text().isalpha():
            self.display_error("Invalid characters in city name")
            return

        self.geocode()

    def geocode(self): # returns the latitude and longitude
        city = self.city_input.text()

        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit={5}&appid={self.api_key}"
        # geocoding converts city names to latitude and longitudes to use in weather API request

        # error handling. terminate this function if an exception is raised
        response = self.get_response(url)
        if response == -1:
            return

        try:
            data = response.json()
        except Exception:
            self.display_error("Cannot read data")

        if data == []:
            self.display_error("Location not found")
            return
        elif (data[0]['name']).upper() != city.upper():
            self.display_error("Location not found")
            return

        # If there is no error in geocoding
        else:
            self.final_geodata = self.use_georesponse(data)
            # final_geodata is a list of dictionaries of locations
            if len(self.final_geodata) > 1:
                # if there are multiple locations then show options
                #  Multiples locations ask for further input
                # Don't call get weather from here then
                self.show_options(self.final_geodata)

            else:
                # If only one location call get weather
                self.get_weather(self.final_geodata[0]['lat'], self.final_geodata[0]['lon'])

    def use_georesponse(self, data): # will return a list of dict of unique locations to use
        data_geocoding = data # gives a list of multiple responses if more cities found with same name

        # need to check if the state and country same or not
        try: # check if there is state in data
            data_geocoding[0]['state']
            seen_state = set()
            seen_country = set()
            final_geodata = [d for d in data_geocoding if not ((d['state'] in seen_state or seen_state.add(d['state']) and
                                                             d['country'] in seen_country or seen_country.add(d['country'])))]
        except Exception: # if there is no state in the dictionary then use country
            seen_country = set()
            final_geodata = [d for d in data_geocoding if not (d['country'] in seen_country or seen_country.add(d['country']))]

        return final_geodata

    def show_options(self, data):
        central_widget = QWidget()

        n = len(data)
        # setting text in button_names here
        button_names = []
        for i in range(n):
            try:
                button_names.append(f"{data[i]['name']} | {data[i]['state']} | {data[i]['country']}") # if changing separate symbol also change split method in click_options method
            except Exception:
                button_names.append(f"{data[i]['name']} | {data[i]['country']}")

        self.list_buttons = QListWidget(central_widget)
        self.list_buttons.addItems(button_names)

        # make styling of list buttons
        self.list_buttons.setStyleSheet("""
                    QListWidget{
                        font-size: 22px;
                        background-color: white;
                        border: 0px;
                        border-radius: 25px;
                    }
                    QListWidget::item{
                        font-family: Roboto; 
                        background-color: white;
                        color: black;
                        border: 0px;
                        border-radius: 25px;
                        padding: 10px 10px;
                    }
                    QListWidget::item:hover{
                        background-color: hsl(0, 0%, 70%);
                    }
        """)
        self.list_buttons.setGeometry(40, 0, 800, 52*n)
        self.list_buttons.setFixedHeight(self.list_buttons.height())
        self.list_buttons.setMaximumSize(self.city_input.maximumWidth(), self.list_buttons.height())

        self.grid_menu_layout.addWidget(self.list_buttons, 1, 0)

        self.list_buttons.itemClicked.connect(self.click_option)

    def click_option(self, clicked_item):
        # need to get lat and lon here from self.final_geodata and make a call the self.get_weather(lat, lon)
        # format is city, state, country
        location = clicked_item.text().split('|')
        location = list(map(str.strip, location))

        if len(location[1]) != 2: # if the second element is not length 2 then it's a state
            # city -> location[0] | state -> location[1] | country -> location[2]
            for item_dict in self.final_geodata:
                if item_dict['state'] == location[1] and item_dict['country'] == location[2]:
                    lat = item_dict['lat']
                    lon = item_dict['lon']
                    break
        else:
            # city -> location[0] | country -> location[1]
            for item_dict in self.final_geodata:
                if item_dict['country'] == location[1]:
                    lat = item_dict['lat']
                    lon = item_dict['lon']
                    break

        self.grid_menu_layout.removeWidget(self.list_buttons)
        self.list_buttons.deleteLater()

        self.get_weather(lat, lon)

    def get_weather(self, lat, lon):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units={self.temp_unit}&lang=eng"

        response = self.get_response(url)
        if response == -1:
            return

        # error handling here
        try:
            self.weather_data = response.json()
        except Exception:
            self.display_error("Cannot read data")
            return

        # print(self.weather_data)
        self.display_weather()

    def get_response(self, url):
        # this takes the url and only checks for exceptions related to it
        # returns the response if no error
        # returns -1 if error
        try:
            response = requests.get(url)
            # this raises an exception if there is an HTTPError (as try doesn't raise this automatically)
            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as e: # some HTTP error like 404
            match response.status_code:
                case 400: # for bad request. Couldn't understand or process it due to something wrong with the request itself, like invalid syntax or data
                    self.display_error("Bad request\n\nPlease check your input")
                case 401: # for unauthorized request. Maybe the API key is incorrect or inactive
                    self.display_error("Unauthorized\n\nInvalid API key")
                case 403: # forbidden. Client doesn't have authority to use data even though the server knows the client
                    self.display_error("Forbidden\n\nAccess is denied")
                case 404: # Not found
                    self.display_error("City not found")
                case 500: # internal server error
                    self.display_error("Internal server error\n\nPlease try again later")
                case 502: # bad gateway
                    self.display_error("Bad gateway\n\nInvalid response from the server")
                case 503: # service unavailable
                    self.display_error("Service unavailable\n\nServer is down")
                case 504: # gateway timeout
                    self.display_error("Gateway timeout\n\nNo response from the server")
                case _:
                    self.display_error(f"HTTP Error {e}")
            return -1
        except requests.exceptions.ConnectionError:
            self.display_error("Network Error\n\nCheck your internet connection")
            return -1
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error\n\nThe request timed out")
            return -1
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too many redirects\n\nCheck the URL")
            return -1
        except requests.exceptions.RequestException as e: # exception due to network or bad url
            self.display_error(f"Request Error:\n\n{e}")
            return -1

    def display_error(self, message): # error if location not found or request unsuccessful
        error_label = QLabel(message)
        error_label.setStyleSheet("""
                font-size: 45px;
                font-family: Roboto;
                font-weight: bold;
                color: hsl(136, 0%, 80%);
        """)
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setCentralWidget(error_label)

    def display_weather(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # making widgets start ----------------------------------------------
        place_label = QLabel(f"{self.weather_data['name']}, {self.weather_data['sys']['country']}")

        temperature = f"{self.weather_data['main']['temp']}°{'C' if self.temp_unit == 'metric' else 'F'}"
        temp_label = QLabel(temperature)

        feels_like_label = QLabel(f"Feels like: {self.weather_data['main']['feels_like']}°{'C' if self.temp_unit == 'metric' else 'F'}")
        max_temp = self.weather_data['main']['temp_max']
        min_temp = self.weather_data['main']['temp_min']
        max_min_templabel = QLabel(f"{max_temp}° | {min_temp}°")

        iconid = self.weather_data['weather'][0]['icon']
        image_pixmap = QPixmap(f"icons/{iconid}.png")
        image_label = QLabel()
        image_label.setPixmap(image_pixmap)

        description_label = QLabel(f"{self.weather_data['weather'][0]['main']} ({self.weather_data['weather'][0]['description']})")

        humidity_label = QLabel(f"{self.weather_data['main']['humidity']}%\nHumidity")
        wind_speed = int(self.weather_data['wind']['speed']) * (18/5)
        windspeed_label = QLabel(f"{wind_speed:.2f}km/h\nWind Speed")

        humidity_pixmap = QPixmap("icons/humidity.png")
        humidity_imglabel = QLabel()
        humidity_imglabel.setScaledContents(True)
        humidity_imglabel.setFixedSize(100, 100)
        humidity_imglabel.setPixmap(humidity_pixmap)

        wind_pixmap = QPixmap("icons/wind.png")
        wind_imglabel = QLabel()
        wind_imglabel.setScaledContents(True)
        wind_imglabel.setFixedSize(100, 100)
        wind_imglabel.setPixmap(wind_pixmap)
        # making widgets end ----------------------------------------------

        place_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        temp_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        max_min_templabel.setAlignment(Qt.AlignmentFlag.AlignBottom)
        feels_like_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        humidity_imglabel.setStyleSheet("background-color: white;"
                                        "padding: 5px 5px;")
        wind_imglabel.setStyleSheet("background-color: white;"
                                    "padding: 5px 5px;")

        main_grid_layout = QGridLayout()
        main_grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        temp_group1 = QWidget()
        temp_group1_layout = QHBoxLayout()
        temp_group1_layout.addWidget(temp_label)
        temp_group1_layout.addWidget(max_min_templabel)
        temp_group1_layout.setSpacing(10)
        temp_group1.setLayout(temp_group1_layout)

        temp_group_widget = QWidget()
        temp_group_vbox = QVBoxLayout()
        temp_group_vbox.addWidget(temp_group1)
        temp_group_vbox.addWidget(feels_like_label)
        temp_group_vbox.setSpacing(0)
        temp_group_widget.setLayout(temp_group_vbox)

        humidity_group = QWidget()
        humidity_layout = QHBoxLayout()
        humidity_layout.addWidget(humidity_imglabel)
        humidity_layout.addWidget(humidity_label)
        humidity_group.setStyleSheet("background-color: transparent;")
        humidity_group.setLayout(humidity_layout)

        wind_group = QWidget()
        wind_layout = QHBoxLayout()
        wind_layout.addWidget(wind_imglabel)
        wind_layout.addWidget(windspeed_label)
        wind_group.setStyleSheet("background-color: transparent;")
        wind_group.setLayout(wind_layout)

        hbox = QHBoxLayout()
        humi_wind_group = QWidget()
        hbox.addWidget(humidity_group)
        hbox.addWidget(wind_group)
        hbox.setSpacing(150)
        humi_wind_group.setLayout(hbox)
        humi_wind_group.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);"
                                      "border-radius: 25px;"
                                      "margin: 20px;")
        humi_wind_group.setMaximumSize(wind_group.sizeHint().width() * 3, wind_group.sizeHint().height() + 60)
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_data_group = QWidget()
        icon_data_layout = QVBoxLayout()
        icon_data_layout.addWidget(image_label)
        icon_data_layout.addWidget(description_label)
        icon_data_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_data_layout.setSpacing(0)
        icon_data_group.setLayout(icon_data_layout)

        data_group = QWidget()
        data_layout = QHBoxLayout()
        data_layout.addWidget(temp_group_widget)
        data_layout.addWidget(icon_data_group)
        data_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_layout.setSpacing(50)
        data_group.setLayout(data_layout)

        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(data_group)
        central_layout.addWidget(place_label)
        central_layout.addWidget(humi_wind_group)
        central_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        place_label.setObjectName("place")
        temp_label.setObjectName("temp")
        description_label.setObjectName("description")
        max_min_templabel.setObjectName("min_max_temp")
        feels_like_label.setObjectName("feels_like")
        central_widget.setStyleSheet("""
                    QLabel{
                        font-size: 20px;
                        font-family: Roboto;
                    }
                    QLabel#place{
                        font-weight: bold;
                        font-size: 35px;
                    }
                    QLabel#temp{
                        font-size: 50px;
                    }
                    QLabel#description{
                        font-size: 25px;
                    }
                    QLabel#min_max_temp{
                        font-size: 16px;
                        padding: 6px 0px;
                    }
                    QLabel#feels_like{
                        font-size: 20px;
                        padding: 0px 12px;
                    }
        """)

def main():
    api_key = "c465d1d55d43cf5e2092537966bef293"
    app = QApplication(sys.argv)
    window = WeatherApp(api_key)
    window.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()