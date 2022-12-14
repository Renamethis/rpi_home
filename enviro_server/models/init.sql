GRANT ALL PRIVILEGES ON DATABASE rpi TO root;
CREATE TABLE IF NOT EXISTS environment_data(
    ptime timestamp not null primary key,
    temperature float not null,
    humidity float not null,
    pressure float not null,
    illumination float not null,
    reducing float not null,
    oxidising float not null,
    nh3 float not null
);
CREATE TABLE IF NOT EXISTS environment_units(
    field_name varchar(50) not null primary key,
    unit varchar(10) not null
);