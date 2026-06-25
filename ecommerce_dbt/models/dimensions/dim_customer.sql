{{ config(as_columnstore=false) }}

with staged as (
    select * from {{ ref('stg_customers') }}
),

final as (
    select
        customer_id                         as customer_key,
        customer_id,
        first_name,
        last_name,
        full_name,
        email,
        city,
        country,
        customer_tier,
        signup_date,
        is_active,
        cast(getdate() as date)             as valid_from,
        cast('9999-12-31' as date)          as valid_to,
        1                                   as is_current
    from staged
)

select * from final