
# Library Analysis Dashboard 

In this project I have done some sort of analysis using python on library data available in the 
format sqlite3 database. The tables has all detail of reader, loan date, etc. I have
calculated aggregate metrics and individual reader analysis. And finally deploy this analysis using streamlit.

Live - https://manish-singh12-library-dashboard-library-sjgl84.streamlitapp.com/

 


## Project Organization

.streamlit/config.toml                                                   app page configuration
library.db                                                               library database (sqlite3)
library.py                                                               python file (streamlit app)
requirements.txt                                                         libraries and packages 
## Library Analysis

A library is a collection of materials, books or media that are accessible for use and not just for display purposes. A library provides physical (hard copies) or digital access (soft copies) materials, and may be a physical location or a virtual space, or both.

In this dashboard I have done analysis based on all readers collectively (Aggregate metrics) as well as individually (Individual reader analysis). 
## Overview

Aggregate metrics (First page): 

Select sidebar 'Aggregate metrics' to get the following insights.

- Basic Insights
- Monthly Insights
- Quarterly Insights
- Yearly Insights

Individual reader analysis (Second page):

Select sidebar 'Individual reader analysis' to get the insights about 
all individual readers.

- Click on plus to switch forward to next reader and minus to switch back to previous reader.


## Data available

- library.db with the following tables and schema:

![App Screenshot](https://github.com/Manish-Singh12/library_dashboard/blob/main/library_schema.png)



## Steps

- sqlite3.connect to connect the database.
- Python for filtering data.
- plotly.express for making charts.
- Streamlit for deployment.




## Libraries mostly used

- Streamlit
- Plotly
- sqlite3
- Pandas




## Screenshots

![App Screenshot](https://github.com/Manish-Singh12/library_dashboard/blob/main/Screenshot%201.png)

![App Screenshot](https://github.com/Manish-Singh12/library_dashboard/blob/main/Screenshot%202.png)


## Author

- [@manish](https://github.com/Manish-Singh12)
- LinkedIn - https://www.linkedin.com/in/manish-singh-pokhariya/

