import os

def list_files(folder, extensions=None):
    file_list = []
    all_files = os.listdir(folder)
    for name in all_files:
        if extensions is not None:
            for ext in extensions:
                if name.endswith(ext):
                    file_list.append(f'{folder}{os.sep}{name}')
        else:
            file_list.append(f'{folder}{os.sep}{name}')
    return file_list

def main():
	images = list_files('.', ['png'])
	for counter, image in enumerate(images):
		if 'field_parts' in image:
			print(f'{image.split(os.sep)[-1]} -> {counter +1:02}.png')
			os.rename(image, f'{counter +1:02}.png')

if __name__ == '__main__':
	main()