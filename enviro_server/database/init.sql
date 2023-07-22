GRANT ALL PRIVILEGES ON DATABASE rpi TO root;
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