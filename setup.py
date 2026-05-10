from setuptools import setup
import os
from glob import glob

package_name = 'avaliacao_ai' # CONFIRA: Deve ser o nome da pasta do seu pacote

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name], # Deve ser igual ao package_name
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Brena',
    maintainer_email='brena@exemplo.com',
    description='Prova de Robotica Computacional',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # FORMATO: 'comando_terminal = nome_do_pacote.nome_do_arquivo:main'
            # MUDE AQUI PARA CADA QUESTÃO DA PROVA:
            'executavel_q1 = avaliacao_ai.q1:main',
            'executavel_q2 = avaliacao_ai.q2:main',
            'executavel_q3 = avaliacao_ai.q3:main',
        ],
    },
)