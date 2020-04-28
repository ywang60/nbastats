# nbastats

This project allows user to input their favorate team and look at team stats

A valid API is provided in secret.py file.
- The program will ask users to input their intended search region which include central, pacific, southeast, southwest, northwest. Enter the valid key to continue the program. a new promot will be initiated if uses's input is invalid
- If user's input is valid, the program will ask user to select a team inside of the region and ask if the user want to see the stats page of the team. If user entered yes, the program will lead the user to the web page. If the user entered no, the program will ask user id the user want to see the stats plot of the team instead of directing to the web page. 
- User could select four kinds of stats which are GS, GP, PTS, MIN. With entering a valid stats key, the program will generate the user a scatter plot with players' name as x and stats as y axis. 
-User could switch region and team during certain point as well as exit the program by entering 'exit'.
