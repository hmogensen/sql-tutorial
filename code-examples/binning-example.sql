SELECT 
weeks_ago, COUNT(*)
FROM
(
SELECT
DATEDIFF(WEEK, GETDATE(), sa.ScheduledStartTime) [weeks_ago]
FROM 
VARIAN.dbo.ScheduledActivity sa WITH (NOLOCK)
WHERE sa.ScheduledStartTime >= '20210601'
) AS [count_weekly]
WHERE count_weekly.weeks_ago >= -10 AND count_weekly.weeks_ago <= 10
GROUP BY weeks_ago
ORDER BY weeks_ago
