#!/usr/bin/env python

#===============================================================================
# title           : remove_old_backup.py
# description     : script to check old existing backup file which is need to remove
# authors         : Sodjamts
# create date     : July 20, 2019
# last updated:   : July 20, 2019
# version         : 1.0
# usage           : python remove_old_backup.py
# requirement     : python2
#===============================================================================

import os, time, sys, logging

logging.basicConfig(filename='/mydir/monitoring/log/backupremoved.log', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
path = "/backupg/sdbackup/dumps"
now = time.time()

for file in os.listdir(path):
	fileWithPath = os.path.join(path,file)
	if os.stat(fileWithPath).st_mtime < now - 30 * 86400:
		if os.path.isfile(fileWithPath):
                        logging.warning(fileWithPath + " - file has removed.")
			os.remove(fileWithPath)
                else:
                    logging.warning("File does not exist.")
