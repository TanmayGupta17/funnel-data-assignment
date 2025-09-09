SELECT
    device,

    COUNT(DISTINCT CASE WHEN event_name = 'Loaded' THEN user_id END) AS loaded_users,
    COUNT(DISTINCT CASE WHEN event_name = 'Interact' THEN user_id END) AS interact_users,
    COUNT(DISTINCT CASE WHEN event_name = 'Clicks' THEN user_id END) AS clicks_users,
    COUNT(DISTINCT CASE WHEN event_name = 'Purchase' THEN user_id END) AS purchase_users,

    ROUND(
        (COUNT(DISTINCT CASE WHEN event_name = 'Interact' THEN user_id END)::numeric * 100) /
        NULLIF(COUNT(DISTINCT CASE WHEN event_name = 'Loaded' THEN user_id END), 0),
        2
    ) AS conv_loaded_to_interact_pct,

    ROUND(
        (COUNT(DISTINCT CASE WHEN event_name = 'Clicks' THEN user_id END)::numeric * 100) /
        NULLIF(COUNT(DISTINCT CASE WHEN event_name = 'Interact' THEN user_id END), 0),
        2
    ) AS conv_interact_to_clicks_pct,

    ROUND(
        (COUNT(DISTINCT CASE WHEN event_name = 'Purchase' THEN user_id END)::numeric * 100) /
        NULLIF(COUNT(DISTINCT CASE WHEN event_name = 'Clicks' THEN user_id END), 0),
        2
    ) AS conv_clicks_to_purchase_pct

FROM events
WHERE event_name IN ('Loaded', 'Interact', 'Clicks', 'Purchase')
GROUP BY device
ORDER BY device;
