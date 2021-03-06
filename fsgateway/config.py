# Copyright 2012 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Wrapper for keystone.common.config that configures itself on import."""

import os

from oslo.config import cfg
from oslo.db import options

from fsgateway import debugger
from fsgateway import paths
from fsgateway import rpc
import version


_DEFAULT_SQL_CONNECTION = 'sqlite:///' + paths.state_path_def('fsgateway.sqlite')

CONF = cfg.CONF

opts = [
    cfg.IntOpt('rest_port',
               default=7077, help='Port of fs gateway rest service.'),
    cfg.IntOpt('proxy_port',
               default=8899, help='Port of fs gateway proxy service.'),
    cfg.DictOpt('cascaded_keystone_url_map',
               help='cascaded keystone auth url map.'),
        
    cfg.StrOpt('cascading_keystone_url',
               help='cascading keystone auth url.'),
    cfg.StrOpt('cascading_admin_user',
           help='cascading keystone admin user.'),
    cfg.StrOpt('cascading_tenant_name',
           help='cascading keystone tenant name'),
    cfg.StrOpt('cascading_admin_password',
               secret=True,
               help='cascading keystone admin user password.'),
    cfg.IntOpt('cascaded_token_expiration', default=86400, help='cascaded token default time (seconds)'),
    cfg.StrOpt('http_host_prefix',
           default='gateway--', 
           help='cascading keystone tenant name'),
]

CONF.register_opts(opts)


def parse_args(argv, default_config_files=None):
    options.set_defaults(CONF, connection=_DEFAULT_SQL_CONNECTION,
                         sqlite_db='fsgateway.sqlite')
    rpc.set_defaults(control_exchange='fsgateway')
    debugger.register_cli_opts()
    CONF(argv[1:],
         project='fsgateway',
         version=version.version_string(),
         default_config_files=default_config_files)
    rpc.init(CONF)
    for key in ('cascading_admin_password', 'cascaded_admin_password'):
        if key in CONF:
            password = CONF[key]

            try:
                from FSComponentUtil import crypt
                CONF.set_override(key, crypt.decrypt(password))
            except Exception:
                pass

