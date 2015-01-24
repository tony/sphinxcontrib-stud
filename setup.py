"""
sphinxcontrib-stud
~~~~~~~~~~~~~~~~~~~~

stud directives and roles for sphinx.


Links
-----

* `stud repository <https://www.github.com/tony/sphinxcontrib-stud>`_

"""
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    install_reqs = [line for line in f.read().split('\n') if line]
    tests_reqs = []

setup(
    name='sphinxcontrib-stud',
    version='0.1.0',
    url='https://github.com/tony/sphinxcontrib-stud/',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-stud',
    license='BSD',
    author='Tony Narlock and Guibog',
    author_email='wengu@git-pull.com',
    description='stud directives and roles for sphinx',
    long_description=open('README.rst').read(),
    zip_safe=False,
    packages=find_packages(),
    install_requires=install_reqs,
    namespace_packages=['sphinxcontrib'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
)
