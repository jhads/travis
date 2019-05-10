from setuptools import setup


packages = [
    'travis',
    'travis.readme_scorer',
]

package_dir = {
    'travis':'.',
    'travis.readme_scorer':'readme_scorer',
}


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='travis',
    version='0.1.0',
    description='',
    author='jhads',
    author_email='',
    url='https://github.com/jhads/travis',
    packages=packages,
    package_dir=package_dir,
    include_package_data=True,
    install_requires=[x for x in required],
    license='MIT',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Intended Audience :: Developers',
    ],
    scripts = ['bin/readme_scorer'],
)
