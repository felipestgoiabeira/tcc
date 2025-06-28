from setuptools import setup, find_packages

setup(
    name='rdf-mapper',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'rdflib>=6.0.0'
    ],
    author='Felipe dos Santos Goiabeira',
    author_email='felipe.goiabeira@discente.ufma.br',
    description='Pequeno framework estilo JPA para RDF com suporte a mapeamento e consulta dinâmica',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/felipestgoiabeira/rdf-mapper',  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
    python_requires='>=3.8',
)