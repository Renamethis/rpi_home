GRANT ALL PRIVILEGES ON DATABASE rpi TO root;

-- If you need to clean-up tables:
-- DROP TABLE IF EXISTS environment_record;
-- DROP TABLE IF EXISTS environment_units;
-- DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users(
    nickname varchar(50) not null primary key,
    password varchar(100) not null,
    registered_on datetime not null,
    is_admin boolean not null
);

CREATE TABLE IF NOT EXISTS environment_units(
    type varchar(50) not null primary key,
    unit varchar(10) not null
);

CREATE TABLE IF NOT EXISTS environment_record(
    id int primary key,
    ptime timestamp not null,
    field_name varchar(50) not null,
    unit varchar(50) references environment_units,
    value float not null
);