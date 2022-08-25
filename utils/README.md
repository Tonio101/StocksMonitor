## Create Database

`TODO: Script that create database with retention policy`
Assuming influx db resides in localhost

```bash
> influx
> CREATE DATABASE "stocks" WITH DURATION 30d REPLICATION 1 SHARD DURATION 1h NAME "stocks_policy"
```
