cd /root/IMSI-catcher


if [ $# -gt 1 ]
then    
        xterm -e "bash -c 'python /root/grgsm_livemon.py'" &
        python3 simple_IMSI-catcher.py -s -w /root/cell_info.db -l $1 $2 

else    
        xterm -e "bash -c 'python /root/grgsm_livemon.py'" &
        python3 simple_IMSI-catcher.py -s -w /root/cell_info.db -l 39.36044374110071 22.949124812591084

fi

cd

python3 check_in.py
