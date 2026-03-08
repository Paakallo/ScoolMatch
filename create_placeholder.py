from PIL import Image, ImageDraw

# Tworzymy obrazek 600x400 z szkolnym kolorem (niebieski)
width, height = 600, 400
background_color = (13, 110, 253)  # Niebieski Bootstrap
image = Image.new('RGB', (width, height), background_color)
draw = ImageDraw.Draw(image)

# Dodajemy tekst
text = "I Liceum Ogólnokształcące\nim. Adama Mickiewicza"
text_color = (255, 255, 255)

# Rysujemy tekst w środku
bbox = draw.textbbox((0, 0), text)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (width - text_width) // 2
y = (height - text_height) // 2

draw.text((x, y), text, fill=text_color)

# Zapisujemy obrazek
image.save('website/static/liceum-mickaiewicza.jpg')
print("Stworzony plik: website/static/liceum-mickaiewicza.jpg")

