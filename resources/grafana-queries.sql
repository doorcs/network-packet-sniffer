--------------------------------------------------------------------------------

-- Visualization: Time series
-- Panel title: 전체 네트워크 트래픽

SELECT
  $__timeGroup(time, '5s') AS time,
  COUNT(*) AS '전체 네트워크 트래픽'
FROM
  log
WHERE
  $__timeFilter(time)
GROUP BY
  time
ORDER BY
  time;

--------------------------------------------------------------------------------

-- Visualization: Bar Chart
-- Panel title: 출발지 <> 도착지 IP 쌍
-- Orientation: Horizontal

SELECT
    CONCAT(LEAST(src_ip, dst_ip), ' <-> ', GREATEST(src_ip, dst_ip)) AS '통신 쌍 (IP Pair)',
    SUM(CASE WHEN src_ip < dst_ip THEN 1 ELSE 0 END) AS '정방향 (A→B)',
    SUM(CASE WHEN src_ip > dst_ip THEN 1 ELSE 0 END) AS '역방향 (B→A)'
FROM
    log
WHERE
    $__timeFilter(time)
GROUP BY
    1
ORDER BY
    COUNT(*) DESC
LIMIT 10;

--------------------------------------------------------------------------------

-- Visualization: Bar Chart
-- Panel title: 프로토콜별 트래픽
-- Orientation: Horizontal

SELECT
  protocol,
  COUNT(*) AS 'count'
FROM
  log
WHERE
  $__timeFilter(time)
GROUP BY
  protocol
ORDER BY
  2 DESC;

--------------------------------------------------------------------------------

-- Visualization: Table
-- Panel title: 포트별 트래픽

SELECT
  port,
  COUNT(*) AS 'count'
FROM (
  SELECT src_port AS port FROM log WHERE $__timeFilter(time)
  UNION ALL
  SELECT dst_port AS port FROM log WHERE $__timeFilter(time)
) AS ports
GROUP BY
  port
ORDER BY
  2 DESC;

--------------------------------------------------------------------------------
