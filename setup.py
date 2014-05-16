from setuptools import setup, find_packages

version = '2.0.5.eea'

setup(name='plone.locking',
      version=version,
      description="webdav locking support",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
        ],
      keywords='locking webdav plone archetypes',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.locking',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'Products.Archetypes',
            'Products.PloneTestCase',
        ]
      ),
      install_requires=[
        'setuptools',
        'zope.annotation',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        'zope.viewlet',
        'Acquisition',
        'DateTime',
        'Products.CMFCore',
        'ZODB3',
        'Zope2',
      ],
      )
