print("Hello from World C!")
import os
with open(os.path.join(os.getcwd(), "world_c_results", "simple_test_output.txt"), "w") as f:
    f.write("Simple test output for job_llama_3_3_1790995718_acb4\n")