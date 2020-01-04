TODO:
2019/12/27
1. I need to add the hard_miss_lst to the aggregate db
2. What's the problem with the right margin
1. what metrics do I want
    1. time
    2. number of problems
    3. correct
    4. hard

other plots:
    1. total time trend (math_performance, or math_aggregate_time)
    2. where in the book they are and how they are progressing (math_performance)
    3. percent correct time trend (math_performance, or math_aggregate)
    4. percent hard time trend (math_performance, or new aggregate db)

main plot: (math_performance)
    * time
    * number of problems
    * correct per problem (positive)
    * hard per problem (negative)
    
    * (no) time per problem (negative)
    fraction correct ---------------- fraction easy
                           |
                           |
                           |
                     time per problem
    
    pcorr: good interval between .9 and 1
    pnhard: should be at 1...no interval
    dur: good interval between 90 minutes and 120.
    probs: good interval is 2/3 of an assignment to 1.
        Use the average number of problems in a chapter to determine 1 and 2/3.
        
    
    
    
    
    
2. what do I need to get these metrics
3. build out the infrastructure
4. make the picture


* need to provide documentation about when to use scripts in db_mgmt_scripts
* kind of thinking I don't do the remove thing correctly...what if I click then remove then click then remove?
* what is the purpose of the entire problems missed, aggregate database? Seems like a lot of wasted storage (but maybe it's not too much).
    * not if I incorporate that other visualization, maybe?




server:
1. set up supervisor
    1. https://www.vultr.com/docs/installing-and-configuring-supervisor-on-ubuntu-16-04
    2. https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvii-deployment-on-linux
2. no kill on logout but redirect.
3. set up crons jobs 
    1. backup data
    2. shutdown the server at a certain time? Or should I just leave it up and running?
        1. Have Calvin turn it on around the time he uses it.
        2. Have a Chron job turn it off at like 10 pm
        3. Turn it off manually if done with it.
            1. I could have an endpoint that turns it off.
    3. pull from master
4. clean up repo for production


if logged in , redirect to main menu


1. enter math book info data
2. server
    1. production and development frameworks.
        1. I'm thinking I'll just use develop for building
        2. When ready, merge into master.
        3. Never prototype in master.
        4. the server pulls master in cron job every day
        5. the server only runs master
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
    3. pull master
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
