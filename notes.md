1. enter math book info data
2. server
    1. production and development frameworks.
3. dashboards
    1. I'd like to change the daily math input to show the daily performance after the record button is hit
        1. draw from the aggregate table and then just use the current data with it to show an updated table.
        2. eventually, update the main menu dashboards  
    2. put the dashboards on the main menu page
4. aggregation table
    1. remove and rewrite table daily
5. cron jobs (updating the aggregation table)
    1. https://www.ostechnix.com/a-beginners-guide-to-cron-jobs/
    2. https://kb.iu.edu/d/afiz
    1. update the aggregation table
    2. pay my kids weekly
6. validate forms that I wasn't able to before.



what about a report of time spent with math and vocab?
Maybe enter the information from the time sheet every week.
Get fitbits and pull that information in.


smaller bugs
1. chart js I'm seeing in console inspect
3. refactor the pages with some javascript like enter_performance done differently maybe so there aren't as many strange calls to the server.



weekly input could be formatted better so some of the fields fill the page.


vocab issues:
- quiz
    - red and green colors don't pad the image nicely
- practice
    - button padding and spacing: I can't get the buttons centered.

checks to make sure the data is inserted correctly.
the math exercise input drop down looks funny
the math performance record button is in a weird place.

can send messages to the kids



If I host the server on the raspberry pi
- can I access it from the mac?
- would I want it to send the data to github periodically?
    - I could simply store it on a usb or external harddrive.
    - how would I back it up automatically?
    - just put a dev database in github and develop using that?
        - probably a good idea anyway

https://stackoverflow.com/questions/12657651/connect-device-to-mac-localhost-server
https://stackoverflow.com/questions/9304058/how-to-view-localhost-on-my-ipod-touch
https://stackoverflow.com/questions/3132105/how-do-you-access-a-website-running-on-localhost-from-iphone-browser/41857012#41857012










TODO


1. get things setup on the white computer to run without me having to upload a new executable.
2. generating a pdf with the questions and thoughts from the kids and their scripture study.


todo: predict whether a child is going to miss the next problem from this chapter: condition on history with those types of problems, recent history, etc.
todo: click to zoom into seven or so days before and after that point.
-how do you have a click feature anywhere on the plot and not on a path or circle, etc.?
todo: make sure everything is correct

BACKEND

TIME
* click on book and shows the datapoints, stats, and lines for that book
* be able to click and then get the stats only for that segment.

MIXED
* put a feature in that allows me to order bars by either mean or chapter origin number
* zoom in and out of supplementary plot.

TESTS
* red line that denotes the average across tests completed

VOCAB
* vocab dashboards
    * how many minutes per day
    * how many cards per day and of which type?
    * time per card
    * which cards in a chapter did he spend the most time on?
    * total time per chapter
    * total time per card in chapter

SCRIPTURE THOUGHTS

MAKE THE CHAPTER COME UP AUTOMATICALLY AND CHECK IF ALREADY BEEN ENTERED.
