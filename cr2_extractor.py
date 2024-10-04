import os
import cr2_extractor  # Import the compiled Cython module

def main():
    input_file = input("Enter the path to the binary image file containing CR2 files: ").strip()

    # Validate the input file path
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    output_dir = 'Carved'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Call the function to find CR2 files
    cr2_extractor.find_cr2_files(input_file, output_dir)

if __name__ == "__main__":
    main()
