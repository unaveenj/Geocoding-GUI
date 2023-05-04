import PySimpleGUI as sg
import pandas as pd
import os
from geopy.geocoders import Nominatim
from tqdm import tqdm

def retrieve_lat_long(file_path, road_column, window):
    # Load the csv file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Create an instance of the Nominatim geocoder
    geolocator = Nominatim(user_agent="geoapiExercises")

    # Get the number of records in the DataFrame
    num_records = len(df)

    # Divide the number of records by 100 to get the number of chunks
    num_chunks = num_records // 100

    # Check if there are any incomplete chunks
    if num_records % 100 > 0:
        num_chunks += 1

    # Keep track of the starting index of each chunk
    start_index = 0

    # Loop through each chunk with a progress bar
    for i in tqdm(range(num_chunks), desc='Retrieving Latitude and Longitude', leave=False, unit=' chunks', position=0, ascii=True):
        # Get the end index for the current chunk
        end_index = min(start_index + 100, num_records)

        # Get the sub-DataFrame for the current chunk
        chunk = df.iloc[start_index:end_index]

        # Check if the latitude and longitude for the current chunk have already been saved to a csv file
        filename = 'roads_lat_long_{}.csv'.format(start_index)
        if os.path.exists(filename) and not pd.read_csv(filename, error_bad_lines=False, warn_bad_lines=False).empty:
            # If the file exists, update the starting index for the next chunk
            start_index = end_index
            continue

        # Create two empty lists to store the latitude and longitude values
        latitude = []
        longitude = []

        # Iterate over the road names in the current chunk
        for road in chunk[road_column]:
            try:
                # Use the geocoder to retrieve the latitude and longitude of the road
                location = geolocator.geocode(road + ', Singapore')
                latitude.append(location.latitude)
                longitude.append(location.longitude)
            except:
                latitude.append(0)
                longitude.append(0)
                print('Timeout error at record {}'.format(start_index + len(latitude)))
                continue

        # Add the latitude and longitude lists as new columns in the current chunk
        chunk['latitude'] = latitude
        chunk['longitude'] = longitude

        # Save the current chunk to a csv file
        chunk.to_csv(filename, index=False)

        # Update the starting index for the next chunk
        start_index = end_index

    # Update the window to indicate that the retrieval is complete
    window.FindElement('tqdm').Update(value='Output generated')

def main():

    layout = [
        [sg.Input(key='file_path'), sg.FileBrowse()],
        [sg.Button('Upload')],
        [sg.Text('Select the road name column:')],
        [sg.Combo(values=[], key='road_column', size=(20, 1))],
        [sg.Button('Submit'), sg.Cancel()],
        [sg.Text(key='tqdm', size=(40, 1))]
    ]



    # Create the window
    window = sg.Window('Retrieve Latitude and Longitude').Layout(layout)

    # Loop until the user closes the window or clicks the Cancel button
    while True:
        event, values = window.Read()
        if event in (None, 'Cancel'):
            break

        if event == 'OK':
            # Get the file path from the user input
            file_path = values['file_path']

            # Read the first few rows of the csv file to get the column names
            df = pd.read_csv(file_path, nrows=0)
            column_names = df.columns.tolist()

            # Update the values in the drop-down list with the column names
            window.FindElement('road_column').Update(values=column_names)

        if event == 'Submit':
            # Get the road name column from the user input
            road_column = values['road_column']

            # Call the retrieve_lat_long function to retrieve the latitude and longitude
            retrieve_lat_long(file_path, road_column, window)

    # Close the window
    window.Close()

if __name__ == '__main__':
    main()
