from data.data_manager import Data


def create_word(uid: int):
    CATEGORY_DICT = Data.category_dict  # read only
    USER_DF = Data.project_df[Data.project_df.User_ID == uid]  # read only
    word = ''
    for row in list(USER_DF.Venue_category_name.values):
        word += chr(CATEGORY_DICT[row])

    return word


def levenshtein(s1, s2):  # returns integer of the distance between the two strings
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[
                             j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character
            # longer than s2
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]
