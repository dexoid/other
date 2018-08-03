#!/bin/env bash
IFS=$'\n'
PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin
imagelist=$(find /home/cshelp/images -type f \! -name "\.\*" \! -path "/home/cshelp/images/backup/\*")
db="/var/lib/image_optim/sole.db"

# Create DB: sqlite3 /var/lib/image_optim/sole.db  "create table md5sum (id TEXT);"

for a in $imagelist
do
  md5=$(md5sum $a | awk '{ print $1}')
  result=$(sqlite3 $db "select id from md5sum where id='"$md5"';")
 if [[ `echo "$result" |grep $md5` ]]
  then
    continue
  else
    image_optim $a
    md5=$(md5sum $a | awk '{ print $1}')
    sqlite3 $db "insert into md5sum (id) values ('"$md5"');"
  fi
done

