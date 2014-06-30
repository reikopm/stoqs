#!/usr/bin/env python
__author__    = 'Mike McCann'
__copyright__ = '2013'
__license__   = 'GPL v3'
__contact__   = 'mccann at mbari.org'

__doc__ = '''

Loader for IOOS Glider DAC

Mike McCann
MBARI 22 April 2014

@var __date__: Date of last svn commit
@undocumented: __doc__ parser
@status: production
@license: GPL
'''

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))      # So that IOOS and DAPloaders are found
import logging 
import datetime
from IOOS import IOOSLoader
from DAPloaders import runGliderLoader
from thredds_crawler.crawl import Crawl

logger = logging.getLogger('__main__')

il = IOOSLoader('stoqs_ioos_gliders', 'IOOS Gliders',
                                x3dTerrains = {
                                    'http://dods.mbari.org/terrain/x3d/Globe_1m_bath_10x/Globe_1m_bath_10x_scene.x3d': {
                                        'position': '14051448.48336 -15407886.51486 6184041.22775',
                                        'orientation': '0.83940 0.33030 0.43164 1.44880',
                                        'centerOfRotation': '0 0 0',
                                        'VerticalExaggeration': '10',
                                    }
                                }
)

il.parms = ['temperature', 'salinity', 'density']

# Start and end dates of None will load entire archive
il.startDatetime = None
il.endDatetime = None

def loadGliders(loader, stride=1):
    '''
    Crawl the IOOS Glider TDS for OPeNDAP links of Time aggregated files and load into STOQS
    '''

    c = Crawl("http://tds.gliders.ioos.us/thredds/catalog.xml", select=[".*_Time$"])
    urls = [s.get("url") for d in c.datasets for s in d.services if s.get("service").lower() == "opendap"]
    colors = loader.colors.values()

    for url in urls:
        aName = url.split('/')[-1].split('.')[0]
        pName = aName.replace('_Time', '')
        if pName.find('-') != -1:
            logger.warn("Replacing '-' characters in platform name %s with '_'s", pName)
            pName = pName.replace('-', '_')

        logger.info("Executing runGliderLoader with url = %s", url)
        try:
            runGliderLoader(url, loader.campaignName, aName, pName, colors.pop(), 'glider', 'Glider Mission', 
                            loader.parms, loader.dbAlias, stride, loader.startDatetime, loader.endDatetime)
        except Exception, e:
            logger.error('%s. Skipping this dataset.', e)


# Execute the load
il.process_command_line()

if il.args.test:
    loadGliders(il, stride=100)

elif il.args.optimal_stride:
    loadGliders(il, stride=10)

else:
    loadGliders(il, stride=il.args.stride)

# Add any X3D Terrain information specified in the constructor to the database - must be done after a load is executed
il.addTerrainResources()

print "All Done."
