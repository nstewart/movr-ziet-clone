# MovR

MovR is a fictional ride sharing company. This repo contains links to datasets and a load generator.


## Getting started
First, [download CockroachDB](https://www.cockroachlabs.com/docs/stable/install-cockroachdb.html) and start a local cluster with `cockroach start --insecure --host localhost --background`

Then create the database `movr` with `cockroach sql --insecure --host localhost -e "create database movr;"`

Generating fake data: `docker run -it --rm cockroachdb/movr --url "postgres://root@docker.for.mac.localhost:26257/movr?sslmode=disable" load --num-users 100 --num-rides 100 --num-vehicles 10`

Generating load for cities: `docker run -it --rm cockroachdb/movr --url "postgres://root@docker.for.mac.localhost:26257/movr?sslmode=disable" --num-threads 10 run --city "new york" --city "boston"`

## Partitioning MovR
MovR can automatically partition data and apply zone configs using the `partition` command.
Use region-city pairs to map cities to regional partitions and use region-zone pairs to map regional partitions to zones
`docker run -it --rm cockroachdb/movr --echo-sql --app-name "movr-partition" --url "postgres://root@[ipaddress]/movr?sslmode=disable" partition --region-city-pair us_east:"new york" --region-city-pair central:chicago --region-city-pair us_west:seattle  --region-zone-pair us_east:us-east1 --region-zone-pair central:us-central1 --region-zone-pair us_west:us-west1`

If you want to partition by hand (perhaps in a demo), MovR can print the partition commands with the `--preview-queries` command. Example:
```
Partitioning Setting Summary

partition    city
-----------  --------
chicago      chicago
new_york     new york
seattle      seattle

partition    zone where partitioned data will be moved
-----------  -------------------------------------------
new_york     us-east1
chicago      us-central1
seattle      us-west1

reference table    zones where index data will be replicated
-----------------  -------------------------------------------
promo_codes        us-east1
promo_codes        us-central1
promo_codes        us-west1

queries to geo-partition the database
===table and index partitions===
ALTER TABLE vehicles PARTITION BY LIST (city) (PARTITION new_york VALUES IN ('new york' ), PARTITION chicago VALUES IN ('chicago' ), PARTITION seattle VALUES IN ('seattle' ));
ALTER TABLE users PARTITION BY LIST (city) (PARTITION new_york VALUES IN ('new york' ), PARTITION chicago VALUES IN ('chicago' ), PARTITION seattle VALUES IN ('seattle' ));
ALTER TABLE rides PARTITION BY LIST (city) (PARTITION new_york VALUES IN ('new york' ), PARTITION chicago VALUES IN ('chicago' ), PARTITION seattle VALUES IN ('seattle' ));
```

## Pre-built datasets

### MovR 1M
This dataset contains 1M users, 1M rides, and 10k vehicles.


Import Users
```
IMPORT TABLE users (
        id UUID NOT NULL,
        city VARCHAR NOT NULL,
        name VARCHAR NULL,
        address VARCHAR NULL,
        credit_card VARCHAR NULL,
        CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
        FAMILY "primary" (id, city, name, address, credit_card)
)
CSV DATA (
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.0.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.1.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.2.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.3.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.4.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.5.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.6.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.7.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.8.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.9.csv',
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/users/n1.10.csv');

```
Import vehicles
```
IMPORT TABLE vehicles (
        id UUID NOT NULL,
        city VARCHAR NOT NULL,
        type VARCHAR NULL,
        owner_id UUID NULL,
        creation_time TIMESTAMP NULL,
        status VARCHAR NULL,
        current_location VARCHAR NULL,
        ext JSONB NULL,
        CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
        INDEX vehicles_auto_index_fk_city_ref_users (city ASC, owner_id ASC),
        INVERTED INDEX ix_vehicle_ext (ext),
        FAMILY "primary" (id, city, type, owner_id, creation_time, status, current_location, ext)
)                                                                                                                                                                
CSV DATA ('https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/vehicles/n1.0.csv');

```

Import rides
```
IMPORT TABLE rides (
        id UUID NOT NULL,
        city VARCHAR NOT NULL,
        vehicle_city VARCHAR NULL,
        rider_id UUID NULL,
        vehicle_id UUID NULL,
        start_address VARCHAR NULL,
        end_address VARCHAR NULL,
        start_time TIMESTAMP NULL,
        end_time TIMESTAMP NULL,
        revenue DECIMAL(10,2) NULL,
        CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
        INDEX rides_auto_index_fk_city_ref_users (city ASC, rider_id ASC),
        INDEX rides_auto_index_fk_vehicle_city_ref_vehicles (vehicle_city ASC, vehicle_id ASC),
        FAMILY "primary" (id, city, vehicle_city, rider_id, vehicle_id, start_address, end_address, start_time, end_time, revenue),
        CONSTRAINT check_vehicle_city_city CHECK (vehicle_city = city)
) 
CSV DATA (
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.0.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.1.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.2.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.3.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.4.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.5.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.6.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.7.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.8.csv', 
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.9.csv',
'https://s3-us-west-1.amazonaws.com/cockroachdb-movr/datasets/movr-1m/rides/n1.10.csv');
```

Setup and validate integrity constraints
```
ALTER TABLE vehicles ADD CONSTRAINT fk_city_ref_users FOREIGN KEY (city, owner_id) REFERENCES users (city, id);
ALTER TABLE rides ADD CONSTRAINT fk_city_ref_users FOREIGN KEY (city, rider_id) REFERENCES users (city, id);
ALTER TABLE rides ADD CONSTRAINT fk_vehicle_city_ref_vehicles FOREIGN KEY (vehicle_city, vehicle_id) REFERENCES vehicles (city, id);

ALTER TABLE vehicles VALIDATE CONSTRAINT fk_city_ref_users;
ALTER TABLE rides VALIDATE CONSTRAINT fk_city_ref_users;
ALTER TABLE rides VALIDATE CONSTRAINT fk_vehicle_city_ref_vehicles;


```
