{{ config(as_columnstore=false) }}

with staged as (
    select * from {{ ref('stg_products') }}
),

final as (
    select
        product_id                          as product_key,
        product_id,
        product_name,
        category,
        unit_price,
        is_active,
        cast(getdate() as date)             as valid_from,
        cast('9999-12-31' as date)          as valid_to,
        1                                   as is_current
    from staged
)

select * from final