Introduction:

LeisureRadar is an interest-based location recommendation system using FourSquare data.


Installation:

Requires Python 3.10+. Required modules can be installed via the requirements.txt.


Features:

The program has a simple command line interface where a command can be executed via entering the digit or letter:

(1) Recommend ten locations
(2) Recommend meetup location
(3) Find ten most similar users
(h) Show available users and categories
(q) Quit program

- recommend_similar_locations(): will have you specify a User ID (int) and a Category Name (str) and return a list of (up to) ten unvisited locations.

- recommend_meetup(): will have you specify five User IDs (int) and return a fitting location where these five users can meet up.

- recommend_similar_users(): will have you specify a User ID (int) and return a list of the ten most similar users.

All results will be displayed on the command line.