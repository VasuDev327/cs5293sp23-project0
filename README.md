## cs5293sp23-project0
## author-Vasu Deva Sai Nadha Reddy Janapala

I wrote this code in a single code file, named it as **project0.py**
Used Libraries:
```python
import PyPDF2
import requests

import argparse
import io
import re
import sqlite3
```
The libraries mentioned above are utilized in this code.

### Step 1:
```python
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
    args = parser.parse_args()
    if args.incidents:
       read_pdf = main(args.incidents)
       extractincidents(read_pdf)
```  
This section of the code facilitates the reading of the provided incident URL from the command line which is a string parameter passes to the main function within the code. If no URL is passed via the command line, an error message is displayed as follows:
![image](https://user-images.githubusercontent.com/102677891/223544057-70625319-523a-4e06-81a3-5c227bcfb968.png)

### Step 2:
```python
def main(url):
    # Download data
    # incident_data = fetchincidents(url)
    response = requests.get(url)
    file = io.BytesIO(response.content)
    pdf_reader = PyPDF2.PdfReader(file)
    return (pdf_reader)
    # Extract data
    # incidents = extractincidents(incident_data)
```
This part of the code is responsible for retrieving data from the specified PDF URL. To achieve this, I have employed the requests, io and pyPDF2 libraries. After reading the PDF file, I return the retrieved data to the invoking function where it is stored in a variable named **read_pdf**.

### Step 3:
```python
def extractincidents(pdf_reader):
```
This block of functions performs nearly all of the necessary operations. The retrieved data, stored in read_pdf, is passed to the extractincidents() function where data preprocessing occurs. Once the preprocessing is complete, the values are stored in their respective variables and are subsequently inserted into the created table. If the database does not exist when connecting to it, it will be created. Similarly, if the table does not exist, it will be created, and the respective values will be inserted. In this instance, the database is named **project0.db** and the table is called **norman_inc_data**. These operations are carried out using sub-functions within the extractincidents(pdf_reader) function. These sub-functions include createdb(db, date_time, incident, address, nature, incident_ori) for creating or connecting to the database and populatedb() for inserting the data into the database.

### Step 4:
Within the extractincidents(pdf_reader) function, there are two additional functions: incidentcounts(db) and status(db). The incidentcounts(db) function tallies the total number of incidents contained within the table, while the status(db) function displays the nature column value and the frequency of its occurrence within the norman_inc_data table.

### Sample Output:
![image](https://user-images.githubusercontent.com/102677891/223553397-7cc565b0-9195-4e9b-b00e-97b22002c71f.png)

### Note:
In this code I have considered the hardcoded information of the Incident_ORI as shown below:
```python
Incident_ORI = ['OK0140200',
                '14005',
                'EMSSTAT',
                '14009']
```
Based on what I have observed, the files I have encountered contain only this particular information. Since there are limited values, I utilized this information to separate the data from the record.
