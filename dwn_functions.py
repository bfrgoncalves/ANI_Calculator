#!/usr/bin/python
import ftplib
import os
from datetime import datetime
import sys


def func_dwnFTP(target_bug, target_dir, file_type):
    

    def DownloadAndSetTimestamp(local_file,fi,nt):
        lf=open(local_file,'wb')
        f.retrbinary("RETR " + fi, lf.write, 8*1024)
        lf.close()
        print fi + " downloaded!"

        #set the modification time the same as server for future comparison
        os.utime(local_file,( int(nt) , int(nt) ))

    startTime =datetime.now()

    print "Connecting to ftp.ncbi.nih.gov..."   
    f=ftplib.FTP('ftp.ncbi.nih.gov')
    f.login()
    f.cwd('/genomes/Bacteria/')
    listing=[]
    dirs=f.nlst();
    print "Connected and Dir list retrieved."

    print "Searching for :"+ target_bug
    ct=0;
    countDownloaded = 0
    countSeen = 0
    under1MB = 0
    for item in dirs:
        if countDownloaded >= 100:
            break
        if item.find(target_bug)>-1:
            print
            print "----------------------------------------------"
            print "Dir: " + item
            # #create the dir
            biggestFnaFile = ''
            currentTopSize = 0
            countSeen += 1
            # if not os.path.isdir(os.path.join(target_dir,target_bug)):
            #     print "Dir not found. Creating it..."
            #     os.makedirs(os.path.join(target_dir,target_bug))
            # #1) change the dir
            f.cwd(item)
            #2) get  files from file_type in dir
            try:
                files=f.nlst(file_type)
                for fi in files:
                    newFileName = str(item.split('/')[0]) + '.fna'
                    local_file = os.path.join(target_dir,newFileName)
                    f.sendcmd("TYPE i") 
                    statSize = f.size(fi)
                    f.sendcmd("TYPE A")
                    print statSize
                    
                    if statSize > currentTopSize: #Checks for the biggest fna file to download. Rejects small files like plasmids
                        currentTopSize = statSize
                        biggestFnaFile = local_file

                if os.path.isfile(local_file):
                    print "Dir:" + item 
                    print "File " + local_file + " already exists."
                    #get remote modification time           
                    mt = f.sendcmd('MDTM '+ fi)
                    #converting to timestamp
                    nt = datetime.strptime(mt[4:], "%Y%m%d%H%M%S").strftime("%s")

                    if int(nt)==int(os.stat(local_file).st_mtime):
                        print fi +" not modified. Download skipped"
                    else:
                        print "New version of "+fi
                        ct+=1
                        DownloadAndSetTimestamp(local_file,fi,nt)
                        print "NV Local M timestamp : " + str(os.stat(local_file).st_mtime)
                        print "NV Local A timestamp : " + str(os.stat(local_file).st_atime)

                elif statSize < 1000000:
                    under1MB += 1
                    print 'File has a size lower than 1MB. Possibly a plasmid.'
                else:
                    print "New file: "+fi
                    ct+=1
                    mt = f.sendcmd('MDTM '+ fi)
                    #converting to timestamp
                    nt = datetime.strptime(mt[4:], "%Y%m%d%H%M%S").strftime("%s")
                    countDownloaded += 1
                    DownloadAndSetTimestamp(local_file,fi,nt)
            except ftplib.error_temp,  resp:
                if str(resp) == "450 No files found":
                    print "No "+ file_type +" files in this directory. Skipping"
            f.cwd('..')
    f.quit()
    print "# of "+target_bug+" new files found and downloaded: " + str(ct)

    timeDownload = datetime.now() - startTime

    return timeDownload, countSeen, countDownloaded, under1MB
