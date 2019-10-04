#!/usr/bin/env python

# ===============================================================================
# title           : mycnf_generator.py
# description     : script to generate MySQL configuration file which has ensured best practice
# authors         : AndrianBdn, Sodjamts
# create date     : Aug 06, 2019
# last updated:   : Sep 02, 2019
# version         : 1.2
# usage           : python mycnf_generator.py mysql_ram_gb=2
# requirement     : python2
# ===============================================================================

import sys
import math
import random
from textwrap import dedent

defaults = {
    'tmp_dir': "/var/tmp",
    'mysql_dir': "/var/lib/mysql",
    'mysql_log_dir': "/var/lib/mysql-log",
    'log_error': "/var/log/mysql/mysql-error.log",
    'slow_query_log_file': "/var/log/mysql/mysql-slow.log",
    'pid_file': "/var/run/mysqld/mysqld.pid",

    'character_set': "utf8mb4",
    'collation_server': "utf8mb4_general_ci",

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
    default_storage_engine         = InnoDB
    socket                         = {mysql_dir}/mysql.sock
    pid_file                       = {pid_file}
    character_set_server	       = {character_set}
    collation_server	           = {collation_server}
    #tmpdir	  = {tmp_dir}
    
    # MyISAM #
    key_buffer_size                = 32M
    myisam_recover_options         = FORCE,BACKUP
    
    # SAFETY #
    max_allowed_packet             = 128M
    max_connect_errors             = 1000000
    skip_name_resolve
    skip_external_locking
    #transaction_isolation          = READ-COMMITTED
    
    # DATA STORAGE #
    datadir                        = {mysql_dir}
    
    # BINARY LOGGING #
    log_bin                        = {mysql_log_dir}/mysql-bin
    relay_log                      = {mysql_log_dir}/mysql-relay-bin
    binlog_format                  = ROW
    max_binlog_size                = 1024M
    expire_logs_days               = 7
    sync_binlog                    = 1
    #log_slave_updates              = 1
    
    # SERVER ID # 
    server_id                      = {server_id}
    
    # REPLICATION #
    master_info_repository         = TABLE
    relay_log_info_repository      = TABLE
    #gtid_mode                      = on
    #enforce_gtid_consistency
    
    # CACHES AND LIMITS #
    tmp_table_size                 = {tmp_table_size}
    max_heap_table_size            = {tmp_table_size}
    query_cache_type               = {query_cache_type}
    query_cache_size               = {query_cache_size}
    max_connections                = {max_connections}
    thread_cache_size              = 100
    open_files_limit               = 65535
    table_definition_cache         = 1024
    table_open_cache               = 2048
    
    # INNODB #
    innodb_flush_method            = O_DIRECT
    innodb_log_files_in_group      = 2
    innodb_log_file_size           = {innodb_log_file_size}
    innodb_log_buffer_size         = {innodb_log_buffer_size}
    innodb_log_group_home_dir      = {mysql_log_dir}
    innodb_flush_log_at_trx_commit = 1
    innodb_file_per_table          = 1
    innodb_buffer_pool_size        = {innodb_buffer_pool_size}
    innodb_buffer_pool_instances   = {innodb_buffer_pool_instances}
    
    # LOGGING #
    log_error                      = {log_error}
    log_error_verbosity            = 3
    log_queries_not_using_indexes  = 0
    slow_query_log                 = 1
    slow_query_log_file            = {slow_query_log_file}
    long_query_time                = {long_query_time}
    
    # SECURITY #
    local_infile                   = 0
    old_passwords                  = 0
    log_raw                        = off
    
    [mysqldump]
    max_allowed_packet             = 128M
    default_character_set          = {character_set}
    socket                         = {mysql_dir}/mysql.sock
    """.format(**mycnf_make(_metaconf))))


def mycnf_innodb_log_file_size_mb(mysql_ram_gb):
    if int(mysql_ram_gb) > 60:
        return '2G'
    if int(mysql_ram_gb) > 15:
        return '1G'
    if float(mysql_ram_gb) > 7.2:
        return '512M'
    if float(mysql_ram_gb) > 3.6:
        return '256M'
    if float(mysql_ram_gb) > 1.6:
        return '128M'
    return '64M'


def mycnf_innodb_buffer_pool_instance(mysql_ram_gb):
    if int(mysql_ram_gb) > 60:
        return 16
    if int(mysql_ram_gb) > 15:
        return 12
    if int(mysql_ram_gb) > 7.2:
        return 8
    if int(mysql_ram_gb) > 3.6:
        return 4
    if int(mysql_ram_gb) > 1.6:
        return 2
    return 1


def mycnf_innodb_log_buffer_size_mb(mysql_ram_gb):
    if int(mysql_ram_gb) > 60:
        return '512M'
    if int(mysql_ram_gb) > 30:
        return '256M'
    if int(mysql_ram_gb) > 15:
        return '128M'
    if float(mysql_ram_gb) > 7.2:
        return '64M'
    return '32M'


def mycnf_tmp_table_size_mb(mysql_ram_gb):
    if int(mysql_ram_gb) > 120:
        return '128M'
    if float(mysql_ram_gb) > 30:
        return '64M'
    return '32M'


def output_memory_gb(gb):
    if math.fabs(math.ceil(gb) - gb) < 0.01:
        return str(int(gb)) + 'G'

    return str(int(gb * 1024)) + 'M'


def mycnf_make(m):
    m['innodb_buffer_pool_size'] = output_memory_gb(float(m['mysql_ram_gb']) * 0.7)
    m['innodb_log_file_size'] = mycnf_innodb_log_file_size_mb(m['mysql_ram_gb'])
    m['innodb_buffer_pool_instances'] = mycnf_innodb_buffer_pool_instance(m['mysql_ram_gb'])
    m['innodb_log_buffer_size'] = mycnf_innodb_log_buffer_size_mb(m['mysql_ram_gb'])
    m['tmp_table_size'] = mycnf_tmp_table_size_mb(m['mysql_ram_gb'])
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

