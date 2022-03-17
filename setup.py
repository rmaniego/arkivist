import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name = 'arkivist',
    packages = ["arkivist"],
    version = '1.1.37',
    license='MIT',
    description = 'Arkivist, a Python Dictionary wrapper for JSON files.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = 'Rodney Maniego Jr.',
    author_email = 'rod.maniego23@gmail.com',
    url = 'https://github.com/rmaniego/arkivist',
    download_url = 'https://github.com/rmaniego/arkivist/archive/v1.0.tar.gz',
    keywords = ['Dictionary', 'JSON', 'File', 'Storage'],
    install_requires=["requests"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers', 
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.6'
)