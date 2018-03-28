"""
    Author: Koushik Thai
"""

from pathlib import Path
import io
import os
import glob
from bs4 import BeautifulSoup
import csv

# Method to get the score panel information whcih is at the top
def getScoreDetails(scorePanel,movieDetails):
    # Getting the value of the TomatoMeter link 
    ahrefValue = scorePanel.find("a",{"id":"tomato_meter_link"})
    criticRating = ahrefValue.find("span",{"class":"superPageFontColor"}).text
    if criticRating:  
        movieDetails["criticRating"] = criticRating[:-1]
    else:
        movieDetails["criticRating"] = None
    # Rotten Meter    
    rottenMeter = ahrefValue.find("span",{"class":"meter-tomato"})
    if rottenMeter:
        movieDetails["tomatoMeter"] = rottenMeter.get('class')[4]
    else: movieDetails["tomatoMeter"] = None
    # Getting the Score stats container whcih contains all the scores values(user+critic)
    scoreStatsValue = scorePanel.find("div",{"id":"scoreStats"})
    #For each score status value from the critic getting all the details from the critic side
    j=0;
    for eachScore in scoreStatsValue.find_all("div",{"class":"superPageFontColor"}):
        parseEachScore = eachScore.text.split(":")
        if j==0:
            movieDetails[parseEachScore[0].strip()] = parseEachScore[1].strip().strip().split("/")[0]
            j+=1
        else:
            movieDetails[parseEachScore[0].strip()] = parseEachScore[1].strip()
    criticConsensus = scorePanel.find("p",{"class":"critic_consensus"})
    movieDetails["criticConsensus"] = criticConsensus.text.split(":")[1].strip()
    # Moving to audience panel and getting the audience contianer 
    audienceScoreContainer = scorePanel.find("div",{"class":"audience-panel"})
    # Audience rating which was represented as a meter %liked values
    if audienceScoreContainer.find("div",{"class":"meter-value"}):
        movieDetails["audienceMeter"] = (audienceScoreContainer.find("div",{"class":"meter-value"}).find("span",{"class":"superPageFontColor"}).text)[:-1]
    else: movieDetails['audienceMeter'] = None
    # Audience Score details #of user ratings and average rating
    audienceScoreDetails = audienceScoreContainer.find("div",{"class":"audience-info"}).text
    allDetails = ' '.join(audienceScoreDetails .split()).split(" ")
    allSubContainers = audienceScoreContainer.find_all("span",{"class":"subtle superPageFontColor"})
    i=2
    for eachValue in allSubContainers:
        rate = ""
        name = str(eachValue.text)
        rate += "audience - "+name
        if i==2: 
            movieDetails[rate] = allDetails[i].strip().split("/")[0]
        else:
            movieDetails[rate] = allDetails[i].strip()
        i+=3
    return movieDetails
    
# Method to get complete Movie Information like release date etc.,
def getMovieInformation(contentInfo, movieDetails):
    movieSynopsis = contentInfo.find("div",{"id":"movieSynopsis"})
    movieDetails["synopsis"] = movieSynopsis.text.strip()
    movieInfoListContainer = contentInfo.find("ul",{"class":"content-meta info"})
    for eachInfoList in movieInfoListContainer.find_all("li",{}):
        movieDetails[eachInfoList.find("div",{"class":"meta-label subtle"}).text.strip()[:-1]] = eachInfoList.find("div",{"class":"meta-value"}).text.strip()
        #print(eachInfoList.find("div",{"class":"meta-value"}).text.strip())
    return movieDetails

# Method to get the Cast information for the movie
def getCast(castSection, movieDetails):
    actors = []
    if not castSection:
        movieDetails['actos'] = actors
    else:
        for eachInList in castSection.find_all("div",{"class":"media-body"}):
            eachL = eachInList.find("span",{})
            actors.append(eachL.text.strip())
        movieDetails["actors"] = actors
    return movieDetails
    
# Method to get the top critic reviews info present in the page
def getCriticReviewInfo(reviewInfo, movieDetails):
    reviews = []
    for eachReviewsInfo in reviewInfo.find_all("div",{"class":"review_quote"}):
        reviewsInfoEach = eachReviewsInfo.find("div",{"class":"media-body"})
        reviewText = reviewsInfoEach.find("p",{})
        reviewTextInfo = reviewText.text.strip()
        reviews.append(reviewTextInfo)
    movieDetails["criticReviews"] = reviews
    return movieDetails
   
# Method to get the top critic reviews info present in the page
def getAudienceReviewInfo(reviewInfo, movieDetails):
    reviews = []
    for eachReviewInfo in reviewInfo.find_all("div",{"class":"media-body"}):
        reviews.append(eachReviewInfo.find("p",{}).text.strip().replace("Super Reviewer",""))
    movieDetails['topAudienceReviews'] = reviews
    return movieDetails    

# Method to get Movie Name
def getMovieName(movieNameContainer, movieDetails):
    movieName = movieNameContainer.find("h2",{}).text
    print(movieName)
    #movieDetails["movieName"] = movieName.strip()
    return movieDetails
    
# Loading the local path where all the HTML files contain
path = "New Folder/PROJHTML/"
files = glob.glob(path)
i=0;
 
for infile in glob.glob( os.path.join(path, '*.html') ):
    file_exists = os.path.isfile('output2.csv')
    f = open("error.txt","w+")
    print(infile)
    i+=1 
    movieDetails = dict()
    file = open(infile,"r", encoding='utf-8')
    soupified = BeautifulSoup(file,'lxml')
    #soupified = soupified_Bef.encode("utf-8")
    # Get the Movie Name
    if not soupified.find("h1",{"class":"title"}):
        f.write(str(i)+"\t"+infile+"\n")
        continue
    else:
        movieNameInfo = soupified.find("h1",{"class":"title"}).text.strip()
        movieDetails["movieName"] = movieNameInfo
        #movieDetails = getMovieName(movieNameInfo, movieDetails)
        # Get the score panel information container and get all the data
        scorePanel = soupified.find("div",{"id":"scorePanel"})
        movieDetails = getScoreDetails(scorePanel, movieDetails)
        # Get the Movie information containter and get all the data
        contentInfo = soupified.find("section",{"class":"panel panel-rt panel-box movie_info media"})
        movieDetails = getMovieInformation(contentInfo, movieDetails)
        # Get the cast section container and get all the data
        castSection = soupified.find("div",{"class":"castSection"})
        print(movieDetails['movieName'])
        movieDetails = getCast(castSection, movieDetails)
        # Get the Critic Reviews container and get all the data
        criticReviewInfo = soupified.find("div",{"id":"reviews"})
        movieDetails = getCriticReviewInfo(criticReviewInfo, movieDetails)
        # Get the Audience Reviews container and get all the data
        audienceReviewInfo = soupified.find("section",{"id":"audience_reviews"})
        movieDetails = getAudienceReviewInfo(audienceReviewInfo, movieDetails)
        # A dictionary(movieDetails) contains all the information for the movie present in the page
        print(i)
        if not movieDetails.get('In Theaters',None):
            movieDetails['In Theaters'] = ""
        else:
            inTheaters = movieDetails['In Theaters'].split("\n")
            movieDetails['In Theaters'] = inTheaters[0].strip() 
        file.close()
        with open('output2.csv', 'a') as csvfile:
            headers = ['Movie Name', 'Fresh', 'In Theaters','Runtime','Studio','tomatoMeter', 'criticConsensus','audience - User Ratings','actors','Average Rating','Genre','Written By','synopsis','Reviews Counted','criticRating','audience - Average Rating','criticReviews','audienceMeter','Rotten','topAudienceReviews','Rating','Directed By','On Disc/Streaming']
            writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n',fieldnames=headers)
            if not file_exists:
                writer.writeheader() 
            #writer.writeheader()
            writer.writerow({'Movie Name':movieDetails.get('movieName',""),'Fresh':movieDetails.get('Fresh',""),'Runtime':movieDetails.get('Runtime',""),'Studio':movieDetails.get('Studio',""),'tomatoMeter':movieDetails.get('tomatoMeter',""),'criticConsensus':movieDetails.get('criticConsensus',""),'audience - User Ratings':movieDetails.get('audience - User Ratings:',""),'actors':movieDetails.get('actors',""),'Average Rating':movieDetails.get('Average Rating',""),'Genre':movieDetails.get('Genre',""),'Written By':movieDetails.get('Written By',""),'In Theaters':movieDetails.get('In Theaters',""),'synopsis':movieDetails.get('synopsis',""),'Reviews Counted':movieDetails.get('Reviews Counted',""), 'criticRating':movieDetails.get('criticRating',""),'audience - Average Rating':movieDetails.get('audience - Average Rating:',""),'criticReviews':movieDetails.get('criticReviews',""), 'audienceMeter':movieDetails.get('audienceMeter',""),'Rotten':movieDetails.get('Rotten',""),'topAudienceReviews':movieDetails.get('topAudienceReviews',""),'Rating':movieDetails.get('Rating',""),'Directed By':movieDetails.get('Directed By',""),'On Disc/Streaming':movieDetails.get('On Disc/Streaming',"") })