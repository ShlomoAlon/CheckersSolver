import subprocess
import time

# List of input files and output files
input_files = ["checkers7.txt", "checkers1.txt", "checkers2.txt", "checkers3.txt", "checkers4.txt", "test3.txt", "message2.txt", "message4.txt"]
output_files = ["output1.txt", "output2.txt", "output3.txt", "output4.txt", "output5.txt", "output6.txt", "output7.txt",
                "output8.txt"]

# Run checkers_starter.py for each combination of input and output files
for i in range(0, len(input_files)):
    input_file = input_files[i]
    output_file = output_files[i]

    # Measure the execution time
    start_time = time.time()

    # Run the checkers_starter.py script with the given input and output files
    command = f"python checkers.py --inputfile {input_file} --outputfile {output_file}"
    subprocess.run(command, shell=True)

    # Calculate and print the time taken
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time for {input_file}: {elapsed_time} seconds")
    file = open(output_file, "r")
    print("number of board states in the file",(len(file.readlines()) + 1) // 9)