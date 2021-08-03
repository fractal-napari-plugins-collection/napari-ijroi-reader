from setuptools import setup, find_packages


setup(
    name='fractal-napari-plugins-colletion:ijroi-reader',
    version='1.0.0',
    author='Dario Vischi, Marco Franzon',
    author_email='dario.vischi@fmi.ch, marco.franzon@exact-lab.it',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    license='MIT',
    description=(
        'Plugin for reading ImageJ ROI files into Napari.'
    ),
    long_description=open('README.md').read(),
    python_requires='>=3.6',
    install_requires=[
        "napari[all] >= 0.3.8",
        "napari_plugin_engine >= 0.1.9",
        "dask[complete] >= 2021.3.0",
        "numpy >= 1.19.5",
        "imagecodecs >= 2020.5.30"
    ],
    entry_points={
        'napari.plugin': [
            'napari_ijroi_reader = napari_ijroi_reader.napari_ijroi_reader'
        ],
    },
    setup_requires=['pytest-runner',],
    tests_require=['pytest',],

)
