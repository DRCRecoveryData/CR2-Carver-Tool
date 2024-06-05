import binascii
import os

def find_cr2_files(input_file, output_dir):
    cr2_signature = binascii.unhexlify('49492A0010000000')  # CR2 file signature in hexadecimal

    with open(input_file, 'rb') as f:
        file_size = os.path.getsize(input_file)

        # Read the entire file into memory for faster processing
        data = f.read()

    index = 0
    file_number = 1

    while True:
        # Find the next occurrence of CR2 file header
        index = data.find(cr2_signature, index)
        if index == -1:
            break
        
        # Determine the start and end positions of the CR2 file
        start_offset = index
        end_index = data.find(cr2_signature, start_offset + 1)

        if end_index == -1:
            end_offset = file_size  # If no next signature, take till end of file
        else:
            end_offset = end_index

        # Extract the CR2 file data
        cr2_data = data[start_offset:end_offset]

        # Generate filename based on offset
        offset_hex = hex(start_offset)
        output_filename = f'0x{offset_hex[2:].zfill(8)}.CR2'  # Example: 0x12345678.cr2

        # Write the CR2 file to output directory
        output_file = os.path.join(output_dir, output_filename)
        with open(output_file, 'wb') as cr2_file:
            cr2_file.write(cr2_data)

        print(f'Extracted CR2 file {file_number} to {output_file}')

        # Move index forward to search for the next CR2 file
        index = end_offset
        file_number += 1

if __name__ == "__main__":
    # Prompt user for input file path
    input_file = input("Enter the path to the binary image file containing CR2 files: ").strip()

    # Ensure the input file exists
    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        exit(1)

    # Create output directory
    output_dir = 'Carved'  # Replace with your desired output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Call function to find and extract CR2 files
    find_cr2_files(input_file, output_dir)
