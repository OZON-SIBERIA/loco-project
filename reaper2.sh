#!/bin/bash
mysql -N -e"select from_unixtime(timestamp), rpm_diesel, power_generator, poz_kont_sec from full_sql_locodataseconds where loco_id = '11' and from_unixtime(timestamp) >= '2016-02-28 00:00:00' AND timestamp < '2016-02-28 23:59:00'" > /home/mark/PycharmProjects/loko-project/lokodata_11.txt -h 'lokosampledb.cozlbgcgmptq.us-east-2.rds.amazonaws.com' -u readslave -przd_2020 dbloko

