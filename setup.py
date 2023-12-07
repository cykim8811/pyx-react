from setuptools import setup, find_packages

setup(
    name='pyx-react',
    version='0.1.1-alpha.0',
    description='A framework that enables Python objects to be easily rendered on a web server',
    author='Kim Changyeon',
    author_email='cykim8811@snu.ac.kr',
    url='https://github.com/cykim8811/pyx-react',
    packages=find_packages(where='src'),
    install_requires=[],
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords=['pyx', 'react', 'python', 'visualization', 'web'],
    package_dir = {'': 'src'},
    package_data={'pyx': ['assets/*']},
)

