import os

# Obtém o número de núcleos de CPU disponíveis
num_nucleos = os.cpu_count()
print(f"Número de núcleos disponíveis: {num_nucleos}")
