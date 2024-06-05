import binascii
import os
import concurrent.futures

def find_cr2_files_in_segment(data, start_index, file_size, cr2_signature):
    extracted_files = []
    index = start_index
    file_number = 1

    while True:
        index = data.find(cr2_signature, index)
        if index == -1 or index >= file_size:
            break

        start_offset = index
        end_index = data.find(cr2_signature, start_offset + 1)

        if end_index == -1 or end_index >= file_size:
            end_offset = file_size
        else:
            end_offset = end_index

        cr2_data = data[start_offset:end_offset]

        offset_hex = hex(start_offset)
        output_filename = f'0x{offset_hex[2:].zfill(8)}.CR2'

        extracted_files.append((output_filename, cr2_data))

        index = end_offset
        file_number += 1

    return extracted_files

def save_extracted_files(output_dir, extracted_files):
    for filename, data in extracted_files:
        output_file = os.path.join(output_dir, filename)
        with open(output_file, 'wb') as cr2_file:
            cr2_file.write(data)
        print(f'Extracted CR2 file to {output_file}')

def find_cr2_files(input_file, output_dir):
    cr2_signature = binascii.unhexlify('49492A0010000000')

    with open(input_file, 'rb') as f:
        data = f.read()

    file_size = len(data)
    segment_size = file_size // os.cpu_count()

    futures = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(os.cpu_count()):
            start_index = i * segment_size
            end_index = (i + 1) * segment_size if i != os.cpu_count() - 1 else file_size
            futures.append(executor.submit(find_cr2_files_in_segment, data, start_index, end_index, cr2_signature))

        all_extracted_files = []
        for future in concurrent.futures.as_completed(futures):
            all_extracted_files.extend(future.result())

    save_extracted_files(output_dir, all_extracted_files)

if __name__ == "__main__":
    input_file = input("Enter the path to the binary image file containing CR2 files: ").strip()

    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        exit(1)

    output_dir = 'Carved'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    find_cr2_files(input_file, output_dir)
