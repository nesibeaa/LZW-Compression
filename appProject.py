from tkinter.ttk import Style

from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
import numpy as np
import os



class LZWCoding(tk.Tk):
    path = "tobe.txt"


    def __init__(self,  codelength=12):
        super().__init__()
        style = Style()
        style.configure("main", background="blue")

        self.title("Text Proccesser")

        self.compressed = []
        self.decompressed = []
        self.codelength = codelength

        button = tk.Button(self, text="Open File", fg="red", command=self.write_compressed_file)
        button.pack(side=tk.LEFT)
        slogan = tk.Button(self, text="Save Text", command=self.decompress_file)
        slogan.pack(side=tk.LEFT)

    def compress(self, uncompressed):

        dict_size = 256
        dictionary = {chr(i): i for i in range(dict_size)}

        w = ""
        result = []
        for c in uncompressed:
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])

                dictionary[wc] = dict_size
                dict_size += 1
                w = c

        if w:
            result.append(dictionary[w])
        return result

    def get_compressed_data(self, path):
        self.configure(state="disabled", text="Loading Text")
        with open(path, "rb") as file:
            bit_string = ""
            byte = file.read(1)
            while (len(byte) > 0):
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
        self.configure(state="normal", text="Open Image")
        return bit_string



    def decompress(self, compressed):

        from io import StringIO
        print("from decompressed: compressed data: ", compressed)

        dict_size = 256
        dictionary = {i: chr(i) for i in range(dict_size)}

        result = StringIO()
        w = chr(compressed.pop(0))
        result.write(w)
        for k in compressed:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + w[0]
            else:
                raise ValueError('Bad compressed k: %s' % k)
            result.write(entry)
            dictionary[dict_size] = w + entry[0]
            dict_size += 1

            w = entry
        return result.getvalue()

    def pad_encoded_text(self, encoded_text):
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"

        padded_info = "{0:08b}".format(extra_padding)
        print("padded info: ", padded_info)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        if (len(padded_encoded_text) % 8 != 0):
            print("Encoded text")
            exit(0)

        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i + 8]
            b.append(int(byte, 2))
        return b

    def int_array_to_binary_string(self, int_array):

        bitstr = ""
        bits = self.codelength
        for num in int_array:
            for n in range(bits):
                if num & (1 << (bits - 1 - n)):
                    bitstr += "1"
                else:
                    bitstr += "0"
        return (bitstr)

    def write_compressed_file(self):

        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + ".bin"
        output_path_2 = filename + "_out.txt"

        with open(self.path, 'r+') as file, open(output_path, 'wb') as output, open(output_path_2, 'w+') as file2:
            text = file.read()
            text = text.rstrip()
            int_encoded = self.compress(text)
            file2.write(str(int_encoded))
            encoded_text = self.int_array_to_binary_string(int_encoded)
            padded_encoded_text = self.pad_encoded_text(encoded_text)
            b = self.get_byte_array(padded_encoded_text)
            output.write(bytes(b))

        print("Compressed")
        file2.close()
        return output_path

    def remove_padding(self, padded_encoded_text):
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-1 * extra_padding]
        int_codes = []
        for bits in range(0, len(encoded_text), self.codelength):
            int_codes.append(int(encoded_text[bits:bits + self.codelength], 2))
        return int_codes

    def decompress_file(self, input_path):

        filename, file_extension = os.path.splitext(self.path)
        output_path = filename + "_decompressed" + ".txt"

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""

            byte = file.read(1)
            while (len(byte) > 0):
                byte = ord(byte)
                print("byte :", byte)

                bits = bin(byte)[:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)
            print()
            encoded_text = self.remove_padding(bit_string)
            print("decompressed_file - encoded integers", encoded_text)
            decompressed_text = self.decompress(encoded_text)

            output.write(decompressed_text)

        print("Decompressed")
        return output_path



class LZWapp(tk.Tk):

    def __init__(self, *args: list, **kwargs: dict) -> None:

        super().__init__(*args, **kwargs)



        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.title("Image Proccesser - Default")

        self.FileNameApp = os.getcwd()
        self.path_photo = os.path.join(self.FileNameApp, "<path/thumbs_up.png")
        try:
            self.original_image = Image.open(self.path_photo)

            self.temporary_image = Image.open(self.path_photo)
        except:
            self.path_photo = None
            self.original_image = Image.new('RGB', (256, 256), (0, 0, 0))
            self.temporary_image = Image.new('RGB', (256, 256), (0, 0, 0))
        self.original_reference = ImageTk.PhotoImage(self.original_image)
        self.temporary_reference = ImageTk.PhotoImage(self.temporary_image)

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)

        self.trash = ttk.Frame(self,padding=5)
        self.trash.grid(row=0,column=0)

        self.trash.columnconfigure((0,1,2,3),weight=1)
        self.trash.rowconfigure((0,1,2,3,4),weight=1)

        original_title_label = ttk.Label(self.trash, text="Original Image",anchor="center")
        original_title_label.grid(row=0, column=0, columnspan=2)

        temporary_title_label = ttk.Label(self.trash, text="Temporary Image",anchor="center")
        temporary_title_label.grid(row=0, column=2,columnspan=2)

        self.original_photo_label = ttk.Label(self.trash, image=self.original_reference,anchor="center")
        self.original_photo_label.grid(row=1, column=0,columnspan=2)

        self.temporary_photo_label = ttk.Label(self.trash, image=self.temporary_reference,anchor="center")
        self.temporary_photo_label.grid(row=1, column=2,columnspan=2)

        self.original_info_label = ttk.Label(self.trash)
        self.original_info_label.grid(row=2, column=0,columnspan=2)
        self.__update_photo_info_label("original")

        self.temporary_info_label = ttk.Label(self.trash)
        self.temporary_info_label.grid(row=2, column=2,columnspan=2)
        self.__update_photo_info_label("temporary")

        self.ask_file_button = ttk.Button(self.trash, text="Open Image",command=self.__load_file)
        self.ask_file_button.grid(row=3, column=0, columnspan=1)

        self.reset_image_button = ttk.Button(self.trash, text="Reset Image",command=self.__reset_image)
        self.reset_image_button.grid(row=3, column=1,columnspan=2)

        self.save_file_button = ttk.Button(self.trash, text="Save Image",command=self.__save_file)
        self.save_file_button.grid(row=3, column=3, columnspan=1)

        self.proccess_gray_scale_button = ttk.Button(self.trash, text="Gray Scale",command=lambda: self.__procces_conversion())
        self.proccess_gray_scale_button.grid(row=4, column=0,columnspan=1)

        self.proccess_red_button = ttk.Button(self.trash, text="Red", command=lambda: self.__procces_conversion(0))
        self.proccess_red_button.grid(row=4, column=1,columnspan=1)

        self.proccess_green_button = ttk.Button(self.trash, text="Green", command=lambda: self.__procces_conversion(1))
        self.proccess_green_button.grid(row=4, column=2, columnspan=1)

        self.proccess_blue_button = ttk.Button(self.trash, text="Blue", command=lambda: self.__procces_conversion(2))
        self.proccess_blue_button.grid(row=4, column=3,columnspan=1)

        for child in self.trash.winfo_children():
            child.grid_configure(padx=5, pady=5, sticky='nsew')

    def __reset_image(self) -> None:

        original_image = self.original_image
        self.temporary_image = original_image
        self.temporary_reference = ImageTk.PhotoImage(self.temporary_image)
        self.temporary_photo_label.configure(image=self.temporary_reference)
        self.__update_photo_info_label("temporary")

    def __procces_conversion(self, color_index: int = None) -> None:

        rgb_image = self.original_image

        if color_index is None:
            gray_image = rgb_image.convert('L')
            self.temporary_image = gray_image
        else:
            rgb_image = self._pil_to_np(rgb_image)
            rgb_image[:, :, np.where(np.arange(3) != color_index)] = 0
            rgb_image = self._np_to_pil(rgb_image)
            self.temporary_image = rgb_image

        self.temporary_reference = ImageTk.PhotoImage(self.temporary_image)
        self.temporary_photo_label.configure(image=self.temporary_reference)
        self.__update_photo_info_label("temporary")

    def __load_file(self) -> None:

        self.ask_file_button.configure(state='disabled',text='Loading Image')

        input_file_path = filedialog.askopenfile(initialdir=self.FileNameApp, title='Select an image file', filetypes=[('png files', '*.png')])

        if input_file_path:
            self.path_photo = input_file_path.name

            file_name = os.path.basename(self.path_photo)
            self.title(f"Image Proccesser - {file_name}")

            self.original_image = Image.open(self.path_photo)
            self.original_reference = ImageTk.PhotoImage(self.original_image)
            self.original_photo_label.configure(image=self.original_reference)
            self.__update_photo_info_label("original")

            self.temporary_image = Image.open(self.path_photo)
            self.temporary_reference = ImageTk.PhotoImage(self.temporary_image)
            self.temporary_photo_label.configure(image=self.temporary_reference)
            self.__update_photo_info_label("temporary")

        self.ask_file_button.configure(state='normal',text='Open Image')

    def __save_file(self) -> None:

        self.save_file_button.configure(state='disabled',text='Saving Image')

        output_file_path = filedialog.asksaveasfilename(initialdir=self.FileNameApp, title='Select an image file',filetypes=[('png files','*.png')])

        if output_file_path:

            if not output_file_path.endswith('.png'):output_file_path += '.png'

            output_image = self.temporary_image
            output_image.save(output_file_path)

        self.save_file_button.configure(state='normal',text='Save Image')

    def __update_photo_info_label(self, label_id: str) -> None:

        if label_id == "original":
            photo_info = self._get_image_info(self.original_image)
            self.original_info_label.configure(text=photo_info,anchor="center")
        elif label_id == "temporary":
            photo_info = self._get_image_info(self.temporary_image)
            self.temporary_info_label.configure(text=photo_info,anchor="center")
        else:
            print("Invalid label id.")
            return

    def _get_image_info(self, image: Image) -> str:

        image_array = self._pil_to_np(image)
        image_width = image_array.shape[1]
        image_height = image_array.shape[0]
        image_channels = image_array.ndim

        to_return = f"Size : {image_width}  x {image_height}, Dimensions : {image_channels}"

        return to_return

    def _pil_to_np(self, image: Image) -> np.array:

        return np.array(image)

    def _np_to_pil(self, image_array: np.array) -> Image:

        return Image.fromarray(np.uint8(image_array))






if __name__ == '__main__':

    LZWapp().mainloop()

if __name__ == '__main__':
    LZWCoding().mainloop()
