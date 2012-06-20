from setuptools import setup, find_packages
import os

version = '1'

setup(name='collective.pfg.mailchimp',
      version=version,
      description="Adds subscribing to Singing & Dancing newsletter to PloneFormGen",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Thomas Clement Mogensen',
      author_email='thomas@headnet.dk',
      url='http://svn.plone.org/svn/plone/plone.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.pfg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.PloneFormGen',
          'collective.mailchimp',
      ],
      entry_points="""
      # -*- Entry points: -*-

      """,
      )
