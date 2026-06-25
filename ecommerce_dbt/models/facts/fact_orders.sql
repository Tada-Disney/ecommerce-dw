{{ config(
    as_columnstore=false,
    incremental_strategy='append'
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select customer_key, customer_id
    from {{ ref('dim_customer') }}
    where is_current = 1
),

products as (
    select product_key, product_id
    from {{ ref('dim_product') }}
    where is_current = 1
),

final as (
    select
        o.order_id,
        c.customer_key,
        p.product_key,
        o.order_date,
        o.quantity,
        o.unit_price,
        o.discount_pct,
        o.total_amount,
        o.order_status
    from orders o
    left join customers c on o.customer_id = c.customer_id
    left join products p on o.product_id = p.product_id

    {% if is_incremental() %}
    where o.order_date > (select max(order_date) from {{ this }})
    {% endif %}
)

select * from final