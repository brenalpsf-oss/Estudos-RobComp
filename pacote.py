""""NO TERMINAL"""

# 1. Entre na pasta de código (src) do seu repositório da prova
# O caminho exato depende do nome que o GitHub Classroom deu à sua pasta
cd ~/colcon_ws/src/projeto_da_prova

# 2. Crie o pacote ROS 2
# Substitua 'avaliacao_ai' pelo nome que o professor pedir
# As dependências 'robcomp_util' e 'robcomp_interfaces' são padrão do Insper
ros2 pkg create --build-type ament_python avaliacao_ai --dependencies rclpy robcomp_util robcomp_interfaces geometry_msgs sensor_msgs

# 3. Entre na pasta onde os scripts .py devem morar
cd avaliacao_ai/avaliacao_ai

# 4. Crie o arquivo da questão (ex: q1.py)
touch q1.py


""" sempre que você mudar o setup ou criar arquivos novos precisa rodar isso"""

# 1. Vá para a raiz do workspace
cd ~/colcon_ws

# 2. Compile apenas o seu pacote (economiza tempo na prova!)
colcon build --packages-select avaliacao_ai

# 3. Avise ao terminal onde estão os novos binários
source install/setup.bash

# 4. Rode o seu código (usando o nome que você colocou no setup.py)
ros2 run avaliacao_ai executavel_q1