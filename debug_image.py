import requests

def test_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        print(f"URL: {url}")
        print(f"Status: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")
        print(f"Length: {len(resp.content)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test a typical Myntra asset URL
    test_url("https://assets.myntassets.com/h_1440,q_90,w_1080/v1/assets/images/13646282/2021/3/12/119a0a4c-5a3d-4c3e-8c6c-9a4d3a2b1c0a1615546252431-T-shirt-1.jpg")
