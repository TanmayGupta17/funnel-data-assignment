SELECT
          CASE WHEN detected_intent IS NULL OR TRIM(detected_intent) = '' THEN 'unknown'
               ELSE detected_intent
          END AS intent,
          COUNT(*) AS total_intents,
          ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM messages), 2) AS pct_of_total,
          ROUND(
            100.0 * SUM(CASE WHEN e.event_name = 'Purchase' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(DISTINCT m.session_id), 0),
            2
          ) AS purchase_conversion_rate
        FROM messages m
        LEFT JOIN events e ON m.session_id = e.session_id
        GROUP BY intent
        ORDER BY total_intents DESC;