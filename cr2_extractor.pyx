import binascii
import os
import concurrent.futures

# cimport necessary Cython types for performance optimization
from libc.stdlib cimport malloc, free
from libc.string cimport memset
from cython cimport boundscheck, wraparound

# Define the CR2 signature for easy reference
CR2_SIGNATURE = binascii.unhexlify('49492A0010000000')
HEADER_SIZE = 16  # The size of the CR2 header

# Static types
@boundscheck(False)  # Disable bounds checking for performance
@wraparound(False)   # Disable negative index wrapping
cdef inline bint validate_cr2_header(unsigned char* cr2_data, Py_ssize_t data_len):
    """Validates the CR2 file header structure."""
    if data_len < HEADER_SIZE:
        return False

    # Check the byte order and TIFF magic number
    if cr2_data[0:2] != b'II' or cr2_data[2:4] != b'\x2A\x00':
        return False

    # Check Canon RAW magic number and version
    if cr2_data[8:10] != b'CR' or cr2_data[10] != 2:
        return False

    return True

@boundscheck(False)
@wraparound(False)
cdef tuple process_chunk(unsigned char* chunk_data, Py_ssize_t chunk_len, unsigned char* cr2_signature, Py_ssize_t sig_len, int global_file_number):
    cdef int index = 0, start_offset, end_offset, end_index
    cdef list extracted_files = []
    
    while True:
        index = chunk_data.find(cr2_signature, index)
        if index == -1 or index >= chunk_len:
            break

        start_offset = index
        end_index = chunk_data.find(cr2_signature, start_offset + 1)

        if end_index == -1:
            end_offset = chunk_len
        else:
            end_offset = end_index

        cr2_data = chunk_data[start_offset:end_offset]

        # Validate the CR2 header before extraction
        if validate_cr2_header(cr2_data, end_offset - start_offset):
            output_filename = f'{global_file_number:08d}.CR2'
            extracted_files.append((output_filename, cr2_data))
            global_file_number += 1

        index = end_offset

    return extracted_files, global_file_number

def save_extracted_files(output_dir, list extracted_files):
    for filename, data in extracted_files:
        output_file = os.path.join(output_dir, filename)
        with open(output_file, 'wb') as cr2_file:
            cr2_file.write(data)
        print(f'Extracted CR2 file to {output_file}')

def find_cr2_files(str input_file, str output_dir):
    cr2_signature = CR2_SIGNATURE
    file_size = os.path.getsize(input_file)
    chunk_size = 512 * 1024 * 1024  # 512MB chunk size
    overlap_size = 16  # 16-byte overlap between chunks

    global_file_number = 1  # Start file numbering from 1

    with open(input_file, 'rb') as f:
        chunk_number = 0
        while True:
            start_offset = max(0, chunk_number * chunk_size - overlap_size)
            f.seek(start_offset)
            chunk_data = f.read(chunk_size + overlap_size)

            if not chunk_data:
                break

            # Process this chunk and update the global file number
            extracted_files, global_file_number = process_chunk(chunk_data, len(chunk_data), cr2_signature, len(cr2_signature), global_file_number)

            # Save the extracted files
            save_extracted_files(output_dir, extracted_files)

            chunk_number += 1
            if start_offset + len(chunk_data) >= file_size:
                break

if __name__ == "__main__":
    input_file = input("Enter the path to the binary image file containing CR2 files: ").strip()

    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        exit(1)

    output_dir = 'Carved'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    find_cr2_files(input_file, output_dir)
