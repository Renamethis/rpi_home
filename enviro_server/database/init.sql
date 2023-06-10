GRANT ALL PRIVILEGES ON DATABASE rpi TO root;
CREATE TABLE IF NOT EXISTS environment_units(
    field_name varchar(50) not null primary key,
    unit varchar(10) not null
);
CREATE TABLE IF NOT EXISTS record(
    ptime timestamp not null primary key,
    field_name varchar(50) references environment_units,
    value float not null
);