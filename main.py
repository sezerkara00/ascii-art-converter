import sys
import os
from PIL import Image
import imageio
import tkinter as tk
from tkinter import ttk
from tkinter import Text, Frame
from tkinter.filedialog import askopenfilename

ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

def resize_image(image, new_width=100):
    width, height = image.size
    # Minimum genişlik kontrolü
    if width < 400:
        ratio = height / width
        new_width = 400
        new_height = int(new_width * ratio)
        return image.resize((new_width, new_height))
    
    # Maksimum genişlik 800 piksel
    if width > 800:
        ratio = height / width
        new_width = 800
        new_height = int(new_width * ratio)
        return image.resize((new_width, new_height))
    
    return image

def grayify(image):
    return image.convert("L")

def adjust_color(r, g, b):
    # Renkleri daha belirgin yapmak için doygunluğu artır
    saturation_factor = 2.0
    # Minimum parlaklık değeri (renklerin çok açık olmasını önler)
    min_brightness = 0.5
    
    # Renk değerlerini 0-1 aralığına normalize et
    r, g, b = r/255.0, g/255.0, b/255.0
    
    # Parlaklığı hesapla
    brightness = (r + g + b) / 3
    
    # Renkleri daha parlak yap
    if brightness > min_brightness:
        r = r * saturation_factor * (1 - min_brightness) + r * min_brightness
        g = g * saturation_factor * (1 - min_brightness) + g * min_brightness
        b = b * saturation_factor * (1 - min_brightness) + b * min_brightness
    
    # Değerleri 0-255 aralığına geri dönüştür ve sınırla
    r = max(0, min(255, int(r * 255)))
    g = max(0, min(255, int(g * 255)))
    b = max(0, min(255, int(b * 255)))
    
    return r, g, b

def pixels_to_ascii(image):
    pixels = image.getdata()
    characters = "".join([ASCII_CHARS[pixel//25] for pixel in pixels])
    return characters

def image_to_ascii_string(image_path, new_width=100):
    try:
        image = Image.open(image_path)
        print(f"Resim açıldı: {image_path}")  # Debug
    except Exception as e:
        print(f"Uygulama açılırken hata oluştu: {e}")
        return []
    
    # Resmi yeniden boyutlandır
    image = resize_image(image)
    
    # ASCII karakterleri için boyut hesaplama
    ascii_width = image.width // 10  # Her 10 piksel için 1 ASCII karakter
    ascii_height = image.height // 20  # Her 20 piksel için 1 ASCII karakter
    image = image.resize((ascii_width, ascii_height))
    image_gray = grayify(image)

    ascii_art = []
    pixels = list(image_gray.getdata())
    pixels_color = list(image.getdata())

    for y in range(image.height):
        line = []
        for x in range(image.width):
            idx = y * image.width + x
            pixel = pixels[idx]
            ascii_char = ASCII_CHARS[pixel // 25]
            color = pixels_color[idx][:3]  # RGB
            # Renkleri ayarla
            adjusted_color = adjust_color(color[0], color[1], color[2])
            color_hex = "#{:02x}{:02x}{:02x}".format(*adjusted_color)
            line.append((ascii_char, color_hex))
        ascii_art.append(line)

    return ascii_art

def display_ascii(colored_ascii_art):
    ascii_text.config(state='normal')
    ascii_text.delete(1.0, tk.END)
    for line in colored_ascii_art:
        for char, color in line:
            if color not in color_tags:
                tag_name = f"color_{color}"
                ascii_text.tag_config(tag_name, foreground=color)
                color_tags[color] = tag_name
            else:
                tag_name = color_tags[color]
            ascii_text.insert(tk.END, char, tag_name)
        ascii_text.insert(tk.END, "\n")
    ascii_text.config(state='disabled')

# Animasyon için global değişken
current_animation = None

def update_frame(frame_index, frames):
    global current_animation
    if frame_index < len(frames):
        display_ascii(frames[frame_index])
        # Bir sonraki kareyi 100ms sonra göster
        current_animation = root.after(100, update_frame, (frame_index + 1) % len(frames), frames)

def stop_animation():
    global current_animation
    if current_animation is not None:
        root.after_cancel(current_animation)
        current_animation = None

def process_file(file_path):
    # Mevcut animasyonu durdur
    stop_animation()
    
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
        colored_ascii_art = image_to_ascii_string(file_path)
        display_ascii(colored_ascii_art)
    elif file_ext == '.gif':
        colored_ascii_art = gif_to_ascii(file_path)
    elif file_ext in ['.mp4', '.avi', '.mov']:
        video_to_ascii(file_path)
    else:
        print("Desteklenmeyen dosya formatı.")

color_tags = {}

def gif_to_ascii(gif_path, new_width=100):
    try:
        gif = imageio.mimread(gif_path)
        print(f"GIF yüklendi: {gif_path}")  # Debug
    except Exception as e:
        print(f"GIF okunurken hata oluştu: {e}")
        return []

    ascii_art_all_frames = []
    for frame in gif:
        image = Image.fromarray(frame)
        # Resmi yeniden boyutlandır
        image = resize_image(image)
        
        # ASCII karakterleri için boyut hesaplama
        ascii_width = image.width // 10
        ascii_height = image.height // 20
        image = image.resize((ascii_width, ascii_height))
        image_gray = grayify(image)

        ascii_art = []
        pixels = list(image_gray.getdata())
        pixels_color = list(image.getdata())

        for y in range(image.height):
            line = []
            for x in range(image.width):
                idx = y * image.width + x
                pixel = pixels[idx]
                ascii_char = ASCII_CHARS[pixel // 25]
                color = pixels_color[idx][:3]
                adjusted_color = adjust_color(color[0], color[1], color[2])
                color_hex = "#{:02x}{:02x}{:02x}".format(*adjusted_color)
                line.append((ascii_char, color_hex))
            ascii_art.append(line)
        ascii_art_all_frames.append(ascii_art)
    
    # Animasyonu başlat
    if ascii_art_all_frames:
        update_frame(0, ascii_art_all_frames)
    return None

def video_to_ascii(video_path, new_width=100):
    try:
        reader = imageio.get_reader(video_path)
        print(f"Video yüklendi: {video_path}")  # Debug
        
        # Video karelerini saklamak için liste
        ascii_art_all_frames = []
        
        # Her kareyi işle
        for frame in reader:
            image = Image.fromarray(frame)
            ascii_art = image_to_ascii_string_from_image(image, new_width)
            ascii_art_all_frames.append(ascii_art)
        
        # Animasyonu başlat
        if ascii_art_all_frames:
            update_frame(0, ascii_art_all_frames)
        
    except Exception as e:
        print(f"Video okunurken hata oluştu: {e}")
        return

def image_to_ascii_string_from_image(image, new_width=100):
    image = resize_image(image, new_width)
    image_gray = grayify(image)

    ascii_art = []
    pixels = list(image_gray.getdata())
    img_width, img_height = image_gray.size
    pixels_color = list(image.resize((new_width, img_height)).getdata())

    for y in range(img_height):
        line = []
        for x in range(new_width):
            idx = y * new_width + x
            pixel = pixels[idx]
            ascii_char = ASCII_CHARS[pixel // 25]
            color = pixels_color[idx][:3]  # RGB
            color_hex = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
            line.append((ascii_char, color_hex))
        ascii_art.append(line)

    return ascii_art

class ASCIIArtStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Art Studio Pro")
        self.root.configure(bg='#2C3E50')  # Koyu mavi-gri arka plan
        
        # Ana pencere boyutu
        self.root.geometry("1200x800")
        self.root.resizable(False, False)
        
        # Ana başlık
        title_label = tk.Label(root, text="ASCII Art Studio Pro", 
                              font=('Arial', 20, 'bold'), 
                              bg='#2C3E50', fg='white')
        title_label.pack(pady=10)
        
        # Ana container
        self.main_container = Frame(root, bg='#2C3E50')
        self.main_container.pack(fill='both', expand=True, padx=20)
        
        # Sol panel (ASCII görüntü alanı)
        self.left_panel = Frame(self.main_container, bg='#34495E')
        self.left_panel.pack(side='left', fill='both', expand=True, padx=10)
        
        # ASCII Sanat Galerisi başlığı
        gallery_label = tk.Label(self.left_panel, text="ASCII Sanat Galerisi",
                               font=('Arial', 12), bg='#34495E', fg='white')
        gallery_label.pack(pady=5)
        
        # ASCII görüntü alanı
        self.ascii_text = Text(self.left_panel, wrap=tk.NONE, 
                             width=100, height=40,
                             font=("Courier", 8), 
                             bg='black', fg='white')
        self.ascii_text.pack(padx=10, pady=5)
        
        # Sağ panel (Ayarlar)
        self.right_panel = Frame(self.main_container, bg='#34495E', width=300)
        self.right_panel.pack(side='right', fill='y', padx=10)
        
        # Görsel Seçimi bölümü
        self.setup_image_selection()
        
        # Sanat Ayarları bölümü
        self.setup_art_settings()
        
        # Alt butonlar
        self.setup_bottom_buttons()
        
        # Global değişkenler
        self.color_tags = {}
        self.current_animation = None
        self.ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']
        
    def setup_image_selection(self):
        # Görsel Seçimi başlığı
        selection_frame = Frame(self.right_panel, bg='#34495E')
        selection_frame.pack(fill='x', pady=10)
        
        selection_label = tk.Label(selection_frame, text="Görsel Seçimi",
                                 font=('Arial', 12), bg='#34495E', fg='white')
        selection_label.pack()
        
        # Dosya yolu gösterimi
        self.file_path_var = tk.StringVar()
        file_path_entry = tk.Entry(selection_frame, textvariable=self.file_path_var,
                                 width=30)
        file_path_entry.pack(pady=5)
        
        # Görsel Seç butonu
        select_button = tk.Button(selection_frame, text="Görsel Seç",
                                command=self.select_file_gui,
                                bg='#3498DB', fg='white',
                                activebackground='#2980B9')
        select_button.pack(pady=5)
        
    def setup_art_settings(self):
        # Sanat Ayarları başlığı
        settings_frame = Frame(self.right_panel, bg='#34495E')
        settings_frame.pack(fill='x', pady=10)
        
        settings_label = tk.Label(settings_frame, text="Sanat Ayarları",
                                font=('Arial', 12), bg='#34495E', fg='white')
        settings_label.pack()
        
        # Genişlik ayarı
        width_frame = Frame(settings_frame, bg='#34495E')
        width_frame.pack(fill='x', pady=5)
        
        width_label = tk.Label(width_frame, text="Genişlik:",
                             bg='#34495E', fg='white')
        width_label.pack(side='left', padx=5)
        
        self.width_var = tk.StringVar(value="300")
        width_entry = tk.Entry(width_frame, textvariable=self.width_var,
                             width=10)
        width_entry.pack(side='left')
        
        # ASCII Set seçimi
        set_frame = Frame(settings_frame, bg='#34495E')
        set_frame.pack(fill='x', pady=5)
        
        set_label = tk.Label(set_frame, text="ASCII Set:",
                           bg='#34495E', fg='white')
        set_label.pack(side='left', padx=5)
        
        self.ascii_set_var = tk.StringVar(value="Basit")
        set_combo = ttk.Combobox(set_frame, textvariable=self.ascii_set_var,
                                values=["Basit", "Detaylı"], width=15)
        set_combo.pack(side='left')
        
        # Renk ayarları
        color_button = tk.Button(settings_frame, text="Metin Rengi",
                               bg='#3498DB', fg='white')
        color_button.pack(pady=5)
        
        bg_color_button = tk.Button(settings_frame, text="Arkaplan Rengi",
                                  bg='#3498DB', fg='white')
        bg_color_button.pack(pady=5)
        
        # Ek ayarlar
        self.reverse_colors_var = tk.BooleanVar()
        reverse_check = tk.Checkbutton(settings_frame, text="Renkleri Ters Çevir",
                                     variable=self.reverse_colors_var,
                                     bg='#34495E', fg='white',
                                     selectcolor='#2C3E50')
        reverse_check.pack(pady=2)
        
        self.bold_text_var = tk.BooleanVar()
        bold_check = tk.Checkbutton(settings_frame, text="Kalın Yazı",
                                  variable=self.bold_text_var,
                                  bg='#34495E', fg='white',
                                  selectcolor='#2C3E50')
        bold_check.pack(pady=2)
        
        # Dönüştür butonu
        convert_button = tk.Button(settings_frame, text="Dönüştür",
                                 command=self.convert_current_image,
                                 bg='#3498DB', fg='white',
                                 activebackground='#2980B9',
                                 width=20)
        convert_button.pack(pady=10)
        
        # Yazı boyutu ayarı
        size_label = tk.Label(settings_frame, text="Yazı Boyutu",
                            bg='#34495E', fg='white')
        size_label.pack(pady=5)
        
        self.size_scale = ttk.Scale(settings_frame, from_=6, to=16,
                                  orient='horizontal')
        self.size_scale.set(8)
        self.size_scale.pack(fill='x', padx=10)
        
    def setup_bottom_buttons(self):
        button_frame = Frame(self.left_panel, bg='#34495E')
        button_frame.pack(fill='x', pady=10)
        
        save_button = tk.Button(button_frame, text="Kaydet",
                              bg='#3498DB', fg='white')
        save_button.pack(side='left', padx=5)
        
        clear_button = tk.Button(button_frame, text="Temizle",
                               bg='#3498DB', fg='white')
        clear_button.pack(side='left', padx=5)
        
        copy_button = tk.Button(button_frame, text="Kopyala",
                              bg='#3498DB', fg='white')
        copy_button.pack(side='left', padx=5)
        
    def select_file_gui(self):
        file_path = askopenfilename(
            title="Bir dosya seçin",
            filetypes=[
                ("Resim Dosyaları", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("Video Dosyaları", "*.mp4 *.avi *.mov")
            ]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.process_file(file_path)
            
    def process_file(self, file_path):
        # Mevcut animasyonu durdur
        self.stop_animation()
        
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            colored_ascii_art = self.image_to_ascii_string(file_path)
            self.display_ascii(colored_ascii_art)
        elif file_ext == '.gif':
            colored_ascii_art = self.gif_to_ascii(file_path)
        elif file_ext in ['.mp4', '.avi', '.mov']:
            self.video_to_ascii(file_path)
        else:
            print("Desteklenmeyen dosya formatı.")

    def display_ascii(self, colored_ascii_art):
        self.ascii_text.config(state='normal')
        self.ascii_text.delete(1.0, tk.END)
        for line in colored_ascii_art:
            for char, color in line:
                if color not in self.color_tags:
                    tag_name = f"color_{color}"
                    self.ascii_text.tag_config(tag_name, foreground=color)
                    self.color_tags[color] = tag_name
                else:
                    tag_name = self.color_tags[color]
                self.ascii_text.insert(tk.END, char, tag_name)
            self.ascii_text.insert(tk.END, "\n")
        self.ascii_text.config(state='disabled')

    def stop_animation(self):
        if self.current_animation is not None:
            self.root.after_cancel(self.current_animation)
            self.current_animation = None

    def update_frame(self, frame_index, frames):
        if frame_index < len(frames):
            self.display_ascii(frames[frame_index])
            # Bir sonraki kareyi 100ms sonra göster
            self.current_animation = self.root.after(100, self.update_frame, 
                (frame_index + 1) % len(frames), frames)

    def image_to_ascii_string(self, image_path):
        try:
            image = Image.open(image_path)
            print(f"Resim açıldı: {image_path}")
        except Exception as e:
            print(f"Uygulama açılırken hata oluştu: {e}")
            return []
        
        # Resmi yeniden boyutlandır
        image = self.resize_image(image)
        
        # ASCII karakterleri için boyut hesaplama
        ascii_width = image.width // 10
        ascii_height = image.height // 20
        image = image.resize((ascii_width, ascii_height))
        image_gray = self.grayify(image)

        ascii_art = []
        pixels = list(image_gray.getdata())
        pixels_color = list(image.getdata())

        for y in range(image.height):
            line = []
            for x in range(image.width):
                idx = y * image.width + x
                pixel = pixels[idx]
                ascii_char = self.ASCII_CHARS[pixel // 25]
                color = pixels_color[idx][:3]
                adjusted_color = self.adjust_color(color[0], color[1], color[2])
                color_hex = "#{:02x}{:02x}{:02x}".format(*adjusted_color)
                line.append((ascii_char, color_hex))
            ascii_art.append(line)

        return ascii_art

    def resize_image(self, image, new_width=100):
        width, height = image.size
        # Minimum genişlik kontrolü
        if width < 400:
            ratio = height / width
            new_width = 400
            new_height = int(new_width * ratio)
            return image.resize((new_width, new_height))
        
        # Maksimum genişlik 800 piksel
        if width > 800:
            ratio = height / width
            new_width = 800
            new_height = int(new_width * ratio)
            return image.resize((new_width, new_height))
        
        return image

    def grayify(self, image):
        return image.convert("L")

    def adjust_color(self, r, g, b):
        # Renkleri daha belirgin yapmak için doygunluğu artır
        saturation_factor = 2.0
        # Minimum parlaklık değeri (renklerin çok açık olmasını önler)
        min_brightness = 0.5
        
        # Renk değerlerini 0-1 aralığına normalize et
        r, g, b = r/255.0, g/255.0, b/255.0
        
        # Parlaklığı hesapla
        brightness = (r + g + b) / 3
        
        # Renkleri daha parlak yap
        if brightness > min_brightness:
            r = r * saturation_factor * (1 - min_brightness) + r * min_brightness
            g = g * saturation_factor * (1 - min_brightness) + g * min_brightness
            b = b * saturation_factor * (1 - min_brightness) + b * min_brightness
        
        # Değerleri 0-255 aralığına geri dönüştür ve sınırla
        r = max(0, min(255, int(r * 255)))
        g = max(0, min(255, int(g * 255)))
        b = max(0, min(255, int(b * 255)))
        
        return r, g, b

    def gif_to_ascii(self, gif_path, new_width=100):
        try:
            gif = imageio.mimread(gif_path)
            print(f"GIF yüklendi: {gif_path}")  # Debug
        except Exception as e:
            print(f"GIF okunurken hata oluştu: {e}")
            return []

        ascii_art_all_frames = []
        for frame in gif:
            image = Image.fromarray(frame)
            # Resmi yeniden boyutlandır
            image = self.resize_image(image)
            
            # ASCII karakterleri için boyut hesaplama
            ascii_width = image.width // 10
            ascii_height = image.height // 20
            image = image.resize((ascii_width, ascii_height))
            image_gray = self.grayify(image)

            ascii_art = []
            pixels = list(image_gray.getdata())
            pixels_color = list(image.getdata())

            for y in range(image.height):
                line = []
                for x in range(image.width):
                    idx = y * image.width + x
                    pixel = pixels[idx]
                    ascii_char = self.ASCII_CHARS[pixel // 25]
                    color = pixels_color[idx][:3]
                    adjusted_color = self.adjust_color(color[0], color[1], color[2])
                    color_hex = "#{:02x}{:02x}{:02x}".format(*adjusted_color)
                    line.append((ascii_char, color_hex))
                ascii_art.append(line)
            ascii_art_all_frames.append(ascii_art)
        
        # Animasyonu başlat
        if ascii_art_all_frames:
            self.update_frame(0, ascii_art_all_frames)
        return None

    def video_to_ascii(self, video_path, new_width=100):
        try:
            reader = imageio.get_reader(video_path)
            print(f"Video yüklendi: {video_path}")  # Debug
            
            # Video karelerini saklamak için liste
            ascii_art_all_frames = []
            
            # Her kareyi işle
            for frame in reader:
                image = Image.fromarray(frame)
                ascii_art = self.image_to_ascii_string_from_image(image, new_width)
                ascii_art_all_frames.append(ascii_art)
            
            # Animasyonu başlat
            if ascii_art_all_frames:
                self.update_frame(0, ascii_art_all_frames)
            
        except Exception as e:
            print(f"Video okunurken hata oluştu: {e}")
            return

    def image_to_ascii_string_from_image(self, image, new_width=100):
        image = self.resize_image(image, new_width)
        image_gray = self.grayify(image)

        ascii_art = []
        pixels = list(image_gray.getdata())
        img_width, img_height = image_gray.size
        pixels_color = list(image.resize((new_width, img_height)).getdata())

        for y in range(img_height):
            line = []
            for x in range(new_width):
                idx = y * new_width + x
                pixel = pixels[idx]
                ascii_char = self.ASCII_CHARS[pixel // 25]
                color = pixels_color[idx][:3]  # RGB
                adjusted_color = self.adjust_color(color[0], color[1], color[2])
                color_hex = "#{:02x}{:02x}{:02x}".format(*adjusted_color)
                line.append((ascii_char, color_hex))
            ascii_art.append(line)

        return ascii_art

    def convert_current_image(self):
        # Mevcut dosya yolunu al
        current_file = self.file_path_var.get()
        if not current_file:
            return
        
        # Ayarları al
        try:
            width = int(self.width_var.get())
        except ValueError:
            width = 300  # Varsayılan değer
        
        # Font boyutunu al
        font_size = int(self.size_scale.get())
        
        # ASCII set tipini al
        ascii_set = self.ascii_set_var.get()
        if ascii_set == "Detaylı":
            self.ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']
        else:
            self.ASCII_CHARS = ['@', '#', '$', '*', '!', '=', '-', '.']
        
        # Renk tersine çevirme kontrolü
        if self.reverse_colors_var.get():
            self.ASCII_CHARS = self.ASCII_CHARS[::-1]
        
        # Font kalınlığı kontrolü
        font_weight = "bold" if self.bold_text_var.get() else "normal"
        
        # Text widget font ayarlarını güncelle
        self.ascii_text.configure(font=("Courier", font_size, font_weight))
        
        # Dosyayı yeniden işle
        self.process_file(current_file)

if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIIArtStudio(root)
    root.mainloop()
