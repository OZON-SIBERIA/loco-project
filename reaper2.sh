#!/bin/bash
for $loco in 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29
do
mysql -N -e"select timestamp, rpm_diesel, power_generator, poz_kont_sec from full_sql_locodataseconds where loco_id = '$loco' and poz_kont_sec != '0'" > ./lokodata_$loco.txt -h 'lokosampledb.cozlbgcgmptq.us-east-2.rds.amazonaws.com' -u readslave -przd_2020 dbloko
done

