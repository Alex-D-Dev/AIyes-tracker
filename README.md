# AIyes-tracker

I made this project for my studies, and it was assessed by professionals of the sector. 

The project aims at providing a new way to interact with our computer. The idea is to replace the mouse by the gaze. In order to do this, the computer needs to identify the user with the help of the camera. Next, this identification is used by our AI inside the app in order to predict in real time the point of the screen the user is looking at. Then finally, the app will move the cursor to the coordinates predicted by the AI.

With the view to testing this project, you need to use a Python 3.7 environment.

I advise using Anaconda so as to build your environment.

When inside it, you just need to use:

```
pip install --upgrade pip
```

Then

```
pip install -r requirements.txt
```

Now you can use all the notebooks.

If you want to use the full app, you need to install Mysql, import the save_db.sql file and set up your identification.

Then the main script (app.py) is ready to be launched.