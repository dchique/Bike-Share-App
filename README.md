# Bike-Share-App
 
To run our visualization:

- Run `pip install -r requirements.txt`
- Run `python home.py`
- Navigate to http://localhost:8080

----
Our visualization uses a file that contains all predictions for the week of August 25-August 31
Our model exports different files and we use a small script to concated all 4 files from the clusters into a single file.

To run the script:

- Navigate to root directory of the app folder
- run `python Tools/cluster_join.py`