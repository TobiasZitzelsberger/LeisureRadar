import pandas as pd
from collections import Counter


class Data:
    print("Loading dataset...")
    project_df = pd.read_pickle("dataset_project.pkl")
    category_dict = {}
    categories = project_df.Venue_category_name.unique()
    i = 1
    for c in categories:
        category_dict.update({c: i})
        i += 1
    user_ids = project_df.User_ID.unique()

    def get_user_categories(self, uid):  # return a list of all entries of a single user
        user_df = self.project_df[Data.project_df.User_ID == uid]  # in the form of category names
        return list(user_df.Venue_category_name.values)
