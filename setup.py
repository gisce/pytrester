from setuptools import setup, find_packages


setup(
    name='pytrester',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/gisce/pytrester',
    license='MIT',
    author='GISCE-TI, S.L.',
    install_requires=[
        'tqdm',
        'coverage',
        'google-api-python-client',
        'destral'

    ],
    author_email='devel@gisce.net',
    description='CI to test ERP in Py3 environment'
)
