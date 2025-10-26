import subprocess
import os

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.abspath(__file__))

# Construct the paths to the tailwindcss cli.js, input css, and output css
tailwind_cli_js = os.path.join(project_root, 'node_modules', 'tailwindcss', 'lib', 'cli.js')
input_css = os.path.join(project_root, 'static', 'css', 'input.css')
output_css = os.path.join(project_root, 'static', 'css', 'output.css')

# Construct the command
command = ['node', tailwind_cli_js, '-i', input_css, '-o', output_css]

# Run the command
try:
    subprocess.run(command, check=True, shell=True)
    print('Successfully built Tailwind CSS!')
except subprocess.CalledProcessError as e:
    print(f'Error building Tailwind CSS: {e}')
