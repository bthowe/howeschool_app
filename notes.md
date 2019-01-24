1. test enter_performance
2. clean up code
3. merge to master

2. for each page for each user test...
    1. functions correctly
    2. buttons work
    4. writes to database
    5. side menu is correct
    6. cannot access forbidden pages
3. deposit money
4. enter math book info data 
5. dashboards working
    1. I'd like to change the daily math input to show the daily performance
6. production and development frameworks.



math peformance input > input button screen over the performance plot with breadcrumbs to go back to the input screen
math peformance input + input buttons > performance plot with button to return 


I wonder if it would be better to make an aggregation table (the big one) that I can query quickly rather than create and load everytime I login, etc.



smaller bugs
1. chart js I'm seeing in console inspect
2. Why aren't the forms validating
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