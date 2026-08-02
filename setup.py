from setuptools import find_packages, setup

setup(
    name="opensea_mail",
    version="0.2.0",
    description="Scheduled OpenSea floor-price and cryptocurrency alerts",
    packages=find_packages(),
    package_data={"opensea_mail": ["config/*.yaml"]},
    python_requires=">=3.10",
    install_requires=[
        "python-dotenv>=1.0,<2.0",
        "PyYAML>=6.0,<7.0",
        "requests>=2.31,<3.0",
    ],
)
