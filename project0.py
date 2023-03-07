# Text Analytics - 5393
# Project 0
# Vasu Deva Sai Nadha Reddy Janapala

# third party libraries
import PyPDF2
import requests

# built-in libraries
import argparse
import io
import re
import sqlite3

# Assuming that only these are the only incident ori's available in the incident reports.
# So, I have hardcoded this part.
Incident_ORI = ['OK0140200',
                '14005',
                'EMSSTAT',
                '14009']

# The main function helps to fetch the incidents
def main(url):
    # Download data using requests
    response = requests.get(url)
    file = io.BytesIO(response.content)

    # Extracting the information using the pyPDF2
    pdf_reader = PyPDF2.PdfReader(file)
    return (pdf_reader)

# Extracting the data from each page
def extractincidents(pdf_reader):
    # Number of pages
    number_of_pages = len(pdf_reader.pages)

    # Empty list
    new_list = []

    # Reading the data from each page one after the other
    for page in range(number_of_pages):
        updated_element = ''
        if page == 0:
            try:
                page1 = pdf_reader.pages[page]
                page_text = page1.extract_text()

                # To remover the header part of the page
                end_index = page_text.find("NORMAN ")
                incident_data_text = page_text[:end_index]
                lines = incident_data_text.split('\n')
                lines = lines[1:]

                # if any single row and column data is considered as two different values,
                # we have to concatenate them because they belong to the same incident number,
                # to concatenate that, I am using the following block
                for i in range(len(lines)):
                    for j in range(len(lines)-1):
                        if len(re.findall(r"^(?![0-9]).*", lines[j][i])) > 0:
                            updated_element = updated_element + lines[j-1] + lines[j]
                            position = updated_element.find(lines[j-1])
                            if(updated_element[position-1] != " "):
                                updated_element = updated_element[:position] + " " + updated_element[position:]
                                del lines[j-1:j+1]
                                lines.insert(j-1, updated_element)
                    break
            except Exception as e:
                continue
        else:
            try:
                pageN = pdf_reader.pages[page]
                page_text = pageN.extract_text()
                lines = page_text.split('\n')

                # if any single row and column data is considered as two different values,
                # we have to concatenate them because they belong to the same incident number,
                # to concatenate that, I am using the following block
                for i in range(len(lines)):
                    for j in range(len(lines)-1):
                        if len(re.findall(r"^(?![0-9]).*", lines[j][i])) > 0:
                            updated_element = updated_element + lines[j-1] + lines[j]
                            position = updated_element.find(lines[j-1])
                            if(updated_element[position-1] != " "):
                                updated_element = updated_element[:position] + " " + updated_element[position:]
                                del lines[j-1:j+1]
                                lines.insert(j-1, updated_element)
                    break
            except Exception as e:
                continue

        # inserting each preprocessed page data into the created list
        for line in lines:
            new_list.append(line)

    # Removing the last element which is the data extracted date, avoiding that
    updated_list = new_list[:-1]

    # Creating the empty string values to store values, incase if we go beyond the for loop,
    # the updated values will help.
    incident_ori = ''
    nature = ''
    db = ''

    # The following loop helps to extract the individual data based on patterns and the assumptions
    for line in updated_list:

        # date and time pattern
        date_time_pattern = r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}'
        date_time = re.search(date_time_pattern, line)
        date_time = date_time.group(0)         # date and time value is extracted
        incident_pattern = r'\d{4}-\d{8}'      
        incident = re.search(incident_pattern, line)
        incident = incident.group(0)           # incident number is extracted
        substring_to_remove = [date_time, incident]
        for substring in substring_to_remove:
            line = line.replace(substring, '') # updating the line by removing the date and time, and incident number
        for ori in Incident_ORI:
            if ori in line:
                incident_ori = ori             # incident ORI is extracted
                line = line.replace(ori, '')
        pattern = r"[A-Z][a-z]+"               
        matches = re.search(pattern, line)
        if matches:
            position = line.find(matches.group(0))
        if 'Call Nature Unknown' in line:
            nature = line[position-4:]                   # nature is extracted
            line = line.replace(line[position-4:], '')
        else:
            nature = line[position:]                     # nature is extracted
            line = line.replace(line[position:], '')
        line = re.sub(r'^\s+', '', line)
        address = line                                   # address is extracted
    
    # Creating the new database, if it does not exist
        db = createdb()
        
    # Inserting the data
        populatedb(db, date_time, incident, address, nature, incident_ori)
    
    # Incidents Count
    incidentcounts(db) 

    # Status to print the nature and its count   
    status(db)

# Creating the new database, if it does not exist
def createdb():
    conn = sqlite3.connect('project0.db')    # creation of database and connecting to it
    cursor = conn.cursor()                   # creation of cursor object

    # Generating the norman_inc_data table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS norman_inc_data 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dateandtime TEXT,
                    incident_number TEXT,
                    location TEXT,
                    nature_of_incident,
                    incident_ORI)
                ''')
    
    # committing it
    conn.commit()

    # closing the connection
    conn.close()

    # passing back the created database name
    return('project0.db')

def populatedb(db, date_time, incident, address, nature, incident_ori):
    conn = sqlite3.connect(db)    # creation of database and connecting to it
    cursor = conn.cursor()                  # creation of cursor object
    insert_query = '''
                    INSERT INTO norman_inc_data 
                    (dateandtime, 
                    incident_number, 
                    location, 
                    nature_of_incident, 
                    incident_ORI)
                    VALUES (?, ?, ?, ?, ?)
                '''
    cursor.execute(insert_query, (date_time, incident, address, nature, incident_ori))

    # committing it
    conn.commit()

    # closing the connection
    conn.close()

# Print incident counts
def incidentcounts(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('''
            SELECT COUNT(*) 
            FROM norman_inc_data
        ''')
    count = cursor.fetchone()[0]
    print("Incidents Count: ",count)
    conn.commit()
    conn.close()

# status(db)
def status(db):
    
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute('''
                SELECT nature_of_incident, COUNT(*) 
                FROM norman_inc_data 
                GROUP BY nature_of_incident
                ''')
    for row in cursor.fetchall():
        print(f'{row[0]}|{row[1]}')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
       
       # passing the incident url
       read_pdf = main(args.incidents)

       # passing the extracted information
       extractincidents(read_pdf)
