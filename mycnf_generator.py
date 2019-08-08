#!/usr/bin/env python

# ===============================================================================
# title           : mycnf_generator.py
# description     : script to generate MySQL configuration file which has ensured best practice
# authors         : AndrianBdn, Sodjamts
# create date     : Aug 06, 2019
# last updated:   : Aug 06, 2019
# version         : 1.1
# usage           : python mycnf_generator.py mysql_ram_gb=2
# requirement     : python2
# ===============================================================================

import sys
import math
import random
from textwrap import dedent

defaults = {
    'mysql_dir': "/var/lib/mysql",
    'log_error': "/var/log/mysql/mysql-error.log",
    'slow_query_log_file': "/var/log/mysql/mysql-slow.log",
    'pid_file': "/var/run/mysqld/mysqld.pid",

    'mysql_ram_gb': 1,

    'query_cache_type': 0,
    'query_cache_size': 0,

    'long_query_time': 5,
    'max_connections': 300,

    'server_id': random.randint(1000, 9999)
}


def output_my_cnf(_metaconf):
    print(dedent("""
    [mysql]
    
    # CLIENT #
    port                           = 3306
    socket                         = {mysql_dir}/mysql.sock
    
    [mysqld]
    
    # GENERAL #
    user                           = mysql
    default-storage-engine         = InnoDB
    socket                         = {mysql_dir}/mysql.sock
    pid-file                       = {pid_file}
    
    # MyISAM #
    key-buffer-size                = 32M
    myisam-recover                 = FORCE,BACKUP
    
    # SAFETY #
    max-allowed-packet             = 16M
    max-connect-errors             = 1000000
    skip-name-resolve
    sysdate-is-now                 = 1
    
    # DATA STORAGE #
    datadir                        = {mysql_dir}
    
    # SERVER ID # 
    server-id                      = {server_id}

    # BINARY LOGGING #
    log-bin                        = {mysql_dir}/mysql-bin
    expire-logs-days               = 7
    sync-binlog                    = 1
    
    # CACHES AND LIMITS #
    tmp-table-size                 = 32M
    max-heap-table-size            = 32M
    query-cache-type               = {query_cache_type}
    query-cache-size               = {query_cache_size}
    max-connections                = {max_connections}
    thread-cache-size              = 50
    open-files-limit               = 65535
    table-definition-cache         = 1024
    table-open-cache               = 2048
    
    # INNODB #
    innodb-flush-method            = O_DIRECT
    innodb-log-files-in-group      = 2
    innodb-log-file-size           = {innodb_log_file_size}
    innodb-flush-log-at-trx-commit = 1
    innodb-file-per-table          = 1
    innodb-buffer-pool-size        = {innodb_buffer_pool_size}
    
    # LOGGING #
    log-error                      = {log_error}
    log-queries-not-using-indexes  = 0
    slow-query-log                 = 1
    slow-query-log-file            = {slow_query_log_file}
    long_query_time                = {long_query_time}
    
    [mysqldump]
    max-allowed-packet             = 16M
    """.format(**mycnf_make(_metaconf))))


def mycnf_innodb_log_file_size_MB(innodb_buffer_pool_size_GB):
    if int(innodb_buffer_pool_size_GB) > 60:
        return '2G'
    if int(innodb_buffer_pool_size_GB) > 22:
        return '1G'
    if float(innodb_buffer_pool_size_GB) > 7.2:
        return '512M'
    if float(innodb_buffer_pool_size_GB) > 3.6:
        return '256M'
    if float(innodb_buffer_pool_size_GB) > 1.6:
        return '128M'

    return '64M'


def output_memory_gb(gb):
    if math.fabs(math.ceil(gb) - gb) < 0.01:
        return str(int(gb)) + 'G'

    return str(int(gb * 1024)) + 'M'


def mycnf_make(m):
    m['innodb_buffer_pool_size'] = output_memory_gb(float(m['mysql_ram_gb']) * 0.7)
    m['innodb_log_file_size'] = mycnf_innodb_log_file_size_MB(m['mysql_ram_gb'])
    return m


def main(argv):
    actual_conf = defaults
    for arg in argv:
        kv = arg.split('=')
        if len(kv) == 2:
            actual_conf[kv[0]] = kv[1]

    output_my_cnf(actual_conf)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

