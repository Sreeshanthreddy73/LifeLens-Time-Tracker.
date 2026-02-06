# Get Your Computer's IP Address
# Run this to find your IP for accessing from phone

import socket

def get_ip():
    try:
        # Connect to an external server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to get IP"

if __name__ == "__main__":
    ip = get_ip()
    print("\n" + "="*50)
    print("🌐 YOUR COMPUTER'S IP ADDRESS")
    print("="*50)
    print(f"\nIP Address: {ip}")
    print(f"\nAccess your app from phone:")
    print(f"http://{ip}:5001")
    print("\n" + "="*50)
    print("\n📱 Make sure your phone and computer are on the SAME WiFi network!")
    print("\n")
