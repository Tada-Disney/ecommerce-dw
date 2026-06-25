with source as (
    select * from dbo.raw_orders
),

renamed as (
    select
        order_id,
        customer_id,
        product_id,
        cast(order_date as date)            as order_date,
        cast(quantity as int)               as quantity,
        cast(unit_price as decimal(10,2))   as unit_price,
        cast(discount_pct as decimal(5,2))  as discount_pct,
        cast(total_amount as decimal(10,2)) as total_amount,
        lower(status)                       as order_status
    from source
)

select * from renamed