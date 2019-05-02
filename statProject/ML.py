import cv2
import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import csv
import re
import random
import face_recognition
import seaborn as sns

def reccomendMoviesFor(userId):
    warnings.filterwarnings('ignore')  # for runtime warnings
    data = pd.read_csv('ratings.csv', dtype = {'userID' : str, 'rating' : float})
    userRatedMovie = data[(data['userId'].astype(str) == userId)].sort_values(by = "rating", ascending = False).drop_duplicates('movieId')[:5]
    userRatedMovie = userRatedMovie[['movieId', 'rating']]
    moveiesTitles = pd.read_csv('movies.csv')
    moveiesTitles = pd.merge(moveiesTitles, userRatedMovie, on = 'movieId')[['title', 'rating']].sort_values(by = "rating", ascending = False)
    movies = []
    for i in range(len(moveiesTitles)):
        if moveiesTitles['rating'][i] >= 4:
            moveisListId = reccomendMovies(moveiesTitles['title'][i])
            for id in moveisListId:
                movies.append(id)
        else:
            moveisListId = reccomendMovies(moveiesTitles['title'][i], like = False)
            for id in moveisListId:
                movies.append(id)
        if len(list(set(movies))) > 1000:
            break
    movies = random.choices(list(set(movies)), k=50)
    movies = list(set(movies))
    return movies

def searchMovie(movieName):
    warnings.filterwarnings('ignore')  # for runtime warnings
    titles = pd.read_csv('movies.csv', dtype = {'title' : str})['title']
    movies = []
    for title in titles:
        if re.search(movieName, title, re.IGNORECASE):
            moveisListId = reccomendMovies(title)
            for id in moveisListId:
                movies.append(id)
            if len(set(movies)) > 1000:
                break
    movies = list(set(movies))
    movies = random.choices(movies, k = min(50, len(movies)))
    movies = list(set(movies))
    return movies

def isUserRated(userId):
    warnings.filterwarnings('ignore')  # for runtime warnings
    data = pd.read_csv('ratings.csv', dtype={'userID': str})
    data = data[(data['userId'].astype(str) == userId)]
    return len(data) != 0

def reccomendMovies(movieName, ratingLimit = 10, like = True):
    warnings.filterwarnings('ignore')  # for runtime warnings
    data = pd.read_csv('ratings.csv', sep=',')  # read movies data
    moviesTitles = pd.read_csv('movies.csv')  # get movies name and tags
    data = pd.merge(data, moviesTitles, on='movieId')  # merge movies data

    ratings = {'rating': [], 'numOfRating': []}
    ratings = pd.DataFrame(data=ratings)  # creating new DataFrame(like database)
    ratings['rating'] = data.groupby('title')['rating'].mean()
    ratings['numOfRating'] = data.groupby('title')['rating'].count()  # getting number of ratings for each movie

    # visualizing data
    # ratings['rating'].hist(bins = 50) # class interval
    # plt.show()
    # sns.jointplot(x='rating', y='numOfRating', data=ratings)
    # plt.show()

    moviesMatrix = data.pivot_table(index="userId", columns="title",
                                    values="rating")  # creats matrix rows(users id) columns(movie title) values(user rate for the movie)
    movieRating = moviesMatrix[movieName]  # get rating column for the movie which u want to recommend movies like it (Rmovie)
    similarToTheMovie = moviesMatrix.corrwith(movieRating)  # getting correlations among the moves and the Rmovie

    moviesCorr = pd.DataFrame(similarToTheMovie, columns=["correlation"])  # convert correlation to DataFrame
    # print(moviesCorr)
    moviesCorr.dropna(inplace=True)  # drop null values as some movies not rated
    moviesCorr = moviesCorr.join(ratings['numOfRating'])  # adding number of ratings for the correlation of each movie
    moviesCorr = moviesCorr[moviesCorr['numOfRating'] >= ratingLimit]
    moviesCorr = moviesCorr.sort_values(by="correlation",
                                                                                  ascending=False)  # get movies that number of ratings more than the limit and sort by corrleations
    moviesLike = moviesCorr[0:20]  # get first 10 correlations
    moviesLikeId = pd.merge(moviesLike, moviesTitles, on="title")['movieId']  # get movies id
    moviesNotLike = moviesCorr[-21:-1]  # get last 10 correlations
    moviesNotLikeId = pd.merge(moviesNotLike, moviesTitles, on="title")['movieId']  # get movies id
    moviesImdbId = pd.read_csv('links.csv', dtype = {'imdbId' : str})
    moviesLikeId = pd.merge(moviesLikeId, moviesImdbId, on = "movieId")['imdbId']
    moviesNotLikeId = pd.merge(moviesNotLikeId, moviesImdbId, on = "movieId")['imdbId']
    if like:
        return random.choices(moviesLikeId, k=len(moviesLikeId))
    return random.choices(moviesNotLikeId, k=len(moviesNotLikeId))

def getMoviesImmdbID():
    warnings.filterwarnings('ignore')  # for runtime warnings
    moviesIdbID = pd.read_csv('links.csv', dtype = {'imdbId' : str})['imdbId']
    moviesIdbID = moviesIdbID.tolist()
    moviesIdbID = random.choices(moviesIdbID, k=len(moviesIdbID))
    return moviesIdbID

def addUserRating(userId, movieId, rate, isImdbId = False):
    warnings.filterwarnings('ignore')  # for runtime warnings
    row = [userId, movieId, rate]
    if isImdbId:
        data = pd.read_csv('links.csv', dtype = {'imdbId' : str})
        movieId = data[data.imdbId == movieId]
        movieId = movieId.iloc[0]['movieId'].astype(str)
    row = [userId, movieId, rate +'.0', '0000000000']
    with open('ratings.csv', 'a') as file:
        writer = csv.writer(file, lineterminator = '\n')
        writer.writerow(row)
    file.close()


def addFavouriteMove(userid, imdbId):
    imdbId = imdbId[2:len(imdbId)]
    row = [userid, imdbId]
    with open('favouriteMovies.csv', 'a') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(row)
    file.close()


def getUserFavouritMovies(userId):
    data = pd.read_csv('favouriteMovies.csv', dtype={'userId' : str, 'imdbId' : str})
    movies = [];
    for i in range(len(data)):
        if userId == data['userId'][i]:
            movies.append(data['imdbId'][i])
    movies = list(set(movies))
    print(movies)
    return movies

def recognize():
    # This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
    # other example, but it includes some basic performance tweaks to make things run a lot faster:
    #   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
    #   2. Only detect faces in every other frame of video.

    # PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
    # OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
    # specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    # Load a sample picture and learn how to recognize it.
    obama_image = face_recognition.load_image_file("ahmed.jpg")
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

    # Load a second sample picture and learn how to recognize it.
    biden_image = face_recognition.load_image_file("biden.jpg")
    biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

    # Create arrays of known face encodings and their names
    known_face_encodings = [
        obama_face_encoding,
        biden_face_encoding
    ]
    known_face_names = [
        "Ahmed Emam",
        "Joe Biden"
    ]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.125, fy=0.125)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()