# ETL App with Flask and SQLite
Connex One Project

## Setup
#### Root Directory Tree
```
.
├── IMDB-Movie-Data.csv
├── Readme.md
├── app.py
├── db.py
├── downloads
├── main.py
├── requirements.txt
├── templates
│   ├── dataset.html
│   └── index.html
└── uploads
```

##### Recommended Environment
```
Python 3.8.5
pip3 install -r requirements.txt
```

### How to run
##### Run the command when the above steps are complete at the root directory
```
python3 main.py
```

### Descriptions
##### Following endpoint should be ready for a csv file upload
```
0.0.0.0:5000
```

##### Once file is chosen and uploaded, it will be immediately processed and the result downloaded to your device

##### On the console, the table would be visible in print

##### For pagination of the table, use the following endpoint
```
0.0.0.0:5000/dataset/
```
