SELECT 
count(*), ActivityCategoryENU 
FROM variandw.DWH.DimActivity da  
group by ActivityCategoryENU 
order by count(*) desc
