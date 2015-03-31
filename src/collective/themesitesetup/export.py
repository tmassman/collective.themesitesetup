# -*- coding: utf-8 -*-
from io import BytesIO
import tarfile

from Products.Five import BrowserView
from plone import api

import time


# noinspection PyPep8Naming
class ExportView(BrowserView):
    def __call__(self):
        # Create export
        portal_setup = api.portal.get_tool('portal_setup')
        tarball = portal_setup.runAllExportSteps()['tarball']

        # Open the exported tarball
        fb = BytesIO(tarball)
        tar = tarfile.open(fileobj=fb, mode='r:gz')

        # Create base directory
        directoryName = '-'.join([self.__name__, str(time.time())])
        self.context.makeDirectory(directoryName)
        baseDirectory = self.context[directoryName]

        # Export tarball contents into the base directory
        for info in tar:
            if info.type == tarfile.DIRTYPE:
                baseDirectory.makeDirectory(info.name)
            else:
                path = info.path

                # Fix names filtered by resourcedirectory
                path = path.replace('/.objects', '/objects')
                path = path.replace('/.properties', '/properties')

                baseDirectory.writeFile(path, tar.extractfile(info))

        # Close the tarfile
        tar.close()

        # Redirect to mapper
        next_url = self.request.URL.replace(
            self.__name__, 'theming-controlpanel-mapper')
        self.request.response.setBody('', lock=True)
        self.request.response.redirect(next_url)
