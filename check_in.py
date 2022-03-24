import sqlite3
from sqlite3 import Error
import os
import time

def sqlite_file(filename): 
    try:
        sqlite_con = sqlite3.connect(filename)
    except Error as e:
        print(e)

    sqlite_con.execute("CREATE TABLE IF NOT EXISTS subscribers(first_check_in datetime, imsi text, cell integer, status text, counter integer);")

    return(sqlite_con)

def select_all_tasks(conn,name):
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM %s" % (name))

    rows = cur.fetchall()
#    for row in rows:
#        print(row)
    return(rows)


if __name__ == "__main__":
    
    sub_conn = sqlite_file("/root/check_in.db")
    obs_conn = sqlite3.connect("/root/cell_info.db")
    
    subs = select_all_tasks(sub_conn,'subscribers')
    obs = select_all_tasks(obs_conn,'observations')
    
   
    flag = False
    imsi = 0
    for row in obs:
        if(row[3] == ''):
            if(row[1] == ''):
                if(row[2] == ''):
                    continue
                else:
                    imsi = row[2]
            else:
                imsi = row[1]
        else:
            imsi = row[3]

        if len(subs) == 0:
            sub_conn.execute(
                u"INSERT INTO subscribers(first_check_in, imsi, cell, status, counter) " + "VALUES (?, ?, ?, ?, ?);",
                (row[0], imsi, row[10], " Active", 3)
            )
            sub_conn.commit()
        else:
            for sub in subs:
                if(imsi == sub[1]):
                    flag = True
                    break
                else:
                    continue
            
            if(flag == True):    
                sql = ''' UPDATE subscribers
                        SET first_check_in = ? ,
                            imsi = ? ,
                            cell = ?,
                            status = ?, 
                            counter = ?
                        WHERE imsi = ? '''
                
                cur = sub_conn.cursor()
                cur.execute(sql, (sub[0],imsi, sub[2]," Active",3,imsi))
                sub_conn.commit()
            else:
                sub_conn.execute(
                    u"INSERT INTO subscribers(first_check_in, imsi, cell, status, counter) " + "VALUES (?, ?, ?, ?, ?);",
                    (row[0], imsi, row[10], " Active", 3)
                )
                sub_conn.commit()


    subs = select_all_tasks(sub_conn,'subscribers')
    #print(subs)
    #print(obs)
    
    exist = False
    for sub in subs:
        imsi = 0
        for row in obs:
           if(row[3] == ''):
                if(row[1] == ''):
                    if(row[2] == ''):
                        continue
                    else:
                        imsi = row[2]
                else:
                    imsi = row[1]
           else:
                imsi = row[3]
           if(sub[1] == imsi):
                exist = True
                break

        if(exist == True):
            continue
        else: 

            new_counter = sub[4]
            if(new_counter > 0):
                new_counter -= 1
            if(new_counter == 0):
                new_status = "Offline"
            else:
                new_status = " Active"

        sql = ''' UPDATE subscribers
                  SET first_check_in = ? ,
                      imsi = ? ,
                      cell = ?,
                      status = ?, 
                      counter = ?
                  WHERE imsi = ? '''
                
        cur = sub_conn.cursor()


        cur.execute(sql, (sub[0], sub[1], sub[2],new_status,new_counter,sub[1]))
        sub_conn.commit()

    subs = select_all_tasks(sub_conn,'subscribers')

    print("       First Check In      |        IMSI       | Cell-ID |  Status   | Counter ")
    print("-------------------------------------------------------------------------------")
    for sub in subs:
        cel_id= ''
        if(sub[2] != ''):
            cel_id = sub[2]
        else:
            cel_id = "00000"
        if(len(str(cel_id))<5 and cel_id != None):
            cel_id= str(cel_id)+" "
        if(sub[1] != None):
            if(len(sub[1]) < 17):
                print ("%s |     %s    |  %s  |  %s  |    %s" % (sub[0],sub[1],cel_id,sub[3],sub[4]))
            else:
                print ("%s | %s |  %s  |  %s  |    %s" % (sub[0],sub[1],cel_id,sub[3],sub[4]))
    
    print("\n")
   

  
 
