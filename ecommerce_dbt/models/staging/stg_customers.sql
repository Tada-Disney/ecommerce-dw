with source as (
    select * from dbo.raw_customers
),

renamed as (
    select
        customer_id,
        first_name,
        last_name,
        first_name + ' ' + last_name   as full_name,
        lower(email)                    as email,
        city,
        country,
        upper(tier)                     as customer_tier,
        cast(signup_date as date)       as signup_date,
        cast(is_active as bit)          as is_active
    from source
)

select * from renamed