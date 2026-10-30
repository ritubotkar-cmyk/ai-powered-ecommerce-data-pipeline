
-- 1. Overall order and revenue summary
SELECT
    COUNT(*) AS total_orders,

    COUNT(*) FILTER (
        WHERE status = 'DELIVERED'
    ) AS delivered_orders,

    COUNT(*) FILTER (
        WHERE status = 'CANCELLED'
    ) AS cancelled_orders,

    ROUND(
        SUM(
            quantity * unit_price * (1 - discount)
        ) FILTER (WHERE status = 'DELIVERED'),
        2
    ) AS delivered_revenue,

    ROUND(
        SUM(
            quantity * unit_price * (1 - discount)
        ) FILTER (WHERE status IN ('PROCESSING', 'SHIPPED')),
        2
    ) AS in_progress_order_value

FROM raw_orders;


-- 2. Sales performance by category
SELECT
    category,

    COUNT(*) AS total_orders,

    SUM(quantity) AS total_quantity,

    ROUND(
        SUM(quantity * unit_price * (1 - discount))
            FILTER (WHERE status = 'DELIVERED'),
        2
    ) AS delivered_revenue

FROM raw_orders

WHERE status <> 'CANCELLED'

GROUP BY category

ORDER BY delivered_revenue DESC NULLS LAST;

