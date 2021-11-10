import pyodbc
import pandas as pd
import datetime as dt
import matplotlib as mat
import matplotlib.pyplot as plt
from functools import partial

def get_months(start_date, end_date):
    months = []
    next_date = start_date
    while next_date <= end_date:
        months.append(next_date)
        if next_date.month<12:
            next_date = dt.datetime(next_date.year, next_date.month+1, next_date.day)
        else:
            next_date = dt.datetime(next_date.year+1, 1, next_date.day)
    return months

# Split dataset according to time ranges defined by input parameter bins, applied to the date
# values in column date_column
def split(dataset, date_column, bins):
    split_data = []
    for indx in range(len(bins)-1):
        start_at = bins[indx]
        end_at   = bins[indx+1]
        split_data.append(dataset.loc[(dataset[date_column] >= start_at) & (dataset[date_column] < end_at)])
    return split_data

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

diagnos_label = "Diagnos"
fraction_label = "AntalFraktioner"
query = """
select distinct
ddc.DiagnosisClinicalDescriptionENU [""" + diagnos_label + """],
dc.CourseStartDateTime				[Startdatum], 
dp.NoFractionsPlanned               [""" + fraction_label + """],
dpat.PatientId
from variandw.DWH.DimDiagnosisCode ddc
inner join variandw.DWH.FactPatientDiagnosis 	fpd ON ddc.DimDiagnosisCodeID 		= fpd.DimDiagnosisCodeID 
inner join variandw.DWH.FactCourseDiagnosis 	fcd ON fpd.FactPatientDiagnosisID 	= fcd.FactPatientDiagnosisID 
inner join variandw.DWH.DimCourse 				dc	ON fcd.DimCourseID  			= dc.DimCourseID 	 
inner join variandw.DWH.DimPlan 			    dp  ON dc.DimCourseID 				= dp.DimCourseID 
inner join variandw.DWH.DimPatient 				dpat ON dc.DimPatientID 			= dpat.DimPatientID 
WHERE dc.CourseStartDateTime >= '20160101' 
AND dp.NoFractionsPlanned > 0
AND dp.NoFractionsPlanned = dp.NoFractionsTreated 
ORDER BY dc.CourseStartDateTime 
"""
data = read_sql(query)
data.to_pickle("temp.py")
max_nbr_of_categories = 5
data = pd.read_pickle("temp.py")
diagnos_key = "Diagnos"
unique  = list(set(data[diagnos_key]))
counts = {un: len([x for x in data[diagnos_key] if x == un]) for un in unique}
counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
diagnos_categories = list(counts.keys())[0:max_nbr_of_categories]
time_bins = get_months(dt.datetime(2016,1,1), dt.datetime.now())
split_data = split(data, "Startdatum", time_bins)
nbr_of_fractions = {dc: [s.loc[s[diagnos_label] == dc][fraction_label].tolist() for s in split_data] for dc in diagnos_categories}
nbr_of_fractions["Övrigt"] = [[f for f, d in zip(s[fraction_label], s[diagnos_label]) if d not in diagnos_categories] for s in split_data]

def onclick(event, key, axes):
    clicked_date = mat.dates.num2date(event.xdata).replace(tzinfo=None)
    print(clicked_date)

    try:
        indx = next(i for i in range(len(time_bins)) if time_bins[i] > clicked_date)
    except StopIteration:
        return

    axes.cla()
    axes.hist(nbr_of_fractions[key][indx])
    axes.set_ylabel("N")
    axes.set_xlabel("Antal fraktioner")
    axes.set_title(time_bins[indx])
    plt.draw()

for diagnosis_key in nbr_of_fractions:
    fig, (ax1, ax2) = plt.subplots(2,1)
    ax1.plot(time_bins[:-1], [len(n) for n in nbr_of_fractions[diagnosis_key]])
    ax1.set_title(diagnosis_key)
    ax1.set_ylabel("Antal courses")
    ax1.set_xlabel("Månad")
    cid = fig.canvas.mpl_connect('button_press_event', partial(onclick, key=diagnosis_key, axes=ax2))
plt.show()
