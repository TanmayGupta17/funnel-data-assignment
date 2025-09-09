SELECT
    COUNT(*) AS total_orders,
    SUM(CASE
            WHEN canceled_at IS NOT NULL THEN 1
            ELSE 0
        END) AS canceled,
    SUM(CASE
            WHEN canceled_at IS NOT NULL
                 AND (canceled_at - created_at) > INTERVAL '60 minutes'
            THEN 1
            ELSE 0
        END) AS violations,
    ROUND(
        100.0 * SUM(CASE
                        WHEN canceled_at IS NOT NULL
                             AND (canceled_at - created_at) > INTERVAL '60 minutes'
                        THEN 1
                        ELSE 0
                    END)
        / COUNT(*),
        2
    ) AS violation_rate_pct
FROM
    orders;
