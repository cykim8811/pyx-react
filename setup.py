from setuptools import setup, find_packages

setup(
    name='pyx-react',
    version='0.2.0',
    description='Python object visualization library',
    author='cykim8811',
    author_email='cykim8811@snu.ac.kr',
    url='https://github.com/cykim8811/pyx-react',
    packages=find_packages(where='src'),
    install_requires=[
        'starlette',
        'uvicorn',
    ],
    entry_points={},
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords=['pyx', 'react', 'python', 'visualization', 'web'],
    package_dir = {'': 'src'},
    package_data={'pyx': ['assets/*']},
)

