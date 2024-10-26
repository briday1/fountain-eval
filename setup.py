from setuptools import setup, find_packages

setup(
    name='fountain-eval',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'matplotlib'
    ],
    entry_points={
        'console_scripts': [
            'fountain_eval=fountain_eval.fountain_eval:main',
        ],
    },
    author='Your Name',
    author_email='you@example.com',
    description='A script to analyze Fountain files for character activity and word/line counts.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/fountain-eval',  # If hosted on GitHub
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

