#!/usr/bin/env python

# ===============================================================================
# title           : mysql_memory_calculator.py
# description     : script to check MySQL server memory usage checking from config file
# authors         : Sodjamts
# create date     : August 05, 2019
# last updated:   : August 05, 2019
# version         : 1.0
# usage           : python mysql_memory_calculator.py
# requirement     : python2
# ===============================================================================

import sys
import re

fileWithPath = '/etc/my.cnf'

# FORMULA IS BELOW:
# key_buffer_size + query_cache_size + tmp_table_size + max_heap_table_size + innodb_buffer_pool_size
# tokudb_cache_size + max_connections *
# (sort_buffer_size + read_buffer_size + read_rnd_buffer_size + join_buffer_size + thread_stack + binlog_cache_size)

globalVariables = {'key_buffer_size': '8M',
                   'query_cache_size': '1M',
                   'tmp_table_size': '16M',
                   'max_heap_table_size': '16M',
                   'innodb_buffer_pool_size': '128M',
                   'innodb_log_buffer_size': '16M',
                   'max_connections': '151',
                   'tokudb_cache_size': '128M'}

threadVariables = {'sort_buffer_size': '256K',
                   'read_buffer_size': '128K',
                   'read_rnd_buffer_size': '256K',
                   'join_buffer_size': '256K',
                   'thread_stack': '256K',
                   'binlog_cache_size': '32K'}


def variableparser(_linelist):
    for line in _linelist:
        if 'max_connections' in line:
            globalVariables['max_connections'] = line.split("=")[1].strip()
        for gVar in globalVariables:
            if gVar in line:
                globalVariables[gVar] = line.split("=")[1].strip()
        for tVar in threadVariables:
            if tVar in line:
                threadVariables[tVar] = line.split("=")[1].strip()


def calculator():
    globalresult = 0
    threadresult = 0
    for gList in globalVariables:
        if "M" in globalVariables[gList]:
            globalresult = globalresult + int(re.findall(r'\d+', globalVariables[gList])[0]) * 1024
        elif "G" in globalVariables[gList]:
            globalresult = globalresult + int(re.findall(r'\d+', globalVariables[gList])[0]) * (1024. ** 2)
    for tList in threadVariables:
        if "K" in threadVariables[tList]:
            threadresult = threadresult + int(re.findall(r'\d+', threadVariables[tList])[0])
        elif "M" in threadVariables[tList]:
            threadresult = threadresult + int(re.findall(r'\d+', threadVariables[tList])[0]) * 1024
        elif "G" in threadVariables[tList]:
            threadresult = threadresult + int(re.findall(r'\d+', threadVariables[tList])[0]) * (1024. ** 2)
    totalmemoryusage = round((globalresult + int(globalVariables['max_connections']) * threadresult) / 1024, 2)
    return str(totalmemoryusage)


def osmemory():
    with open("/proc/meminfo") as mem:
        for line in mem.readlines():
            if "MemTotal" in line:
                memorymb = int(re.findall(r'\d+', line.split(":")[1])[0]) / 1024
                break
    return str(round(memorymb, 2))


def getratio(confmem, osmem):
    return str(round(float(confmem) / float(osmem) * 100, 2))


def main():
    linelist = [line.replace('\t', '').replace('-', '_').rstrip('\n') for line in open(fileWithPath)]
    variableparser(linelist)
    confFileMemory = calculator()
    osMemory = osmemory()
    usedPercent = getratio(confFileMemory, osMemory)
    print("Operation system memory:\t" + osMemory + "MB")
    print("MySQL used memory size: \t" + confFileMemory + "MB")
    print("MySQL used memory percent:\t" + usedPercent + "%")
    if float(usedPercent) < 90:
        print("GOOD: Memory configuration is good for dedicated server.")
    else:
        print("BAD: Please make sure to check configuration file. Less than 90% is good.")


if __name__ == "__main__":
    sys.exit(main())

