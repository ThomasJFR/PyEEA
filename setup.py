from setuptools import setup

setup(
  name = 'PyEEA',
  version = '0a2',
  license='MIT',
  description = 'A Python3.8 library for conducting Engineering Economic Analyses',
  author = 'Thomas Richmond',
  author_email = 'thomas.joakim@gmail.com',
  url = 'https://github.com/ThomasJFR/PyEEA',
  download_url = 'https://github.com/ThomasJFR/PyEEA/archive/v0.1.1.tar.gz',
  keywords = ['Engineering', 'Economic', 'Analysis', 'Finance'],
  packages = [
    'PyEEA',
    'PyEEA.analysis',
    'PyEEA.cashflow',
    'PyEEA.output',
    'PyEEA.taxation',
    'PyEEA.valuation'
  ],
  install_requires = [
    'pandas',
    'matplotlib',
    'scipy'
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8'
  ],
)
