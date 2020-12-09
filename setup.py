from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='EOSim',
    version='0.1',
    description='Earth Observation Simulation',
    author='BAERI',
    author_email='vinay.ravindra@nasa.gov',
    packages=['eosim'],
    scripts=[ 
    ],
    install_requires=['numpy', 'pandas', 'scipy', 'lowtran', 'nose', 'sphinx', 'sphinx_rtd_theme', 'cartopy'] 
)
