import argparse
import requests
import io
import PyPDF2
from PyPDF2 import PdfReader
import pandas as pd
import re
import sqlite3

Incident_ORI = ['OK0140200',
                '14005',
                'EMSSTAT',
                '14009']


def main(url):
    # Download data
    # incident_data = fetchincidents(url)
    response = requests.get(url)
    file = io.BytesIO(response.content)
    pdf_reader = PyPDF2.PdfReader(file)
    return (pdf_reader)
    # Extract data
    # incidents = extractincidents(incident_data)

def extractincidents(pdf_reader):
    number_of_pages = len(pdf_reader.pages)
    new_list = []
    for page in range(number_of_pages):
        updated_element = ''
        if page == 0:
            try:
                page1 = pdf_reader.pages[page]
                page_text = page1.extract_text()
                end_index = page_text.find("NORMAN ")
                incident_data_text = page_text[:end_index]
                lines = incident_data_text.split('\n')
                lines = lines[1:]
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
    #             print("Error on page 0:", e)
        else:
            try:
                pageN = pdf_reader.pages[page]
                page_text = pageN.extract_text()
                lines = page_text.split('\n')
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
        for line in lines:
            new_list.append(line)

    updated_list = new_list[:-1]

    incident_ori = ''
    nature = ''
    db = ''
    for line in updated_list:
        # date and time
        date_time_pattern = r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}'
        date_time = re.search(date_time_pattern, line)
        date_time = date_time.group(0)         # insertion of date and time has to happen from here
        incident_pattern = r'\d{4}-\d{8}'      
        incident = re.search(incident_pattern, line)
        incident = incident.group(0)           # insertion of incident number must happen from here
        substring_to_remove = [date_time, incident]
        for substring in substring_to_remove:
            line = line.replace(substring, '')
        for ori in Incident_ORI:
            if ori in line:
                incident_ori = ori             # insertion of incident ori must happen from here
                line = line.replace(ori, '')
        pattern = r"[A-Z][a-z]+" 
        matches = re.search(pattern, line)
        if matches:
            position = line.find(matches.group(0))
        if 'Call Nature Unknown' in line:
            nature = line[position-4:]                   # insertion of nature must happen from here
            line = line.replace(line[position-4:], '')
        else:
            nature = line[position:]                     # insertion of nature must happen from here
            line = line.replace(line[position:], '')
        line = re.sub(r'^\s+', '', line)
        address = line                                   # insertion of address must happen from here
    # Create new database
        db = createdb()
        
    # Insert data
        populatedb(db, date_time, incident, address, nature, incident_ori)
    # Incidents Count
    incidentcounts(db) 

    # Status to print the nature and its count   
    status(db)

def createdb():
    conn = sqlite3.connect('project0.db')    # creation of database and connecting to it
    cursor = conn.cursor()                  # creation of cursor object
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS norman_inc_data 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dateandtime TEXT,
                    incident_number TEXT,
                    location TEXT,
                    nature_of_incident,
                    incident_ORI)
                ''')
    conn.commit()
    conn.close()
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

    conn.commit()
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


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--incidents", type=str, required=True, 
#                          help="Incident summary url.")
     
#     args = parser.parse_args()
#     if args.incidents:
#         main(args.incidents)
url = "https://www.normanok.gov/sites/default/files/documents/2023-01/2023-01-01_daily_incident_summary.pdf"
read_pdf = main(url)
extractincidents(read_pdf)
# incidentcounts()