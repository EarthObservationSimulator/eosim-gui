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
    # Cartopy installation may not work due to additional dependencies it requires. 
    # CartoPy dependencies must be installed before running this setup.
    # If using conda, cartopy along with its dependencies can be installed using the command `conda install -c conda-forge cartopy`
    # In case of Runtime errors involving numpy, try the following command: `pip install numpy --upgrade --ignore-installed`
    install_requires=['numpy', 'pandas', 'scipy', 'lowtran', 'cartopy'] 
)
