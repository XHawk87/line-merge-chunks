from setuptools import setup

setup(
    name='line-merge-chunks',
    version='1.0.0',
    description='Merges separate lines together from standard input, '
                'escaping new line characters, and outputting them in chunks '
                'to standard output limited by time and/or character count.',
    author='XHawk87',
    author_email='hawk87@hotmail.co.uk',
    scripts=['line-merge-chunks'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    python_requires='>=3.6',
)
