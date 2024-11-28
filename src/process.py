import subprocess



command = ["pdal", "pipeline", "src/p_dsm.json"]
result = subprocess.run(command, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Error:", result.stderr)

