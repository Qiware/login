#!/bin/bash

function random()
{
    min=$1;
    max=`expr $2 - $1`;
    num=$(date +%s%N);
    ret=`expr $num % $max + $min`;
    echo $ret
}

idx=0
ip_list=(
10.127.220.161)
ip_num=1
begin=`date +%H%M%S.%N`

#while true
for (( idx=0;idx<100000;idx+=1 ))
do
    idx=`expr $idx + 1`
    len=$(random 1 2);
    ch=`expr $idx % 10`
    mod=`expr $idx % $ip_num`
    curl "http://${ip_list[$mod]}:8081/risk/query?token=$idx"

    #sleep 0
done

end=`date +%H%M%S.%N`

echo
echo $begin
echo $end
diff=`expr $end - $begin`
echo $diff
