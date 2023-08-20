import PySimpleGUI as sg
import pandas as pd
import os
from geopy.geocoders import Nominatim
from tqdm import tqdm


def retrieve_road_name_from_file(file_path, window):
    df = pd.read_csv(file_path)
    geolocator = Nominatim(user_agent="geoapiExercises")

    max_value = len(df)
    progress_bar = window['progressbar']

    road_names = []

    for i, row in enumerate(df.iterrows()):
        latitude, longitude = row[1]['latitude'], row[1]['longitude']
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        address = location.raw.get("address", {})
        road = address.get("road", "Unknown")
        road_names.append(road)

        # Update the progress bar:
        progress = (i + 1) * 100 / max_value
        progress_bar.UpdateBar(progress)
        window['progress_text'].update(f'{int(progress)}%')

    df['road_name'] = road_names
    df.to_csv('output_with_road_names.csv', index=False)


def main():
    layout = [
        [sg.Text('Select a file with Latitude and Longitude:')],
        [sg.Input(size=(60, 1), key='file_path'), sg.FileBrowse('Browse')],
        [sg.Button('Upload and Retrieve Road Names'), sg.Button('Exit')],
        [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progressbar', bar_color=('green', '#D0D0D0')),
         sg.Text('', size=(8, 1), key='progress_text')],
        [sg.Text(size=(80, 1), key='status')]
    ]

    window = sg.Window('Retrieve Road Name from Latitude and Longitude', layout)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        if event == 'Upload and Retrieve Road Names':
            file_path = values['file_path']
            if not file_path:
                sg.popup_error("Please select a valid file first!")
                continue

            try:
                retrieve_road_name_from_file(file_path, window)
                window['status'].update(f'Road names retrieved successfully from {file_path}!')
            except Exception as e:
                sg.popup_error(f"Error processing the file: {e}")
                window['status'].update('Error retrieving road names.')
                window['progressbar'].update_bar(0)  # Reset the progress bar in case of error

    window.close()

if __name__ == '__main__':
    main()
