'''
Module responsible for running the --support option for collecting debug information
'''
import logging
import shlex
import re
import os
import requests
from subprocess import Popen, PIPE, STDOUT
from constants import InsightsConstants as constants
from connection import InsightsConnection

APP_NAME = constants.app_name
logger = logging.getLogger(APP_NAME)


class InsightsSupport(object):
    '''
    Build the support logfile
    '''
    def __init__(self, config):
        self.config = config

    def registration_check(self):
        # check local registration record
        if os.path.isfile(constants.registered_file):
            local_record = 'System is registered.'
            with open(constants.registered_file) as reg_file:
                local_record += ' Registered at ' + reg_file.readline()
        else:
            local_record = 'System is NOT registered.'
        if os.path.isfile(constants.unregistered_file):
            with open(constants.unregistered_file) as reg_file:
                local_record += ' Unregistered at ' + reg_file.readline()

        pconn = InsightsConnection(self.config)
        api_reg_status = pconn.api_registration_check()
        if type(api_reg_status) is bool:
            if api_reg_status:
                api_record = 'Insights API confirms registration.'
            else:
                api_record = 'Insights API could not be reached to confirm registration status.'
        elif api_reg_status is None:
            api_record = 'Insights API says this machine is NOT registered.'
        else:
            api_record = 'Insights API says this machine was unregistered at ' + api_reg_status

        return [local_record, api_record]

    def collect_support_info(self):
        '''
        Collect log info for debug
        '''
        # check insights config
        cfg_block = []

        logger.info('Insights version: %s' % (constants.version))
        cfg_block += self.registration_check()

        lastupload = 'never'
        if os.path.isfile(constants.lastupload_file):
            with open(constants.lastupload_file) as upl_file:
                lastupload = upl_file.readline().strip()
        cfg_block.append('Last successful upload was ' + lastupload)

        cfg_block.append('auto_config: ' + str(self.config.getboolean(APP_NAME, 'auto_config')))
        if self.config.get(APP_NAME, 'proxy'):
            obfuscated_proxy = re.sub(r'(.*)(:)(.*)(@.*)',
                                      r'\1\2********\4',
                                      self.config.get(APP_NAME, 'proxy'))
        else:
            obfuscated_proxy = 'None'
        cfg_block.append('proxy: ' + obfuscated_proxy)

        logger.info('\n'.join(cfg_block))
        logger.info('python-requests: %s' % (requests.__version__))

        # run commands
        commands = ['redhat-access-insights --test-connection --quiet',
                    'uname -a',
                    'cat /etc/redhat-release',
                    'env',
                    'sestatus',
                    'subscription-manager identity']
        for cmd in commands:
            proc = Popen(
                shlex.split(cmd), shell=False, stdout=PIPE, stderr=STDOUT, close_fds=True)
            stdout, stderr = proc.communicate()
            if 'test-connection' in cmd:
                if proc.returncode == 0:
                    logger.info('Connection test: PASS\n')
                else:
                    logger.info('Connection test: FAIL\n')
            else:
                logger.info(stdout)

        # check available disk space for /var/tmp
        tmp_dir = '/var/tmp'
        dest_dir_stat = os.statvfs(tmp_dir)
        dest_dir_size = (dest_dir_stat.f_bavail * dest_dir_stat.f_frsize)
        logger.info('Available space in %s:\t%s bytes\t%.1f 1K-blocks\t%.1f MB' % (
                    tmp_dir, dest_dir_size,
                    dest_dir_size / 1024.0,
                    (dest_dir_size / 1024.0) / 1024.0))
