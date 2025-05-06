from setuptools import setup, find_packages

setup(
    name="inventory-analytics-dashboard",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.13.0",
        "matplotlib>=3.7.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A Streamlit-based inventory analytics dashboard",
    keywords="inventory, analytics, streamlit, dashboard",
    url="https://github.com/yourusername/inventory-analytics-dashboard",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Business/Industry",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)