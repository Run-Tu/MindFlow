from setuptools import setup, find_packages

setup(
    name='mindflow',
    version='0.0.1',
    packages=find_packages(include=['mindflow', 'mindflow.core', 'mindflow.core.utils']),
    install_requires=["gradio_client", "toml", "rich"],
    entry_points={
        'console_scripts': [
            'macro=mindflow.__main__:main',  
        ],
    },
    include_package_data=True, 
    package_data={
        'mindflow': ['core/config.default.toml', 'core/prompts/*', 'extensions/*'],  
    },
    author='Run Tu',
    author_email='run-tu@gmail.com',
    description='Autonomous LLM personal agent.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/run-tu/mindflow',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
