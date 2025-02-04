import sys
import os
from PIL import Image
import imageio
import tkinter as tk
from tkinter import Text
from tkinter.filedialog import askopenfilename

ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

def resize_image(image, new_width=100):
    width, height = image.size
    # Maksimum genişlik 800 piksel
    if width > 800:
        ratio = height / width
        new_width = 800
        new_height = int(new_width * ratio)
    else:
        new_width = width
        new_height = height
    resized_image = image.resize((new_width, new_height))
    return resized_image

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
    except Exception as e:
        print(f"Video okunurken hata oluştu: {e}")
        return

    for frame in reader:
        image = Image.fromarray(frame)
        ascii_art = image_to_ascii_string_from_image(image, new_width)
        display_ascii(ascii_art)
    print("Video işlendi.")

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

def select_file_gui():
    file_path = askopenfilename(title="Bir dosya seçin", 
                                filetypes=[("Resim Dosyaları", "*.jpg *.jpeg *.png *.bmp *.gif"),
                                           ("Video Dosyaları", "*.mp4 *.avi *.mov")])
    print(f"Seçilen dosya: {file_path}")  # Debug
    if file_path:
        process_file(file_path)
    else:
        print("Hiçbir dosya seçilmedi.")

if __name__ == "__main__":
    print("Program başlatılıyor...")  # Debug
    
    # Tkinter Ana Penceresini Oluşturma
    root = tk.Tk()
    root.title("ASCII Görüntüleyici")
    
    # Sabit pencere boyutu
    window_width = 1000
    window_height = 800
    root.geometry(f"{window_width}x{window_height}")
    root.resizable(False, False)  # Pencere boyutunu sabitleme
    
    # Frame oluştur (ortalamak için)
    frame = tk.Frame(root)
    frame.pack(expand=True)
    
    # Frame'in arka planını siyah yap
    frame.configure(bg='black')
    root.configure(bg='black')
    
    # Dosya Seçme Butonu
    select_button = tk.Button(frame, text="Dosya Seç", command=select_file_gui,
                             bg='black', fg='white', font=('Arial', 10),
                             activebackground='#333333', activeforeground='white')
    select_button.pack(pady=10)
    
    # ASCII Görüntüyü Gösteren Metin Alanı
    ascii_text = Text(frame, wrap=tk.NONE, width=100, height=50,
                     font=("Courier", 8), bg='black', fg='white')
    ascii_text.pack(padx=10, pady=10)
    ascii_text.config(state='disabled')
    
    root.mainloop()
