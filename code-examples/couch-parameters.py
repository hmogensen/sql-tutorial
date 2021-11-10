import pyodbc
import pandas as pd

def read_sql(query):
    server_name   = 'MTAPP087'
    database_name = 'variandw'
    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=' + server_name + ';'
                          'Database=' + database_name + ';'
                          'Trusted_Connection=yes;')

    cursor = conn.cursor()
    cursor.execute(query)
    data = None
    count = 0
    for row in cursor:
        count += 1
        if data is None:
            data = [[d for d in row]]
        else:
            data.append([d for d in row])

    d = {}
    if data is not None:

        n = len(data[0])
        headers = [c[0] for c in cursor.description]

        for j in range(len(headers)):
            d[headers[j]] = [data[i][j] for i in range(len(data))]
    return pd.DataFrame(data=d)

patient_ids = ["test_QA_dynMLC",
               "test_zzz lund lin 5"
               # Add patient id number here
               ]

query = """
SELECT DISTINCT
dp.PatientId 
,dtt.CouchLat 			[Lat]
,dtt.CouchLng		 	[Lng]
,dtt.CouchVrt			[Vrt]
,fth.TreatmentStartTime [FractionStartTime]
,fth.TreatmentEndTime   [FractionEndTime]
FROM 
variandw.DWH.DimPatient dp 
INNER JOIN variandw.DWH.DimCourse               dc  ON dp.DimPatientID = dc.DimPatientID 
INNER JOIN variandw.DWH.DimTreatmentTransaction dtt ON dc.DimCourseID  = dtt.DimCourseID 
INNER JOIN variandw.DWH.FactTreatmentHistory    fth ON dtt.DimTreatmentTransactionID = fth.DimTreatmentTransactionID 
"""
if len(patient_ids) > 0:
    query += "AND ("
    for i, p_id in enumerate(patient_ids):
        query += "dp.PatientId = '" + p_id + "'"
        if i<len(patient_ids)-1:
            query += " OR "
        else:
            query += ")"

data = read_sql(query)
data.to_pickle("temp.py")
data = pd.read_pickle("temp.py")
