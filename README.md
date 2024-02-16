# FinalProject
##Parts that include in my project are an app.py a database (sqlite3), a templates folder to store all of the templates and a static folder to store the styling of those html templates.
###In app.py, there are many functions:
- The first part is the import, since I'm using Flask as my frame work, I included all of the needed library. I also include a request since I need to have a login session for users.
- The next part is to define all the necessary variables and connect to the database
- The first function of the program is to get the values from USDA FoodData Central using APIs, using the name of the food input in and return the calories, protein,...
- The next function is index which prompt the user wwith a TDEE calculator. The index will check for name and password from session, if yes, only then will return the index.html. In the index.html, the page ask the user for basic infomation and return the values to the next function(bmr)
The next function is bmr, which takes all the values from index.html and calculate the bmr and update the person data for later login. Bmr will return bmr.html, which will prompt the user with the information the typed in and ask them for their level of activeness and return to the next function(tdee)
The tdee function takes the activeness of a person and the bmr values to calculate the TDEE off that person then it will return the tdee.html. The tdee.html shows the TDEE value and ask the user for the food they consumed and return the add function
The add function will add the value from the food using the first function, insert to the macro table and redirect to tracking
In the tracking function, the data will be pull from the macro table and display in the traking.html. In tracking.html there will be 2 forms that return to the add function(which add more food) and another is delete(which similar to add but use id to delete and return to the delete function).
Last but not least is the logout function to log the user out
