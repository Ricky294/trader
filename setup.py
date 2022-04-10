from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="trader",
        url="https://github.com/Ricky294/trader",
        description="This library helps you to backtest and live trade trading strategies.",
        author="Ricky",
        author_email="p.ricky.dev@gmail.com",
        version="0.1.0",
        packages=find_packages(),
        license="MIT",
        install_requires=["numpy", "pandas", "plotly", "tqdm"],
        extras_require={
            "testing": ["pytest"],
        }
    )
