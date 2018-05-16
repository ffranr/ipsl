from setuptools import setup, find_packages


setup(name='ipsl',
      version='0.1',
      description='InterPlanetary Soft Links (IPSL)',
      packages=find_packages(),
      author='Robyn Ffrancon',
      author_email='robyn.ffrancon@protonmail.com',
      install_requires=[
          'ipfsapi >= 0.4.2-1',
          'docopt >= 0.6.2'
      ],
      entry_points={
          'console_scripts': ['ipsl = ipsl.ipsl:run']
      },
      test_suite='ipsl.tests',
      license='MIT')
