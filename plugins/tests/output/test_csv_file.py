'''
test_csv_file.py

Copyright 2012 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
import os
import csv
import json

import core.data.kb.vuln as vuln

from core.data.parsers.url import URL
from plugins.tests.helper import PluginTest, PluginConfig


class TestCSVFile(PluginTest):
    
    OUTPUT_FILE = 'output-unittest.csv'
    
    xss_url = 'http://moth/w3af/audit/xss/'
    
    _run_configs = {
        'cfg': {
            'target': xss_url,
            'plugins': {
                'audit': (
                    PluginConfig(
                         'xss',
                         ('checkStored', True, PluginConfig.BOOL),
                         ('numberOfChecks', 3, PluginConfig.INT)),
                    ),
                'crawl': (
                    PluginConfig(
                        'web_spider',
                        ('onlyForward', True, PluginConfig.BOOL)),
                ),
                'output': (
                    PluginConfig(
                        'csv_file',
                        ('output_file', OUTPUT_FILE, PluginConfig.STR)),
                )         
            },
        }
    }
    
    def test_found_xss(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])
        
        xss_vulns = self.kb.get('xss', 'xss')
        file_vulns = self._from_csv_get_vulns()
        
        self.assertGreaterEqual(len(xss_vulns), 3)
        
        self.assertEquals(
            set(sorted([v.getURL() for v in xss_vulns])),
            set(sorted([v.getURL() for v in file_vulns]))
        )
        
        self.assertEquals(
            set(sorted([v.get_method() for v in xss_vulns])),
            set(sorted([v.get_method() for v in file_vulns]))
        )

        self.assertEquals(
            set(sorted([v.get_id()[0] for v in xss_vulns])),
            set(sorted([v.get_id()[0] for v in file_vulns]))
        )
        
    def _from_csv_get_vulns(self):
        file_vulns = []
        
        vuln_reader = csv.reader(open(self.OUTPUT_FILE, 'rb'), delimiter=',',
                                     quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for name,method,uri,var,dc,_id,desc in vuln_reader:
            v = vuln.vuln()
            
            v.set_name(name)
            v.set_method( method )
            v.setURI( URL(uri) )
            v.set_var(var)
            v.set_dc(dc)
            v.set_id(json.loads(_id) )
            v.set_desc(desc)
            
            file_vulns.append(v)
        
        return file_vulns
            
    def tearDown(self):
        try:
            os.remove(self.OUTPUT_FILE)
        except:
            pass
