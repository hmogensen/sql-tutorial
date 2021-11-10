SELECT DISTINCT
	dat.AppointmentDateTime,
	dat.AppointmentStatus,
	da.ActivityCategoryENU 
FROM 
	variandw.DWH.DimActivityTransaction dat
LEFT JOIN variandw.DWH.DimActivity da ON dat.DimActivityID = da.DimActivityID 
WHERE dat.AppointmentDateTime >= '20210101'
--AND (AppointmentStatus = 'Completed' OR AppointmentStatus = 'Manually Completed') 
AND dat.AppointmentStatus LIKE '%Completed'
AND da.ActivityCategoryENU = 'Treatment'
ORDER BY dat.AppointmentDateTime