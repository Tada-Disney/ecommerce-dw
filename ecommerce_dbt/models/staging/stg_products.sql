with source as (
    select * from dbo.raw_products
),

renamed as (
    select
        product_id,
        product_name,
        upper(category)                 as category,
        cast(unit_price as decimal(10,2)) as unit_price,
        cast(is_active as bit)          as is_active
    from source
)

select * from renamed