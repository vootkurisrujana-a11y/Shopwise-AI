import sqlite3
import json
from werkzeug.security import generate_password_hash
from database import init_db_standalone, DATABASE

def seed_db():
    init_db_standalone()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Reset product table to allow reloading expanded catalog
    cursor.execute("DELETE FROM products")
    print("Clearing database tables for re-seeding...")

    # Expanded Flipkart-style product list (30+ items)
    products = [
        # --- LAPTOPS ---
        {
            "name": "Asus Vivobook 15",
            "category": "laptop",
            "price": 42990.0,
            "rating": 4.2,
            "description": "Intel Core i3 12th Gen, slim design, perfect for coding students and casual multitasking.",
            "specs": {
                "RAM": "8GB DDR4",
                "Storage": "512GB NVMe SSD",
                "CPU": "Intel Core i3-1215U",
                "Battery": "6 hours",
                "Weight": "1.7 kg",
                "Display": "15.6 inch Full HD"
            },
            "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&q=80"
        },
        {
            "name": "Lenovo IdeaPad Slim 3",
            "category": "laptop",
            "price": 34990.0,
            "rating": 4.0,
            "description": "Intel Core i3 11th Gen, thin bezel display, highly affordable laptop for basic coding, HTML, and browser multitasking.",
            "specs": {
                "RAM": "8GB DDR4",
                "Storage": "512GB SSD",
                "CPU": "Intel Core i3-1115G4",
                "Battery": "5 hours",
                "Weight": "1.65 kg",
                "Display": "15.6 inch FHD"
            },
            "image_url": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=500&q=80"
        },
        {
            "name": "HP Pavilion 14",
            "category": "laptop",
            "price": 54990.0,
            "rating": 4.4,
            "description": "AMD Ryzen 5, metal chassis, backlit keyboard. Superb balance of speed and portability for coding and office use.",
            "specs": {
                "RAM": "16GB DDR4",
                "Storage": "512GB NVMe SSD",
                "CPU": "AMD Ryzen 5 5625U",
                "Battery": "8 hours",
                "Weight": "1.41 kg",
                "Display": "14 inch IPS Full HD"
            },
            "image_url": "https://images.unsplash.com/photo-1496181130204-755241544e35?w=500&q=80"
        },
        {
            "name": "Dell Inspiron 15 3520",
            "category": "laptop",
            "price": 47990.0,
            "rating": 4.1,
            "description": "Intel Core i5 12th Gen, clean professional design, numerical keyboard, smooth 120Hz scrolling refresh rate.",
            "specs": {
                "RAM": "8GB DDR4",
                "Storage": "512GB NVMe SSD",
                "CPU": "Intel Core i5-1235U",
                "Battery": "6 hours",
                "Weight": "1.65 kg",
                "Display": "15.6 inch 120Hz FHD"
            },
            "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&q=80"
        },
        {
            "name": "Lenovo Legion 5",
            "category": "laptop",
            "price": 79990.0,
            "rating": 4.6,
            "description": "Powerful gaming laptop with Nvidia RTX 3050, high refresh rate screen, robust dual-fan cooling system for gaming and heavy programming compiles.",
            "specs": {
                "RAM": "16GB DDR4",
                "Storage": "1TB NVMe SSD",
                "CPU": "AMD Ryzen 7 5800H",
                "Battery": "5 hours",
                "Weight": "2.4 kg",
                "Display": "15.6 inch IPS 120Hz"
            },
            "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&q=80"
        },
        {
            "name": "Acer Nitro V 15",
            "category": "laptop",
            "price": 68990.0,
            "rating": 4.3,
            "description": "Nvidia RTX 4050 graphics, Intel Core i5 13th Gen, backlit keyboard, fast cooling. The value gaming laptop benchmark.",
            "specs": {
                "RAM": "16GB DDR5",
                "Storage": "512GB SSD",
                "CPU": "Intel Core i5-13420H",
                "Battery": "4 hours",
                "Weight": "2.1 kg",
                "Display": "15.6 inch 144Hz FHD"
            },
            "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=500&q=80"
        },
        {
            "name": "Apple MacBook Air M1",
            "category": "laptop",
            "price": 69900.0,
            "rating": 4.8,
            "description": "Apple M1 chip, fanless silent operation, phenomenal battery life, and crystal-clear Retina display. Best choice for developer mobility.",
            "specs": {
                "RAM": "8GB Unified",
                "Storage": "256GB SSD",
                "CPU": "Apple M1 Octa-Core",
                "Battery": "15 hours",
                "Weight": "1.29 kg",
                "Display": "13.3 inch Retina IPS"
            },
            "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&q=80"
        },
        {
            "name": "Apple MacBook Pro M3",
            "category": "laptop",
            "price": 159900.0,
            "rating": 4.9,
            "description": "Apple M3 Chip, Liquid Retina XDR display, active thermal cooling, support for dual external displays. Professional compilation powerhouse.",
            "specs": {
                "RAM": "16GB Unified",
                "Storage": "512GB SSD",
                "CPU": "Apple M3 Deca-Core",
                "Battery": "22 hours",
                "Weight": "1.55 kg",
                "Display": "14.2 inch Liquid Retina"
            },
            "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&q=80"
        },
        
        # --- PHONES ---
        {
            "name": "Redmi Note 12 Pro",
            "category": "phone",
            "price": 21999.0,
            "rating": 4.1,
            "description": "5G-ready, 50MP Sony IMX766 sensor with OIS, 120Hz AMOLED display. Excellent everyday photography on a budget.",
            "specs": {
                "RAM": "6GB",
                "Storage": "128GB",
                "Camera": "50MP Triple",
                "Battery": "5000mAh",
                "Screen": "6.67 inch AMOLED",
                "Processor": "Dimensity 1080"
            },
            "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500&q=80"
        },
        {
            "name": "OnePlus Nord CE 3 Lite",
            "category": "phone",
            "price": 19999.0,
            "rating": 4.2,
            "description": "108MP main camera with lossless zoom, Snapdragon chip, and super-fast 67W charging. Great everyday performance under 20k.",
            "specs": {
                "RAM": "8GB",
                "Storage": "128GB",
                "Camera": "108MP Triple",
                "Battery": "5000mAh",
                "Screen": "6.72 inch 120Hz",
                "Processor": "Snapdragon 695"
            },
            "image_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=500&q=80"
        },
        {
            "name": "Samsung Galaxy A34",
            "category": "phone",
            "price": 27499.0,
            "rating": 4.3,
            "description": "IP67 dust/water resistance, smooth 120Hz display, clean software with 4 years of OS updates. Outstanding durable value.",
            "specs": {
                "RAM": "8GB",
                "Storage": "128GB",
                "Camera": "48MP Triple",
                "Battery": "5000mAh",
                "Screen": "6.6 inch Super AMOLED",
                "Processor": "Dimensity 1080"
            },
            "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&q=80"
        },
        {
            "name": "Google Pixel 7a",
            "category": "phone",
            "price": 39990.0,
            "rating": 4.6,
            "description": "Google Tensor G2 chip, legendary Pixel HDR camera processing, real-time translations, and wireless charging capabilities.",
            "specs": {
                "RAM": "8GB",
                "Storage": "128GB",
                "Camera": "64MP Dual",
                "Battery": "4385mAh",
                "Screen": "6.1 inch OLED 90Hz",
                "Processor": "Google Tensor G2"
            },
            "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500&q=80"
        },
        {
            "name": "Realme Narzo N55",
            "category": "phone",
            "price": 10999.0,
            "rating": 3.9,
            "description": "Extremely affordable phone featuring 33W super fast charging and a sleek borderless screen layout.",
            "specs": {
                "RAM": "4GB",
                "Storage": "64GB",
                "Camera": "64MP Dual",
                "Battery": "5000mAh",
                "Screen": "6.72 inch 90Hz FHD+",
                "Processor": "MediaTek Helio G88"
            },
            "image_url": "https://images.unsplash.com/photo-1565630916779-e303be97b6f5?w=500&q=80"
        },
        {
            "name": "Samsung Galaxy M14",
            "category": "phone",
            "price": 12490.0,
            "rating": 4.0,
            "description": "Massive 6000mAh battery power bank phone, 5G enabled, triple lens configuration, highly popular entry-level value.",
            "specs": {
                "RAM": "6GB",
                "Storage": "128GB",
                "Camera": "50MP Triple",
                "Battery": "6000mAh",
                "Screen": "6.6 inch PLS LCD",
                "Processor": "Exynos 1330"
            },
            "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500&q=80"
        },
        {
            "name": "Poco X5 Pro 5G",
            "category": "phone",
            "price": 18990.0,
            "rating": 4.2,
            "description": "108MP camera, Snapdragon processor, 120Hz Adaptive Xfinity display. Incredible feature-density under 20k.",
            "specs": {
                "RAM": "6GB",
                "Storage": "128GB",
                "Camera": "108MP Triple",
                "Battery": "5000mAh",
                "Screen": "6.67 inch AMOLED",
                "Processor": "Snapdragon 778G"
            },
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&q=80"
        },
        {
            "name": "Apple iPhone 14",
            "category": "phone",
            "price": 62990.0,
            "rating": 4.7,
            "description": "A15 Bionic chip, cinematic video mode stabilization, dual-camera system, crash detection safety systems.",
            "specs": {
                "RAM": "6GB",
                "Storage": "128GB",
                "Camera": "12MP Dual",
                "Battery": "3279mAh",
                "Screen": "6.1 inch Super Retina",
                "Processor": "A15 Bionic"
            },
            "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=500&q=80"
        },
        
        # --- HEADPHONES ---
        {
            "name": "boAt Rockerz 450",
            "category": "headphone",
            "price": 1499.0,
            "rating": 3.8,
            "description": "Wireless on-ear headphones with deep signature boAt bass and up to 15 hours of battery life.",
            "specs": {
                "Type": "On-Ear",
                "Battery": "15 hours",
                "Noise_Cancelling": "Passive Isolation",
                "Driver": "40mm dynamic",
                "Connectivity": "Bluetooth 5.0"
            },
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80"
        },
        {
            "name": "OnePlus Bullets Wireless Z2",
            "category": "headphone",
            "price": 1799.0,
            "rating": 4.2,
            "description": "Neckband wireless earphone, fast charging (10 mins for 20 hrs), bass-boosting drivers, water and sweat resistant.",
            "specs": {
                "Type": "In-Ear Neckband",
                "Battery": "30 hours",
                "Noise_Cancelling": "AI Call Noise Cancellation",
                "Driver": "12.4mm Bass",
                "Connectivity": "Bluetooth 5.0"
            },
            "image_url": "https://images.unsplash.com/photo-1613040809024-b4ef7ba99bc3?w=500&q=80"
        },
        {
            "name": "Sennheiser HD 450SE",
            "category": "headphone",
            "price": 8990.0,
            "rating": 4.3,
            "description": "Audiophile-grade studio acoustics with active noise cancellation, dedicated Alexa voice support button.",
            "specs": {
                "Type": "Over-Ear",
                "Battery": "30 hours",
                "Noise_Cancelling": "Active (ANC)",
                "Driver": "32mm",
                "Connectivity": "Bluetooth 5.0, AAC, aptX"
            },
            "image_url": "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=500&q=80"
        },
        {
            "name": "Sony WH-XB910N",
            "category": "headphone",
            "price": 12990.0,
            "rating": 4.5,
            "description": "Extra Bass wireless noise-canceling headphones. Multipoint connection and advanced vocal control.",
            "specs": {
                "Type": "Over-Ear",
                "Battery": "30 hours",
                "Noise_Cancelling": "Active (ANC)",
                "Driver": "40mm Dome",
                "Connectivity": "Bluetooth 5.2"
            },
            "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500&q=80"
        },
        {
            "name": "JBL Tune 760NC",
            "category": "headphone",
            "price": 5999.0,
            "rating": 4.1,
            "description": "Active Noise Cancelling over-ear headphone, light weight compact folding, signature JBL pure bass sound.",
            "specs": {
                "Type": "Over-Ear",
                "Battery": "35 hours (ANC ON)",
                "Noise_Cancelling": "Active (ANC)",
                "Driver": "40mm",
                "Connectivity": "Bluetooth 5.0"
            },
            "image_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500&q=80"
        },
        {
            "name": "Apple AirPods Pro 2",
            "category": "headphone",
            "price": 22900.0,
            "rating": 4.8,
            "description": "Advanced H2 chip, adaptive audio, spatial acoustics, type C charging, extreme active noise cancellation.",
            "specs": {
                "Type": "In-Ear Buds",
                "Battery": "6 hours (30 hrs with case)",
                "Noise_Cancelling": "2x Active ANC",
                "Driver": "Custom high-excursion",
                "Connectivity": "Bluetooth 5.3"
            },
            "image_url": "https://images.unsplash.com/photo-1588449668338-d1516882247e?w=500&q=80"
        },
        
        # --- CAMERAS ---
        {
            "name": "Canon EOS M50 Mark II",
            "category": "camera",
            "price": 57990.0,
            "rating": 4.5,
            "description": "Mirrorless vlog camera with eye detection autofocus, vertical video mode, and 24.1 megapixel APS-C sensor.",
            "specs": {
                "Sensor": "APS-C CMOS",
                "Resolution": "24.1 Megapixels",
                "Video": "4K 24p / Full HD 60p",
                "Weight": "387 g",
                "Lens_Mount": "Canon EF-M"
            },
            "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&q=80"
        },
        {
            "name": "Nikon D3500 Kit",
            "category": "camera",
            "price": 36990.0,
            "rating": 4.4,
            "description": "Classic entry-level DSLR camera with 18-55mm lens. Great battery life and direct manual dials to learn photography.",
            "specs": {
                "Sensor": "APS-C CMOS",
                "Resolution": "24.2 Megapixels",
                "Video": "Full HD 60p",
                "Weight": "365 g",
                "Lens_Mount": "Nikon F"
            },
            "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&q=80"
        },
        {
            "name": "Sony Alpha ILCE-6400",
            "category": "camera",
            "price": 71990.0,
            "rating": 4.7,
            "description": "Ideal for vloggers and creators. Features 0.02s real-time autofocus speed, 180-degree flip screen, and ISO up to 32000.",
            "specs": {
                "Sensor": "APS-C Exmor CMOS",
                "Resolution": "24.2 Megapixels",
                "Video": "4K HDR 30p",
                "Weight": "403 g",
                "Lens_Mount": "Sony E-mount"
            },
            "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500&q=80"
        },
        {
            "name": "GoPro HERO 11 Black",
            "category": "camera",
            "price": 38990.0,
            "rating": 4.5,
            "description": "The ultimate action camera. Features HyperSmooth 5.0 stabilization, waterproof design, and dual LCD screens.",
            "specs": {
                "Sensor": "1/1.9 inch CMOS",
                "Resolution": "27 Megapixels",
                "Video": "5.3K 60fps / 4K 120fps",
                "Weight": "154 g",
                "Lens_Mount": "Built-in action mount"
            },
            "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500&q=80"
        },
        
        # --- WATCHES ---
        {
            "name": "Noise ColorFit Pulse 3",
            "category": "smartwatch",
            "price": 1799.0,
            "rating": 3.7,
            "description": "1.96-inch curved screen, Bluetooth calling, 100+ sports modes, and smart notification alerts.",
            "specs": {
                "Screen": "1.96 inch TFT LCD",
                "Battery": "7 days",
                "Sensors": "Heart Rate, SpO2",
                "Water_Resistance": "IP68 Water Resistant",
                "Calling": "Bluetooth Calling Support"
            },
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80"
        },
        {
            "name": "OnePlus Nord Watch",
            "category": "smartwatch",
            "price": 4499.0,
            "rating": 4.1,
            "description": "AMOLED screen, 105 sports modes, dynamic heart tracking, sleep metrics, and visual notification chips.",
            "specs": {
                "Screen": "1.78 inch AMOLED",
                "Battery": "10 days",
                "Sensors": "Heart Rate, SpO2, Accelerometer",
                "Water_Resistance": "IP68",
                "Calling": "Notifications Only"
            },
            "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=500&q=80"
        },
        {
            "name": "Samsung Galaxy Watch 4",
            "category": "smartwatch",
            "price": 10999.0,
            "rating": 4.4,
            "description": "Wear OS powered by Samsung, body composition analysis, Google Maps navigation, sleep quality tracking.",
            "specs": {
                "Screen": "1.4 inch Super AMOLED",
                "Battery": "40 hours",
                "Sensors": "BIA Sensor, ECG, Heart Rate, SpO2, GPS",
                "Water_Resistance": "5ATM + IP68",
                "Calling": "Bluetooth / LTE Supported"
            },
            "image_url": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80"
        },
        {
            "name": "Amazfit GTR 4",
            "category": "smartwatch",
            "price": 16999.0,
            "rating": 4.5,
            "description": "Dual-band circularly-polarized GPS antenna, 150+ sports modes, ultra-long 14-day battery cycle.",
            "specs": {
                "Screen": "1.43 inch AMOLED",
                "Battery": "14 days",
                "Sensors": "BioTracker 4.0, GPS, Gyro, Compass",
                "Water_Resistance": "5ATM Waterproof",
                "Calling": "Bluetooth Phone Calls & Music Storage"
            },
            "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=500&q=80"
        },
        {
            "name": "Apple Watch SE (Gen 2)",
            "category": "smartwatch",
            "price": 27900.0,
            "rating": 4.7,
            "description": "Retina display, crash detection, workout tracking, heart rate notifications, swimproof structure.",
            "specs": {
                "Screen": "1.78 inch Retina OLED",
                "Battery": "18 hours",
                "Sensors": "Optical Heart Rate, GPS, Altimeter, Gyro",
                "Water_Resistance": "50m Swimproof",
                "Calling": "Bluetooth / Cellular Support"
            },
            "image_url": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80"
        }
    ]
    
    for p in products:
        cursor.execute(
            'INSERT INTO products (name, category, price, rating, description, specs, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (p['name'], p['category'], p['price'], p['rating'], p['description'], json.dumps(p['specs']), p['image_url'])
        )
        
    # Add dummy users if they don't exist
    admin_pw = generate_password_hash("admin123")
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)',
        ("admin", admin_pw, 1)
    )
    
    user_pw = generate_password_hash("user123")
    cursor.execute(
        'INSERT OR IGNORE INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)',
        ("user", user_pw, 0)
    )
    
    conn.commit()
    conn.close()
    print("Database successfully seeded with expanded 30+ product catalog!")

if __name__ == "__main__":
    seed_db()
