import warnings
from collections import Counter

import pandas as pd
import geopy.distance
from data.data_manager import Data
from data.levenshtein import create_word, levenshtein
from predictor.predictor import predict

warnings.simplefilter(action='ignore', category=Warning)


def recommend_similar_locations(user_id: int, category: str):
    d = Data()
    DATAFRAME = d.project_df  # read-only
    df_user = DATAFRAME[DATAFRAME.User_ID == user_id]

    if df_user.empty:
        print("\n###ID does not exist!###")
        return
    if DATAFRAME[DATAFRAME.Venue_category_name == category].empty:
        print("\n###Category does not exist!###")
        return

    visited_locations = df_user[df_user.Venue_category_name == category]
    most_recent_activity = df_user.loc[df_user['UTC'] == max(df_user.UTC)]

    user_lat = float(most_recent_activity.Lat.values[0])
    user_lon = float(most_recent_activity.Lon.values[0])

    offset = 0.05
    while True:
        locations_df = DATAFRAME.loc[
            (DATAFRAME['Venue_category_name'] == category) & (DATAFRAME['Lat'] <= user_lat + offset) & (
                    DATAFRAME['Lat'] >= user_lat - offset) & (
                    DATAFRAME['Lon'] >= user_lon - offset) & (DATAFRAME['Lon'] <= user_lon + offset)]
        for location in list(visited_locations.Venue_ID.values):
            if (locations_df['Venue_ID'] == location).any():  # remove already visited locations
                locations_df = locations_df.drop(locations_df[locations_df.Venue_ID == location].index)
        locations_df = locations_df.drop_duplicates('Venue_ID', keep='last')
        if len(locations_df.index) >= 10 or offset > 0.5:
            break
        else:
            offset += 0.01
    locations_df = locations_df.drop('User_ID', axis=1).drop('UTC', axis=1).drop('Timezone_offset_min', axis=1)
    list_recommendations = locations_df[:10]

    # TEST

    # user_location = [user_lat, user_lon]
    # for index, row in list_recommendations.iterrows():
    #     print(geopy.distance.geodesic(user_location, [row.Lat, row.Lon]))  # print distance to each location

    # TEST

    return list_recommendations


def recommend_meetup(user_ids: []):
    d = Data()
    DATAFRAME = d.project_df  # read-only
    prediction_str: str = ''
    lat_coordinates = []
    lon_coordinates = []
    for uid in user_ids:
        df_user = DATAFRAME[DATAFRAME.User_ID == uid]
        if df_user.empty:
            print("\n###ID does not exist!###")
            return
        category = df_user.sample()  # choose one random location the user has visited

        # TEST

        # print(category)  # prints the random location that was chosen

        # TEST

        prediction_str += (category.Venue_category_name.values + '.')

        most_recent_activity = df_user.loc[df_user['UTC'] == max(df_user.UTC)]
        lat_coordinates.append(most_recent_activity.Lat.values[0])
        lon_coordinates.append(most_recent_activity.Lon.values[0])

    prediction_str = prediction_str[0][:-1]
    selected_category = predict(prediction_str)  # predict a fitting venue category

    # this creates a "square" within we can look for a suiting location
    min_lat = min(lat_coordinates)
    max_lat = max(lat_coordinates)
    min_lon = min(lon_coordinates)
    max_lon = max(lon_coordinates)
    center = [(max_lat + min_lat) / 2, (max_lon + min_lon) / 2]

    locations_df = DATAFRAME.loc[  # find all locations within the square
        (DATAFRAME['Venue_category_name'] == selected_category) & (DATAFRAME['Lat'] < max_lat) & (
                DATAFRAME['Lat'] > min_lat) & (
                DATAFRAME['Lon'] < max_lon) & (DATAFRAME['Lon'] > min_lon)]

    distance_dict = {}
    for vid in locations_df.Venue_ID.unique():
        venue = locations_df.loc[locations_df['Venue_ID'] == vid]
        coords_venue = (venue.Lat.values[0], venue.Lon.values[0])
        distance = geopy.distance.geodesic(center, coords_venue).km  # get distance between each location
        distance_dict.update({vid: distance})  # and the center of the square

    locations_df = locations_df.drop('User_ID', axis=1).drop('UTC', axis=1).drop('Timezone_offset_min', axis=1)
    # return the location with the minimum distance to the center
    return locations_df.loc[locations_df['Venue_ID'] == min(distance_dict, key=distance_dict.get)].iloc[0]


def recommend_similar_users(user_id: int):
    comparison_dict = {}  # stores user IDs of others and their distance to the user
    uids = Data.project_df[Data.project_df.User_ID != user_id].User_ID.unique()
    user_word = create_word(user_id)  # create the word from all the categories the user visited
    if user_word == '':
        print("\n###ID does not exist!###")
        return
    for uid in uids:
        comparison_dict.update({uid: levenshtein(user_word, create_word(uid))})  # compare with other users
    similar_users = []  # lower value means closer
    i = 0  # to the users' interests
    while i < 10:  # get 10 most similar users
        similar_users.append(min(comparison_dict, key=comparison_dict.get))
        comparison_dict.pop(min(comparison_dict, key=comparison_dict.get))
        i += 1

    # TEST

    # counter_user = dict(Counter(d.get_user_categories(uid=user_id)))
    # keys = counter_user.keys()
    # sorted_keys = sorted(keys)
    # sorted_user = {}
    # for key in sorted_keys:
    #     sorted_user[key] = counter_user[key]
    # print(sorted_user)
    # print()
    # for user in similar_users:
    #     counter_user = dict(Counter(d.get_user_categories(uid=user)))
    #     keys = counter_user.keys()
    #     sorted_keys = sorted(keys)
    #     sorted_user = {}
    #     for key in sorted_keys:
    #         sorted_user[key] = counter_user[key]
    #     print(sorted_user)

    # TEST

    return similar_users


def input_help():
    d = Data()
    print("CATEGORIES:")
    print(d.category_dict.keys())
    print("USERS:")
    print(sorted(d.user_ids))


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 300)
    print("####################################")
    print("########## LEISURE RADAR ###########")
    print("########## OTH REGENSBURG ##########")
    print("####################################\n")

    running = True
    while running:
        print("\n(1) Recommend ten locations")
        print("(2) Recommend meetup location")
        print("(3) Find ten most similar users")
        print("(h) Show available users and categories")
        print("(q) Quit program")

        command = input("Please enter a command: ")
        if command == '1':
            try:
                uid_input = int(input("Enter your ID: "))
            except ValueError:
                print("Input is not a number. It's a string")
                continue
            category_input = input("Enter a category: ")
            result1 = recommend_similar_locations(uid_input, category_input)
            print(result1)
        elif command == '2':
            try:
                uids_input = [int(input("Enter ID of user #1: ")), int(input("Enter ID of user #2: ")),
                              int(input("Enter ID of user #3: ")), int(input("Enter ID of user #4: ")),
                              int(input("Enter ID of user #5: "))]
            except ValueError:
                print("Input is not a number. It's a string")
                continue
            result2 = recommend_meetup(uids_input)
            print(result2)
        elif command == '3':
            try:
                uid_input3 = int(input("Enter your ID: "))
            except ValueError:
                print("Input is not a number. It's a string")
                continue
            result3 = recommend_similar_users(uid_input3)
            print(result3)
        elif command == 'h':
            input_help()
        elif command == 'q':
            running = False
        else:
            print("###Invalid command!###")
