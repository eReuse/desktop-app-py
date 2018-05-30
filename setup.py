from setuptools import find_packages, setup

setup(
    name='ereuse-desktop-app',
    version='0.1',
    packages=find_packages(exclude=('contrib', 'docs', 'scripts')),
    url='https://github.com/ereuse/desktop-app-py',
    license='AGPLv3 License',
    author='eReuse.org team',
    author_email='j.nadeu@ereuse.org',
    description='Desktop App',
    # Updated in 2017-07-29
    install_requires=[
        'flask>=0.11',
        'ereuse-utils [test]',
        'requests',
        'flask-cors',
        'dateutil'
    ],
    keywords='eReuse.org DesktopApp support and diagnostic using Workbench',
    test_suite='workbench_server.tests',
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest',
        'requests_mock'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Office/Business',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ]
)
