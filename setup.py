from setuptools import setup, find_packages


setup(
    name='jsonmapping',
    version='0.4.0',
    description="Map flat data to structured JSON via a mapping.",
    long_description="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='schema jsonschema json data conversion',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://github.com/pudo/jsonmapping',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'test']),
    namespace_packages=[],
    package_data={
        '': ['jsonmapping/schemas/*.json']
    },
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        'typecast',
        'normality',
        'unidecode',
        'jsonschema',
        'six'
    ],
    tests_require=[
        'nose',
        'coverage',
        'wheel',
        'unicodecsv'
    ]
)
