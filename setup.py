#!/usr/bin/env python
import os
import jeffy
import sys
import shutil

from setuptools import setup, find_packages, Command

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

description = 'Serverless "Application" Framework'
long_description = description
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()

class UploadCommand(Command):

    def run(self):
        try:
            cwd = os.path.join(os.path.abspath(os.path.dirname(__file__))
            shutil.rmtree(os.path.join(cwd, 'dist'))
            os.remove(os.path.join(cwd, 'README.txt')
        except FileNotFoundError:
            pass

        os.system("pandoc README.md --from=markdown --to=rst > README.txt")
        os.system('python setup.py sdist')
        os.system('twine upload dist/*')
        os.system('git tag v{0}'.format(jeffy.__version__))
        os.system('git push --tags')
        sys.exit()

setup_options = dict(
    name='jeffy',
    version=jeffy.__version__,
    description=description,
    long_description=long_description,
    author='Masashi Terui',
    author_email='marcy9114+pypi@gmail.com',
    url='https://github.com/marcy-terui/jeffy',
    packages=find_packages(exclude=['tests*', 'lambda_function']),
    install_requires=open('requirements.txt').read().splitlines(),
    license="MIT License",
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    keywords='aws lambda serverless faas',
    cmdclass={
        'upload': UploadCommand,
    },
)

setup(**setup_options)
